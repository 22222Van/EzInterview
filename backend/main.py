from websockets.asyncio.server import ServerConnection
import websockets

import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Any, Literal


class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[37m',     # 白色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[41m',  # 红底白字
    }
    RESET = '\033[0m'

    def format(self, record):
        original_levelname = record.levelname
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{original_levelname}{self.RESET}"
        formatted = super().format(record)
        record.levelname = original_levelname
        return formatted


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    'interview_system.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,          # 最多保留5个备份文件
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

color_formatter = ColorFormatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler.setFormatter(color_formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


# 定义系统状态类型，限定为三种状态之一
SystemStateType = Literal['idle', 'counting', 'interviewing']

# 定义面试者状态类型，限定为五种状态之一
IntervieweeStateType = Literal[
    'preparing', 'waiting', 'counting', 'interviewing', 'finished'
]


async def send_payload(websocket: ServerConnection, payload: Any):
    """
    将给定的payload对象序列化为JSON字符串并发送给指定的WebSocket连接，
    同时在日志中记录发送的消息内容和目标连接ID。

    Args:
        websocket (ServerConnection): 目标WebSocket连接。
        payload (Any): 要发送的数据（将被JSON序列化）。
    """
    payloads_string = json.dumps(payload)
    logger.debug(f"发送消息到{websocket.id}")
    logger.debug(f"消息内容: {payload}")
    await websocket.send(payloads_string)


class InterviewSystem:
    """
    面试系统类，管理面试者的准备、排队、面试和完成状态，
    以及当前题目状态和面试官连接。
    """
    # 题目列表，展示在界面上方 '1 > 2 > 3 > ...' 位置
    questions = [
        ("1",
         """请简要分析人工智能对未来社会的影响。

关键词：
技术变革与社会结构
分析AI如何改变就业、教育、医疗等方面。关注社会公平、技能替代、数字鸿沟等问题。
伦理与法律挑战
是否考虑AI的伦理边界、隐私保护和监管制度？观点应体现深度和现实关照。
未来展望与个人态度
是否表达了对AI发展的个人思考与态度？是否能结合实际做出理性判断？"""),

        ("2",
         """谈谈你对‘内卷’现象的看法。

关键词：
社会竞争与效率悖论
能否分析"内卷"背后的资源分配、职场文化或教育压力？是否能提供多维视角？
个体与集体反应
是否反思个体在内卷中的应对方式，提出建设性建议或替代思维？
批判与自省能力
是否有批判性思维？是否从个人经验出发，展示对现象的深刻认知？"""),

        ("3",
         """环保和经济发展能否兼顾？

关键词：
系统思维与平衡观念
能否看出应聘者是否意识到可持续发展和经济利益之间的张力？是否能提出协调路径？
案例引用与逻辑严密
是否能引用实际案例或政策？论证是否有逻辑性，能否指出短期与长期影响？
价值观与行动建议
是否展现出生态责任感？是否有可行的建议或倡导？"""),

        ("4",
         """如何在压力中保持心理健康？

关键词：
情绪识别与调节能力
是否能描述具体压力来源与影响？是否能展示情绪管理技巧（如冥想、计划管理等）？
资源利用与求助意识
是否提到借助他人帮助或外部资源？展现出非孤立、协作式处理方式更佳。
反思与成长导向
是否从中有反思与改进？是否能从压力中提炼出学习与成长的契机？"""),

        ("5",
         """你如何看待远程办公？

关键词：
自我驱动与时间管理
是否能结合自身经验说明远程办公对效率、自律的影响？是否展现出管理能力？
沟通与协作适应性
是否有应对远程沟通挑战的策略？是否关注团队协作与归属感维系？
综合视角与批判思考
能否权衡优劣？是否提到行业差异、职位属性等影响远程办公效果的变量？"""),

        #         ("6",
        #          """社交媒体对青少年有什么影响？

        # 关键词：
        # 影响维度多样性
        # 是否从心理健康、信息获取、社交能力等角度多维分析？
        # 正反对比与客观态度
        # 是否能权衡利弊，避免非黑即白？是否具备批判性视角？
        # 建设性建议
        # 是否能提出如何引导青少年合理使用社交媒体的方法或制度建议？"""),

        #         ("7",
        #          """你对传统文化在现代社会的价值有何看法？

        # 关键词：
        # 文化认同与现代适应
        # 是否能结合传统元素在当代的表现（如国潮、节日等）进行分析？
        # 创新与传承的张力
        # 是否意识到传统文化如何在技术、市场或审美上实现当代表达？
        # 个体连接与文化参与
        # 是否表达出与传统文化的个人联系或传承意愿？是否体现情感认同？"""),

        #         ("8",
        #          """如果你设计一门新课程，会是什么？

        # 关键词：
        # 洞察需求与定位清晰
        # 是否考虑学生需求或教育痛点？课程目的与内容是否紧密相关？
        # 内容设计与方法创新
        # 是否有创新的教学方法？是否包含跨学科元素或项目式学习？
        # 可行性与价值体现
        # 是否对实施方式、评估机制有考虑？是否展现教育理念和实际价值？"""),

        #         ("9",
        #          """终身学习对职场人意味着什么？

        # 关键词：
        # 学习动力与适应力
        # 是否理解终身学习对应快速变化的工作环境？是否提到主动学习的重要性？
        # 方法与实践结合
        # 是否分享个人学习方式（如阅读、课程、实战）？是否注重应用与反馈？
        # 职业发展视角
        # 是否联系到职业转型、技能更新等实际场景？体现目标感与战略眼光。"""),

        #         ("10",
        #          """请从你的生活经历谈谈一个改变你想法的事件。

        # 关键词：
        # 自我认知与反转时刻
        # 是否能讲述清晰的事件起因、转折与结果？重点在“想法转变”的动因分析。
        # 学习与成长轨迹
        # 是否体现从事件中获得的深刻领悟？是否有持续影响？
        # 真实性与感染力
        # 描述是否真实具体？能否引起共鸣？是否具有情感表达与反思深度？"""),
    ]

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
        self.ratings = []
        self.comments = []

    def init_interview(self) -> None:
        """
        初始化或重置面试状态，设置为计数状态并重置题目索引。
        """
        self.interviewing_state = 'counting'
        self.current_question = 0
        self.ratings = [None for _ in range(len(self.questions))]
        self.comments = ['' for _ in range(len(self.questions))]
        logger.info("面试状态已初始化")

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

    async def next_candidate(self) -> None:
        """
        切换到下一个面试者：
        - 将当前面试者加入已完成集合（如果存在）
        - 从排队列表取出下一个面试者作为当前面试者
        - 初始化面试状态
        """
        if self.interviewing_candidate is not None:
            self.finished_candidates.add(self.interviewing_candidate)
            await send_payload(self.interviewing_candidate, {'type': 'finish'})
            logger.info(f"面试者 {self.interviewing_candidate.id} 已完成面试")
        self.interviewing_candidate = None
        if len(self.queueing_candidates) != 0:
            self.interviewing_candidate = self.queueing_candidates.pop(0)
            self.init_interview()
            logger.info(f"切换到新面试者 {self.interviewing_candidate.id}")

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
                'questionTitles': [t for (t, _) in self.questions],
            })
        elif self.state == 'interviewing':
            i = self.current_question
            await send_payload(self.interviewer, {
                'type': 'interviewing',
                'currentQuestion': i,
                'content': self.questions[i][-1],
                'questionTitles': [t for (t, _) in self.questions],
                'rating': self.ratings[i],
                'comment': self.comments[i]
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
            'questionTitles': [t for (t, _) in self.questions],
            'queueQuestionCount': len(self.questions)-self.current_question,
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
                logger.error(f"发送任务出错：{r}")

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
            logger.info(f"新增面试者 {websocket.id} 进入准备状态")
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
            logger.info(f"准备中的面试者 {websocket.id} 已断开连接")
        elif websocket in self.queueing_candidates:
            self.queueing_candidates.remove(websocket)
            logger.info(f"排队中的面试者 {websocket.id} 已断开连接")
            await self.flush_queue()
        elif websocket is self.interviewing_candidate:
            logger.info(f"当前面试者 {websocket.id} 已断开连接")
            await self.next_candidate()
            await self.flush_current()
            await self.flush_queue()
            await self.flush_interviewer()
        elif websocket in self.finished_candidates:
            self.finished_candidates.remove(websocket)
            logger.info(f"已完成面试者 {websocket.id} 已断开连接")

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
                    logger.info(f'面试者 {websocket.id} 已经准备好')
                    self.preparing_candidates.remove(websocket)
                    if self.state == 'idle':
                        # 当前无面试者，直接开始面试
                        self.interviewing_candidate = websocket
                        self.init_interview()
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
                    logger.info(f'面试者 {websocket.id} 开始正式面试')
                    await self.flush_current()
                    await self.flush_interviewer()
            case _:
                return False
        return True

    async def parse_interviewer_message(
        self, websocket: ServerConnection, data: dict[Any, Any]
    ) -> bool:
        if websocket is not self.interviewer:
            return False

        message_type = data.get('type', None)
        rating = data.get('rating', None)
        comment = data.get('comment', None)

        i = self.current_question
        self.ratings[i] = rating
        self.comments[i] = comment

        match message_type:
            case 'next':
                if self.current_question + 1 >= len(self.questions):
                    return False
                self.current_question += 1
                logger.info(f"面试官切换到下一题，当前题目索引: {self.current_question}")
            case 'last':
                if self.current_question-1 < 0:
                    return False
                self.current_question -= 1
                logger.info(f"面试官切换到上一题，当前题目索引: {self.current_question}")
            case 'finish':
                logger.info("面试官结束当前面试")
                await self.next_candidate()
            case _:
                return False

        await self.flush_current()
        await self.flush_interviewer()
        await self.flush_queue()

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
    logger.info(f"面试者端 {id} 连接")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if not isinstance(data, dict):
                    logger.warning(f"从面试者 {id} 收到非字典消息: {message!r}")
                    continue
                result = await system.parse_interviewee_message(websocket, data)
                if not result:
                    logger.warning(f"从面试者 {id} 收到异常 JSON 消息: {message!r}")
            except json.JSONDecodeError:
                logger.warning(f"从面试者 {id} 收到非 JSON 消息: {message!r}")
    except Exception as e:
        logger.error(f"面试者 {id} 连接处理出错: {e}")
    finally:
        await system.pop_interviewee(websocket)
        logger.info(f"面试者端 {id} 断开")


async def interviewer_handler(websocket: ServerConnection) -> None:
    """
    处理面试官WebSocket连接，允许或拒绝连接，并等待断开。

    Args:
        websocket (ServerConnection): 面试官连接对象。
    """
    global system

    id = websocket.id
    logger.info(f"面试官端 {id} 连接")

    if system.interviewer is not None:
        try:
            await send_payload(system.interviewer, {'type': 'reject'})
            logger.warning(f"已有面试官连接，拒绝旧连接 {system.interviewer.id}")
        except Exception as e:
            logger.error(f"拒绝旧面试官连接时出错: {e}")

    system.interviewer = websocket
    await system.flush_interviewer()

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if not isinstance(data, dict):
                    logger.warning(f"从面试官 {id} 收到非字典消息: {message!r}")
                    continue
                result = await system.parse_interviewer_message(websocket, data)
                if not result:
                    logger.warning(f"从面试官 {id} 收到异常 JSON 消息: {message!r}")
            except json.JSONDecodeError:
                logger.warning(f"从面试官 {id} 收到非 JSON 消息: {message!r}")
    except Exception as e:
        logger.error(f"面试官 {id} 连接处理出错: {e}")
    finally:
        system.interviewer = None
        logger.info(f"面试官端 {id} 断开")


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
        logger.info("WebSocket 服务器已启动...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
