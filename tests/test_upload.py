import contextlib
import io
import unittest

import upload


class ArgumentTests(unittest.TestCase):
    def test_requires_an_action(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                upload.parse_args([])

    def test_rejects_build_with_no_build(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                upload.parse_args(["--build", "--upload", "--no-build"])

    def test_accepts_repeatable_ports(self):
        args = upload.parse_args(
            ["--upload", "--port", "/dev/one", "--port", "/dev/two"]
        )
        self.assertEqual(args.port, ["/dev/one", "/dev/two"])


class PortDiscoveryTests(unittest.TestCase):
    def test_selects_usb_devices_and_skips_bluetooth(self):
        usb_with_id = upload.SerialDevice("COM4", vid=0x1A86, pid=0x7523)
        usb_by_name = upload.SerialDevice("/dev/cu.usbserial-123")
        bluetooth = upload.SerialDevice("/dev/cu.Bluetooth-Incoming-Port")

        self.assertTrue(upload.is_usb_serial_device(usb_with_id))
        self.assertTrue(upload.is_usb_serial_device(usb_by_name))
        self.assertFalse(upload.is_usb_serial_device(bluetooth))

    def test_explicit_ports_override_discovery_and_are_deduplicated(self):
        devices = [upload.SerialDevice("/dev/ttyUSB0", vid=1, pid=2)]
        ports = upload.resolve_ports(["custom", "custom", "other"], devices)
        self.assertEqual(ports, ["custom", "other"])

    def test_automatic_ports_are_sorted(self):
        devices = [
            upload.SerialDevice("/dev/ttyUSB2", vid=1, pid=2),
            upload.SerialDevice("/dev/ttyUSB1", vid=1, pid=3),
        ]
        self.assertEqual(
            upload.resolve_ports([], devices),
            ["/dev/ttyUSB1", "/dev/ttyUSB2"],
        )


class CommandTests(unittest.TestCase):
    def test_build_command(self):
        self.assertEqual(
            upload.build_command("d1_mini", verbose=True),
            ["pio", "run", "-e", "d1_mini", "-v"],
        )

    def test_upload_command_flashes_the_built_image_directly(self):
        self.assertEqual(
            upload.upload_command("d1_mini", "/dev/ttyUSB0"),
            [
                "pio",
                "pkg",
                "exec",
                "-p",
                "platformio/tool-esptoolpy@1.30000.201119",
                "--",
                "esptool.py",
                "--before",
                "default_reset",
                "--after",
                "hard_reset",
                "--chip",
                "esp8266",
                "--port",
                "/dev/ttyUSB0",
                "--baud",
                "115200",
                "write_flash",
                "0x0",
                ".pio/build/d1_mini/firmware.bin",
            ],
        )

    def test_monitor_command_quotes_port(self):
        self.assertEqual(
            upload.monitor_command("/dev/port with spaces"),
            "pio device monitor --port '/dev/port with spaces' --baud 115200",
        )


class UploadTests(unittest.TestCase):
    def test_retries_failed_upload_and_reports_success(self):
        calls = 0

        def runner(_command):
            nonlocal calls
            calls += 1
            return upload.CommandResult(1 if calls == 1 else 0, f"attempt {calls}")

        result = upload.upload_firmware(
            "/dev/ttyUSB0",
            "d1_mini",
            retries=2,
            runner=runner,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.attempts, 2)
        self.assertIn("attempt 1", result.output)
        self.assertIn("attempt 2", result.output)

    def test_aggregates_results_in_port_order(self):
        attempts = {"one": 0, "two": 0}

        def runner(command):
            port = command[command.index("--port") + 1]
            attempts[port] += 1
            if port == "two":
                return upload.CommandResult(1, "failed")
            return upload.CommandResult(0, "ok")

        with contextlib.redirect_stdout(io.StringIO()):
            results = upload.upload_to_ports(
                ["one", "two"],
                "d1_mini",
                jobs=1,
                retries=1,
                runner=runner,
            )

        self.assertEqual([result.port for result in results], ["one", "two"])
        self.assertTrue(results[0].success)
        self.assertFalse(results[1].success)
        self.assertEqual(attempts, {"one": 1, "two": 2})

    def test_dry_run_does_not_execute_commands(self):
        def runner(_command):
            raise AssertionError("runner must not be called during a dry run")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = upload.main(
                [
                    "--upload",
                    "--monitor",
                    "--port",
                    "/dev/fake-one",
                    "--port",
                    "/dev/fake-two",
                    "--dry-run",
                ],
                runner=runner,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("pio run -e d1_mini", output.getvalue())
        self.assertIn("--port /dev/fake-one", output.getvalue())
        self.assertIn("iTerm2: pio device monitor", output.getvalue())


class ItermTests(unittest.TestCase):
    def test_monitoring_is_macos_only(self):
        with self.assertRaisesRegex(RuntimeError, "requires macOS"):
            upload.load_iterm2(platform_name="linux")

    def test_missing_iterm_dependency_has_clear_error(self):
        def missing(_name):
            raise ImportError("missing")

        with self.assertRaisesRegex(RuntimeError, "iTerm2 Python package"):
            upload.load_iterm2(platform_name="darwin", importer=missing)


if __name__ == "__main__":
    unittest.main()
