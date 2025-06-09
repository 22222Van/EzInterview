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
    # 题目列表：每个元素由三元组 (questionMain, questionKeywords, hint) 组成
    #   - questionMain: 给面试官端的题目正文
    #   - questionKeywords: 给面试官端的题目要点
    #   - hint: 给被面试者端的提示文字
    questions = [
        (
            "环保和经济发展能否兼顾？",
            """系统思维与平衡观念
能否看出应聘者是否意识到可持续发展和经济利益之间的张力？是否能提出协调路径？
案例引用与逻辑严密
是否能引用实际案例或政策？论证是否有逻辑性，能否指出短期与长期影响？
价值观与行动建议
是否展现出生态责任感？是否有可行的建议或倡导？""",
            "可以从“可持续发展”与“短期经济利益”两个维度展开，再结合具体案例论证。"
        ),
        (
            "请从你的生活经历谈谈一个改变你想法的事件。",
            """自我认知与反转时刻
是否能讲述清晰的事件起因、转折与结果？重点在“想法转变”的动因分析。
学习与成长轨迹
是否体现从事件中获得的深刻领悟？是否有持续影响？
真实性与感染力
描述是否真实具体？能否引起共鸣？是否具有情感表达与反思深度？""",
            "可先交代事件背景，然后描述转折过程，最后谈得出的领悟和长期影响。"
        ),


        (
            "人工智能会取代人类创造力吗？",
            """创造性本质分析
能否区分算法生成与人类原创的本质差异？是否讨论情感、直觉等非理性要素？
互补协作模式
是否提出人机协同创作案例（如AI辅助设计）？能否说明技术如何扩展创意边界？
伦理与文化影响
是否关注版权归属、文化同质化等风险？是否强调人文精神的核心地位？""",
            "从能力对比切入，再论协同可能性，最后讨论社会文化影响。"
        ),

        (
            "如何平衡代码开发速度与质量？",
            """技术债务认知
能否解释快速迭代导致的技术债务？是否提及具体指标（如代码覆盖率、bug率）？
工程实践应用
是否讨论CI/CD、代码审查、单元测试等质量保障手段？能否说明其时间成本收益？
团队协作策略
是否提出任务拆解、优先级管理等方法？是否强调文档和规范的重要性？""",
            "先分析速度与质量的矛盾点，再介绍工程实践，最后谈团队协作策略。"
        ),
        (
            "微服务架构的利弊及适用场景？",
            """核心优势分析
能否说明独立部署、技术异构等优势？是否结合扩展性和故障隔离具体案例？
挑战与代价
是否讨论分布式事务、运维复杂度等问题？是否提到团队技能和监控成本要求？
架构决策原则
能否提出适用场景判断标准（如业务复杂度、团队规模）？是否对比单体架构？""",
            "按'优势→挑战→决策框架'逻辑展开，需结合具体业务场景说明。"
        ),
        (
            "编程中如何实现有效的错误处理？",
            """防御式编程实践
是否提及输入验证、异常捕获等基础机制？能否区分错误类型（可恢复/致命）？
系统健壮性设计
是否讨论重试策略、熔断机制？是否关注错误日志的可追溯性？
用户体验考量
能否说明如何向用户传递友好错误信息？是否涉及错误监控和报警集成？""",
            "从基础防御措施开始，进阶到系统设计，最后考虑用户交互层面。"
        ),
        (
            "代码可维护性的关键要素有哪些？",
            """基础编码规范
是否强调命名规范、函数单一职责等原则？能否说明文档和注释的最佳实践？
设计模式应用
是否提及模块化、低耦合设计？能否举例说明模式选择（如工厂模式、策略模式）？
技术演进适应
是否讨论应对需求变化的扩展性设计？是否包含重构策略和工具支持？""",
            "按'编码规范→架构设计→演进能力'层次展开，结合具体模式案例。"
        ),
        (
            "如何设计高并发系统？",
            """性能瓶颈识别
能否分析常见瓶颈点（如数据库锁、线程阻塞）？是否提及压测和监控工具？
架构模式选择
是否讨论水平扩展、异步处理、缓存策略？能否说明消息队列和负载均衡的实现？
容错与降级机制
是否涉及限流、熔断设计？是否考虑故障转移和数据一致性保障？""",
            "先定位关键瓶颈，再介绍架构方案，最后讨论容灾机制设计。"
        ),
        (
            "如何设计一个智能电梯调度系统？",
            """核心需求分析
能否识别高峰时段响应速度、节能效率、紧急情况处理等核心指标？是否考虑不同建筑类型需求差异？
调度算法设计
是否提及SCAN/LOOK算法优化？能否说明实时动态调整策略（如基于轿厢负载预测）？
系统容错与扩展
是否讨论故障转移机制（如备用电梯接管）？能否说明如何支持新增电梯的平滑扩展？""",
            "先定义核心指标，再设计调度算法，最后讨论容错机制和扩展性设计。"
        ),
        (
            "请解释KMP字符串匹配算法的原理及优化思想",
            """暴力匹配缺陷分析
是否清晰说明朴素算法O(mn)时间复杂度问题？能否举例展示不必要的回溯？
部分匹配表构建
能否解释next数组的数学定义？是否演示手工计算"ABABC"的next数组过程？
算法加速证明
是否用反证法解释跳过无效比较的原理？能否定量分析O(m+n)时间复杂度的达成？""",
            "按'问题发现→核心创新→实现细节'逻辑：1.对比暴力匹配 2.引入部分匹配表 3.代码实现关键步骤"
        ),
        (
            "基于用户搜索词设计某红书购物推荐算法",
            """特征工程策略
是否融合搜索词语义（NLP）、历史行为（协同过滤）、商品图谱（知识图谱）？能否说明特征加权方式？
冷启动解决方案
是否设计新用户/新商品的推荐策略？能否提及内容相似度匹配或热度衰减机制？
业务场景适配
是否考虑小红书社区属性（种草笔记影响）？能否设计图文内容与商品关联的权重调整？""",
            "分三层实现：1.即时搜索特征提取 2.用户长期兴趣建模 3.业务规则融合"
        ),
        (
            "分布式系统如何保证数据一致性？",
            """CAP理论应用
能否结合场景选择一致性级别？是否说明最终一致性与强一致性的代价差异？
共识算法实践
是否对比Raft/Paxos适用场景？能否解释日志复制和Leader选举的核心流程？
故障处理机制
是否设计数据回滚策略？是否考虑网络分区时的脑裂问题解决方案？""",
            "从理论原则（CAP）到算法实现（Raft），最后讨论异常处理机制"
        ),
        (
            "解释TCP三次握手与四次挥手的必要性",
            """连接建立分析
能否用状态机说明SYN/ACK交互？是否解释为什么两次握手不够（历史连接问题）？
连接终止逻辑
是否说明TIME_WAIT状态的意义？能否定量分析MSL等待时间的设计依据？
协议攻击防范
是否提及SYN Flood攻击原理？能否给出半连接队列保护的实现方案？""",
            "按通信时序逐步解析，重点说明每次交互解决的特定问题"
        )
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
        self.current_questions_list: list[int] = []  # 当前面试者所在的题目索引，从0开始
        self.ratings: dict[int, Optional[int]] = {}
        self.comments: dict[int, str] = {}
        self.hints: dict[int, bool] = {}

    def get_startup_question_list(self) -> list[int]:
        return [i for i in range(len(self.questions)) if i % 2 == 0]

    def init_interview(self) -> None:
        """
        初始化或重置面试状态，设置为计数状态并重置题目索引。
        """
        self.interviewing_state = 'counting'
        self.current_question = 0
        self.current_questions_list = self.get_startup_question_list()
        self.ratings = {i: None for i in range(len(self.questions))}
        self.comments = {i: '' for i in range(len(self.questions))}
        self.hints = {i: False for i in range(len(self.questions))}
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
            try:
                await send_payload(self.interviewing_candidate, {'type': 'finish'})
            except Exception as e:
                logger.error(f"发送完成面试信息出错: {e}")
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
                'questionTitles': [str(i+1) for i in range(len(self.current_questions_list))],
                'availableQuestions': self.current_questions_list,
                'questionMains': [q[0] for q in self.questions]
            })
        elif self.state == 'interviewing':
            ptr = self.current_question
            i = self.current_questions_list[ptr]
            questionMain, questionKeywords, questionHint = self.questions[i]
            await send_payload(self.interviewer, {
                'type': 'interviewing',
                'currentQuestion': ptr,
                'questionMain': questionMain,
                'questionKeywords': questionKeywords,
                'questionHint': questionHint,
                'questionTitles': [str(i+1) for i in range(len(self.current_questions_list))],
                'rating': self.ratings[i],
                'comment': self.comments[i],
                'hint': self.hints[i],
                'availableQuestions': self.current_questions_list,
                'questionMains': [q[0] for q in self.questions],
                'realCurrentQuestion': i,
            })

    async def flush_current(self):
        """
        向当前正在面试的面试者发送当前状态和题目索引。
        """
        if self.interviewing_candidate is not None:
            ptr = self.current_question
            i = self.current_questions_list[ptr]
            _, _, questionHint = self.questions[i]
            await send_payload(self.interviewing_candidate, {
                'type': self.interviewing_state,
                'currentQuestion': self.current_question,
                'questionHint': questionHint if self.hints[i] else '',
                'questionTitles': [str(i+1) for i in range(len(self.current_questions_list))],
            })

    async def flush_queue(self):
        """
        向所有准备中和排队中的面试者广播当前题目标题及其排队信息，
        包括题目总数减去当前题目的剩余数量。

        准备中的面试者收到 'preparing' 状态和队列总数。
        排队中的面试者收到 'waiting' 状态和其在队列中的位置。
        """
        shared_data = {
            'questionTitles': [str(i+1) for i in range(len(self.get_startup_question_list()))],
            'queueQuestionCount': len(self.current_questions_list)-self.current_question,
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

    def change_selection(self, selection: list[int]):
        # 1. 不能为空
        if len(selection) == 0:
            return False

        # 2. 保存“当前正在显示的那道题”的绝对索引
        old_abs = self.current_questions_list[self.current_question]

        # 3. 检查传入列表里的每个元素：必须是 int 且在合法范围内
        for s in selection:
            if not isinstance(s, int):  # type:ignore
                return False
            if s < 0 or s >= len(self.questions):
                return False

        # 4. 去重并升序排序
        new_list = sorted(set(selection))

        # 5. 如果去重之后没有任何题，则无效
        if len(new_list) == 0:
            return False

        # 6. 检查 old_abs 是否在 new_list 中，如果不在就无法保持当前题，返回 False
        if old_abs not in new_list:
            return False

        # 7. 更新题目列表，并把指针设置到 new_list 中 old_abs 的位置
        self.current_questions_list = new_list
        self.current_question = new_list.index(old_abs)

        return True

    async def parse_interviewer_message(
        self, websocket: ServerConnection, data: dict[Any, Any]
    ) -> bool:
        if websocket is not self.interviewer:
            return False

        message_type = data.get('type', None)
        rating = data.get('rating', None)
        comment = data.get('comment', '')
        selection = data.get('selection', [])

        ret = True

        match message_type:
            case 'next':
                # 只在 next 分支修改 rating 和 comment
                ptr = self.current_question
                i = self.current_questions_list[ptr]
                self.ratings[i] = rating
                self.comments[i] = comment

                if self.current_question + 1 >= len(self.current_questions_list):
                    return False
                self.current_question += 1
                logger.info(
                    f"面试官切换到下一题，当前题目索引: {self.current_questions_list[self.current_question]}"
                )

            case 'last':
                # 只在 last 分支修改 rating 和 comment
                ptr = self.current_question
                i = self.current_questions_list[ptr]
                self.ratings[i] = rating
                self.comments[i] = comment

                if self.current_question - 1 < 0:
                    return False
                self.current_question -= 1
                logger.info(
                    f"面试官切换到上一题，当前题目索引: {self.current_questions_list[self.current_question]}"
                )

            case 'finish':
                # 只在 finish 分支修改 rating 和 comment
                ptr = self.current_question
                i = self.current_questions_list[ptr]
                self.ratings[i] = rating
                self.comments[i] = comment

                logger.info("面试官结束当前面试")
                await self.next_candidate()

            case 'select':
                # 只在 select 分支修改 selection
                if self.state == 'idle':
                    return False
                ret = self.change_selection(selection)

            case 'hint':
                ptr = self.current_question
                i = self.current_questions_list[ptr]
                self.hints[i] = True

            case _:
                return False

        await self.flush_current()
        await self.flush_interviewer()
        await self.flush_queue()

        return ret


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
