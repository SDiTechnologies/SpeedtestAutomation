import threading
import queue
from pathlib import Path

from .Loggers import Logger
from .Emails import SmtpHandler, DummySmtpHandler
from .Processes import Speedtest
from .Results import Recorder, Reporter
from .Classes import SpeedtestResponse


def get_env_config():
    config = {}
    config_file = Path(".").joinpath(".env")
    with config_file.open("r") as f:
        cont = [x.replace("\n", "") for x in f.readlines()]
        cont_pairs = [x.split("=") for x in cont]
        config = {k: v for k, v in cont_pairs}
    return config


class ProcessRunner:
    jobqueue = queue.Queue()
    _logger = Logger()

    def __init__(self):
        # start worker thread at instantiation
        self.worker_start()

    # # TODO: reports routine
    # def run_stats_report(self):
    #     report = Reporter()
    #     pass

    # def run_daily_stats():
    #     pass

    # def run_weekly_stats():
    #     pass

    # def run_monthly_stats():
    #     pass

    # speedtest routine
    def run_speedtest(self):
        try:
            self._logger.log(
                f"Initiating Speedtest on Thread {threading.current_thread()}"
            )
            # initialize new Speedtest()
            test = Speedtest()
            # fetch dict result
            resp_dict = test.get_result()
            # deserialize json data into an object
            result = SpeedtestResponse.from_dict(resp_dict)

            # DEBUG catch if returned value is not anticipated response type
            if not isinstance(result, SpeedtestResponse):
                raise Exception("Error Retrieving Speedtest Data: Wrong Type")

            # run check for email notification message
            self.run_notify(result)
            # save the updated records for later
            self.publish(result)

        except Exception as e:
            self._logger.log(f"{e}")

    def run_notify(self, result: SpeedtestResponse, send: bool = False):
        """check if notification is required and transmit related messages"""
        _config = get_env_config()
        try:
            if send:
                # create a real smtp handle
                _smtp = SmtpHandler(
                    host=_config.get("host"),
                    port=_config.get("port"),
                    username=_config.get("username"),
                    password=_config.get("password"),
                )
            else:
                _mailFile = result.timestamp.strftime("%Y-%m-%d_%H:%M")
                _smtp = DummySmtpHandler(
                    path=f"{_mailFile}-email.txt",
                    host=_config.get("host"),
                    port=_config.get("port"),
                    username=_config.get("username"),
                    password=_config.get("password"),
                )
            if result.check_notify():
                result.notify(
                    smtpHandler=_smtp,
                    sender="sender@example.com",
                    recipients=["receiver@example.com"],
                )
            # DEBUG CODE
            else:
                result.notify(
                    smtpHandler=_smtp,
                    sender="sender@example.com",
                    recipients=["receiver@example.com"],
                )
        except Exception as e:
            self._logger.log(f"{e}")

    def publish(self, result: SpeedtestResponse):
        """write entries to file"""
        try:
            record = Recorder()
            record.add_entry(result.to_df())
            record.update_entries()
        except Exception as e:
            self._logger.log(f"{e}")

    # threaded processes and queue management
    def worker_main(self):
        """checks for scheduled tasks and processes existing queue items"""
        while 1:
            try:
                job_func = self.jobqueue.get()
                job_func()
                self.jobqueue.task_done()
            except Exception as e:
                self._logger.log(e)
                exit()

    def worker_start(self):
        """starts a new process in the queue"""
        worker = threading.Thread(target=self.worker_main)
        worker.start()

    def worker_start_func(self, job_func):
        """starts a new process seperate from the ProcessRunner task queue"""
        worker = threading.Thread(target=job_func)
        worker.start()
