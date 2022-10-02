from pandas import read_json, DataFrame, concat, Grouper, to_datetime
from pathlib import Path
from pprint import pformat

from .Loggers import Logger

# class ValueConverter:
#     '''ValueConverter for simple conventional conversion of values in static class methods'''
#     def __init__(self):
#         pass

#     def convert_to_mbps(self, size, elapsed):
#         """return mbps conversion aka 'bitrate' from size (bytes), elapsed (milliseconds)"""
#         # mbps = (size of file * 8) / (( timeEnd - timeBegin) / 60) / 1048576
#         kilobit = (2**10)
#         megabit = (kilobit**2)  # binary mega rather than 1,000,000
#         bits = (size * 8)
#         per_second = (elapsed / 1000)
#         bps = (bits / per_second)
#         mbps = (bps / megabit)
#         mbps_rnd = round(mbps, 3)
#         return mbps_rnd


class Recorder:
    path: str = None
    _logger: Logger = Logger()

    def __init__(self, path="results.json"):
        self.path = Path(".").joinpath("data", path)
        self.entries = self.get_entries()

    def get_entries(self) -> DataFrame:
        entries = DataFrame()
        try:
            self._logger.log(f"Attempting entry retrieval from: {self.path}")
            # TODO: runs into perms issues with current version of docker scripts when running on host machine vs. docker machine
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


class Reporter(Recorder):
    def __init__(
        self,
        cols=[
            "timestamp",
            "isp",
            "down_mbps",
            "down_bytes",
            "down_elapsed",
            "up_mbps",
            "up_bytes",
            "up_elapsed",
            "server_id",
            "server_host",
            "server_name",
            "server_location",
            "server_country",
        ],
    ):
        super().__init__()
        self.cols = cols
        self.df = self.entries[self.cols]
        self._convert_cols()

    def _convert_cols(self):
        """force any required dtypes here; normally achieved by `df = df.astype(dtypes={"column": type})` though, the unix datetime column seems to be the primary issue"""
        df = self.df.copy()
        # # TODO: review once modifications to base classes complete
        rename_cols = {"down_bytes": "download", "up_bytes": "upload"}
        # dtype_cols = {}

        # # rename columns
        # # df.rename/
        df.rename(columns=rename_cols, inplace=True)
        # # convert datetime column
        df["timestamp"] = to_datetime(df["timestamp"], unit="ms")

        # apply updates to existing
        self.df = df.copy()

    # # create the sections of a report; What's most important?
    # def report_general(self):
    #     cols = [[]]

    def report_by_agg(self):
        df = self.entries[self.cols]
        pass

    def report_by_day(self):
        df = self.entries[self.cols]
        # results_by_day
        df.groupby(by=[Grouper(key="local_timestamp", freq="1D")])
        pass

    def report_by_week(self):
        pass

    def report_by_month(self):
        pass
