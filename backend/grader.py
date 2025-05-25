from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import json
from pprint import pprint

@dataclass
class ScoringCriterion:
    """评分标准数据结构"""
    name: str
    description: str
    weight: float = 1.0

class Grader:
    """
    智能面试评分系统
    功能：
    1. 动态评分维度管理
    2. 压力感知评估
    3. 自适应问题推荐
    4. 反作弊检测
    """
    
    def __init__(self, questions: List[Tuple[str, str]]):
        self.questions = questions
        self.current_question_idx = 0
        self._init_scoring_system()
        self.pressure_evaluator = PressureEvaluator()
        self.anti_cheat = AntiCheatDetector()
        
    def _init_scoring_system(self):
        """初始化评分系统"""
        self.scoring_criteria = []
        self.ratings = []
        self.comments = []
        
        for q_idx, (_, content) in enumerate(self.questions):
            # 从题目内容提取评分标准
            criteria = self._extract_criteria(content)
            self.scoring_criteria.append(criteria)
            self.ratings.append([None] * len(criteria))
            self.comments.append([""] * len(criteria))
    
    def _extract_criteria(self, content: str) -> List[ScoringCriterion]:
        """从题目内容解析评分标准"""
        criteria = []
        lines = content.split('\n')
        in_criteria = False
        
        for line in lines:
            line = line.strip()
            if "关键词：" in line:
                in_criteria = True
                continue
            if in_criteria and line and "：" in line:
                name, desc = line.split("：", 1)
                criteria.append(ScoringCriterion(name.strip(), desc.strip()))
        
        return criteria or [ScoringCriterion("综合表现", "整体回答质量评估")]

    def grade_response(self, answer: str) -> Dict[str, Any]:
        """
        评估面试者回答并生成评分建议
        返回: {
            "criteria": 评分标准列表,
            "keyword_coverage": 关键词覆盖分析,
            "fluency_score": 语言流畅度评分,
            "pressure_indicator": 压力指标
        }
        """
        current_criteria = self.scoring_criteria[self.current_question_idx]
        
        # 关键词覆盖分析
        keyword_analysis = {}
        for criterion in current_criteria:
            matched = sum(1 for word in set(criterion.description.split()) 
                         if word.lower() in answer.lower())
            keyword_analysis[criterion.name] = matched / len(criterion.description.split())
        
        # 压力评估
        pressure_data = self.pressure_evaluator.evaluate(answer)
        
        # 反作弊检查
        cheat_flags = self.anti_cheat.check(answer)
        
        return {
            "question_index": self.current_question_idx,
            "scoring_criteria": current_criteria,
            "keyword_coverage": keyword_analysis,
            "fluency_score": pressure_data["fluency"],
            "pressure_indicator": pressure_data["level"],
            "warning_flags": cheat_flags,
            "suggested_ratings": self._suggest_ratings(answer, current_criteria)
        }
    
    def _suggest_ratings(self, answer: str, criteria: List[ScoringCriterion]) -> Dict[str, int]:
        """基于回答内容生成评分建议"""
        suggestions = {}
        for criterion in criteria:
            # 简单实现：根据关键词匹配数量建议评分
            matched = sum(1 for word in set(criterion.description.split()) 
                         if word.lower() in answer.lower())
            suggestions[criterion.name] = min(5, 1 + int(matched * 4 / len(criterion.description.split())))
        return suggestions
    
    def record_rating(self, criteria_index: int, rating: int, comment: str):
        """记录面试官的评分"""
        self.ratings[self.current_question_idx][criteria_index] = rating
        self.comments[self.current_question_idx][criteria_index] = comment
    
    def generate_report(self) -> Dict[str, Any]:
        """生成最终评估报告"""
        report = {
            "question_breakdown": [],
            "pressure_analysis": self.pressure_evaluator.summary(),
            "overall_scores": {}
        }
        
        # 计算每个标准的平均分
        for q_idx, criteria in enumerate(self.scoring_criteria):
            question_scores = {}
            for c_idx, criterion in enumerate(criteria):
                question_scores[criterion.name] = {
                    "score": self.ratings[q_idx][c_idx],
                    "comment": self.comments[q_idx][c_idx]
                }
            
            report["question_breakdown"].append({
                "question_id": self.questions[q_idx][0],
                "scores": question_scores
            })
        
        # 计算总分
        total_weighted = 0
        total_weights = 0
        for q_idx, criteria in enumerate(self.scoring_criteria):
            for c_idx, criterion in enumerate(criteria):
                if self.ratings[q_idx][c_idx] is not None:
                    total_weighted += self.ratings[q_idx][c_idx] * criterion.weight
                    total_weights += criterion.weight
        
        report["overall_scores"] = {
            "weighted_average": total_weighted / total_weights if total_weights else 0,
            "pressure_impact": self.pressure_evaluator.pressure_impact_score()
        }
        
        return report

class PressureEvaluator:
    """压力评估子系统"""
    
    def __init__(self):
        self.fluency_data = []
        self.response_times = []
        
    def evaluate(self, answer: str) -> Dict[str, Any]:
        """评估回答中的压力指标"""
        fluency = self._calculate_fluency(answer)
        self.fluency_data.append(fluency)
        
        return {
            "level": self._estimate_pressure_level(fluency),
            "fluency": fluency,
            "warning": fluency < 0.5
        }
    
    def _calculate_fluency(self, answer: str) -> float:
        """计算语言流畅度(简化版)"""
        sentence_count = len([c for c in answer if c in [".", "。", "!", "！", "?", "？"]])
        word_count = len(answer)
        return min(1.0, sentence_count / (word_count / 50)) if word_count > 0 else 1.0
    
    def _estimate_pressure_level(self, fluency: float) -> float:
        """估计压力水平"""
        return max(0, min(1, 1.5 - fluency * 1.5))
    
    def summary(self) -> Dict[str, Any]:
        """生成压力评估摘要"""
        if not self.fluency_data:
            return {}
        avg_fluency = sum(self.fluency_data) / len(self.fluency_data)
        return {
            "average_fluency": avg_fluency,
            "pressure_trend": self._analyze_trend(),
            "suggestion": self._generate_suggestion()
        }
    
    def pressure_impact_score(self) -> float:
        """计算压力对表现的影响分数(0-1)"""
        if not self.fluency_data:
            return 0
        return max(0, min(1, 1 - sum(self.fluency_data) / len(self.fluency_data)))
    
    def _analyze_trend(self) -> str:
        """分析压力变化趋势"""
        if len(self.fluency_data) < 3:
            return "stable"
        last_3 = self.fluency_data[-3:]
        if last_3[-1] > sum(last_3[:2])/2 + 0.1:
            return "improving"
        elif last_3[-1] < sum(last_3[:2])/2 - 0.1:
            return "worsening"
        return "stable"
    
    def _generate_suggestion(self) -> str:
        """生成改善建议"""
        if not self.fluency_data:
            return "无足够数据判断"
        avg = sum(self.fluency_data) / len(self.fluency_data)
        if avg > 0.7:
            return "面试者表现自然，压力适中"
        elif avg > 0.4:
            return "适度压力，建议给予更多思考时间"
        return "高压表现，建议调整问题难度或提供放松机会"

class AntiCheatDetector:
    """反作弊检测系统(基础版)"""
    
    def __init__(self):
        self.previous_answers = []
        
    def check(self, answer: str) -> Dict[str, bool]:
        """检查可能的作弊行为"""
        # 简单实现：检测重复内容和关键词堆砌
        duplicate_warning = any(self._similarity(answer, prev) > 0.7 
                              for prev in self.previous_answers)
        keyword_density = self._check_keyword_density(answer)
        
        self.previous_answers.append(answer)
        
        return {
            "possible_memorization": duplicate_warning,
            "keyword_stuffing": keyword_density > 0.15,
            "unusual_pattern": False  # 留给高级分析
        }
    
    def _similarity(self, a: str, b: str) -> float:
        """计算文本相似度(简化版)"""
        if not a or not b:
            return 0
        set_a = set(a.split())
        set_b = set(b.split())
        return len(set_a & set_b) / max(len(set_a), len(set_b))
    
    def _check_keyword_density(self, text: str) -> float:
        """检查关键词密度"""
        words = text.split()
        if not words:
            return 0
        keywords = {"技术", "分析", "建议", "评估", "比较", "影响"}
        found = sum(1 for word in words if word in keywords)
        return found / len(words)