import json
import logging
import asyncio
import threading

from aioflask import Flask, render_template
from aiocoap import *
#
# logging.basicConfig(level=logging.INFO)
#
# print(f"In flask global level: {threading.current_thread().name}")
# app = Flask(__name__)
#
# context = None
#
device_object = [
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


async def get_resources(ctx):
    """
    gibt alle Resources der Resource Directory zurück.
    Wenn ein Fehler auftritt wird null zurückgegeben.
    """
    print("get_resources")
    print(f"Inside flask function: {threading.current_thread().name}")
    request = Message(code=Code.GET, uri="coap://localhost/resource-lookup/")

    try:
        # Alle resourcen alleer diveces abfragen
        print("get_resources 2")
        response = await ctx.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
        return []
    else:
        # Antwort ausprinten und verarbeitbar machen, bestimmte zeichen löschen
        # print(f'Result: {response.code} \n {response.payload.decode("UTF-8")}')
        resources = response.payload.decode('UTF-8')
        resources = resources.replace("<", "").replace(">", "").split(",")
        return resources
#
#
# @app.route('/')
# async def get_device_dashboard():
#     print('get_device_dashboard')
#     print(f"Inside flask function: {threading.current_thread().name}")
#     try:
#         # TODO Device abfrage an aiocoap-rd.
#         # TODO kann http-webserver mit coap auf aiocoap-rd zugreifen??
#         resources = await get_resources()
#         print(resources)
#         res = device_object  # requests.get("https://api.npoint.io/4af156202f984d3464c3")
#     except Exception as e:
#         print('Failed to fetch resource:')
#         print(e)
#         return ""
#     # alle dives als josn objekte
#     all_devices = res  # json.loads(res.text)
#     # webseite rendern mit allen devices
#     return render_template("index.html", all_devices=all_devices)
#
#
# async def create_context():
#     global context
#     context = await Context.create_client_context()
#     await asyncio.sleep(3)
#
#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(create_context())
#     app.run(host='0.0.0.0')
#
#
import asyncio
from aioflask import Flask, render_template

app = Flask(__name__)

@app.route('/')
async def index():
    context = await Context.create_client_context()
    await asyncio.sleep(3)
    x = await get_resources(context)
    print(x)
    return await render_template('index.html')


app.run(host='0.0.0.0')
