from fastapi import FastAPI, Depends
from fastapi_mqtt import MQQTConfig, FastMQTT
from traceback import print_tb
from sqlalchemy.orm import Session
from typing import List
import json


from sql_app.database import SessionLocal, engine
from sql_app import crud, models, schemas

######################################################
#### Initilising FastAPI, FastAPI-MQTT & Database ####
######################################################
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

mqtt_config = MQQTConfig(host="broker.mqttdashboard.com")
# host="172-31-26-94", port=1883, username="sammy", password="raspberry"


mqtt = FastMQTT(config=mqtt_config)

mqtt.init_app(app)

#############################
#### Database Dependency ####
#############################


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#######################
#### MQTT Features ####
#######################


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    """
    Connecting to broker and subscribing to topics
    """
    mqtt.client.subscribe("IC.embedded/cdc/#")  # subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    """
    Dealing with messages depending on topic
    """
    print("Received message: ", topic, payload.decode(), qos, properties)

    if topic == "IC.embedded/cdc/conditions":
        db = SessionLocal()

        # Getting latest session ID, TODO: Do this inside CRUD and check session is valid
        sessions = crud.get_session_id(db)
        current_session = sessions.id
        decoded_data = json.loads(payload.decode())

        # Storring condition with correct sesssion ID
        crud.store_condition(
            db, current_session, decoded_data["temp"], decoded_data["humidity"]
        )
        print("stored condition and closing db")
        db.close()


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


print(mqtt_config.host)


##################
#### HTTP GET ####
##################


@app.get("/session/start")
def start_session(db: Session = Depends(get_db)):
    """
    Starting session and sending notice of session start to Pi via mqtt.

    """
    result = crud.start_session(db)
    if not result:
        print("session cannot start")
        return "error: session cannot start"

    sessions = crud.get_session_id(db)
    current_session = sessions.id
    mqtt.publish("IC.embedded/cdc/session/start", current_session)
    return "session started"


@app.get("/session/stop")
def stop_session(db: Session = Depends(get_db)):
    """
    Stopping session adn sending notice of session stop to Pi via mqtt
    """
    sessions = crud.get_session_id(db)
    current_session = sessions.id
    mqtt.publish("IC.embedded/cdc/session/stop", current_session)
    crud.stop_session(db)
    return "session stopped"


# ---- Tests  ---- #


@app.get("/test/conditions")
def func():

    sensor_data = {"temp": 11.2, "humidity": 13.1}

    json_object = json.dumps(sensor_data, indent=4)

    mqtt.publish("IC.embedded/cdc/conditions", json_object)

    # mqtt.publish("IC.embedded/cdc/conditions", )
    return {"message": "sending msg to client"}


@app.get("/conditions/store", response_model=schemas.Condition)
def store_condition(db: Session = Depends(get_db)):
    sessions = crud.get_session_id(db)
    current_session = sessions.id
    print(f"current session: {current_session}")
    crud.store_condition(db, current_session, 22.1, 11.2)
    print("stored condition")


@app.get("/conditions/see", response_model=List[schemas.Condition])
def see_conditions(db: Session = Depends(get_db)):
    sessions = crud.get_condition_log(db)
    # print(sessions)
    return sessions


@app.get("/session/see", response_model=List[schemas.Session])
def see_session(db: Session = Depends(get_db)):
    sessions = crud.get_session_log(db)
    # print(sessions)
    return sessions


@app.get("/session/id")
def see_session_id(db: Session = Depends(get_db)):
    sessions = crud.get_session_id(db)

    print(sessions.id)
    return sessions.id


@app.get("/session/feeling")
def submit_session_feeling(db: Session = Depends(get_db)):
    result = crud.submit_feeling(db, 4)
    if not result:
        print("unable to submit feeling")
        return "error: unable to submit feeling"
    return "feeling submitted"


@app.get("/session/description")
def submit_session_description(db: Session = Depends(get_db)):
    result = crud.submit_description(db, "yeah it was alright")
    if not result:
        print("unable to submit description")
        return "error: unable to submit description"
    return "description submitted"


@app.get("/session/2")
def g_session(db: Session = Depends(get_db)):
    return crud.get_session_conditions(db, 2)


###################
#### HTTP POST ####
###################
"""
@app.post("/session/description")
def add_description(description:str, db: Session = Depends(get_db)):
"""
