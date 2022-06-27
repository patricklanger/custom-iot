import json
import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)


async def get_sensor_data(context, url):
    request = Message(code=Code.GET, uri=url)
    response = await context.request(request).response
    res = response.payload.decode("UTF-8").replace('\x00', '')
    return json.loads(res)


async def switch_all_leds(context, led_urls, value):
    """
    value: 1: lampen an; 0: lampen aus
    """
    for url in led_urls:
        print("switch_leds ", led_urls.index(url), " to ", value)
        # TODO Was muss in den payload?? Nur 1 oder 0
        url = url.replace("(", "%28").replace(")", "%29")
        request = Message(code=Code.PUT, payload=str.encode(str(value)), uri=url)
        await context.request(request).response
        # TODO Response verarbeiten: Failure catchen oder so?  


async def get_resources(context):
    """
    gibt alle Resources der Resource Directory zurück.
    Wenn ein Fehler auftritt wird null zurückgegeben.
    """
    request = Message(code=Code.GET, uri="coap://localhost/resource-lookup/")

    try:
        # Alle resourcen alleer diveces abfragen
        response = await context.request(request).response
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


async def main():
    """Startet einen Loop um alle Lampen anzuschalten bzw. alles auszuschalten, sofern mindestens ein Device über
    Kopf gehalten wird."""

    context = await Context.create_client_context()

    await asyncio.sleep(3)

    while True:

        # Request um alle Resourcen abfragen zu können vorbereiten
        resources = await get_resources(context)
        accel_urls = [url for url in resources if "SENSE_ACCEL" in url]
        led_urls = [url for url in resources if "LED" in url]

        # über alle Sensoren iterieren und nach SENSE_ACCEL Sensoren suchen
        #if any("SENSE_ACCEL" in url for url in resources):
        for url in accel_urls:
            print("check ACCL url: ", accel_urls.index(url))
            all_dives_up = True
            acc_list = await get_sensor_data(context, url)
            # in 'd' ist das value des Sensors

            # Wenn index 2 im Acc_List < -0.5 ist, ist er über kopf
            if acc_list['d'][2] < -0.5:
                all_dives_up = False
                await switch_all_leds(context, led_urls, 0)
            print("all_dives_up: ", all_dives_up)
            if all_dives_up:
                await switch_all_leds(context, led_urls, 1)

        await asyncio.sleep(2)
















    # await context.shutdown()


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
