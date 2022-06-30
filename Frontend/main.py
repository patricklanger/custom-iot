from .tdgenerator import TDGenerator

import json
import asyncio
import _thread as thread

from aioflask import Flask, render_template
from wotpy.wot.servient import Servient
from wotpy.wot.wot import WoT


app = Flask(__name__)

THINGS = []  # hier speichern wir unsere -> consumed Things <-
ATTRIBUTES = ["temperature", "humidity", "color"]
DATA_OBJECTS = [  # Dummy Object. Nur damit wir nicht ganz ohne was starten. kann eigentlich ein [] sein.
    {
        "name": "device_1",
        "attributes": [
            {
                "name": "temperature",
                "d": 23,  # digit / wert
                "u": "°C"  # unit / maßeinheit
            },
            {
                "name": "accelerometer",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            }
        ]
    },
    {
        "name": "device_2",
        "attributes": [
            {
                "name": "temperature",
                "d": 24,  # digit / wert
                "u": "°C"  # unit / maßeinheit
            },
            {
                "name": "accelerometer",
                "d": [0.1, 0.2, -0.9],
                "u": "g"
            }
        ]
    }
]


async def update_data_objects():
    while True:
        data_obj = []
        # iteriere über alle consumed THINGS
        for idx, thing in enumerate(THINGS):
            data_obj.append({
                "name": f"device_{idx}",  # TODO Thing ID auslesen?
                "attributes": []
            })
            # lies und speicher alle Sensor Attribute dieses Things
            for attr in ATTRIBUTES:
                val = await thing.read_property(attr)
                print(f"recived {attr}-value: {val}")
                obj = {
                    "name": attr,
                    "d": val["d"],
                    "u": val["u"]
                }
                data_obj[0]["attributes"].append(obj)
        print("DATA_OBJECTS updated ####################")
        print(data_obj)
        print("#########################################")
        # Sensordaten global hinterlegen um sie in der Indexmethode abrufen zu können
        global DATA_OBJECTS
        DATA_OBJECTS = data_obj
        await asyncio.sleep(3)


async def create_things():
    """
    Hole alle TDs und erzeuge consumed things daraus.
    """
    wot = WoT(servient=Servient())
    global THINGS
    tdgen = TDGenerator()
    for td in tdgen.get_thing_descriptions():
        THINGS.append(wot.consume(json.dumps(td)))


@app.route('/')
async def index():
    """
    Returne die Indexseite und alle DATA_OBJECTS, also aufbereitete Sensorwerte.
    """
    return await render_template('index.html', all_devices=DATA_OBJECTS)

# app.run(host='0.0.0.0')
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_things())
    # TODO funktioniert das so? Neuer Thread läuft im hintergrund und updated alle 3 sek unser DATA_OBJECTS
    thread.start_new_thread(update_data_objects, ())  # start_new_thread(function, (function_parameter1, function_parameter2))
    app.run(host='0.0.0.0')
