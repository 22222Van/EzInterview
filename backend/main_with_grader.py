from websockets.asyncio.server import ServerConnection
import websockets
import asyncio
import json
from pprint import pprint
from typing import Optional, Any, Literal, Dict, List, Tuple
from grader import Grader

# 定义系统状态类型
SystemStateType = Literal['idle', 'counting', 'interviewing']
IntervieweeStateType = Literal['preparing', 'waiting', 'counting', 'interviewing', 'finished']

async def send_payload(websocket: ServerConnection, payload: Any):
    """
    将给定的payload对象序列化为JSON字符串并发送给指定的WebSocket连接，
    同时在控制台打印发送的消息内容和目标连接ID。

    Args:
        websocket (ServerConnection): 目标WebSocket连接。
        payload (Any): 要发送的数据（将被JSON序列化）。
    """
    payload_str = json.dumps(payload)
    print(f"发送消息到{websocket.id}")
    pprint(payload)
    print()
    await websocket.send(payload_str)

class InterviewSystem:
    """主面试系统"""
    
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
    能否分析“内卷”背后的资源分配、职场文化或教育压力？是否能提供多维视角？
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
        self._init_state()
        self.grader: Optional[Grader] = Grader(questions=self.questions)  # 初始化评分器
    
    def _init_state(self):
        """初始化系统状态"""
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
    
    async def next_candidate(self) -> None:
        """切换到下一个面试者"""
        if self.interviewing_candidate:
            self.finished_candidates.add(self.interviewing_candidate)
            await send_payload(self.interviewing_candidate, {'type': 'finish'})
        
        self.interviewing_candidate = None
        self.grader = None
        
        if self.queueing_candidates:
            self.interviewing_candidate = self.queueing_candidates.pop(0)
            self._init_interview()
            await self._notify_state_change()

    def _init_interview(self):
        """初始化新的面试会话"""
        self.interviewing_state = 'counting'
        self.current_question = 0
        self.grader = Grader(self.questions)
    
    async def _notify_state_change(self):
        """通知所有客户端状态变化"""
        await self.flush_current()
        await self.flush_interviewer()
        await self.flush_queue()

    @property
    def state(self) -> SystemStateType:
        """获取当前系统状态"""
        if not self.interviewing_candidate:
            return 'idle'
        return self.interviewing_state
    
    async def flush_interviewer(self):
        """更新面试官界面"""
        if not self.interviewer:
            return
        
        if self.state == 'idle':
            await send_payload(self.interviewer, {'type': 'idle'})
        elif self.state == 'counting':
            await send_payload(self.interviewer, {
                'type': 'counting',
                'questionTitles': [t for t, _ in self.questions]
            })
        elif self.state == 'interviewing' and self.grader:
            grading_data = self.grader.grade_response("")  # 初始空数据
            await send_payload(self.interviewer, {
                'type': 'interviewing',
                'currentQuestion': self.current_question,
                'content': self.questions[self.current_question][1],
                'questionTitles': [t for t, _ in self.questions],
                'gradingData': grading_data,
                'hasNext': self.current_question < len(self.questions) - 1,
                'hasPrevious': self.current_question > 0
            })
    
    async def flush_current(self):
        """更新当前面试者界面"""
        if self.interviewing_candidate:
            await send_payload(self.interviewing_candidate, {
                'type': self.interviewing_state,
                'currentQuestion': self.current_question
            })
    
    async def flush_queue(self):
        """更新排队面试者界面"""
        shared_data = {
            'questionTitles': [t for t, _ in self.questions],
            'queueQuestionCount': len(self.questions) - self.current_question,
        }
        
        total_queue = len(self.queueing_candidates)
        if self.state != 'idle':
            total_queue += 1
        
        tasks = []
        for c in self.preparing_candidates:
            tasks.append(send_payload(c, {
                'type': 'preparing',
                'queueCount': total_queue,
                **shared_data
            }))
        
        for i, c in enumerate(self.queueing_candidates):
            tasks.append(send_payload(c, {
                'type': 'waiting',
                'queueCount': i + 1,
                **shared_data
            }))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def add_interviewee(self, websocket: ServerConnection):
        """添加新面试者"""
        if websocket not in self.queueing_candidates and \
           websocket is not self.interviewing_candidate and \
           websocket not in self.finished_candidates:
            self.preparing_candidates.add(websocket)
            await self.flush_queue()
    
    async def pop_interviewee(self, websocket: ServerConnection):
        """移除断开连接的面试者"""
        if websocket in self.preparing_candidates:
            self.preparing_candidates.remove(websocket)
        elif websocket in self.queueing_candidates:
            self.queueing_candidates.remove(websocket)
            await self.flush_queue()
        elif websocket is self.interviewing_candidate:
            await self.next_candidate()
        elif websocket in self.finished_candidates:
            self.finished_candidates.remove(websocket)
    
    async def parse_interviewee_message(self, websocket: ServerConnection, data: Dict) -> bool:
        """处理面试者消息"""
        match data:
            case {'type': 'ready'}:
                return await self._handle_ready(websocket)
            case {'type': 'start'}:
                return await self._handle_start(websocket)
            case {'type': 'answer', 'text': answer} if self.grader:
                # 评估答案并更新评分数据（示例）
                self.grader.grade_response(answer)
                return True
            case _:
                return False
    
    async def _handle_ready(self, ws: ServerConnection) -> bool:
        """处理考生准备就绪消息"""
        if ws in self.preparing_candidates:
            self.preparing_candidates.remove(ws)
            
            if self.state == 'idle':
                self.interviewing_candidate = ws
                self._init_interview()
            else:
                self.queueing_candidates.append(ws)
            
            await self._notify_state_change()
            return True
        return False
    
    async def _handle_start(self, ws: ServerConnection) -> bool:
        """处理考生开始面试消息"""
        if ws is self.interviewing_candidate:
            self.interviewing_state = 'interviewing'
            await self._notify_state_change()
            return True
        return False
    
    async def parse_interviewer_message(self, websocket: ServerConnection, data: Dict) -> bool:
        """处理面试官消息"""
        if websocket is not self.interviewer or not self.grader:
            return False
        
        match data:
            case {'type': 'grade', 'criteria': int(cidx), 'rating': int(r), 'comment': str(cmt)}:
                return await self._handle_grade(cidx, r, cmt)
            case {'type': 'next'}:
                return await self._handle_question_change(1)
            case {'type': 'prev'}:
                return await self._handle_question_change(-1)
            case {'type': 'finish'}:
                await self.next_candidate()
                return True
            case _:
                return False
    
    async def _handle_grade(self, cidx: int, rating: int, comment: str) -> bool:
        """处理评分操作"""
        if 0 <= cidx < len(self.grader.scoring_criteria[self.current_question]):
            self.grader.record_rating(cidx, rating, comment)
            await self.flush_interviewer()
            return True
        return False
    
    async def _handle_question_change(self, delta: int) -> bool:
        """处理题目切换"""
        new_idx = self.current_question + delta
        if 0 <= new_idx < len(self.questions):
            self.current_question = new_idx
            await self._notify_state_change()
            return True
        return False

# 系统实例和服务器逻辑
system = InterviewSystem()

async def interviewee_handler(websocket: ServerConnection):
    global system
    await system.add_interviewee(websocket)
    print(f"面试者连接: {websocket.id}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                result = await system.parse_interviewee_message(websocket, data)
                if not result:
                    print(f"无效面试者消息: {message}")
            except json.JSONDecodeError:
                print(f"非JSON消息: {message}")
    finally:
        await system.pop_interviewee(websocket)
        print(f"面试者断开: {websocket.id}")

async def interviewer_handler(websocket: ServerConnection):
    global system
    print(f"面试官连接: {websocket.id}")
    
    # 确保只有一个面试官
    if system.interviewer:
        try:
            await send_payload(system.interviewer, {'type': 'reject'})
        except:
            pass
    
    system.interviewer = websocket
    await system.flush_interviewer()
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                result = await system.parse_interviewer_message(websocket, data)
                if not result:
                    print(f"无效面试官消息: {message}")
            except json.JSONDecodeError:
                print(f"非JSON消息: {message}")
    finally:
        system.interviewer = None
        print(f"面试官断开: {websocket.id}")

async def main():
    interviewee_server = websockets.serve(interviewee_handler, "0.0.0.0", 9009)
    interviewer_server = websockets.serve(interviewer_handler, "0.0.0.0", 9008)
    
    async with interviewee_server, interviewer_server:
        print("面试系统服务器已启动...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())