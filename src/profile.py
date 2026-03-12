import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, List

PROFILE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "profile.json")

INTEREST_FIELDS = [
    "数码产品",
    "美妆护肤",
    "家居生活",
    "汽车用品",
    "服装时尚",
    "食品饮料",
    "运动健身",
    "图书影音",
    "旅游出行",
    "母婴育儿",
    "游戏动漫",
    "艺术品",
    "其他"
]

PRICE_SENSITIVITY = [
    ("budget", "平价实惠"),
    ("mid-range", "中端品质"),
    ("premium", "高端奢华")
]

DECISION_FACTORS = [
    ("function", "功能实用"),
    ("appearance", "外观颜值"),
    ("brand", "品牌知名度"),
    ("price", "价格优惠"),
    ("quality", "质量品质"),
    ("reviews", "用户口碑"),
    ("uniqueness", "独特稀有"),
    ("service", "售后服务")
]


@dataclass
class UserProfile:
    name: str = ""
    nickname: str = ""
    age_range: str = ""
    gender: str = ""
    
    interests: List[str] = None
    
    price_sensitivity: str = "mid-range"
    
    decision_factors: List[str] = None
    
    occupation: str = ""
    personality: str = ""
    communication_style: str = "friendly"
    
    def __post_init__(self):
        if self.interests is None:
            self.interests = []
        if self.decision_factors is None:
            self.decision_factors = []
    
    def get_interests_display(self) -> str:
        if not self.interests:
            return "未设置"
        return ", ".join(self.interests)
    
    def get_decision_factors_display(self) -> str:
        if not self.decision_factors:
            return "未设置"
        factors = []
        for key, label in DECISION_FACTORS:
            if key in self.decision_factors:
                factors.append(label)
        return ", ".join(factors) if factors else "未设置"
    
    def get_price_sensitivity_display(self) -> str:
        for key, label in PRICE_SENSITIVITY:
            if key == self.price_sensitivity:
                return label
        return "中端品质"
    
    def to_prompt_context(self) -> str:
        context_parts = []
        
        if self.name:
            context_parts.append(f"助手的名字叫 {self.name}")
        if self.nickname:
            context_parts.append(f"小名叫 {self.nickname}")
        
        if self.interests:
            context_parts.append(f"感兴趣的领域: {', '.join(self.interests)}")
        
        if self.price_sensitivity:
            context_parts.append(f"价格敏感度: {self.get_price_sensitivity_display()}")
        
        if self.decision_factors:
            factors = self.get_decision_factors_display()
            context_parts.append(f"购买决策关注因素: {factors}")
        
        if self.personality:
            context_parts.append(f"性格特点: {self.personality}")
        
        if self.occupation:
            context_parts.append(f"职业: {self.occupation}")
        
        if context_parts:
            return "\n".join([f"[用户画像信息]\n", "\n".join(context_parts)])
        return ""


def load_profile() -> UserProfile:
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UserProfile(**data)
        except Exception:
            pass
    return UserProfile()


def save_profile(profile: UserProfile) -> bool:
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False
