#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WoT application to expose a Thing that provides simulated temperature values.
"""

import json
import logging
import random

# import tornado.gen
# from tornado.ioloop import IOLoop, PeriodicCallback

from wotpy.protocols.http.server import HTTPServer
from wotpy.protocols.ws.server import WebsocketServer
from wotpy.wot.servient import Servient

from aiocoap import *
import asyncio

CATALOGUE_PORT = 9090
WEBSOCKET_PORT = 9393
HTTP_PORT = 9494

GLOBAL_TEMPERATURE = None
PERIODIC_MS = 3000
DEFAULT_TEMP_THRESHOLD = "coap://[2001:67c:254:b0b2:affe:2896:134b:16e6]/saul/5-hdc1000-SENSE_TEMP"  # 27.0

logging.basicConfig()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

ID_THING = "urn:temperaturething"
NAME_PROP_TEMP = "temperature"
NAME_PROP_TEMP_THRESHOLD = "high-temperature-threshold"
NAME_EVENT_TEMP_HIGH = "high-temperature"

DESCRIPTION = {
    "id": ID_THING,
    "name": ID_THING,
    "properties": {
        NAME_PROP_TEMP: {
            "type": "number",
            "readOnly": True,
            "observable": True
        },
        # Link zum device
        NAME_PROP_TEMP_THRESHOLD: {
            "type": "number",
            "observable": True
        }
    },
    "events": {
        NAME_EVENT_TEMP_HIGH: {
            "data": {
                "type": "number"
            }
        }
    }
}


def update_temp():
    """Updates the global temperature value."""

    # globale Variable, die zufallszahlen generiert
    global GLOBAL_TEMPERATURE
    GLOBAL_TEMPERATURE = round(random.randint(20.0, 30.0) + random.random(), 2)
    LOGGER.info("Current temperature: {}".format(GLOBAL_TEMPERATURE))


async def emit_temp_high(exp_thing, context):
    """Emits a 'Temperature High' event if the temperature is over the threshold.
    - der funktion wird das ExposedThing übergeben.
    - der wert NAME_PROP_TEMP_THRESHOLD wird aus dem Thing ausgelesen
    - anschließen verglichen ob Global Temp höher ist als die ausgelsene Temp aus dem device"""

    # vermutlich kann man so den link aus der description auslesen
    temp_threshold = await exp_thing.read_property(NAME_PROP_TEMP_THRESHOLD)
    request = Message(code=Code.GET, uri=temp_threshold)
    response = await context.request(request).response
    res = response.payload.decode("UTF-8").replace('\x00', '')
    LOGGER.info("Emitting high temperature event: {}".format(json.loads(res)))

    # if temp_threshold and GLOBAL_TEMPERATURE > temp_threshold:
    #     LOGGER.info("Emitting high temperature event: {}".format(GLOBAL_TEMPERATURE))
    #     # TODO Was ist dieses emit_event??
    #     exp_thing.emit_event(NAME_EVENT_TEMP_HIGH, GLOBAL_TEMPERATURE)


def temp_read_handler():
    """Custom handler for the 'Temperature' property.
    ... vermutlich müsste hier der coap call zum device passieren um die temp abzufragen"""

    LOGGER.info("Doing some work to simulate temperature retrieval")



async def main():
    update_temp()

    LOGGER.info("Creating WebSocket server on: {}".format(WEBSOCKET_PORT))

    ws_server = WebsocketServer(port=WEBSOCKET_PORT)

    LOGGER.info("Creating HTTP server on: {}".format(HTTP_PORT))

    http_server = HTTPServer(port=HTTP_PORT)

    LOGGER.info("Creating servient with TD catalogue on: {}".format(CATALOGUE_PORT))

    # Servient kann sowohl Client, als auch Server sein und man kann sich und reserviert Port fuer Katalog / TD
    servient = Servient(catalogue_port=CATALOGUE_PORT)
    servient.add_server(ws_server)
    servient.add_server(http_server)

    LOGGER.info("Starting servient")

    # startet server und gibt wot object zurück
    wot = await servient.start()

    LOGGER.info("Exposing and configuring Thing")

    context = await Context.create_client_context()
    await asyncio.sleep(3)

    # macht aus der json-description ein ExposedThing-Object
    # an dem Objekt können diverse funktionalitäten des beschriebenen devies abgelesen/aufgerufen werden
    # u.a. die Interaktionsmöglichkeiten: Property(werte auslesen), action (lampe an machen), event (benachrichtigt werden, wenn ...)
    exposed_thing = wot.produce(json.dumps(DESCRIPTION))
    # read handler wird gesetzt um für bestimmte properties aktionen auszuführen. .. zB angefügte URL abfragen.. ? vermutlich
    exposed_thing.set_property_read_handler(NAME_PROP_TEMP, temp_read_handler)
    # in das property NAME_PROP_TEMP_THRESHOLD in der TD wird ein value eingetragen
    await exposed_thing.properties[NAME_PROP_TEMP_THRESHOLD].write(DEFAULT_TEMP_THRESHOLD)
    # Thing wird anschließen benutzbar / interagierbar gemacht. .. vorher wurde es quasi initianlisiert
    exposed_thing.expose()

    # GLOBAL_TEMPERATURE wird alle drei sekunden mit neuen random werten gesetzt
    # periodic_update = PeriodicCallback(update_temp, PERIODIC_MS)
    # periodic_update.start()

    # async def emit_for_exposed_thing():
    #     await emit_temp_high(exposed_thing, context)
    #
    # periodic_emit = PeriodicCallback(emit_for_exposed_thing, PERIODIC_MS)
    # periodic_emit.start()

    await emit_temp_high(exposed_thing, context)


if __name__ == "__main__":
    LOGGER.info("Starting loop")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())