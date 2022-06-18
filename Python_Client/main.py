import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)


async def main():
    """Perform a single PUT request to localhost on the default port, URI
    "/other/block". The request is sent 2 seconds after initialization.

    The payload is bigger than 1kB, and thus sent as several blocks."""

    context = await Context.create_client_context()

    await asyncio.sleep(2)

    payload = ""  # b"The quick brown fox jumps over the lazy dog.\n" * 30
    request = Message(code=GET, payload=payload, uri="coap://localhost/.well-known/core")

    try:
        response = await context.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print(f'Result: {response.code} \n {response.payload}')

    # response sieht irgendwie so aus:
    # {
    #     name: "",
    #     actions: {
    #         link1: "/resources", <- Das wollen wir haben
    #         link2: "/devices",
    #         ...
    #     }
    # }
    #
    # Funktion um alle sensoren auszulesen:
    # -> wir machen einen zweiten aufruf mit dem resources link und bekommen zugriff auf alle resources.
    # -> Für jeden Sensor ein GET request machen und ergebnis printen.
    # Funktion alle zwei sekunden wiederholen.. oder so
    #

if __name__ == "__main__":
    asyncio.run(main())
