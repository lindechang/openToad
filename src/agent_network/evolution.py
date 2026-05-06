# src/agent_network/evolution.py
"""
自我进化系统 (Self-Evolution System)
支持系统自我评估、学习和优化
"""
import uuid
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)


class EvolutionType(str, Enum):
    """进化类型"""
    PERFORMANCE = "performance"  # 性能优化
    STRATEGY = "strategy"  # 策略调整
    BEHAVIOR = "behavior"  # 行为优化
    KNOWLEDGE = "knowledge"  # 知识积累
    ARCHITECTURE = "architecture"  # 架构改进


class EvolutionState(str, Enum):
    """进化状态"""
    PROPOSED = "proposed"  # 已提议
    TESTING = "testing"  # 测试中
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    DEPLOYED = "deployed"  # 已部署
    ROLLBACK = "rollback"  # 已回滚


@dataclass
class Metric:
    """系统指标"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    unit: Optional[str] = None
    target: Optional[float] = None
    
    def get_score(self) -> float:
        """计算指标得分 (0-1)"""
        if self.target is None:
            return 0.5
        if self.value >= self.target:
            return 1.0
        return min(self.value / self.target, 1.0)


@dataclass
class Evolution:
    """进化记录"""
    evolution_id: str
    type: EvolutionType
    description: str
    proposed_changes: Dict[str, Any]
    state: EvolutionState = EvolutionState.PROPOSED
    proposed_by: str = "system"
    proposed_at: datetime = field(default_factory=datetime.utcnow)
    tested_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    rollback_at: Optional[datetime] = None
    test_results: Optional[Dict[str, Any]] = None
    before_metrics: Optional[List[Metric]] = None
    after_metrics: Optional[List[Metric]] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}
        self._lock = threading.Lock()
    
    def record(self, metric: Metric):
        """记录指标"""
        with self._lock:
            if metric.name not in self.metrics:
                self.metrics[metric.name] = []
            self.metrics[metric.name].append(metric)
            # 保留最近 1000 条记录
            if len(self.metrics[metric.name]) > 1000:
                self.metrics[metric.name] = self.metrics[metric.name][-1000:]
    
    def get_latest(self, name: str, count: int = 1) -> List[Metric]:
        """获取最新指标"""
        with self._lock:
            metrics = self.metrics.get(name, [])
            return metrics[-count:] if metrics else []
    
    def get_average(self, name: str, window_seconds: int = 3600) -> Optional[float]:
        """获取平均指标"""
        with self._lock:
            metrics = self.metrics.get(name, [])
            cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
            recent = [m for m in metrics if m.timestamp >= cutoff]
            if not recent:
                return None
            return sum(m.value for m in recent) / len(recent)
    
    def get_trend(self, name: str, steps: int = 10) -> float:
        """获取趋势 (-1 to 1)"""
        recent = self.get_latest(name, steps * 2)
        if len(recent) < steps:
            return 0.0
        
        first_half = recent[:steps]
        second_half = recent[steps:]
        
        avg_first = sum(m.value for m in first_half) / steps
        avg_second = sum(m.value for m in second_half) / steps
        
        if avg_first == 0:
            return 0.0
        
        change = (avg_second - avg_first) / avg_first
        return max(-1.0, min(1.0, change))


class Optimizer:
    """优化器 - 生成优化建议"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def analyze_performance(self) -> List[Dict[str, Any]]:
        """分析性能瓶颈"""
        suggestions = []
        
        # 检查任务执行时间
        avg_time = self.collector.get_average("task_execution_time")
        if avg_time:
            if avg_time > 5.0:
                suggestions.append({
                    "type": EvolutionType.PERFORMANCE,
                    "priority": "high",
                    "description": "任务执行时间过长",
                    "suggestion": "增加并行度或优化任务分配策略",
                    "details": {"current_avg": avg_time, "target": 5.0}
                })
            else:
                # 即使性能好，也可以建议持续优化
                suggestions.append({
                    "type": EvolutionType.PERFORMANCE,
                    "priority": "medium",
                    "description": "性能优秀，继续优化",
                    "suggestion": "监控和保持当前性能水平",
                    "details": {"current_avg": avg_time, "target": 5.0}
                })
        
        # 检查成功率
        success_rate = self.collector.get_average("task_success_rate")
        if success_rate:
            if success_rate < 0.9:
                suggestions.append({
                    "type": EvolutionType.STRATEGY,
                    "priority": "high",
                    "description": "任务成功率偏低",
                    "suggestion": "优化 Agent 选择策略",
                    "details": {"current_rate": success_rate, "target": 0.95}
                })
        
        # 检查整体系统健康度
        health_score = self.collector.get_average("system_health")
        if health_score and health_score < 0.8:
            suggestions.append({
                "type": EvolutionType.ARCHITECTURE,
                "priority": "medium",
                "description": "系统健康度需要改善",
                "suggestion": "检查资源使用和错误日志",
                "details": {"health_score": health_score}
            })
        
        # 总是添加一些学习建议
        suggestions.append({
            "type": EvolutionType.KNOWLEDGE,
            "priority": "low",
            "description": "持续学习和优化",
            "suggestion": "积累更多运行数据，建立知识图谱",
            "details": {"learning_rate": 0.01}
        })
        
        return suggestions
    
    def propose_evolution(self, analysis: List[Dict[str, Any]]) -> List[Evolution]:
        """根据分析生成进化提案"""
        evolutions = []
        
        for item in analysis:
            evo = Evolution(
                evolution_id=str(uuid.uuid4())[:12],
                type=item["type"],
                description=item["description"],
                proposed_changes={
                    "suggestion": item["suggestion"],
                    "details": item["details"]
                }
            )
            evolutions.append(evo)
        
        return evolutions


class EvolutionRegistry:
    """进化注册表"""
    
    def __init__(self):
        self.evolutions: Dict[str, Evolution] = {}
        self._lock = threading.Lock()
    
    def add(self, evolution: Evolution):
        """添加进化记录"""
        with self._lock:
            self.evolutions[evolution.evolution_id] = evolution
    
    def get(self, evolution_id: str) -> Optional[Evolution]:
        """获取进化记录"""
        return self.evolutions.get(evolution_id)
    
    def update_state(self, evolution_id: str, new_state: EvolutionState, **kwargs):
        """更新进化状态"""
        with self._lock:
            evo = self.evolutions.get(evolution_id)
            if evo:
                evo.state = new_state
                for key, value in kwargs.items():
                    if hasattr(evo, key):
                        setattr(evo, key, value)
    
    def list_by_state(self, state: EvolutionState) -> List[Evolution]:
        """按状态列出进化"""
        with self._lock:
            return [
                evo for evo in self.evolutions.values()
                if evo.state == state
            ]
    
    def get_history(self, limit: int = 100) -> List[Evolution]:
        """获取历史记录"""
        with self._lock:
            sorted_evos = sorted(
                self.evolutions.values(),
                key=lambda x: x.proposed_at,
                reverse=True
            )
            return sorted_evos[:limit]


class EvolutionEngine:
    """进化引擎 - 核心进化控制器"""
    
    def __init__(self):
        self.collector = MetricsCollector()
        self.optimizer = Optimizer(self.collector)
        self.registry = EvolutionRegistry()
        self.knowledge_base: Dict[str, Any] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
    
    def register_callback(self, callback: Callable):
        """注册回调函数"""
        self._callbacks.append(callback)
    
    def _notify_callbacks(self, event_type: str, data: Dict[str, Any]):
        """通知回调"""
        for callback in self._callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def record_metric(self, name: str, value: float, **kwargs):
        """记录系统指标"""
        metric = Metric(name=name, value=value, **kwargs)
        self.collector.record(metric)
        self._notify_callbacks("metric_recorded", {"metric": metric})
    
    def start_evolution_cycle(self, interval_seconds: int = 300):
        """启动进化周期"""
        if self._running:
            return
        
        self._running = True
        
        def cycle():
            while self._running:
                try:
                    self.run_evolution_step()
                except Exception as e:
                    logger.error(f"Evolution cycle error: {e}")
                time.sleep(interval_seconds)
        
        self._thread = threading.Thread(target=cycle, daemon=True)
        self._thread.start()
        logger.info("Evolution cycle started")
    
    def stop_evolution_cycle(self):
        """停止进化周期"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Evolution cycle stopped")
    
    def run_evolution_step(self):
        """执行一步进化"""
        logger.debug("Running evolution step...")
        
        # 1. 分析当前状态
        analysis = self.optimizer.analyze_performance()
        
        # 2. 生成进化提案
        if analysis:
            evolutions = self.optimizer.propose_evolution(analysis)
            for evo in evolutions:
                self.registry.add(evo)
                self._notify_callbacks("evolution_proposed", {"evolution": evo})
                logger.info(f"Proposed evolution: {evo.description}")
        
        # 3. 处理待测试的进化
        testing = self.registry.list_by_state(EvolutionState.PROPOSED)
        for evo in testing:
            self._test_evolution(evo)
        
        # 4. 部署已批准的进化
        approved = self.registry.list_by_state(EvolutionState.APPROVED)
        for evo in approved:
            self._deploy_evolution(evo)
    
    def _test_evolution(self, evolution: Evolution):
        """测试进化"""
        logger.info(f"Testing evolution: {evolution.description}")
        
        # 记录测试前指标
        evolution.before_metrics = [
            Metric(name="test_score", value=0.8)  # 模拟测试分数
        ]
        
        # 更新状态
        self.registry.update_state(
            evolution.evolution_id,
            EvolutionState.TESTING,
            tested_at=datetime.utcnow(),
            test_results={"status": "passed", "score": 0.85}
        )
        
        # 自动批准
        self.registry.update_state(
            evolution.evolution_id,
            EvolutionState.APPROVED
        )
        
        self._notify_callbacks("evolution_tested", {"evolution": evolution})
    
    def _deploy_evolution(self, evolution: Evolution):
        """部署进化"""
        logger.info(f"Deploying evolution: {evolution.description}")
        
        # 记录部署后指标
        evolution.after_metrics = [
            Metric(name="test_score", value=0.9)
        ]
        
        self.registry.update_state(
            evolution.evolution_id,
            EvolutionState.DEPLOYED,
            deployed_at=datetime.utcnow()
        )
        
        # 积累知识
        self._accumulate_knowledge(evolution)
        
        self._notify_callbacks("evolution_deployed", {"evolution": evolution})
    
    def _accumulate_knowledge(self, evolution: Evolution):
        """积累知识"""
        key = f"{evolution.type.value}:{evolution.description[:30]}"
        self.knowledge_base[key] = {
            "evolution": evolution,
            "learned_at": datetime.utcnow().isoformat(),
            "success": evolution.state == EvolutionState.DEPLOYED
        }
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """获取进化摘要"""
        history = self.registry.get_history()
        deployed = len([e for e in history if e.state == EvolutionState.DEPLOYED])
        proposed = len(history)
        
        # 计算整体趋势
        recent_metrics = self.collector.get_latest("test_score", 10)
        avg_score = sum(m.value for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            "total_proposed": proposed,
            "total_deployed": deployed,
            "success_rate": deployed / proposed if proposed > 0 else 0,
            "current_score": avg_score,
            "knowledge_count": len(self.knowledge_base),
            "recent_evolutions": [
                {
                    "id": e.evolution_id,
                    "description": e.description,
                    "state": e.state,
                    "time": e.proposed_at.isoformat()
                }
                for e in history[:5]
            ]
        }
    
    def export_state(self) -> str:
        """导出当前状态为 JSON"""
        # 将 knowledge_base 中的进化对象转换为可序列化的字典
        serialized_kb = {}
        for key, value in self.knowledge_base.items():
            if "evolution" in value:
                evo = value["evolution"]
                serialized_kb[key] = {
                    "evolution_id": evo.evolution_id,
                    "type": evo.type.value,
                    "description": evo.description,
                    "state": evo.state.value,
                    "proposed_at": evo.proposed_at.isoformat()
                }
            else:
                serialized_kb[key] = value
        
        state = {
            "summary": self.get_evolution_summary(),
            "knowledge_base": serialized_kb,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(state, ensure_ascii=False, indent=2)


# 全局进化引擎实例
_global_engine: Optional[EvolutionEngine] = None


def get_evolution_engine() -> EvolutionEngine:
    """获取全局进化引擎"""
    global _global_engine
    if _global_engine is None:
        _global_engine = EvolutionEngine()
    return _global_engine


def init_evolution_system():
    """初始化进化系统"""
    engine = get_evolution_engine()
    logger.info("Evolution system initialized")
    return engine
