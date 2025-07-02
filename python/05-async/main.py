from wit_world import exports
import asyncio

# Define an asynchronous task that waits for 2 seconds
async def task1():
    print("Starting task 1...")
    await asyncio.sleep(2)  # Simulates an I/O-bound task
    print("Task 1 completed after 2 seconds")

# Define another asynchronous task that waits for 1 second
async def task2():
    print("Starting task 2...")
    await asyncio.sleep(1)
    print("Task 2 completed after 1 second")

# Main coroutine that runs both tasks sequentially
async def main():
    await task1()
    await task2()

# Required empty IncomingHandler (for WASM exports)
class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        pass

# Run entry point (called by WASM host)
class Run(exports.Run):
    def run(self) -> None:
        asyncio.run(main())
