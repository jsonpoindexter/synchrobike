from __future__ import annotations

import argparse
import asyncio
import importlib
import os
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


DEFAULT_ENVIRONMENT = "d1_mini"
DEFAULT_MONITOR_BAUD = 115200
DEFAULT_UPLOAD_BAUD = 115200
DEFAULT_RETRIES = 2
ESPTOOL_PACKAGE = "platformio/tool-esptoolpy@1.30000.201119"
ITERM2_MONITOR_WINDOW = "ESP Serial Monitor Window"
PROJECT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class SerialDevice:
    device: str
    description: str = ""
    hwid: str = ""
    vid: int | None = None
    pid: int | None = None


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    output: str = ""


@dataclass(frozen=True)
class UploadResult:
    port: str
    success: bool
    attempts: int
    output: str = ""


CommandRunner = Callable[[Sequence[str]], CommandResult]


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be at least 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, flash, and optionally monitor one or more ESP8266 devices."
    )
    parser.add_argument("--build", action="store_true", help="Build the firmware.")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Build once and upload to every selected port in parallel.",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Open or reuse an iTerm2 serial-monitor pane for every selected port.",
    )
    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List detected serial ports and mark ports selected automatically.",
    )
    parser.add_argument(
        "--port",
        action="append",
        default=[],
        metavar="PORT",
        help="Use an explicit serial port. Repeat for multiple devices.",
    )
    parser.add_argument(
        "--environment",
        default=DEFAULT_ENVIRONMENT,
        help=f"PlatformIO environment (default: {DEFAULT_ENVIRONMENT}).",
    )
    parser.add_argument(
        "--jobs",
        type=positive_int,
        help="Maximum concurrent uploads (default: number of selected ports).",
    )
    parser.add_argument(
        "--retries",
        type=nonnegative_int,
        default=DEFAULT_RETRIES,
        help=f"Retries after a failed upload (default: {DEFAULT_RETRIES}).",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Upload the existing firmware without rebuilding it first.",
    )
    parser.add_argument(
        "--split",
        choices=("vertical", "horizontal"),
        default="vertical",
        help="Direction for new iTerm2 monitor panes (default: vertical).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print build, upload, and monitor commands without running them.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show command output, including successful uploads.",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not any((args.build, args.upload, args.monitor, args.list_ports)):
        parser.error(
            "choose at least one action: --build, --upload, --monitor, or --list-ports"
        )
    if args.no_build and not args.upload:
        parser.error("--no-build requires --upload")
    if args.no_build and args.build:
        parser.error("--build and --no-build cannot be used together")

    return args


def list_serial_devices() -> list[SerialDevice]:
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise RuntimeError(
            "PySerial is required for port discovery; install requirements.txt first"
        ) from exc

    return [
        SerialDevice(
            device=port.device,
            description=port.description or "",
            hwid=port.hwid or "",
            vid=port.vid,
            pid=port.pid,
        )
        for port in list_ports.comports()
    ]


def is_usb_serial_device(port: SerialDevice) -> bool:
    if port.vid is not None:
        return True

    details = " ".join((port.device, port.description, port.hwid)).lower()
    usb_markers = (
        "usbserial",
        "usbmodem",
        "ttyusb",
        "ttyacm",
        "wchusb",
        "ch340",
        "cp210",
        "ftdi",
        "usb vid:",
    )
    return any(marker in details for marker in usb_markers)


def deduplicate_ports(ports: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(ports))


def resolve_ports(
    explicit_ports: Sequence[str], devices: Sequence[SerialDevice]
) -> list[str]:
    if explicit_ports:
        return deduplicate_ports(explicit_ports)
    return sorted(port.device for port in devices if is_usb_serial_device(port))


def print_serial_devices(devices: Sequence[SerialDevice]) -> None:
    if not devices:
        print("No serial ports detected.")
        return

    for port in sorted(devices, key=lambda item: item.device):
        selected = "auto" if is_usb_serial_device(port) else "skip"
        usb_id = ""
        if port.vid is not None and port.pid is not None:
            usb_id = f" [{port.vid:04x}:{port.pid:04x}]"
        description = f" - {port.description}" if port.description else ""
        print(f"{port.device}{usb_id}{description} ({selected})")


def build_command(environment: str, verbose: bool = False) -> list[str]:
    command = ["pio", "run", "-e", environment]
    if verbose:
        command.append("-v")
    return command


def firmware_path(environment: str) -> str:
    return os.path.join(".pio", "build", environment, "firmware.bin")


def upload_command(environment: str, port: str) -> list[str]:
    return [
        "pio",
        "pkg",
        "exec",
        "-p",
        ESPTOOL_PACKAGE,
        "--",
        "esptool.py",
        "--before",
        "default_reset",
        "--after",
        "hard_reset",
        "--chip",
        "esp8266",
        "--port",
        port,
        "--baud",
        str(DEFAULT_UPLOAD_BAUD),
        "write_flash",
        "0x0",
        firmware_path(environment),
    ]


def monitor_command(port: str) -> str:
    return (
        "pio device monitor "
        f"--port {shlex.quote(port)} --baud {DEFAULT_MONITOR_BAUD}"
    )


def format_command(command: Sequence[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def run_command(command: Sequence[str]) -> CommandResult:
    try:
        completed = subprocess.run(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            cwd=PROJECT_DIR,
        )
    except OSError as exc:
        return CommandResult(returncode=127, output=str(exc))
    return CommandResult(completed.returncode, completed.stdout or "")


def build_firmware(
    environment: str,
    *,
    verbose: bool = False,
    dry_run: bool = False,
    runner: CommandRunner = run_command,
) -> bool:
    command = build_command(environment, verbose)
    if dry_run:
        print(f"[dry-run] {format_command(command)}")
        return True

    print(f"Building firmware for {environment}...")
    result = runner(command)
    if result.output and (verbose or result.returncode != 0):
        print(result.output.rstrip())
    if result.returncode != 0:
        print(f"Firmware build failed for {environment}.", file=sys.stderr)
        return False

    print(f"Firmware build succeeded for {environment}.")
    return True


def upload_firmware(
    port: str,
    environment: str,
    *,
    retries: int,
    verbose: bool = False,
    runner: CommandRunner = run_command,
) -> UploadResult:
    command = upload_command(environment, port)
    outputs: list[str] = []

    for attempt in range(1, retries + 2):
        result = runner(command)
        if result.output:
            outputs.append(result.output.rstrip())
        if result.returncode == 0:
            return UploadResult(port, True, attempt, "\n".join(outputs))

    return UploadResult(port, False, retries + 1, "\n".join(outputs))


def upload_to_ports(
    ports: Sequence[str],
    environment: str,
    *,
    jobs: int | None,
    retries: int,
    verbose: bool = False,
    dry_run: bool = False,
    runner: CommandRunner = run_command,
) -> list[UploadResult]:
    if dry_run:
        results = []
        for port in ports:
            print(f"[dry-run] {format_command(upload_command(environment, port))}")
            results.append(UploadResult(port, True, 1))
        return results

    worker_count = min(jobs or len(ports), len(ports))
    completed_results: dict[str, UploadResult] = {}
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(
                upload_firmware,
                port,
                environment,
                retries=retries,
                verbose=verbose,
                runner=runner,
            ): port
            for port in ports
        }
        for future in as_completed(futures):
            result = future.result()
            completed_results[result.port] = result
            status = "succeeded" if result.success else "failed"
            print(
                f"Upload {status} on {result.port} "
                f"after {result.attempts} attempt(s)."
            )
            if result.output and (verbose or not result.success):
                print(result.output)

    return [completed_results[port] for port in ports]


def load_iterm2(
    *,
    platform_name: str = sys.platform,
    importer: Callable[[str], object] = importlib.import_module,
):
    if platform_name != "darwin":
        raise RuntimeError("--monitor requires macOS and iTerm2")
    try:
        return importer("iterm2")
    except ImportError as exc:
        raise RuntimeError(
            "--monitor requires the iTerm2 Python package; install requirements.txt first"
        ) from exc


async def find_monitor_window(connection, iterm2_module):
    app = await iterm2_module.async_get_app(connection)
    for window in app.terminal_windows:
        marker = await window.async_get_variable("user.monitor_window")
        if marker == ITERM2_MONITOR_WINDOW:
            return window
    return None


async def create_or_reuse_monitor_window(connection, iterm2_module):
    window = await find_monitor_window(connection, iterm2_module)
    if window is None:
        window = await iterm2_module.Window.async_create(connection)
        await window.async_set_variable("user.monitor_window", ITERM2_MONITOR_WINDOW)
    return window


def window_sessions(window) -> list:
    return [session for tab in window.tabs for session in tab.sessions]


async def stop_monitoring(connection, iterm2_module) -> None:
    window = await find_monitor_window(connection, iterm2_module)
    if window is None:
        return
    for session in window_sessions(window):
        port = await session.async_get_variable("user.monitor_port")
        if port:
            await session.async_send_text("\x03")


async def manage_monitoring_panes(
    connection,
    iterm2_module,
    ports: Sequence[str],
    split_direction: str,
) -> None:
    window = await create_or_reuse_monitor_window(connection, iterm2_module)
    existing: dict[str, object] = {}
    reusable: list[object] = []

    for session in window_sessions(window):
        port = await session.async_get_variable("user.monitor_port")
        if port in ports and port not in existing:
            existing[port] = session
        else:
            reusable.append(session)

    anchor = next(iter(existing.values()), None)
    for port in ports:
        session = existing.get(port)
        if session is None:
            if reusable:
                session = reusable.pop(0)
                await session.async_send_text("\x03")
            else:
                if anchor is None:
                    if window.current_tab is None:
                        raise RuntimeError("iTerm2 monitor window has no active tab")
                    anchor = window.current_tab.current_session
                session = await anchor.async_split_pane(
                    vertical=(split_direction == "vertical")
                )
            await session.async_set_variable("user.monitor_port", port)
            existing[port] = session
            anchor = session
        await session.async_send_text(f"{monitor_command(port)}\n")

    for session in reusable:
        await session.async_close()


def stop_iterm_monitors(iterm2_module) -> None:
    async def run(connection):
        await stop_monitoring(connection, iterm2_module)

    try:
        iterm2_module.run_until_complete(run)
    except Exception as exc:
        raise RuntimeError(f"could not stop iTerm2 monitors: {exc}") from exc


def start_iterm_monitors(
    iterm2_module,
    ports: Sequence[str],
    split_direction: str,
    *,
    delay: float = 0,
) -> None:
    async def run(connection):
        if delay:
            await asyncio.sleep(delay)
        await manage_monitoring_panes(
            connection, iterm2_module, ports, split_direction
        )

    try:
        iterm2_module.run_until_complete(run)
    except Exception as exc:
        raise RuntimeError(f"could not start iTerm2 monitors: {exc}") from exc


def main(
    argv: Sequence[str] | None = None, *, runner: CommandRunner = run_command
) -> int:
    args = parse_args(argv)
    needs_ports = args.upload or args.monitor
    devices: list[SerialDevice] = []

    try:
        if args.list_ports or (needs_ports and not args.port):
            devices = list_serial_devices()
        if args.list_ports:
            print_serial_devices(devices)

        ports = resolve_ports(args.port, devices) if needs_ports else []
        if needs_ports and not ports:
            print(
                "No USB serial devices found; connect a device or pass --port explicitly.",
                file=sys.stderr,
            )
            return 1

        iterm2_module = None
        if args.monitor and not args.dry_run:
            iterm2_module = load_iterm2()

        should_build = args.build or (args.upload and not args.no_build)
        if should_build and not build_firmware(
            args.environment,
            verbose=args.verbose,
            dry_run=args.dry_run,
            runner=runner,
        ):
            return 1

        if args.monitor and not args.dry_run:
            stop_iterm_monitors(iterm2_module)

        upload_results: list[UploadResult] = []
        if args.upload:
            image_path = firmware_path(args.environment)
            if not args.dry_run and not (PROJECT_DIR / image_path).is_file():
                print(
                    f"Firmware image not found at {image_path}; "
                    "build first or omit --no-build.",
                    file=sys.stderr,
                )
                return 1
            upload_results = upload_to_ports(
                ports,
                args.environment,
                jobs=args.jobs,
                retries=args.retries,
                verbose=args.verbose,
                dry_run=args.dry_run,
                runner=runner,
            )

        if args.monitor:
            monitor_ports = (
                [result.port for result in upload_results if result.success]
                if args.upload
                else ports
            )
            if args.dry_run:
                for port in monitor_ports:
                    print(f"[dry-run] iTerm2: {monitor_command(port)}")
            elif monitor_ports:
                start_iterm_monitors(
                    iterm2_module,
                    monitor_ports,
                    args.split,
                    delay=2 if args.upload else 0,
                )

        if upload_results and not all(result.success for result in upload_results):
            return 1
        return 0
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
