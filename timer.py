import time
import threading


YELLOW_THRESHOLD = 10 * 60  # 10 minutes in seconds
RED_THRESHOLD = 15 * 60     # 15 minutes in seconds


class AlertSender:
    """Base class for sending alerts to devices."""

    def send(self, alert_level, message):
        raise NotImplementedError


class SmartphoneAlertSender(AlertSender):
    """Sends push notifications to a smartphone."""

    def __init__(self, device_id):
        self.device_id = device_id

    def send(self, alert_level, message):
        # TODO: Integrate with a push notification service (e.g. Firebase, APNs)
        print(f"[{alert_level.upper()}] -> Device {self.device_id}: {message}")


class MachineTimer:
    """Tracks usage time on a gym machine and sends alerts when thresholds are exceeded."""

    def __init__(self, machine_name, alert_sender):
        self.machine_name = machine_name
        self.alert_sender = alert_sender
        self._start_time = None
        self._running = False
        self._yellow_sent = False
        self._red_sent = False
        self._monitor_thread = None

    def start(self):
        """Start tracking machine usage."""
        self._start_time = time.time()
        self._running = True
        self._yellow_sent = False
        self._red_sent = False
        print(f"Timer started for {self.machine_name}")
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def stop(self):
        """Stop tracking and reset the timer."""
        self._running = False
        elapsed = self.elapsed_seconds()
        self._start_time = None
        print(f"Timer stopped for {self.machine_name} after {elapsed:.0f}s")
        return elapsed

    def elapsed_seconds(self):
        """Return how many seconds have passed since the timer started."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def _monitor_single_check(self):
        """Run one check against thresholds and send alerts if needed."""
        elapsed = self.elapsed_seconds()

        if not self._yellow_sent and elapsed >= YELLOW_THRESHOLD:
            self.alert_sender.send(
                "yellow",
                f"You've been on {self.machine_name} for over 10 minutes. "
                "Consider wrapping up so others can use it."
            )
            self._yellow_sent = True

        if not self._red_sent and elapsed >= RED_THRESHOLD:
            self.alert_sender.send(
                "red",
                f"You've been on {self.machine_name} for over 15 minutes. "
                "Please finish up — others are waiting."
            )
            self._red_sent = True

    def _monitor(self):
        """Background loop that checks thresholds and sends alerts."""
        while self._running:
            self._monitor_single_check()

            if self._red_sent:
                break

            time.sleep(1)


if __name__ == "__main__":
    sender = SmartphoneAlertSender(device_id="user-phone-001")
    timer = MachineTimer("Leg Press #3", alert_sender=sender)

    timer.start()
    try:
        while timer._running:
            time.sleep(1)
    except KeyboardInterrupt:
        timer.stop()
        print("Session ended by user.")
