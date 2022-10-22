import subprocess
from traceback import print_exc
import json

from .Loggers import Logger


class Speedtest:
    """Manage speedtest-cli process and return formatted results"""

    _logger: Logger = Logger()

    def __init__(self):
        pass

    def get_result(self) -> dict | None:
        result = None
        try:
            result = self._perform_speedtest()
        except Exception as e:
            self._logger.log(f"{e} - {print_exc()}")
        finally:
            return result

    def _perform_speedtest(self, cmdstr="speedtest -p no -f json") -> dict:
        # example: speedtest -p no -f json (worked with the debian provided script, but not the python provided script)
        # pip package version command: 'speedtest --json' (information output varies)
        # -p    --progress
        # -f    --format
        cmd = cmdstr.split()
        self._logger.log(f"Attempting Speedtest with command: $> {cmdstr}")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            stdout = proc.stdout
            stderr = proc.stderr
            self._logger.log(
                f"Speedtest Complete With Results:\nError: {stderr}\nResult: {stdout}"
            )
            # if it returns data, give it back as a dict object
            return json.loads(stdout)
        except Exception as e:
            self._logger.log(f"{e}")
            self._logger.log(f"StdErr: {stderr}")
