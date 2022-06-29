#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WoT client application that takes a Thing Description URL and
subscribes to all observable properties and events in the consumed Thing.
"""

import argparse
import asyncio
import logging

from wotpy.wot.servient import Servient
from wotpy.wot.wot import WoT

import wotpy

logging.basicConfig()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


DESCRIPTION = {
    "id": "urn:dev:wot:com:example:servient:lamp",
    "title": "MyLampThing",
    "description": "MyLampThing uses JSON-LD 1.1 serialization",
    "security": [{"scheme": "nosec"}],
    "properties": {
        # Link zum device
        "temperature": {
            "description": "Shows the current status of the lamp",
            "type": "string",
            "observable": True,
            "forms": [{
                "href": "coap://[2001:67c:254:b0b2:affe:2896:134b:16e6]/saul/9-mpl3115a2-SENSE_TEMP"
            }]
        }
    }
}


async def main():
    """Subscribes to all events and properties on the remote Thing."""

    wot = WoT(servient=Servient())
    consumed_thing = wot.consume(DESCRIPTION)

    # LOGGER.info("ConsumedThing: {}".format(consumed_thing))

    val = wotpy.wot.consumed.interaction_map.ConsumedThingProperty(consumed_thing, 'temperature')
    # val = consumed_thing.read_property('temperature')
    print(val.read())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())