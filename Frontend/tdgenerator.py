#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WoT application to generate Thing Discriptions from Resource Directory - Resource-Lookup request
"""

import logging
from aiocoap import *
import asyncio
from copy import copy

logging.basicConfig()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#  --------------------------------
temp_url = "coap://[2001:67c:254:b0b2:affe:2896:134b:16e6]/saul/9-mpl3115a2-SENSE_TEMP"
# ---------------------------------

RD_URL = "coap://localhost/resource-lookup/"

DESCRIPTION = {
    "id": "",
    "@context": "https://www.w3.org/2022/wot/td/v1.1",
    "title": "IoT Device",
    "description": "IoT Sensor Device that sense humidity, temperature and light color",
    "properties": {
        "temperature": {
            "type": "string",
            "forms": [
                {
                    "op": "readproperty",
                    "contentType": "text/plain",
                    "href": ""
                }
            ]
        },
        "humidity": {
            "type": "string",
            "forms": [
                {
                    "op": "readproperty",
                    "contentType": "text/plain",
                    "href": ""
                }
            ]
        },
        "color": {
            "type": "string",
            "forms": [
                {
                    "op": "readproperty",
                    "contentType": "text/plain",
                    "href": ""
                }
            ]
        },
    }
}


async def get_resources(ctx):
    """
    gibt alle Resources der Resource Directory zurück.
    Wenn ein Fehler auftritt wird null zurückgegeben.
    """
    print("get_resources")
    request = Message(code=Code.GET, uri=RD_URL)

    try:
        # Alle resourcen aller diveces abfragen
        response = await ctx.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
        return []
    else:
        # Antwort ausprinten und verarbeitbar machen, bestimmte zeichen löschen
        resources = response.payload.decode('UTF-8')
        resources = resources.replace("<", "").replace(">", "").split(",")
        return resources


async def device_registration(context):
    """
    Erstellt eine Liste von TD-dicts.
    Diese bekommen als id die device-ip.
    Links zu entsprechenden resourcen werden den td-dicts hinzugefügt
    """
    print("device_registration")
    # Das wird die Liste fuer die Thing Descriptions
    td_list = []
    # get_resources gibt uns die URLs zu allen Ressourcen, die wir haben zurueck
    resources = await get_resources(context)
    # für jede IP die in den Resourcen vorkommt lege eine TD an
    # ... mehrere IPs kommen vor wenn es mehrere Things gibt.
    for url in resources:
        ip = url.split("/")[2]
        if [td for td in td_list if td['id'] == ip]:
            # Fuer jede neue IP wird neue DESCRIPTION erstellt (TD pro Device)
            td = copy(DESCRIPTION)
            # die Id bekommt die IP
            td['id'] = ip
            # Thing Description fuegen wir in die Liste ein
            td_list.append(td)
    # füge den angelegten TDs die urls zu ihren resourcen zu.
    print(td_list)
    for url in resources:
        td = [td for td in td_list if td['id'] == url.split("/")[2]][0]
        if 'SENSE_TEMP' in url:
            td["properties"]["temperature"]["forms"]["href"] = url
        if 'SENSE_HUM' in url:
            td["properties"]["humidity"]["forms"]["href"] = url
        if 'SENSE_COLOR' in url:
            td["properties"]["color"]["forms"]["href"] = url
    return td_list


class TDGenerator:
    """
    Erstellt für alle devices in der Resource Directory eine TD als dictionary.
    """
    def __init__(self):
        self.td_list = []

    # Context wird erzeugt
    async def startup(self):
        context = await Context.create_client_context()
        await asyncio.sleep(3)

        # Erzeugen einer Liste von Thing Descriptions
        self.td_list = await device_registration(context)
        print(f"registration for {len(self.td_list)} finished")

    def get_thing_descriptions(self):
        """
        Gibt alle Thing Descriptions in einer Liste zurück.
        """
        return self.td_list

