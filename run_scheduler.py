from superset.scheduler.jobs import start_scheduler
import time

if __name__ == "__main__":
    sched = start_scheduler()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sched.shutdown()