from websockets.asyncio.server import ServerConnection
import websockets

import asyncio
import random
from uuid import UUID
import json
from pprint import pprint

# 示例题目池
questions: list[str] = [
    "请简要分析人工智能对未来社会的影响。",
    "谈谈你对‘内卷’现象的看法。",
    "环保和经济发展能否兼顾？",
    "如何在压力中保持心理健康？",
    "你如何看待远程办公？",
    "社交媒体对青少年有什么影响？",
    "你对传统文化在现代社会的价值有何看法？",
    "如果你设计一门新课程，会是什么？",
    "终身学习对职场人意味着什么？",
    "请从你的生活经历谈谈一个改变你想法的事件。"
]

# 存储当前连接和任务的映射
# interviewee_client_tasks: dict[ServerConnection, asyncio.Task[None]] = {}


async def send_questions_to_client(
    websocket: ServerConnection, id: UUID
) -> None:
    for i in range(10, 0, -1):
        payload = {
            'type': 'waiting',
            'count': i,
        }
        payloads_string = json.dumps(payload)
        print(f"发送消息到{id}")
        pprint(payload)
        print()
        await websocket.send(payloads_string)
        await asyncio.sleep(1)

    while True:
        question: str = random.choice(questions)
        payload = {
            'type': 'question',
            'content': question,
        }
        payloads_string = json.dumps(payload)
        print(f"发送消息到{id}")
        pprint(payload)
        print()
        await websocket.send(payloads_string)
        await asyncio.sleep(1)


async def interviewee_handler(websocket: ServerConnection) -> None:
    id = websocket.id

    print(f"面试者端{id}连接")
    task: asyncio.Task[None] = asyncio.create_task(
        send_questions_to_client(websocket, id)
    )
    # interviewee_client_tasks[websocket] = task

    try:
        await websocket.wait_closed()
    finally:
        print(f"面试者端{id}断开")
        task.cancel()
        # interviewee_client_tasks.pop(websocket, None)


async def interviewer_handler(websocket: ServerConnection) -> None:
    pass  # TODO


async def main() -> None:
    interviewee_server = websockets.serve(interviewee_handler, "0.0.0.0", 9009)
    interviewer_server = websockets.serve(interviewer_handler, "0.0.0.0", 9008)

    async with interviewee_server, interviewer_server:
        print("WebSocket 服务器已启动...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
