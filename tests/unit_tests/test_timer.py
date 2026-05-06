import unittest
from unittest.mock import patch, MagicMock

from timer import (
    MachineTimer,
    SmartphoneAlertSender,
    AlertSender,
    YELLOW_THRESHOLD,
    RED_THRESHOLD,
)


class TestAlertSender(unittest.TestCase):
    """Tests for the AlertSender base class."""

    def test_base_send_raises_not_implemented(self):
        sender = AlertSender()
        with self.assertRaises(NotImplementedError):
            sender.send("yellow", "test")


class TestSmartphoneAlertSender(unittest.TestCase):
    """Tests for the SmartphoneAlertSender."""

    def test_send_prints_alert(self, ):
        sender = SmartphoneAlertSender(device_id="phone-123")
        with patch("builtins.print") as mock_print:
            sender.send("yellow", "Wrap it up")
            mock_print.assert_called_once_with(
                "[YELLOW] -> Device phone-123: Wrap it up"
            )

    def test_device_id_stored(self):
        sender = SmartphoneAlertSender(device_id="phone-456")
        self.assertEqual(sender.device_id, "phone-456")


class TestMachineTimerInit(unittest.TestCase):
    """Tests for MachineTimer initialization."""

    def setUp(self):
        self.sender = MagicMock(spec=AlertSender)
        self.timer = MachineTimer("Bench Press #1", self.sender)

    def test_initial_state(self):
        self.assertEqual(self.timer.machine_name, "Bench Press #1")
        self.assertFalse(self.timer._running)
        self.assertIsNone(self.timer._start_time)
        self.assertFalse(self.timer._yellow_sent)
        self.assertFalse(self.timer._red_sent)

    def test_elapsed_seconds_before_start(self):
        self.assertEqual(self.timer.elapsed_seconds(), 0.0)


class TestMachineTimerStartStop(unittest.TestCase):
    """Tests for starting and stopping the timer."""

    def setUp(self):
        self.sender = MagicMock(spec=AlertSender)
        self.timer = MachineTimer("Treadmill #2", self.sender)

    @patch("timer.time")
    @patch("timer.threading")
    def test_start_sets_running(self, mock_threading, mock_time):
        mock_time.time.return_value = 1000.0
        self.timer.start()
        self.assertTrue(self.timer._running)
        self.assertEqual(self.timer._start_time, 1000.0)

    @patch("timer.time")
    @patch("timer.threading")
    def test_start_resets_alert_flags(self, mock_threading, mock_time):
        mock_time.time.return_value = 1000.0
        self.timer._yellow_sent = True
        self.timer._red_sent = True
        self.timer.start()
        self.assertFalse(self.timer._yellow_sent)
        self.assertFalse(self.timer._red_sent)

    @patch("timer.time")
    def test_stop_returns_elapsed(self, mock_time):
        mock_time.time.return_value = 1300.0
        self.timer._start_time = 1000.0
        self.timer._running = True
        elapsed = self.timer.stop()
        self.assertAlmostEqual(elapsed, 300.0)
        self.assertFalse(self.timer._running)
        self.assertIsNone(self.timer._start_time)


class TestMachineTimerElapsed(unittest.TestCase):
    """Tests for elapsed time calculation."""

    def setUp(self):
        self.sender = MagicMock(spec=AlertSender)
        self.timer = MachineTimer("Cable Machine", self.sender)

    @patch("timer.time")
    def test_elapsed_seconds(self, mock_time):
        self.timer._start_time = 1000.0
        mock_time.time.return_value = 1120.0
        self.assertAlmostEqual(self.timer.elapsed_seconds(), 120.0)


class TestMachineTimerAlerts(unittest.TestCase):
    """Tests for the alert monitoring logic."""

    def setUp(self):
        self.sender = MagicMock(spec=AlertSender)
        self.timer = MachineTimer("Squat Rack", self.sender)

    def test_no_alert_before_yellow_threshold(self):
        self.timer._running = True
        self.timer._start_time = 0
        with patch("timer.time") as mock_time:
            mock_time.time.return_value = YELLOW_THRESHOLD - 1
            # Simulate one iteration of _monitor
            self.timer._monitor_single_check()
        self.sender.send.assert_not_called()
        self.assertFalse(self.timer._yellow_sent)

    def test_yellow_alert_at_threshold(self):
        self.timer._running = True
        self.timer._start_time = 0
        with patch("timer.time") as mock_time:
            mock_time.time.return_value = YELLOW_THRESHOLD
            self.timer._monitor_single_check()
        self.sender.send.assert_called_once()
        args = self.sender.send.call_args
        self.assertEqual(args[0][0], "yellow")
        self.assertTrue(self.timer._yellow_sent)

    def test_red_alert_at_threshold(self):
        self.timer._running = True
        self.timer._start_time = 0
        self.timer._yellow_sent = True
        with patch("timer.time") as mock_time:
            mock_time.time.return_value = RED_THRESHOLD
            self.timer._monitor_single_check()
        self.sender.send.assert_called_once()
        args = self.sender.send.call_args
        self.assertEqual(args[0][0], "red")
        self.assertTrue(self.timer._red_sent)

    def test_yellow_not_sent_twice(self):
        self.timer._running = True
        self.timer._start_time = 0
        self.timer._yellow_sent = True
        with patch("timer.time") as mock_time:
            mock_time.time.return_value = RED_THRESHOLD
            self.timer._monitor_single_check()
        # Only red should be sent, not yellow again
        self.sender.send.assert_called_once()
        args = self.sender.send.call_args
        self.assertEqual(args[0][0], "red")

    def test_both_alerts_sent_at_red_threshold(self):
        self.timer._running = True
        self.timer._start_time = 0
        with patch("timer.time") as mock_time:
            mock_time.time.return_value = RED_THRESHOLD
            self.timer._monitor_single_check()
        # Both yellow and red should fire
        self.assertEqual(self.sender.send.call_count, 2)
        self.assertTrue(self.timer._yellow_sent)
        self.assertTrue(self.timer._red_sent)


class TestThresholdConstants(unittest.TestCase):
    """Tests that threshold constants are correct."""

    def test_yellow_threshold_is_10_minutes(self):
        self.assertEqual(YELLOW_THRESHOLD, 600)

    def test_red_threshold_is_15_minutes(self):
        self.assertEqual(RED_THRESHOLD, 900)


if __name__ == "__main__":
    unittest.main()
