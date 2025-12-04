from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime

@dataclass
class ContextPacket:
    """候选信息包

    Attributes:
        content: 信息内容
        timestamp: 时间戳
        token_count: Token 数量
        relevance_score: 相关性分数(0.0-1.0)
        metadata: 可选的元数据
    """
    context: str
    timestamp: datetime
    token_count: int
    relevance_score: float = 0.5
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime object")
        if not isinstance(self.data, dict):
            raise TypeError("data must be a dictionary")