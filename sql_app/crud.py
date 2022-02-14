from multiprocessing import Condition
from pyexpat import model
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import datetime


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
    db_session = models.Sessions(start=time_stamp, device_serial_number=serial_number)
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
        .all()[-1]
    )
    db_session.stop = time_stamp
    db.add(db_session)
    db.commit()
    return True


def submit_feeling(db: Session, feeling: int, serial_number: str) -> bool:
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
        .all()[-1]
    )

    # Update session with feeling value
    latest_session.feeling = feeling
    db.add(latest_session)
    db.commit()
    db.refresh(latest_session)
    return True


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
        .all()[-1]
    )
    """
    if (
        latest_session.description != None or latest_session.stop == None
    ) and latest_session.id != None:
        return False
    """
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
    db: Session, serial_number: str, temp: float, humidity: float
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
        .all()[-1]
    )

    time_stamp = datetime.datetime.now()
    db_condition = models.Conditions(
        time_stamp=time_stamp,
        temp=temp,
        humidity=humidity,
        session_id=latest_session.id,
    )
    db.add(db_condition)
    db.commit()
    db.refresh(db_condition)
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
    return db.query(models.Sessions).order_by("id").all()[-1]


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


def get_devices_sessions(db: Session, serial_number: str) -> List[schemas.Condition]:
    """
    Returns all sessions related to a specific device

    :param db: current database session.

    :param serial_number: serial number of device.

    :returns: list of schemas.Conditions related to a specific serial_number.

    """
    # TODO: not sure how we are going to want this to be implimented


#########################
#### User Management ####
#########################

"""
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    
    Stores user details in databse.

    :param db: current database session.

    :param user: a schema of the user (containing password and username).

    :return: a model of the user type models.use.

    

    # TODO: hash password

    hashed_password = user.password

    db_new_user = models.User(username=user.username, password=hashed_password)
    db.add(db_new_user)
    db.commit()
    db.refresh(db_new_user)
    return db_new_user
"""
