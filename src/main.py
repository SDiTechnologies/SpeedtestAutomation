from time import sleep
import schedule
from models import *

p = ProcessRunner()

# pretty neat little library: https://schedule.readthedocs.io/en/stable/examples.html#run-a-job-every-x-minute
# schedule.every(5).minutes.do(p.jobqueue.put, p.run_speedtest)
schedule.every(30).to(120).minutes.do(p.jobqueue.put, p.run_speedtest)
# schedule.every().day.at('10:30').do(p.jobqueue.put, p.run_report)

if __name__ == '__main__':
    try:
        while True:
            schedule.run_pending()
            sleep(1)
    except:
        pass