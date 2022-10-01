from time import sleep
import schedule
from models import *

runner = ProcessRunner()

# pretty neat little library: https://schedule.readthedocs.io/en/stable/examples.html#run-a-job-every-x-minute
# schedule.every(1).minutes.do(runner.jobqueue.put, runner.run_speedtest)
schedule.every(30).to(45).minutes.do(runner.jobqueue.put, runner.run_speedtest)

## TODO: create a report generating process from Recorded entries
# schedule.every().day.at('10:30').do(runner.jobqueue.put, runner.run_report)

if __name__ == "__main__":
    try:
        while True:
            schedule.run_pending()
            sleep(1)
    except:
        pass
