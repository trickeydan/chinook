import asyncio_mqtt as aiomqtt
import asyncio

from chinook import ChinookService, ChinookState

class TestService(ChinookService):

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

    async def handle_state(self, state: ChinookState) -> None:
        print(state)
        if state["tick"] and state["tick"].n > 40:
            print("Time to exit!")
            await self._cancel_tasks()



if __name__ == "__main__":
    service = TestService()
    try:
        asyncio.run(service.main())
    except asyncio.CancelledError:
        print("Exited")