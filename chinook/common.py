"""Common structures."""
from typing import Dict, Literal, Type, TypedDict, Union

from pydantic import BaseModel


class DiskState(BaseModel):
    """The state of the disks."""

    disks: list[str]


class ProcessState(BaseModel):
    """The state of the process."""

    running: bool


class TickState(BaseModel):
    """The tick state."""

    n: int


StateDomain = Union[Literal["disks"], Literal["process"], Literal["tick"]]


DOMAIN_MAP: Dict[StateDomain, Type[BaseModel]] = {
    "disks": DiskState,
    "process": ProcessState,
    "tick": TickState,
}


class ChinookState(TypedDict):
    """The overall state."""

    disks: DiskState | None
    process: ProcessState | None
    tick: TickState | None
