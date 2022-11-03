from typing import TypedDict
from pydantic import BaseModel

class DiskState(BaseModel):

    disks: list[str]


class ProcessState(BaseModel):

    running: bool

class TickState(BaseModel):

    n: int


DOMAIN_MAP = {
    "disks": DiskState,
    "process": ProcessState,
    "tick": TickState,
}

class AstoriaState(TypedDict):

    disks: DiskState | None
    process: ProcessState | None
    tick: TickState | None
