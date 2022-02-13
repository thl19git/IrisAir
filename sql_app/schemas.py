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
    stop: Optional[Timestamp] = None
    feeling: Optional[int] = None
    description: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int
    feeling: int

    class Config:
        orm_mode = True
