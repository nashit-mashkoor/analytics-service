from enum import Enum
from typing import List

from pydantic import BaseModel


class Status(str, Enum):
    error = "error"
    OK = "OK"
    shutting_down = "shutting_down"


class HealthDto(BaseModel):
    status: Status = None


class PeripheryDto(HealthDto):
    dependencies: List[str]
