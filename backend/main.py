from websockets.asyncio.server import ServerConnection
import websockets

import asyncio
import json
from pprint import pprint

from typing import Optional, Any, Literal

# 定义系统状态类型，限定为三种状态之一
SystemStateType = Literal['idle', 'counting', 'interviewing']

# 定义面试者状态类型，限定为五种状态之一
IntervieweeStateType = Literal[
    'preparing', 'waiting', 'counting', 'interviewing', 'finished'
]


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
    """
    将给定的payload对象序列化为JSON字符串并发送给指定的WebSocket连接，
    同时在控制台打印发送的消息内容和目标连接ID。

    Args:
        websocket (ServerConnection): 目标WebSocket连接。
        payload (Any): 要发送的数据（将被JSON序列化）。
    """
    payloads_string = json.dumps(payload)
    print(f"发送消息到{websocket.id}")
    pprint(payload)
    print()
    await websocket.send(payloads_string)


class InterviewSystem:
    """
    面试系统类，管理面试者的准备、排队、面试和完成状态，
    以及当前题目状态和面试官连接。
    """
    # 题目列表，展示在界面上方 '1 > 2 > 3 > ...' 位置
    question_titles = ['1', '2', '3', '4', '5', '6', '7', '8']

    def __init__(self) -> None:
        """
        初始化面试系统，包含不同状态的面试者集合和面试状态变量。
        """
        super().__init__()
        self.preparing_candidates: set[ServerConnection] = set()  # 准备中的面试者集合
        self.queueing_candidates: list[ServerConnection] = []  # 等待排队的面试者列表（队列）
        self.interviewing_candidate: Optional[ServerConnection] = None  # 当前面试者
        self.finished_candidates: set[ServerConnection] = set()  # 已完成面试者集合
        self.interviewer: Optional[ServerConnection] = None  # 当前连接的面试官
        self.interviewing_state: SystemStateType = 'counting'  # 当前面试者的面试状态
        self.current_question: int = 0  # 当前面试者所在的题目索引，从0开始

    def init_interview(self) -> None:
        """
        初始化或重置面试状态，设置为计数状态并重置题目索引。
        """
        self.interviewing_state = 'counting'
        self.current_question = 0

    @property
    def state(self) -> SystemStateType:
        """
        获取当前系统状态。
        如果没有面试者正在面试，则为'idle'，
        否则返回当前面试状态。

        Returns:
            SystemStateType: 当前系统状态。
        """
        if self.interviewing_candidate is None:
            return 'idle'
        return self.interviewing_state

    def next_candidate(self) -> None:
        """
        切换到下一个面试者：
        - 将当前面试者加入已完成集合（如果存在）
        - 从排队列表取出下一个面试者作为当前面试者
        - 初始化面试状态
        """
        if self.interviewing_candidate is not None:
            self.finished_candidates.add(self.interviewing_candidate)
        self.interviewing_candidate = None
        if len(self.queueing_candidates) != 0:
            self.interviewing_candidate = self.queueing_candidates.pop(0)
            self.init_interview()

    async def flush_interviewer(self):
        if self.interviewer is None:
            return

        if self.state == 'idle':
            await send_payload(self.interviewer, {
                'type': 'idle',
            })
        elif self.state == 'counting':
            await send_payload(self.interviewer, {
                'type': 'counting',
            })
        elif self.state == 'interviewing':
            await send_payload(self.interviewer, {
                'type': 'interviewing',
            })

    async def flush_current(self):
        """
        向当前正在面试的面试者发送当前状态和题目索引。
        """
        if self.interviewing_candidate is not None:
            await send_payload(self.interviewing_candidate, {
                'type': self.interviewing_state,
                'currentQuestion': self.current_question
            })

    async def flush_queue(self):
        """
        向所有准备中和排队中的面试者广播当前题目标题及其排队信息，
        包括题目总数减去当前题目的剩余数量。

        准备中的面试者收到 'preparing' 状态和队列总数。
        排队中的面试者收到 'waiting' 状态和其在队列中的位置。
        """
        shared_data = {
            'questionTitles': self.question_titles,
            'queueQuestionCount': len(self.question_titles)-self.current_question,
        }

        tasks = []

        # 计算当前排队总人数（包括正在面试者）
        total_queue_count = len(self.queueing_candidates)
        if self.state != 'idle':
            total_queue_count += 1

        # 给准备中的面试者发送准备状态及队列信息
        for c in self.preparing_candidates:
            data = {
                'type': 'preparing',
                'queueCount': total_queue_count,
                **shared_data
            }
            tasks.append(send_payload(c, data))

        # 给排队中的面试者发送等待状态及其排队位置
        for i, c in enumerate(self.queueing_candidates):
            data = {
                'type': 'waiting',
                'queueCount': i + 1,
                **shared_data
            }
            tasks.append(send_payload(c, data))

        # 并发执行所有发送任务，处理可能的异常
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"发送任务出错：{r}")

    async def add_interviewee(self, websocket: ServerConnection):
        """
        添加新的面试者进入准备状态（如果不在任何列表中），并刷新队列状态。

        Args:
            websocket (ServerConnection): 新连接的面试者WebSocket。
        """
        if (
            websocket not in self.queueing_candidates and
            websocket is not self.interviewing_candidate and
            websocket not in self.finished_candidates
        ):
            self.preparing_candidates.add(websocket)
            await self.flush_queue()

    async def pop_interviewee(self, websocket: ServerConnection):
        """
        移除断开连接的面试者，从相应的状态集合或列表中删除，
        并根据需要更新当前面试者及刷新状态。

        Args:
            websocket (ServerConnection): 断开连接的面试者WebSocket。
        """
        if websocket in self.preparing_candidates:
            self.preparing_candidates.remove(websocket)
        elif websocket in self.queueing_candidates:
            self.queueing_candidates.remove(websocket)
            await self.flush_queue()
        elif websocket is self.interviewing_candidate:
            self.next_candidate()
            await self.flush_current()
            await self.flush_queue()
        elif websocket in self.finished_candidates:
            self.finished_candidates.remove(websocket)

    async def parse_interviewee_message(
        self, websocket: ServerConnection, data: dict[Any, Any]
    ) -> bool:
        """
        解析来自面试者的消息，根据消息类型更新系统状态。

        支持的消息类型：
        - {'type': 'ready'}: 表示面试者准备好，加入排队或进入面试
        - {'type': 'start'}: 表示面试者开始正式面试，状态转为interviewing

        Args:
            websocket (ServerConnection): 发送消息的面试者连接。
            data (dict): 解析后的JSON消息内容。

        Returns:
            bool: 是否成功处理该消息。
        """
        match data:
            case {'type': 'ready'}:
                if websocket in self.preparing_candidates:
                    print(f'面试者{websocket.id}已经准备好')
                    self.preparing_candidates.remove(websocket)
                    if self.state == 'idle':
                        # 当前无面试者，直接开始面试
                        self.init_interview()
                        self.interviewing_candidate = websocket
                        await self.flush_current()
                        await self.flush_interviewer()
                    else:
                        # 系统正在面试，加入排队列表
                        self.queueing_candidates.append(websocket)
                    await self.flush_queue()
                else:
                    return False
            case {'type': 'start'}:
                if websocket is self.interviewing_candidate:
                    # 当前面试者开始正式面试
                    self.interviewing_state = 'interviewing'
                    await self.flush_current()
            case _:
                return False
        return True


system = InterviewSystem()


async def interviewee_handler(websocket: ServerConnection) -> None:
    """
    处理面试者WebSocket连接，管理消息收发与状态更新。

    Args:
        websocket (ServerConnection): 面试者连接对象。
    """
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
    """
    处理面试官WebSocket连接，允许或拒绝连接，并等待断开。

    Args:
        websocket (ServerConnection): 面试官连接对象。
    """
    global system

    id = websocket.id
    print(f"面试官端{id}连接")

    if system.interviewer is not None:
        await send_payload(system.interviewer, {'type': 'reject'})

    system.interviewer = websocket
    await system.flush_interviewer()

    try:
        await websocket.wait_closed()
    finally:
        print(f"面试官端{id}断开")
        if system.interviewer is websocket:
            system.interviewer = None


async def main() -> None:
    """
    程序入口，启动两个WebSocket服务器：
    - 面试者端口9009
    - 面试官端口9008
    并保持服务器持续运行。
    """
    interviewee_server = websockets.serve(interviewee_handler, "0.0.0.0", 9009)
    interviewer_server = websockets.serve(interviewer_handler, "0.0.0.0", 9008)

    async with interviewee_server, interviewer_server:
        print("WebSocket 服务器已启动...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
