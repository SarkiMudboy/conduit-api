import concurrent.futures
import queue
from functools import partial


class TestWorker:
    """Test class for ThreadPoolExecutor"""

    def __init__(self, name):
        self.name = name
        self.queue = queue.Queue()

    def work(self, subject, org):

        for i in range(subject["age"]):
            message = f'he is {subject["name"]} at {i} years old and height:{subject["height"]}'
            self.queue.put(message)
            print(message)

        print(f"reported by -> {org}")

    def launch(self, data):

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as exec:
            sig = partial(self.work, org="MdHealth")
            exec.map(sig, data)

        msgs = []
        while not self.queue.empty():
            msgs.append(self.queue.get())
        print(msgs)


if __name__ == "__main__":

    data = [
        {
            "name": "John",
            "age": 1,
            "height": 20,
        },
        {"name": "Maya", "age": 3, "height": 19},
        {"name": "Hans", "age": 2, "height": 10},
    ]

    worker = TestWorker("first")
    worker.launch(data)
