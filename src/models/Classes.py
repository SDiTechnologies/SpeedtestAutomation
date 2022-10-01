from typing import Any
from dataclasses import dataclass
from datetime import datetime
from pandas import DataFrame

from .Loggers import Logger
from .Emails import SmtpHandler, Email


@dataclass
class Latency:
    iqm: float
    low: float
    high: float
    jitter: float

    @staticmethod
    def from_dict(obj: Any) -> "Latency":
        _iqm = float(obj.get("iqm"))
        _low = float(obj.get("low"))
        _high = float(obj.get("high"))
        _jitter = float(obj.get("jitter"))
        return Latency(_iqm, _low, _high, _jitter)


@dataclass
class Download:
    bandwidth: int
    bytes: int
    elapsed: int
    latency: Latency

    @staticmethod
    def from_dict(obj: Any) -> "Download":
        _bandwidth = int(obj.get("bandwidth"))
        _bytes = int(obj.get("bytes"))
        _elapsed = int(obj.get("elapsed"))
        _latency = Latency.from_dict(obj.get("latency"))
        return Download(_bandwidth, _bytes, _elapsed, _latency)


@dataclass
class Interface:
    internalIp: str
    name: str
    macAddr: str
    isVpn: bool
    externalIp: str

    @staticmethod
    def from_dict(obj: Any) -> "Interface":
        _internalIp = str(obj.get("internalIp"))
        _name = str(obj.get("name"))
        _macAddr = str(obj.get("macAddr"))
        _isVpn = bool(obj.get("isVpn"))
        _externalIp = str(obj.get("externalIp"))
        return Interface(_internalIp, _name, _macAddr, _isVpn, _externalIp)


@dataclass
class Ping:
    jitter: float
    latency: float
    low: float
    high: float

    @staticmethod
    def from_dict(obj: Any) -> "Ping":
        _jitter = float(obj.get("jitter"))
        _latency = float(obj.get("latency"))
        _low = float(obj.get("low"))
        _high = float(obj.get("high"))
        return Ping(_jitter, _latency, _low, _high)


@dataclass
class Result:
    id: str
    url: str
    persisted: bool

    @staticmethod
    def from_dict(obj: Any) -> "Result":
        _id = str(obj.get("id"))
        _url = str(obj.get("url"))
        _persisted = bool(obj.get("persisted"))
        return Result(_id, _url, _persisted)


@dataclass
class Server:
    id: int
    host: str
    port: int
    name: str
    location: str
    country: str
    ip: str

    @staticmethod
    def from_dict(obj: Any) -> "Server":
        _id = int(obj.get("id"))
        _host = str(obj.get("host"))
        _port = int(obj.get("port"))
        _name = str(obj.get("name"))
        _location = str(obj.get("location"))
        _country = str(obj.get("country"))
        _ip = str(obj.get("ip"))
        return Server(_id, _host, _port, _name, _location, _country, _ip)


@dataclass
class Upload:
    bandwidth: int
    bytes: int
    elapsed: int
    latency: Latency

    @staticmethod
    def from_dict(obj: Any) -> "Upload":
        _bandwidth = int(obj.get("bandwidth"))
        _bytes = int(obj.get("bytes"))
        _elapsed = int(obj.get("elapsed"))
        _latency = Latency.from_dict(obj.get("latency"))
        return Upload(_bandwidth, _bytes, _elapsed, _latency)


@dataclass
class OoklaResponse:
    _logger = Logger()
    type: str
    local_timestamp: str
    timestamp: str
    ping: Ping
    download: Download
    upload: Upload
    packet_loss: float
    isp: str
    interface: Interface
    server: Server
    result: Result

    @staticmethod
    def from_dict(obj: Any) -> "OoklaResponse":
        _type = str(obj.get("type"))
        _local_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        _timestamp = str(obj.get("timestamp"))
        _ping = Ping.from_dict(obj.get("ping"))
        _download = Download.from_dict(obj.get("download"))
        _upload = Upload.from_dict(obj.get("upload"))
        _packet_loss = (
            float(obj.get("packetLoss"))
            if obj.get("packetLoss") is not None
            else "NULL"
        )
        _isp = str(obj.get("isp"))
        _interface = Interface.from_dict(obj.get("interface"))
        _server = Server.from_dict(obj.get("server"))
        _result = Result.from_dict(obj.get("result"))
        return OoklaResponse(
            _type,
            _local_timestamp,
            _timestamp,
            _ping,
            _download,
            _upload,
            _packet_loss,
            _isp,
            _interface,
            _server,
            _result,
        )

    def check_notify(self, down_min=25, up_min=3):
        """verify if notify process should follow based on bool return value"""
        result = False
        try:
            down_mbps = self.convert_to_mbps(self.download.bytes, self.download.elapsed)
            up_mbps = self.convert_to_mbps(self.upload.bytes, self.upload.elapsed)

            if down_mbps < down_min:
                result = True
            if up_mbps < up_min:
                result = True
        finally:
            self._logger.log(
                f"check_notify() results: {result}, {down_mbps} Mbps(download) / {up_mbps} Mbps(upload)"
            )
            return result

    def notify(self, smtpHandler: SmtpHandler, sender: str, recipients: list[str]):
        e = Email()
        e.from_addr = sender
        e.to_addr = recipients
        # TODO: consider migrating subject and content templates to a seperate file for convenient access
        e.subject = f"Unsatisfactory Broadband Services Notification Report - {self.local_timestamp}"
        e.content = f"""To whom it may concern:\n\nAn automated speedtest conducted at {self.local_timestamp} failed to meet the minimum FCC performance requirements of products marketed as 'broadband service products' (min. 25 Mbps, download / min. 3 Mbps, upload).\n\nPlease review the following details:\n\n[\n\t'timestamp': {self.timestamp}\n\t'isp': {self.isp}\n\t'location': {self.server.location}, {self.server.country}\n\t'server': {self.server.name}\n\t'download(mbps)': {self.convert_to_mbps(self.download.bytes, self.download.elapsed)} Mbps\n\t'upload(mbps)': {self.convert_to_mbps(self.upload.bytes, self.upload.elapsed)} Mbps\n]\n\n- Thanks"""
        smtpHandler.send(e)

    def convert_to_mbps(self, size, elapsed_time):
        """return mbps conversion aka bitrate from size (bytes), elapsed_time (milliseconds)"""
        # mbps = (size of file * 8) / (( timeEnd - timeBegin) / 60) / 1048576
        mega = 1024**2  # binary mega rather than 1,000,000
        bits = size * 8
        # our elapsed time is provided given in milliseconds
        per_second = elapsed_time / 1000
        bps = bits / per_second
        mbps = bps / mega

        return mbps

    def to_df(self) -> DataFrame:
        data = {
            # flat fields
            "type": self.type,
            "timestamp": self.timestamp,
            "isp": self.isp,
            "packet_loss": self.packet_loss,
            # ping fields
            "ping_jitter": self.ping.jitter,
            "ping_iqm": self.ping.latency,
            "ping_low": self.ping.low,
            "ping_high": self.ping.high,
            # download fields
            "down_bandwidth": self.download.bandwidth,
            "down_bytes": self.download.bytes,
            "down_elapsed": self.download.elapsed,
            "down_iqm": self.download.latency.iqm,
            "down_low": self.download.latency.low,
            "down_high": self.download.latency.high,
            "down_jitter": self.download.latency.jitter,
            # upload fields
            "up_bandwidth": self.upload.bandwidth,
            "up_bytes": self.upload.bytes,
            "up_elapsed": self.upload.elapsed,
            "up_iqm": self.upload.latency.iqm,
            "up_low": self.upload.latency.low,
            "up_high": self.upload.latency.high,
            "up_jitter": self.upload.latency.jitter,
            # interface fields
            "interface_external_ip": self.interface.externalIp,
            "interface_internal_ip": self.interface.internalIp,
            "interface_is_vpn": self.interface.isVpn,
            "interface_mac_addr": self.interface.macAddr,
            "interface_name": self.interface.name,
            # result fields
            "result_id": self.result.id,
            "result_persisted": self.result.persisted,
            "result_url": self.result.url,
            # server fields
            "server_id": self.server.id,
            "server_host": self.server.host,
            "server_port": self.server.port,
            "server_name": self.server.name,
            "server_location": self.server.location,
            "server_country": self.server.country,
            "server_ip": self.server.ip,
        }
        d = {k: [v] for k, v in data.items()}
        return DataFrame(d)


# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
