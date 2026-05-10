from typing import Optional
from datetime import datetime, timedelta


def calculate_importance(
    explicit_important: bool = False,
    is_identity_related: bool = False,
    is_preference_related: bool = False,
    is_emotional: bool = False,
    access_count: int = 0,
    last_accessed: Optional[datetime] = None
) -> float:
    score = 0.0
    
    if explicit_important:
        score += 3.0
    if is_identity_related:
        score += 2.5
    if is_preference_related:
        score += 2.0
    if is_emotional:
        score += 1.5
    
    score += min(access_count * 1.0, 5.0)
    
    if last_accessed:
        days_since = (datetime.now() - last_accessed).days
        if days_since < 7:
            score += 0.8
    
    return min(score, 10.0)
