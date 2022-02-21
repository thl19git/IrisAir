# from turtle import back
from numbers import Integral
from xmlrpc.client import DateTime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from zmq import device

from .database import Base


class Sessions(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(String)
    start = Column(DateTime)
    stop = Column(DateTime)
    description = Column(String)
    feeling = Column(Integer)
    avg_temp = Column(Float)
    avg_humidity = Column(Float)
    count = Column(Integer)


class Conditions(Base):
    __tablename__ = "conditions"

    time_stamp = Column(DateTime, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("sessions.id"))

    temp = Column(Float, index=True)
    humidity = Column(Float, index=True)

    # = relationship("Sessions", back_populates="id")
