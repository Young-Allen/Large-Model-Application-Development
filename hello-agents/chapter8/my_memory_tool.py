from typing import Dict, Any, List
from datetime import datetime

from ..base import Tool, ToolParameter
from ...memory import MemoryManager, MemoryConfig

class MemoryTool(Tool):
    def __init__(
            self,
            user_id: str,
            memory_config: MemoryConfig = None,
            memory_type: List[str] = None,
        ):
            super().__init__(
                name="MemoryTool",
                description="用于管理和操作记忆的工具，包括添加、搜索、遗忘和整合记忆等功能。"
            )
            self.memory_config = memory_config or MemoryConfig()
            self.memory_type = memory_type or ["working", "episodic", "semantic", "perceptual"]

            self.memory_manager = MemoryManager(
                config  = self.memory_config,
                user_id = user_id,
                enable_working="working" in self.memory_types,
                enable_episodic="episodic" in self.memory_types,
                enable_semantic="semantic" in self.memory_types,
                enable_perceptual="perceptual" in self.memory_types
            )


    def execute(self, action: str, **kwargs) -> Any:
        if action == "add":
            return self._add_memory(**kwargs)
        elif action == "search":
            return self._search_memory(**kwargs)
        elif action == "summary":
            return self._get_summary(**kwargs)

    def _add_memory(
            self, 
            content: str, 
            memory_type: str = "working", 
            importance: float = 0.5,    
            file_path: str = None,
            modality: str = None,
            **metadata
        ) -> str:
        try:
            # 确保会话ID存在
            if self.current_session_id is None:
                self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 感知记忆文件支持
            if memory_type == "perceptual" and file_path:
                inferred = modality or self._infer_modality(file_path)
                metadata.setdefault("modality", inferred)
                metadata.setdefault("raw_data", file_path)

            metadata.update({
                "session_id": self.current_session_id,
                "timestamp": datetime.now().isoformat(),
            })

            memory_id = self.memory_manager.add_memory(
                content=content,
                memory_type=memory_type,
                importance=importance,
                metadata=metadata
            )
            
            return f"✅ 记忆已添加，ID: {memory_id}"
        except Exception as e:
            return f"❌ 添加记忆失败: {str(e)}"
        
    def _search_memory(
		self,
		query: str,
		limit: int = 5,
		memory_type: str = None,
		memory_types: List[str] = None,
		min_importance: float = 0.1
	):
        try:
            if memory_types and not memory_types:
                memory_types = [memory_type] if memory_type else []
            
            results = self.memory_manager.search_memories(
                query=query,
                limit=limit,
                memory_types=memory_types,
                min_importance=min_importance
            )
            if not results:
                return "🔍 未找到相关记忆。"
            
            formatted_results = "\n\n".join(
                [f"ID: {mem['id']}\n类型: {mem['type']}\n重要性: {mem['importance']}\n内容: {mem['content']}" for mem in results]
            )
            return f"🔍 找到以下相关记忆:\n\n{formatted_results}"
        except Exception as e:
            return f"❌ 搜索记忆失败: {str(e)}"

    def _forget(
        self,
        strategy: str = "importance_based",
        threshold: float = 0.2,
        max_age_days: int = 30
    ) -> str:
        try:
            count = self.memory_manager.forget_memories(
                strategy=strategy,
                threshold=threshold,
                max_age_days=max_age_days
            )
            return f"🧹 已遗忘 {count} 条记忆（策略: {strategy}）"
        except Exception as e:
            return f"❌ 遗忘记忆失败: {str(e)}"

    def _consolidate(
        self,
        from_type: str = "working",
        to_type: str = "epiosdic",
        importance_threshold: float = 0.7
    ) -> str:
        try:
            count = self.memory_manager.consolidate_memories(
                from_type=from_type,
                to_type=to_type,
                importance_threshold=importance_threshold
            )
            return f"🧠 已整合 {count} 条记忆（从 {from_type} 到 {to_type}）"
        except Exception as e:
            return f"❌ 整合记忆失败: {str(e)}"


    def _infer_modality(self, file_path: str) -> str:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            return "image"
        elif file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return "video"
        elif file_path.lower().endswith(('.mp3', '.wav', '.flac')):
            return "audio"
        else:
            return "unknown"