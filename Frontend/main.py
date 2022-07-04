import json
import asyncio
import threading

from aioflask import Flask, render_template
from wotpy.wot.servient import Servient
from wotpy.wot.td import ThingDescription
from wotpy.wot.wot import WoT

from tdgenerator import TDGenerator


app = Flask(__name__)

THINGS = []  # hier speichern wir unsere -> consumed Things <-
ATTRIBUTES = ["temperature_1", "temperature_2", "humidity", "pressure"]  # , "color"]
DATA_OBJECTS = [  # Dummy Object. Nur damit wir nicht ganz ohne was starten. kann eigentlich ein [] sein.
    {
        "name": "device_1",
        "attributes": [
            {
                "name": "temperature_1",
                "d": 23,  # digit / wert
                "u": "°C"  # unit / maßeinheit
            },
            {
                "name": "temperature_2",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            },
            {
                "name": "humidity",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            },
            {
                "name": "pressure",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            }
        ]
    },
    {
        "name": "device_2",
        "attributes": [
            {
                "name": "temperature_1",
                "d": 23,  # digit / wert
                "u": "°C"  # unit / maßeinheit
            },
            {
                "name": "temperature_2",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            },
            {
                "name": "humidity",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            },
            {
                "name": "pressure",
                "d": [0.5, 0.7, -0.4],
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
                "name": f"device_{idx}",  # TODO Thing ID auslesen? thing.td["id"]
                "attributes": []
            })
            # lies und speicher alle Sensor Attribute dieses Things
            #ThingDescription.from_thing(thing.thing)
            print(thing.td)
            for attr in ATTRIBUTES:  # TODO for prop in thing.properties
                val = await thing.read_property(attr)  # TODO prop
                # print(f"recived {attr}-value: {val}")
                obj = {
                    "name": attr,  # TODO prop
                    "d": val["d"],
                    "u": val["u"]
                }
                data_obj[idx]["attributes"].append(obj)
                await asyncio.sleep(1)
        print("DATA_OBJECTS updated ####################")
        print(data_obj)
        print("#########################################")
        # Sensordaten global hinterlegen um sie in der Indexmethode abrufen zu können
        global DATA_OBJECTS
        DATA_OBJECTS = data_obj
        await asyncio.sleep(1)


def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_data_objects())


async def create_things():
    """
    Hole alle TDs und erzeuge consumed things daraus.
    """
    wot = WoT(servient=Servient())
    global THINGS
    tdgen = TDGenerator()
    await tdgen.startup()
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
    # Things erzeugen
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_things())
    # Neuer Thread läuft im hintergrund und updated alle 3 sek unser DATA_OBJECTS
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=loop_in_thread, args=(loop,))
    t.start()
    # HTTP Server starten
    app.run(host='0.0.0.0')
