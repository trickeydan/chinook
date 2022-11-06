from __future__ import annotations

import asyncio
import contextlib
import json
from typing import AsyncGenerator, TYPE_CHECKING, Type

import asyncio_mqtt as aiomqtt
from pydantic import BaseModel, ValidationError, parse_raw_as

from common import DOMAIN_MAP, AstoriaState, StateDomain

if TYPE_CHECKING:
    from paho.mqtt.client import MQTTMessage

class AstoriaService:

    def __init__(self) -> None:
        self._state = AstoriaState(disks=None, process=None, tick=None)
        self._state_lock = asyncio.Lock()

    async def main(self) -> None:
        async with contextlib.AsyncExitStack() as stack:
            client = aiomqtt.Client("localhost", client_id="test")
            await stack.enter_async_context(client)

            await self.setup(client)

            tasks = set()

            for domain, model in DOMAIN_MAP.items():
                manager = client.filtered_messages(f"ast/dom/{domain}")
                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self._handle_state_message(messages, domain, model))
                tasks.add(task)

            messages = await stack.enter_async_context(client.unfiltered_messages())
            task = asyncio.create_task(self._handle_unknown_message(messages))
            tasks.add(task)

            await client.subscribe("ast/dom/+")

            await asyncio.gather(*tasks)

        await self._cancel_tasks()

    async def setup(self, client) -> None:
        pass

    async def handle_state(self, state: AstoriaState) -> None:
        pass

    async def _handle_unknown_message(self, messages: AsyncGenerator[MQTTMessage, None]) -> None:
        async for message in messages:
            print(f"[unknown@{message.topic}]{message.payload}")

    async def _handle_state_message(
        self,
        messages: AsyncGenerator[MQTTMessage, None],
        domain: StateDomain,
        model: Type[BaseModel],
    ) -> None:
        async for message in messages:
            if message.payload:
                try:
                    data = parse_raw_as(model, message.payload)
                    async with self._state_lock:
                        self._state[domain] = data  # type: ignore[typeddict-item]
                        asyncio.create_task(self.handle_state(self._state))
                except ValidationError as e:
                    print(e)
                except json.JSONDecodeError as e:
                    print(e)
            else:
                async with self._state_lock:
                    self._state[domain] = None
                    asyncio.create_task(self.handle_state(self._state))

    async def _cancel_tasks(self):
        for task in asyncio.all_tasks():
            if task.done():
                continue
            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass


class TestService(AstoriaService):

    async def tick(self, client: aiomqtt.Client) -> None:
        await asyncio.sleep(1)
        n = 1
        while True:
            async with self._state_lock:
                if self._state["tick"]:
                    n += self._state["tick"].n
                else:
                    n += 1
            await client.publish("ast/dom/tick", f"{{\"n\": {n}}}")
            await asyncio.sleep(1)

    async def forever(self) -> None:
        while True:
            print("yeet")
            await asyncio.sleep(0.5)

    async def setup(self, client) -> None:
        asyncio.create_task(self.forever())
        asyncio.create_task(self.tick(client))

    async def handle_state(self, state: AstoriaState) -> None:
        print(state)
        if state["tick"] and state["tick"].n > 4000:
            print("Time to exit!")
            await self._cancel_tasks()



if __name__ == "__main__":
    service = TestService()
    try:
        asyncio.run(service.main())
    except asyncio.CancelledError:
        print("Exited")