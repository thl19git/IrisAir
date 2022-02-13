"""
from traceback import print_tb
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import crud, models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/create", response_model=schemas.Session)
def c_session(db: Session = Depends(get_db)):
    crud.create_session(db)
    print("created session")


@app.get("/users/get", response_model=schemas.Session)
def g_session(db: Session = Depends(get_db)):
    sessions = crud.get_session(db)
    # print(sessions)
    return sessions
"""