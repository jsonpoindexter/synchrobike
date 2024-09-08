import asyncio
import iterm2
import os
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
import argparse
import time

# Define the iTerm2 window title variable name
ITERM2_HOST_WINDOW_VAR = "ESP Serial Monitor Window"

async def list_serial_ports():
    """
    List all available serial ports, filtering for specific devices.
    """
    system_platform = platform.system()
    if system_platform == "Windows":
        available_ports = ['COM{}'.format(i + 1) for i in range(256)]
        return [port for port in available_ports if check_port_exists(port)]
    elif system_platform == "Darwin":
        # Only list 'tty.usbserial' ports for macOS (Darwin)
        available_ports = [port for port in os.listdir('/dev/') if 'tty.usbserial' in port]
        return ['/dev/' + port for port in available_ports]
    else:
        available_ports = [port for port in os.listdir('/dev/') if 'ttyUSB' in port]
        return ['/dev/' + port for port in available_ports]

def check_port_exists(port):
    """
    Check if the specified port exists.
    """
    try:
        with open(port):
            return True
    except Exception:
        return False

async def build_firmware(env, verbose=False):
    """
    Build the firmware for the specified environment.
    """
    print(f"Building firmware for environment {env}...")
    command = ["pio", "run", "-e", env]
    if verbose:
        command.append("--verbose")

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"Successfully built firmware for environment {env}.")
        if verbose:
            print(result.stdout.decode())
        return True
    else:
        print(f"Failed to build firmware for environment {env}.\nError: {result.stderr.decode()}")
        return False

def upload_firmware(port, env, verbose=False):
    """
    Upload the pre-built firmware to the device connected to the specified serial port.
    """
    print(f"Uploading firmware to device on port {port}...")
    command = ["pio", "run", "--target", "upload", "-e", env, "--upload-port", port]
    if verbose:
        command.append("--verbose")

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"Successfully uploaded firmware to device on port {port}.")
        if verbose:
            print(result.stdout.decode())
    else:
        print(f"Failed to upload firmware to device on port {port}.\nError: {result.stderr.decode()}")

async def get_iterm2_window(connection):
    """
    Get the dedicated iTerm2 window for monitoring.
    """
    app = await iterm2.async_get_app(connection)
    windows = app.terminal_windows

    # Check if the dedicated window already exists using a custom variable
    for window in windows:
        title = await window.async_get_variable("user.monitor_window")
        if title == ITERM2_HOST_WINDOW_VAR:
            return window

    return None

async def create_or_reuse_iterm2_window(connection):
    """
    Create a dedicated iTerm2 window for monitoring or reuse it if it already exists.
    """
    window = await get_iterm2_window(connection)

    # Create a new window if it doesn't exist
    if window is None:
        window = await iterm2.Window.async_create(connection)
        await window.async_set_variable("user.monitor_window", ITERM2_HOST_WINDOW_VAR)
    return window

async def stop_monitoring_for_existing_panes(connection):
    """
    Send CTRL-C to existing panes in the dedicated iTerm2 window to stop current monitoring.
    """
    window = await get_iterm2_window(connection)
    if window:
        for tab in window.tabs:
            for session in tab.sessions:
                # send CTRL+C to stop the serial monitor
                await session.async_send_text("\x03")

async def close_disconnected_sessions(connection, current_ports):
    """
    Close sessions in iTerm2 that are no longer associated with a connected port.
    """
    window = await get_iterm2_window(connection)
    if window:
        for tab in window.tabs:
            for session in tab.sessions:
                # Retrieve the port associated with the session
                port = await session.async_get_variable("user.monitor_port")
                if port and port not in current_ports:
                    # Close sessions that are no longer connected
                    await session.async_close()

async def manage_monitoring_panes(connection, ports, split_direction="vertical"):
    """
    Manage monitoring panes: reuse existing ones for the same ports, remove those for disconnected ports, and add new ones for newly connected ports.
    """
    window = await create_or_reuse_iterm2_window(connection)

    # Create a mapping of sessions for currently connected ports
    session_port_map = {}
    for tab in window.tabs:
        for session in tab.sessions:
            # Retrieve the custom variable for the session
            port = await session.async_get_variable("monitor_port")
            if port:
                session_port_map[port] = session

    # Iterate over currently connected ports and manage sessions
    for port in ports:
        if port in session_port_map:
            # Reuse existing session for this port
            session = session_port_map[port]
            # Send the serial monitor command again to resume monitoring
            await session.async_send_text(f"pio device monitor --port {port} --baud 115200\n")
            del session_port_map[port]  # Remove from the map, as it's still valid
        else:
            # Create a new pane for new ports
            if window.current_tab:
                current_session = window.current_tab.current_session
                new_session = await current_session.async_split_pane(vertical=(split_direction == "vertical"))
                await new_session.async_set_variable(   "user.monitor_port", port)  # Set the custom variable to identify the session
                await new_session.async_send_text(f"pio device monitor --port {port} --baud 115200\n")

    # Close sessions that no longer have corresponding ports connected
    for session in session_port_map.values():
        await session.async_close()

async def main(connection):
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Flash and optionally monitor ESP8266 devices.")
    parser.add_argument('--monitor', action='store_true', help="Open a monitor for each flashed device.")
    parser.add_argument('--build', action='store_true', help="Build the firmware before uploading.")
    parser.add_argument('--upload', action='store_true', help="Upload firmware to connected devices.")
    parser.add_argument('--split', choices=['vertical', 'horizontal'], default='vertical', help="Split direction for iTerm2 panes.")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose output for PlatformIO operations.")
    args = parser.parse_args()

    env = "d1_mini"

    # Stop existing monitoring to allow uploads to complete
    await stop_monitoring_for_existing_panes(connection)

    # Build the firmware if the --build argument is specified
    if args.build:
        build_success = await build_firmware(env, args.verbose)
        if not build_success:
            print("Build failed. Exiting.")
            return

    ports = await list_serial_ports()
    print(f"Found ports: {ports}")
    if not ports:
        print("No devices found.")
        return

    # Upload firmware to devices in parallel if the --upload argument is specified
    if args.upload:
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(executor, upload_firmware, port, env, args.verbose) for port in ports]
            await asyncio.gather(*tasks)

    # Monitor devices if the --monitor argument is specified
    if args.monitor:
        time.sleep(2)  # Delay to ensure all upload processes are done
        await manage_monitoring_panes(connection, ports, args.split)

if __name__ == "__main__":
    iterm2.run_until_complete(main)