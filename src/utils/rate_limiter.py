from datetime import datetime
import time

class RateLimiter:
    def __init__(self, requests_per_minute=30):
        self.requests_per_minute = requests_per_minute
        self.requests = []

    def wait_if_needed(self):
        now = datetime.now()
        self.requests = [req_time for req_time in self.requests
                        if (now - req_time).total_seconds() < 60]

        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0]).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.requests.append(now)
