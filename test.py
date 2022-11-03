from __future__ import annotations
import asyncio
import contextlib
import json
from typing import TypedDict, AsyncGenerator, TYPE_CHECKING

import asyncio_mqtt as aiomqtt
from pydantic import BaseModel, parse_raw_as, ValidationError

if TYPE_CHECKING:
    from paho.mqtt.client import MQTTMessage

class YeetException(Exception):
    pass

class DiskState(BaseModel):

    disks: list[str]


class ProcessState(BaseModel):

    running: bool

MAP = {
    "disks": DiskState,
    "process": ProcessState
}

class AstoriaState(TypedDict):

    disks: DiskState | None
    process: ProcessState | None


state = AstoriaState(disks=None, process=None)
state_lock = asyncio.Lock()
running = asyncio.Event()


async def handle_unknown_message(messages):
    async for message in messages:
        print(f"[unknown@{message.topic}]{message.payload}")

async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        try:
            task.cancel()
            await task
        except asyncio.CancelledError:
            pass

async def handle_state(messages: AsyncGenerator[MQTTMessage, None], domain: str):
    async for message in messages:
        model = MAP[domain]
        if message.payload:
            try:
                data = parse_raw_as(model, message.payload)
                print(f"[domain={domain}] {data}")
                async with state_lock:
                    state[domain] = data
                    print(state)
                    if state["disks"] and state["disks"].disks == ["boo"]:
                        raise YeetException("YEET")
            except ValidationError as e:
                print(e)
            except json.JSONDecodeError as e:
                print(e)
        else:
            async with state_lock:
                state[domain] = None
                print(state)


async def main():
    # We 💛 context managers. Let's create a stack to help us manage them.
    async with contextlib.AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        # Connect to MQTT broker
        client = aiomqtt.Client("localhost", client_id="test")
        await stack.enter_async_context(client)

        for domain in MAP:
            # Print all messages that match the filter
            manager = client.filtered_messages(f"ast/dom/{domain}")
            messages = await stack.enter_async_context(manager)
            task = asyncio.create_task(handle_state(messages, domain))
            tasks.add(task)

        # Handle messages that don't match a filter
        messages = await stack.enter_async_context(client.unfiltered_messages())
        task = asyncio.create_task(handle_unknown_message(messages))
        tasks.add(task)

        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("ast/dom/+")

        # Wait for everything to complete (or fail due to, e.g., network errors)
        await asyncio.gather(*tasks)

try:
    asyncio.run(main())
except YeetException:
    print("Quit")