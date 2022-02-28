from fastapi import FastAPI, Depends, HTTPException
from fastapi_mqtt import MQQTConfig, FastMQTT
from traceback import print_tb
from sqlalchemy.orm import Session
from typing import List
import json


from sql_app.database import SessionLocal, engine
from sql_app import crud, models, schemas
from knn import convert_for_knn, get_label

#################
#### Globals ####
#################
broker_address = "172.31.26.94"
general_broker_address = "broker.mqttdashboard.com"
conditions_topic = "IC.embedded/cdc/conditions"
test_topic = "test"


######################################################
#### Initilising FastAPI, FastAPI-MQTT & Database ####
######################################################
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

mqtt_config = MQQTConfig(
    username="sammy", password="raspberry"
)  # host="broker.mqttdashboard.com"


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
        decoded_data = json.loads(payload.decode())

        # Storring condition with correct sesssion ID
        err = crud.store_condition(
            db,
            decoded_data["serial_number"],
            decoded_data["temp"],
            decoded_data["humidity"],
            decoded_data["light_data"],
            decoded_data["intensity"],
        )
        if not err:
            print("error: session closed")
        else:
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


@app.get("/test/knn")
def test_knn():
    """
    returns prediction of feeling related to current conditions
    """
    features = [[0, 0], [1, 0], [2, 2], [3, 2]]
    labels = [0, 0, 1, 1]
    current_condition = [[0.5, 1]]
    # Obtain a prediction of feeling for current data
    prediction = get_label(current_condition, features, labels)

    return prediction


###################
#### HTTP POST ####
###################

# --- Session management --- #


@app.post("/session/start")
def start_session(serial_number: str, db: Session = Depends(get_db)):
    """
    Starting session and sending notice of session start to Pi with correct serial via mqtt.
    """
    crud.start_session(db, serial_number)
    mqtt.publish(f"IC.embedded/cdc/{serial_number}", "start")
    return True


@app.post("/session/stop")
def stop_session(serial_number: str, db: Session = Depends(get_db)):
    """
    Stopping session adn sending notice of session stop to Pi with correct serial via mqtt
    """
    mqtt.publish(f"IC.embedded/cdc/{serial_number}", "stop")
    err = crud.stop_session(db, serial_number)
    if not err:
        raise HTTPException(status_code=404, detail="session already stopped")
    else:
        return "session stopped"


@app.post("/session/feeling")
def submit_session_feeling(request: schemas.Feeling, db: Session = Depends(get_db)):
    """
    Submits feeling to latest session related to a specific device
    """
    session = crud.submit_feeling(db, request.feeling, request.serial_number)

    if session == None:
        print("error: session doesnt exist")
        raise HTTPException(
            status_code=404, detail="feeling not submitted, session doesnt exist"
        )

    else:

        if request.feeling >= 7:
            crud.add_to_ideals(db, session, request.feeling)

        return "feeling submitted"


@app.post("/session/description")
def submit_session_description(
    request: schemas.Description, db: Session = Depends(get_db)
):
    """
    Submits description to latest session with correct serial number
    """
    crud.submit_description(db, request.description, request.serial_number)
    return "description submitted"


# --- Condition Management --- #


@app.post("/condition/store")
def store_condition(request: schemas.NewCondition, db: Session = Depends(get_db)):
    """
    Stores a condition to the latest session of a specifc device
    """
    light_data = {
        "violet": 3,
        "blue": 3,
        "green": 3,
        "yellow": 3,
        "orange": 3,
        "red": 3,
    }
    err = crud.store_condition(
        db,
        request.serial_number,
        request.temp,
        request.humidity,
        light_data,
        request.intensity,
    )
    return True


# --- Session Extraction ---#


@app.post("/session/data", response_model=List[schemas.Condition])
def g_session(serial_number: str, db: Session = Depends(get_db)):
    """
    returns all conditions related to the current session of a specific device
    """

    return crud.get_current_device_session(db, serial_number)


@app.post("/session/extract")
def g_session(serial_number: str, db: Session = Depends(get_db)):
    """
    returns all sessions related to a specific device
    """
    return crud.get_devices_sessions(db, serial_number)


# --- KNN --- #


@app.post("/predict")
def knn(serial_number: str, db: Session = Depends(get_db)):
    """
    returns prediction of feeling related to current conditions
    """
    # Obtain data highlights from specific devce
    data = crud.get_session_highlights(db, serial_number)

    if data == []:
        print("error: No available data")
        return 0

    elif len(data) < 3:
        print("error: Not enough data")
        return 0

    # Obtain current session from data
    current_session = data[-1]

    # Obtain latest conditions from device
    current_condition = crud.get_current_conditions(db, current_session.id)

    if current_condition == [[None, None]]:
        print("error: No current data")
        return 0

    # Convert data into correct format for knn
    features, labels = convert_for_knn(data)

    # Obtain a prediction of feeling for current data
    prediction = get_label(current_condition, features, labels)

    if prediction < 7 and prediction > 0:
        ideals = crud.get_ideals(db, serial_number)

        if ideals == []:
            return (prediction, None, None)

        ideal_temp = ideals.ideal_temp / ideals.count
        ideal_humidity = ideals.ideal_humidity / ideals.count

        temp_diff = ideal_temp - current_condition[0][0]
        humidity_diff = ideal_humidity - current_condition[0][1]

        print(f"temp diff: {temp_diff}, humidity diff: {humidity_diff}")

        return (prediction, temp_diff, humidity_diff)

    else:
        return (prediction, None, None)
