from dataclasses import dataclass
import typing


@dataclass
class LogResult():
    file: str
    host: str
    logs: typing.List
