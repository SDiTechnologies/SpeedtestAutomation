from pandas import read_json, DataFrame, concat
from pathlib import Path
from pprint import pformat

from .Loggers import Logger

# class ValueConverter:
#     def __init__(self):
#         pass

#     def convert_to_mbps(self, size, elapsed_time):
#         '''convert to mbps for size (bytes) and elapsed_time (milliseconds)'''
#         mega = (1024**2)  # binary vs 1,000,000
#         bits = (size * 8)
#         per_second = (elapsed_time / 1000)
#         bps = bits / per_second
#         mbps = bps / mega
#         return mbps


class Recorder:
    path: str = None
    _logger: Logger = Logger()

    def __init__(self, path="results.json"):
        self.path = Path(".").joinpath("data", path)
        self.entries = self.get_entries()

    def get_entries(self) -> DataFrame:
        entries = DataFrame()
        try:
            self._logger.log(f"Attemting entry retrieval from: {self.path}")
            entries = read_json(self.path)
        except Exception as e:
            self._logger.log(f"No entries found. Returning empty DataFrame() object")
            self._logger.log(f"Exception: {e}")
        finally:
            return entries

    def add_entry(self, data: DataFrame) -> None:
        try:
            if self.entries.empty:
                self.entries = data
            else:
                self.entries = concat([self.entries, data], ignore_index=True)
            self._logger.log(f"Added new entry at: {self.path}")
        except Exception as e:
            self._logger.log(f"Error occurred while adding new entry: {self.path}")
            self._logger.log(f"{e}")

    def update_entries(self) -> None:
        try:
            self.entries.to_json(self.path)
            self._logger.log(f"Updated entries at: {self.path}")
        except Exception as e:
            self._logger.log(f"Error occurred while updating entries at: {self.path}")
            self._logger.log(f"{e}")
