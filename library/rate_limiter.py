import time

class CalendarMinuteRateLimiter:
    def __init__(self, requests_per_minute=5):
        self.requests_per_minute = requests_per_minute
        self.current_minute = int(time.time() // 60)
        self.request_count = 0

    def wait_if_needed(self):
        now = time.time()
        minute = int(now // 60)

        # minute changed → reset everything
        if minute != self.current_minute:
            self.current_minute = minute
            self.request_count = 0

        # limit reached → wait for next minute boundary
        if self.request_count >= self.requests_per_minute:
            sleep_time = (minute + 1) * 60 - now
            if sleep_time > 0:
                time.sleep(sleep_time)

            # start fresh minute
            self.current_minute = int(time.time() // 60)
            self.request_count = 0

        self.request_count += 1
