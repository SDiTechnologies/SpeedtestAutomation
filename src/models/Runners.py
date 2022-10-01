import threading
import queue

from .Loggers import Logger
from .Emails import SmtpHandler, DummySmtpHandler
from .Processes import Speedtest
from .Results import Recorder
from .Classes import OoklaResponse


class ProcessRunner:
    jobqueue = queue.Queue()
    _logger = Logger()

    def __init__(self):
        # start worker thread at instantiation
        self.worker_start()

    def run_stats_report(self):
        pass

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
            result = OoklaResponse.from_dict(resp_dict)

            # DEBUG catch if returned value is not anticipated response type
            if not isinstance(result, OoklaResponse):
                raise Exception("Error Retrieving Speedtest Data: Wrong Type")

            # run check for email notification message
            self.run_notify(result)
            # save the updated records for later
            self.publish(result)

        except Exception as e:
            self._logger.log(f"{e}")

    def run_notify(self, result: OoklaResponse):
        """check if notification is required and transmit related messages"""
        try:
            # if check_notify() -> True then logic for smtp should follow
            _mailFile = result.local_timestamp.strftime("%Y-%m-%d_%H:%M%:%S")
            _smtp = DummySmtpHandler(path=f"{_mailFile}-email.txt")
            if result.check_notify():
                result.notify(
                    smtpHandler=_smtp,
                    sender="sender@example.com",
                    recipients=["receiver@example.com"],
                )
            # # DEBUG CODE
            # else:
            # result.notify(
            #     smtpHandler=_smtp,
            #     sender="sender@example.com",
            #     recipients=["receiver@example.com"],
            # )
        except Exception as e:
            self._logger.log(f"{e}")

    def publish(self, result: OoklaResponse):
        """write entries to file"""
        try:
            record = Recorder()
            record.add_entry(result.to_df())
            record.update_entries()
        except Exception as e:
            self._logger.log(f"{e}")

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
