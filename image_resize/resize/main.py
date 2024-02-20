import asyncio
import random
import time
import signal



RUN=True
DRAIN = False


def drain (signum, frame):
    print("Draining ", signum, frame )
    global DRAIN
    DRAIN = True


signal.signal(signal.SIGTERM, drain)




async def worker(name, queue: asyncio.Queue):
    while True:
        # Get a "work item" out of the queue.
        task = await queue.get()

        # Sleep for the "sleep_for" seconds.
        await asyncio.sleep(3)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

        print(f'{name} has solved task {task}!')

        if DRAIN and queue.empty():
            print("Ending task worker loop.")
            break


async def task_creation(queue: asyncio.Queue):
    i = 0
    while True:

        if DRAIN:
            print("Ending task creation loop.")
            break

        print(f'Putting task {i} in the queue')
        queue.put_nowait(i)
        i += 1



        await asyncio.sleep(2)




async def main(queue):
    # Create a queue that we will use to store our "workload".



    # Create three worker tasks to process the queue concurrently.
    asyncio.create_task(worker(f'worker-1', queue))


    await asyncio.gather(task_creation(queue))


if __name__ == '__main__':
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()
    asyncio.run(main(queue))
    print("Done")