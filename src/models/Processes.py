import subprocess
from traceback import print_exc
import json

from .Loggers import Logger


class Speedtest:
    '''Manage speedtest-cli process and return formatted results'''
    _logger:Logger = Logger()

    def __init__(self):
        pass

    def get_result(self) -> dict|None:
        result = None
        try:
            result = self._perform_speedtest()
        except Exception as e:
            self._logger.log(f"{e} - {print_exc()}")
        finally:
            return result

    def _perform_speedtest(self, cmdstr='speedtest -p no -f json') -> dict:
        # -p    --progress
        # -f    --format
        cmd = cmdstr.split()
        self._logger.log(f"Attempting Speedtest with command: $> {cmdstr}")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            result = proc.stdout
            error = proc.stderr
            self._logger.log('Speedtest Complete')
            print(f'Speedtest Complete With Results:\nError: {error}\nResult: {result}')
            # if it returns data, give it back as a dict object
            return json.loads(result)
        except Exception as e:
            self._logger.log(f'{e}')
            self._logger.log(f'StdErr: {proc.stderr}')