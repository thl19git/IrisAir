from multiprocessing import Condition
from pyexpat import model
from unittest import mock
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
import datetime
import numpy as np


from . import models, schemas

############################
#### Session Management ####
############################


def start_session(db: Session, serial_number: str) -> bool:
    """
    Creats new session.

    :param db: current database session.

    :param serial_number: serial number of device related to session.

    :return: bool regarding sucsess of creating new session.
    """

    # Create new session
    time_stamp = datetime.datetime.now()
    db_session = models.Sessions(
        start=time_stamp,
        device_serial_number=serial_number,
        avg_temp=0,
        avg_humidity=0,
        count=0,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return True


def stop_session(db: Session, serial_number: str) -> bool:
    """
    Stops current session.

    :param db: current database session.

    :param serial_number: serial number of device related to session.

    :return: bool regarding sucsess of creating new session.
    """
    # Stop session
    time_stamp = datetime.datetime.now()
    db_session = (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .order_by("id")
        .all()
    )

    if db_session == []:
        return False

    db_session = db_session[-1]

    # Check if already stopped
    if db_session.stop != None:
        return False

    db_session.stop = time_stamp

    # Calculate and store averages for temp and humidity
    if db_session.avg_temp != 0 and db_session.count != 0:
        db_session.avg_temp = round((db_session.avg_temp / db_session.count), 2)

    if db_session.avg_humidity != 0 and db_session.count != 0:
        db_session.avg_humidity = round((db_session.avg_humidity / db_session.count), 2)

    db.add(db_session)
    db.commit()
    return True


def submit_feeling(db: Session, feeling: int, serial_number: str) -> schemas.Session:
    """
    Stores users current feeling in latest session.

    :param db: current database session.

    :param feeling: integer value between 0 and 10 corrosponding to the users feeling of how the study session went

    :param serial_number: serial number of device related to session.

    :return: bool regarding sucsess of feeling submission
    """
    # Obtaining latest session
    latest_session = (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .order_by("id")
        .all()
    )

    if latest_session == []:
        return None

    latest_session = latest_session[-1]

    # Update session with feeling value
    latest_session.feeling = feeling
    db.add(latest_session)
    db.commit()
    db.refresh(latest_session)
    return latest_session


def submit_description(db: Session, description: str, serial_number: str) -> bool:
    """
    Stores users current feeling in latest session.

    :param db: current database session.

    :param description: string corrosponding to the users description of how the study session went.

    :param serial_number: serial number of device related to session.

    :return: bool regarding sucsess of feeling submission.
    """
    # Obtaining latest session and checking if valid
    latest_session = (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .order_by("id")
        .all()
    )

    if latest_session == []:
        return False

    latest_session = latest_session[-1]

    # Update session with feeling value
    latest_session.description = description
    print(latest_session)
    db.add(latest_session)
    db.commit()
    db.refresh(latest_session)
    return True


#############################
#### Condition Managment ####
#############################


def store_condition(
    db: Session,
    serial_number: str,
    temp: float,
    humidity: float,
    light_data: Dict[str, int],
    intensity: float,
) -> bool:
    """
    Updates condition log with new condition.

    :param db: current databse session.

    :param serial_number: serial_number of device.

    :param temp: tempriture value.

    :param humidity: humidity value.

    :return: bool describing sucsess of operation
    """
    # Obtaining latest session id related to device
    latest_session = (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .order_by("id")
        .all()
    )

    if latest_session == []:
        return False

    latest_session = latest_session[-1]

    # Checking session hasnt finished
    if latest_session.stop != None:
        return False

    # Storring Condition
    time_stamp = datetime.datetime.now()
    db_condition = models.Conditions(
        time_stamp=time_stamp,
        temp=temp,
        humidity=humidity,
        violet=light_data["violet"],
        blue=light_data["blue"],
        green=light_data["green"],
        yellow=light_data["yellow"],
        orange=light_data["orange"],
        red=light_data["red"],
        intensity=intensity,
        session_id=latest_session.id,
    )
    db.add(db_condition)
    db.commit()
    db.refresh(db_condition)

    # Updating avg values and count
    latest_session.avg_temp += temp
    latest_session.avg_humidity += humidity
    latest_session.count += 1
    db.add(latest_session)
    db.commit()
    db.refresh(latest_session)
    return True


#####################################################
#### Accessing Session and Condition Information ####
#####################################################


def get_session_log(
    db: Session, skip: int = 0, limit: int = 100
) -> List[schemas.Session]:
    """
    Obtaining the full or sectioon of log of sessions within the database.

    :param db: current database session.

    :param skip: integer value describing the number of sessions you want to skip before reading the remaining.

    :param limit: max number of sessions you want to return.

    :return: a list containing type schemas.Session.
    """
    return db.query(models.Sessions).offset(skip).limit(limit).all()


def get_session_id(db: Session) -> schemas.Session:
    """
    returns latest session.

    :param db: current database session.

    :return: lates session of type schemas.Session.
    """
    latest_session = db.query(models.Sessions).order_by("id").all()

    if latest_session == []:
        return None

    return latest_session[-1]


def get_condition_log(
    db: Session, skip: int = 0, limit: int = 100
) -> List[schemas.Condition]:
    """
    Obtaining the full or section of log of conditions within the database.

    :param db: current database session.

    :param skip: integer value describing the number of conditions you want to skip before reading the remaining.

    :param limit: max number of conditions you want to return.

    :return: a list containing type schemas.Condition.
    """
    return db.query(models.Conditions).offset(skip).limit(limit).all()


def get_session_conditions(db: Session, id: int) -> List[schemas.Condition]:
    """
    Returns list of conditions related to a specific session.

    :param db: current database session.

    :param id: id of session

    :return: list of schemas.Condition related to a specific session id
    """
    return (
        db.query(models.Conditions)
        .filter(models.Conditions.session_id == id)
        .offset(0)
        .limit(100)
        .all()
    )


def get_devices_sessions(db: Session, serial_number: str) -> List[schemas.Session]:
    """
    Returns all sessions related to a specific device

    :param db: current database session.

    :param serial_number: serial number of device.

    :returns: list of schemas.Conditions related to a specific serial_number.

    """
    return (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .offset(0)
        .limit(100)
        .all()
    )


def get_session_highlights(db: Session, serial_number: str) -> List[schemas.Session]:
    """
    Returns all sessions related to a specific device

    :param db: current database session.

    :param serial_number: serial number of device.

    :returns: list of schemas.sessions related to a specific serial_number.
    """
    return (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .offset(0)
        .limit(100)
        .all()
    )


def get_current_conditions(db: Session, id: int) -> List[List[float]]:
    """
    extracts the latest condition given a specific session id

    :param db: current database session.

    :param id: session id.

    :returns: list of temp and humidity.
    """
    current_condition = (
        db.query(models.Conditions)
        .filter(models.Conditions.session_id == id)
        .order_by("time_stamp")
        .all()
    )

    if current_condition == []:
        return [[None, None]]

    current_condition = current_condition[-1]

    return [[current_condition.temp, current_condition.humidity]]


def get_current_device_session(
    db: Session, serial_number: str
) -> List[schemas.Condition]:
    """
    Obtains full condition log for the current session for a specific device

    :param db: current database session.

    :param serial_number: serial number of device.

    :returns: list of schemas.condition related to a specific serial_number and session.

    """
    # Getting latest session ID
    latest_session = (
        db.query(models.Sessions)
        .filter(models.Sessions.device_serial_number == serial_number)
        .order_by("id")
        .all()
    )

    if latest_session == []:
        return []

    latest_session = latest_session[-1]

    return get_session_conditions(db, latest_session.id)


################
#### Ideals ####
################


def add_to_ideals(db: Session, session: schemas.Session, feeling: int) -> bool:
    """
    checks if ideal information already exists and update/upload correct data

    :param db:

    :param session:

    :param feeling:

    :return:
    """

    # Check session
    ideals = (
        db.query(models.Ideals)
        .filter(models.Ideals.serial_number == session.device_serial_number)
        .all()
    )

    if ideals == []:
        # session doesnt exist so create one
        print("ideals doesnt exist")

        db_session = models.Ideals(
            serial_number=session.device_serial_number,
            ideal_temp=session.avg_temp,
            ideal_humidity=session.avg_humidity,
            count=1,
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

    else:
        # Session exists so update
        ideals = ideals[0]
        print("ideals exist")

        ideals.ideal_temp += session.avg_temp
        ideals.ideal_humidity += session.avg_humidity
        ideals.count += 1

        db.add(ideals)
        db.commit()
        db.refresh(ideals)

    return True


def get_ideals(db, serial_number) -> schemas.Ideals:
    ideals = (
        db.query(models.Ideals)
        .filter(models.Ideals.serial_number == serial_number)
        .all()
    )

    if ideals == []:
        print("no ideal data")
        return []

    else:
        return ideals[0]
