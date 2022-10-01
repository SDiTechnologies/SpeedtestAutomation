# import time
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
        self.worker_start()

    def run_speedtest(self):
        try:
            self._logger.log(f"Initiating Speedtest on Thread {threading.current_thread()}")
            # initialize new Speedtest() 
            test = Speedtest()
            # fetch dict result
            resp_dict = test.get_result()
            # deserialize json data into an object
            result = OoklaResponse.from_dict(resp_dict)

            # run check for email notification message
            self.run_notify(result)
            # save the updated records for later
            self.publish(result)

            # if isinstance(current_result, Result):
            #     self.run_notify(current_result)
            #     self.publish(current_result)
            # else:
            #     raise Exception("Error Retrieving Test Data")
        except Exception as e:
            self._logger.log(f"{e}")
 
    
    def run_notify(self, result:OoklaResponse):
        try:
            # if check_notify() -> True then logic for smtp should follow
            _mailFile = result.local_timestamp
            _smtp = DummySmtpHandler(path=f"{_mailFile}-email.txt")
            if (result.check_notify()):
                result.notify(smtpHandler=_smtp, sender='sender@example.com', recipients=['receiver@example.com'])
            else:
                result.notify(smtpHandler=_smtp, sender='sender@example.com', recipients=['receiver@example.com'])
        except Exception as e:
            self._logger.log(f"{e}")
    
    def publish(self, result:OoklaResponse):
        try:
            record = Recorder()
            record.add_entry(result.to_df())
            record.update_entries()
        except Exception as e:
            self._logger.log(f'{e}')

    def worker_main(self):
        while 1:
            try:      
                job_func = self.jobqueue.get()
                job_func()
                self.jobqueue.task_done()
            except Exception as e:
                self._logger.log(e)
                exit()

    def worker_start(self):
        worker = threading.Thread(target=self.worker_main)
        worker.start()


    # def run_thread(self, job_func):
    #     job_thread = threading.Thread(target=job_func)
    #     job_thread.start()
    