from datetime import datetime
from enum import Enum, unique
from typing import Dict, Optional, Union

from pydantic import BaseModel, Json


@unique
class STATUS(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class FORMAT(str, Enum):
    JSON = "JSON"
    CSV = "CSV"


class Cid(BaseModel):
    cid: str


class Process(BaseModel):
    uuid: str
    status: int
    configurationId: str
    configurationVersion: int
    params: Optional[Union[Json, None]]
    error: Optional[Union[Json, None]]
    data: Optional[Union[Json, None]]
    processTime: int
    createdAt: datetime
    createdBy: str
    updatedAt: datetime
    updatedBy: str


class Status(BaseModel):
    uuid: str
    value: str
    description: Optional[Union[str, None]]
    createdAt: datetime
    createdBy: str
    updatedAt: datetime
    updatedBy: str


class ProcessResponse(Cid):
    uuid: Optional[Union[str, None]]
    processId: str


class Result(Cid):
    uuid: str
    status: STATUS
    configurationId: str
    params: Optional[Dict[str, str]]
    data: Optional[Dict[str, str]]
    createdAt: datetime
    createdBy: str
    updatedAt: datetime
    updatedBy: str


class AnalyticsRequest(BaseModel):
    uuid: Optional[Union[str, None]]
    configurationId: str
    params: Dict[str, str]
    format: FORMAT
