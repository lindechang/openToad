# src/identity/__init__.py
"""
身份与凭证系统
支持 Agent 身份管理、信誉评分和能力认证
"""
import uuid
import hashlib
from typing import List, Optional, Any, Dict
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class AgentIdentity:
    """Agent 身份"""
    agent_id: str
    name: str
    public_key: Optional[str] = None
    digital_signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_verified: bool = False
    identity_hash: Optional[str] = None

    def generate_identity_hash(self) -> str:
        """生成身份哈希"""
        data = f"{self.agent_id}{self.name}{self.public_key or ''}"
        self.identity_hash = hashlib.sha256(data.encode()).hexdigest()
        return self.identity_hash

    def verify_identity(self) -> bool:
        """验证身份"""
        if not self.identity_hash:
            self.generate_identity_hash()
        return self.is_verified


@dataclass
class ReputationScore:
    """信誉评分"""
    agent_id: str
    score: float = 0.0
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time: float = 0.0
    total_ratings: int = 0
    ratings_sum: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def calculate_success_rate(self) -> float:
        """计算成功率"""
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100

    def calculate_rating(self) -> float:
        """计算平均评分"""
        if self.total_ratings == 0:
            return 0.0
        return self.ratings_sum / self.total_ratings

    def update_task_result(self, success: bool, response_time: Optional[float] = None):
        """更新任务结果"""
        self.total_tasks += 1
        if success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1

        if response_time is not None:
            if self.avg_response_time == 0.0:
                self.avg_response_time = response_time
            else:
                self.avg_response_time = (self.avg_response_time + response_time) / 2

        self.last_updated = datetime.utcnow()
        self._add_history("task_result", {
            "success": success,
            "response_time": response_time
        })

    def add_rating(self, rating: float):
        """添加评分（1-5分）"""
        if not 1.0 <= rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")

        self.total_ratings += 1
        self.ratings_sum += rating
        self.last_updated = datetime.utcnow()
        self._add_history("rating", {"rating": rating})

    def calculate_overall_score(self) -> float:
        """计算综合评分"""
        success_rate = self.calculate_success_rate()
        avg_rating = self.calculate_rating()
        reliability_bonus = 10.0 if self.successful_tasks >= 10 else 0.0

        score = (success_rate * 0.5) + (avg_rating * 10) + reliability_bonus
        self.score = min(score, 100.0)
        return self.score

    def _add_history(self, event_type: str, details: Dict[str, Any]):
        """添加历史记录"""
        self.history.append({
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow()
        })
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def get_trust_level(self) -> str:
        """获取信任等级"""
        score = self.calculate_overall_score()
        if score >= 90:
            return "Highly Trusted"
        elif score >= 75:
            return "Trusted"
        elif score >= 50:
            return "Neutral"
        elif score >= 25:
            return "Low Trust"
        else:
            return "Untrusted"


@dataclass
class Credential:
    """凭证/证书"""
    credential_id: str
    agent_id: str
    credential_type: str
    issuer_id: str
    issuer_name: str
    title: str
    description: str
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_hash: Optional[str] = None

    def is_valid(self) -> bool:
        """检查凭证是否有效"""
        if self.is_revoked:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def revoke(self, reason: str):
        """撤销凭证"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        self.revocation_reason = reason

    def generate_verification_hash(self) -> str:
        """生成验证哈希"""
        data = f"{self.credential_id}{self.agent_id}{self.credential_type}{self.issued_at.isoformat()}"
        self.verification_hash = hashlib.sha256(data.encode()).hexdigest()
        return self.verification_hash

    def verify(self) -> bool:
        """验证凭证"""
        if not self.verification_hash:
            self.generate_verification_hash()
        return self.is_valid()


class IdentityManager:
    """身份管理器"""

    def __init__(self):
        self.identities: Dict[str, AgentIdentity] = {}
        self.reputations: Dict[str, ReputationScore] = {}
        self.credentials: Dict[str, Credential] = {}
        self.agent_credentials: Dict[str, List[str]] = {}

    def create_identity(self, agent_id: str, name: str, public_key: Optional[str] = None) -> AgentIdentity:
        """创建 Agent 身份"""
        identity = AgentIdentity(
            agent_id=agent_id,
            name=name,
            public_key=public_key
        )
        identity.generate_identity_hash()
        self.identities[agent_id] = identity

        reputation = ReputationScore(agent_id=agent_id)
        self.reputations[agent_id] = reputation

        self.agent_credentials[agent_id] = []

        return identity

    def get_identity(self, agent_id: str) -> Optional[AgentIdentity]:
        """获取身份"""
        return self.identities.get(agent_id)

    def verify_identity(self, agent_id: str) -> bool:
        """验证身份"""
        identity = self.get_identity(agent_id)
        if not identity:
            return False
        return identity.verify_identity()

    def update_identity(self, agent_id: str, **kwargs) -> bool:
        """更新身份信息"""
        identity = self.get_identity(agent_id)
        if not identity:
            return False

        for key, value in kwargs.items():
            if hasattr(identity, key):
                setattr(identity, key, value)

        identity.updated_at = datetime.utcnow()
        identity.generate_identity_hash()
        return True

    def get_reputation(self, agent_id: str) -> Optional[ReputationScore]:
        """获取信誉评分"""
        return self.reputations.get(agent_id)

    def update_reputation(self, agent_id: str, success: bool, response_time: Optional[float] = None) -> bool:
        """更新信誉"""
        reputation = self.reputations.get(agent_id)
        if not reputation:
            return False

        reputation.update_task_result(success, response_time)
        return True

    def rate_agent(self, agent_id: str, rating: float) -> bool:
        """评分 Agent"""
        reputation = self.reputations.get(agent_id)
        if not reputation:
            return False

        reputation.add_rating(rating)
        return True

    def issue_credential(
        self,
        agent_id: str,
        credential_type: str,
        issuer_id: str,
        issuer_name: str,
        title: str,
        description: str,
        expires_at: Optional[datetime] = None,
        **metadata
    ) -> Optional[Credential]:
        """颁发凭证"""
        if agent_id not in self.identities:
            return None

        credential = Credential(
            credential_id=str(uuid.uuid4()),
            agent_id=agent_id,
            credential_type=credential_type,
            issuer_id=issuer_id,
            issuer_name=issuer_name,
            title=title,
            description=description,
            expires_at=expires_at,
            metadata=metadata
        )
        credential.generate_verification_hash()

        self.credentials[credential.credential_id] = credential
        self.agent_credentials[agent_id].append(credential.credential_id)

        return credential

    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """获取凭证"""
        return self.credentials.get(credential_id)

    def get_agent_credentials(self, agent_id: str) -> List[Credential]:
        """获取 Agent 的所有凭证"""
        credential_ids = self.agent_credentials.get(agent_id, [])
        return [
            cred for cred in (self.credentials.get(cid) for cid in credential_ids)
            if cred is not None
        ]

    def get_valid_credentials(self, agent_id: str) -> List[Credential]:
        """获取有效凭证"""
        return [
            cred for cred in self.get_agent_credentials(agent_id)
            if cred.is_valid()
        ]

    def revoke_credential(self, credential_id: str, reason: str) -> bool:
        """撤销凭证"""
        credential = self.get_credential(credential_id)
        if not credential:
            return False

        credential.revoke(reason)
        return True

    def get_agent_summary(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 摘要"""
        identity = self.get_identity(agent_id)
        if not identity:
            return None

        reputation = self.get_reputation(agent_id)
        credentials = self.get_valid_credentials(agent_id)

        return {
            "agent_id": agent_id,
            "name": identity.name,
            "is_verified": identity.is_verified,
            "reputation": {
                "score": reputation.calculate_overall_score() if reputation else 0.0,
                "trust_level": reputation.get_trust_level() if reputation else "Unknown",
                "success_rate": reputation.calculate_success_rate() if reputation else 0.0,
                "avg_rating": reputation.calculate_rating() if reputation else 0.0,
                "total_tasks": reputation.total_tasks if reputation else 0
            },
            "credentials": {
                "total": len(credentials),
                "types": list(set(cred.credential_type for cred in credentials))
            },
            "created_at": identity.created_at.isoformat()
        }

    def search_agents_by_reputation(self, min_score: float = 0.0) -> List[str]:
        """按信誉搜索 Agent"""
        return [
            agent_id for agent_id, reputation in self.reputations.items()
            if reputation.calculate_overall_score() >= min_score
        ]

    def search_agents_by_credential(self, credential_type: str) -> List[str]:
        """按凭证类型搜索 Agent"""
        agent_ids = []
        for agent_id, credential_ids in self.agent_credentials.items():
            for cid in credential_ids:
                cred = self.credentials.get(cid)
                if cred and cred.credential_type == credential_type and cred.is_valid():
                    agent_ids.append(agent_id)
                    break
        return agent_ids

    def get_overall_stats(self) -> Dict[str, Any]:
        """获取整体统计"""
        return {
            "total_identities": len(self.identities),
            "total_credentials": len(self.credentials),
            "valid_credentials": sum(
                1 for cred in self.credentials.values() if cred.is_valid()
            ),
            "avg_reputation": sum(
                r.calculate_overall_score() for r in self.reputations.values()
            ) / len(self.reputations) if self.reputations else 0.0,
            "highly_trusted_agents": len([
                agent_id for agent_id, rep in self.reputations.items()
                if rep.get_trust_level() == "Highly Trusted"
            ])
        }
