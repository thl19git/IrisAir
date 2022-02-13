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


def start_session(db: Session) -> bool:
    """
    Creats new session.

    :param db: current database session.

    :return: bool regarding sucsess of creating new session.
    """

    # Create new session
    time_stamp = datetime.datetime.now()
    db_session = models.Sessions(start=time_stamp)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return True


def stop_session(db: Session) -> bool:
    """
    Stops current session.

    :param db: current database session.

    :return: bool regarding sucsess of creating new session.
    """
    # Stop session
    time_stamp = datetime.datetime.now()
    db_session = db.query(models.Sessions).order_by("id").all()[-1]
    db_session.stop = time_stamp
    db.add(db_session)
    db.commit()
    return True


def submit_feeling(db: Session, feeling: int) -> bool:
    """
    Stores users current feeling in latest session.

    :param db: current database session.

    :param feeling: integer value between 0 and 10 corrosponding to the users feeling of how the study session went

    :return: bool regarding sucsess of feeling submission
    """
    # Obtaining latest session
    latest_session = db.query(models.Sessions).order_by("id").all()[-1]

    # Update session with feeling value
    latest_session.feeling = feeling
    db.add(latest_session)
    db.commit()
    return True


def submit_description(db: Session, description: str) -> bool:
    """
    Stores users current feeling in latest session.

    :param db: current database session.

    :param description: string corrosponding to the users description of how the study session went.

    :return: bool regarding sucsess of feeling submission.
    """
    # Obtaining latest session and checking if valid
    latest_session = db.query(models.Sessions).order_by("id").all()[-1]
    """
    if (
        latest_session.description != None or latest_session.stop == None
    ) and latest_session.id != None:
        return False
    """
    # Update session with feeling value
    latest_session.descripton = "helloooo"
    print(latest_session)
    db.add(latest_session)
    db.commit()
    return True


#############################
#### Condition Managment ####
#############################


def store_condition(db: Session, session: int, temp: float, humidity: float) -> bool:
    """
    Updates condition log with new condition.

    :param db: current databse session.

    :param session: current session id (latest session).

    :param temp: tempriture value.

    :param humidity: humidity value.

    :return: bool describing sucsess of operation
    """

    time_stamp = datetime.datetime.now()
    db_condition = models.Conditions(
        time_stamp=time_stamp, temp=temp, humidity=humidity, session_id=session
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
