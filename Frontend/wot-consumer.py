#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WoT client application that takes a Thing Description URL and
subscribes to all observable properties and events in the consumed Thing.
"""

import argparse
import asyncio
import logging

from wotpy.protocols.coap.client import CoAPClient
from wotpy.wot.servient import Servient
from wotpy.wot.td import ThingDescription
from wotpy.wot.wot import WoT

import wotpy

logging.basicConfig()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


DESCRIPTION = {
	"id": "urn:simple",
	"@context": "https://www.w3.org/2022/wot/td/v1.1",
	"title": "MyLampThing",
	"description": "Valid TD copied from the spec's first example",
	"security": [
		"nosec"
	],
	"properties": {
		"status": {
			"type": "string",
			"forms": [
				{
					"href": "coap://[2001:67c:254:b0b2:affe:2896:134b:16e6]/saul/9-mpl3115a2-SENSE_TEMP"
				}
			]
		}
	}
}
#     {
#     "id": "urn:dev:wot:com:example:servient:lamp",
#     "title": "MyLampThing",
#     "description": "MyLampThing uses JSON-LD 1.1 serialization",
#     "security": [{"scheme": "nosec"}],
#     "properties": {
#         # Link zum device
#         "temperature": {
#             "description": "Shows the current status of the lamp",
#             "type": "string",
#             "observable": True,
#             "forms": [{
#                 "href": "coap://[2001:67c:254:b0b2:affe:2896:134b:16e6]/saul/9-mpl3115a2-SENSE_TEMP"
#             }]
#         }
#     }
# }


async def main():
    """Subscribes to all events and properties on the remote Thing."""

    wot = WoT(servient=Servient())
    consumed_thing = wot.consume(DESCRIPTION)

    # LOGGER.info("ConsumedThing: {}".format(consumed_thing))

    # coap = CoAPClient()
    # td = ThingDescription(DESCRIPTION)
    # print(td.to_dict())
    # print(td.get_property_forms('status'))
    # val = wotpy.wot.consumed.interaction_map.ConsumedThingProperty(consumed_thing, 'temperature')
    # print(consumed_thing.td.properties)
    val = await consumed_thing.read_property('status')
    # val = await coap.read_property(DESCRIPTION, 'status')  # AttributeError: 'dict' object has no attribute 'get_property_forms'
    print(val)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())