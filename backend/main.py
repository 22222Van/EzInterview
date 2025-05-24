from websockets.asyncio.server import ServerConnection
import websockets

import asyncio
import json
from pprint import pprint

from typing import Optional, Any, Literal

SystemStateType = Literal['idle', 'counting', 'interviewing']
IntervieweeStateType = Literal[
    'preparing', 'waiting', 'counting', 'interviewing', 'finished'
]


# # 示例题目池
# questions: list[str] = [
#     "请简要分析人工智能对未来社会的影响。",
#     "谈谈你对‘内卷’现象的看法。",
#     "环保和经济发展能否兼顾？",
#     "如何在压力中保持心理健康？",
#     "你如何看待远程办公？",
#     "社交媒体对青少年有什么影响？",
#     "你对传统文化在现代社会的价值有何看法？",
#     "如果你设计一门新课程，会是什么？",
#     "终身学习对职场人意味着什么？",
#     "请从你的生活经历谈谈一个改变你想法的事件。"
# ]


async def send_payload(websocket: ServerConnection, payload: Any):
    payloads_string = json.dumps(payload)
    print(f"发送消息到{websocket.id}")
    pprint(payload)
    print()
    await websocket.send(payloads_string)


# async def send_questions_to_client(
#     websocket: ServerConnection, id: UUID
# ) -> None:
#     for i in range(10, 0, -1):
#         await send_payload(websocket, id, {
#             'type': 'waiting',
#             'count': i,
#         })
#         await asyncio.sleep(1)

#     while True:
#         question: str = random.choice(questions)
#         await send_payload(websocket, id, {
#             'type': 'question',
#             'content': question,
#         })
#         await asyncio.sleep(1)

class InterviewSystem:
    def __init__(self) -> None:
        super().__init__()
        self.preparing_candidates: set[ServerConnection] = set()
        self.queueing_candidates: list[ServerConnection] = []
        self.interviewing_candidate: Optional[ServerConnection] = None
        self.finished_candidates: set[ServerConnection] = set()
        self.interviewer: Optional[ServerConnection] = None
        self.interviewing_state: SystemStateType = 'counting'

    @property
    def state(self) -> SystemStateType:
        if self.interviewing_candidate is None:
            return 'idle'
        return self.interviewing_state

    def next_candidate(self) -> None:
        if self.interviewing_candidate is not None:
            self.finished_candidates.add(self.interviewing_candidate)
        self.interviewing_candidate = None
        if len(self.queueing_candidates) != 0:
            self.interviewing_candidate = self.queueing_candidates.pop(0)
            self.interviewing_state = 'counting'

    async def flush_frontends(self):
        shared_data = {
            'questionTitles': ['1', '2', '3', '4', '5', '6', '7', '8'],
            'queueQuestionCount': 0,
        }

        tasks = []

        total_queue_count = len(self.queueing_candidates)
        if self.state != 'idle':
            total_queue_count += 1
        for c in self.preparing_candidates:
            data = {
                'type': 'preparing',
                'queueCount': total_queue_count,
                **shared_data
            }
            tasks.append(send_payload(c, data))

        for i, c in enumerate(self.queueing_candidates):
            data = {
                'type': 'waiting',
                'queueCount': i + 1,
                **shared_data
            }
            tasks.append(send_payload(c, data))

        if self.interviewing_candidate is not None:
            tasks.append(send_payload(self.interviewing_candidate, {
                'type': self.interviewing_state,
            }))

        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"发送任务出错：{r}")

    async def add_interviewee(self, websocket: ServerConnection):
        if (
            websocket not in self.queueing_candidates and
            websocket is not self.interviewing_candidate and
            websocket not in self.finished_candidates
        ):
            self.preparing_candidates.add(websocket)
            await self.flush_frontends()

    async def pop_interviewee(self, websocket: ServerConnection):
        if websocket in self.preparing_candidates:
            self.preparing_candidates.remove(websocket)
        elif websocket in self.queueing_candidates:
            self.queueing_candidates.remove(websocket)
            await self.flush_frontends()
        elif websocket is self.interviewing_candidate:
            self.next_candidate()
            await self.flush_frontends()
        elif websocket in self.finished_candidates:
            self.finished_candidates.remove(websocket)

    async def parse_interviewee_message(
        self, websocket: ServerConnection, data: dict[Any, Any]
    ) -> bool:
        match data:
            case {'type': 'ready'}:
                if websocket in self.preparing_candidates:
                    print(f'面试者{websocket.id}已经准备好')
                    self.preparing_candidates.remove(websocket)
                    if self.state == 'idle':
                        self.interviewing_state = 'counting'
                        self.interviewing_candidate = websocket
                    else:
                        self.queueing_candidates.append(websocket)
                    await self.flush_frontends()
                else:
                    return False
            case {'type': 'start'}:
                raise NotImplementedError()
            case _:
                return False
        return True


system = InterviewSystem()


async def interviewee_handler(websocket: ServerConnection) -> None:
    global system

    id = websocket.id
    await system.add_interviewee(websocket)
    print(f"面试者端{id}连接")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if not isinstance(data, dict):
                    print(f"从面试者{id}收到非字典消息: {message!r}")
                    continue
                result = await system.parse_interviewee_message(websocket, data)
                if not result:
                    print(f"从面试者{id}收到异常 JSON 消息: {message!r}")
            except json.JSONDecodeError:
                print(f"从面试者{id}收到非 JSON 消息: {message!r}")
    finally:
        await system.pop_interviewee(websocket)
        print(f"面试者端{id}断开")


async def interviewer_handler(websocket: ServerConnection) -> None:
    global system

    id = websocket.id
    print(f"面试官端{id}连接")

    if system.interviewer is None:
        print(f'允许面试官端{id}的连接')
        system.interviewer = websocket
        # TODO: 发送允许消息，设置面试者端的初始状态
    else:
        print(f'拒绝面试官端{id}的连接')
        await send_payload(websocket, {'type': 'reject'})

    try:
        await websocket.wait_closed()
    finally:
        print(f"面试官端{id}断开")
        if system.interviewer is websocket:
            system.interviewer = None


async def main() -> None:
    interviewee_server = websockets.serve(interviewee_handler, "0.0.0.0", 9009)
    interviewer_server = websockets.serve(interviewer_handler, "0.0.0.0", 9008)

    async with interviewee_server, interviewer_server:
        print("WebSocket 服务器已启动...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
