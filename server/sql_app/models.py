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

    violet = Column(Integer)
    blue = Column(Integer)
    green = Column(Integer)
    yellow = Column(Integer)
    orange = Column(Integer)
    red = Column(Integer)

    intensity = Column(Float)


class Ideals(Base):
    __tablename__ = "ideals"

    serial_number = Column(String, primary_key=True)

    ideal_temp = Column(Float)

    ideal_humidity = Column(Float)

    count = Column(Integer)
