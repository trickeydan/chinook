from typing import Dict, Literal, Type, TypedDict, Union
from pydantic import BaseModel

class DiskState(BaseModel):

    disks: list[str]


class ProcessState(BaseModel):

    running: bool

class TickState(BaseModel):

    n: int

StateDomain = Union[Literal["disks"], Literal["process"], Literal["tick"]]

DOMAIN_MAP: Dict[StateDomain, Type[BaseModel]] = {
    "disks": DiskState,
    "process": ProcessState,
    "tick": TickState,
}

class ChinookState(TypedDict):

    disks: DiskState | None
    process: ProcessState | None
    tick: TickState | None
