from sqlite3 import Timestamp
from typing import Optional


# from tkinter import E
from typing import List

from pydantic import BaseModel


class ConditionBase(BaseModel):
    time_stamp: Timestamp
    temp: float
    humidity: float


class CondtionCreate(ConditionBase):
    pass


class Condition(ConditionBase):
    session_id: int

    class Config:
        orm_mode = True


class SessionBase(BaseModel):
    start: Timestamp
    device_serial_number: int
    stop: Optional[Timestamp] = None
    feeling: Optional[int] = None
    description: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int

    class Config:
        orm_mode = True


#########################
#### General Classes ####
#########################


class SessionInformation(BaseModel):
    serial_number: int


class Feeling(SessionInformation):
    feeling: int


class Description(SessionInformation):
    description: str


class NewCondition(SessionInformation):
    temp: float
    humidity: float
