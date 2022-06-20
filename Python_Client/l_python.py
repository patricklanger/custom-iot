import time
import json
import asyncio
import logging
import link_header
from aiocoap import Context, Message, Code

logging.basicConfig(level=logging.ERROR)


async def coap_get(ctx, uri):
    request = Message(code=Code.GET, uri=uri)
    message = await ctx.request(request).response
    return message.payload.decode('utf-8')


async def coap_put(ctx, uri, payload):
    request = Message(code=Code.PUT, payload=payload, uri=uri)
    await ctx.request(request).response


async def core_resources(ctx, query=""):
    res = await coap_get(ctx, f"coap://[::1]/resource-lookup/{query}")
    return link_header.parse(res).links


async def read_buttons(ctx):
    for dev in await core_resources(ctx, "?if=saul&rt=SENSE_BTN"):
        phydat_json = await coap_get(ctx, dev.href)
        phydat_value = json.loads(phydat_json)['d']
        if phydat_value == 1:
            return True
    return False


async def write_lights(ctx, state):
    payload = str.encode(str(state))
    for dev in await core_resources(ctx, "?if=saul&rt=ACT_SWITCH"):
        await coap_put(ctx, dev.href, payload)


async def poll_switch(ctx, event):
    while True:
        pressed = await read_buttons(ctx)
        if pressed:
            event.set()
        await asyncio.sleep(5.0)


async def observe_switch(ctx, uri, event):
    print(f"subscribe {uri}")
    msg = Message(code=Code.GET, uri=uri, observe=0)

    req = ctx.request(msg)
    req.observation.register_errback(lambda msg: print(f"subscribe failed for {uri}"))

    resp = await req.response
    async for r in req.observation:
        event.set()


async def observe_rd(ctx, subs, event):
    msg = Message(code=Code.GET, uri="coap://[::1]/resource-lookup/", observe=0)
    req = ctx.request(msg)
    req.observation.register_errback(lambda msg: print(f"subscribe failed for rd"))

    resp = await req.response

    async for r in req.observation:
        # print(f"rd: {r.payload}")
        links = link_header.parse(r.payload.decode()).links
        for link in links:
            # print(link)
            if not link.href in subs.keys():
                if "rt" in link and len(link.rt) > 0 and link.rt[0] == "SENSE_BTN":
                    task = asyncio.create_task(observe_switch(ctx, link.href, event))
                    subs[link.href] = task


async def main():
    ctx = await Context.create_client_context()
    event = asyncio.Event()
    state = False
    subs = {}

    for dev in await core_resources(ctx, "?if=saul&rt=SENSE_BTN"):
        task = asyncio.create_task(observe_switch(ctx, dev.href, event))
        subs[dev.href] = task
    asyncio.create_task(observe_rd(ctx, subs, event))
    asyncio.create_task(poll_switch(ctx, event))

    while True:
        await event.wait()

        # toggle switch
        state = not state
        print("ON" if state else "OFF")
        await write_lights(ctx, "1" if state else "0")

        # toggle rate limit
        await asyncio.sleep(0.5)
        event.clear()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task = loop.create_task(main())
    try:
        # loop.run_until_complete(task)
        loop.run_forever()
    except KeyboardInterrupt:
        print()