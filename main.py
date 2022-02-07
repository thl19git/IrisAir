from fastapi import FastAPI
from fastapi_mqtt import MQQTConfig, FastMQTT

app = FastAPI()

mqtt_config = MQQTConfig(host="broker.mqttdashboard.com")

mqtt = FastMQTT(config=mqtt_config)

mqtt.init_app(app)


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("IC.embedded/cdc/#")  # subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ", topic, payload.decode(), qos, properties)


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


print(mqtt_config.host)


@app.get("/")
async def func():

    mqtt.publish("IC.embedded/cdc/", "hello from fast api")
    return {"message": "sending msg to client"}
