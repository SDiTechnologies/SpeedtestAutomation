from pathlib import Path
from datetime import datetime

class Logger:
    path:str
    def __init__(self, path='logs.txt'):
        self.path = Path('.').joinpath('logs', path)

    def log(self, msg):
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        formatted_msg = f"[LOG] - {now} - {msg}"
        print(formatted_msg)
        try:
            with open(self.path, 'a+') as f:
                f.write(formatted_msg +'\n')
        finally:
            f.close()