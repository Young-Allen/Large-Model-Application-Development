import os

class RagTool(Tool):
    def __init__(
            self,
            knowledge_base_path: str,
            qdrant_url: str = None,
            qdrant_api_key: str = None,
            collection_name: str = "rag_knowledge_base",
            rag_namespace: str = "default"
    ):
        # 初始化RAG管道
        self._pipelines: Dict[str, Dict[str, Any]] = {}
        self.llm = HelloAgentsLLM()
        
        # 创建默认管道
        default_pipeline = create_rag_pipeline(
            qdrant_url=self.qdrant_url,
            qdrant_api_key=self.qdrant_api_key,
            collection_name=self.collection_name,
            rag_namespace=self.rag_namespace
        )
        self._pipelines[self.rag_namespace] = default_pipeline

    def _convert_to_markdown(path: str) -> str:
        """
        Universal document reader using MarkItDown with enhanced PDF processing.
        核心功能：将任意格式文档转换为Markdown文本
        
        支持格式：
        - 文档：PDF、Word、Excel、PowerPoint
        - 图像：JPG、PNG、GIF（通过OCR）
        - 音频：MP3、WAV、M4A（通过转录）
        - 文本：TXT、CSV、JSON、XML、HTML
        - 代码：Python、JavaScript、Java等
        """
        if not os.path.exists(path):
            return ""
        
        # 对PDF文件使用增强处理
        ext = (os.path.splitext(path)[1] or '').lower()
        if ext == '.pdf':
            return _enhanced_pdf_processing(path)
        
        # 其他格式使用MarkItDown统一转换
        md_instance = _get_markitdown_instance()
        if md_instance is None:
            return _fallback_text_reader(path)
        
        try:
            result = md_instance.convert(path)
            markdown_text = getattr(result, "text_content", None)
            if isinstance(markdown_text, str) and markdown_text.strip():
                print(f"[RAG] MarkItDown转换成功: {path} -> {len(markdown_text)} chars Markdown")
                return markdown_text
            return ""
        except Exception as e:
            print(f"[WARNING] MarkItDown转换失败 {path}: {e}")
            return _fallback_text_reader(path)


    def _split_paragraphs_with_headings(text: str) -> List[Dict]:
        """根据标题层次分割段落，保持语义完整性"""
        lines = text.splitlines()
        heading_stack: List[str] = []
        paragraphs: List[Dict] = []
        buf: List[str] = []
        char_pos = 0
        
        def flush_buf(end_pos: int):
            if not buf:
                return
            content = "\n".join(buf).strip()
            if not content:
                return
            paragraphs.append({
                "content": content,
                "heading_path": " > ".join(heading_stack) if heading_stack else None,
                "start": max(0, end_pos - len(content)),
                "end": end_pos,
            })
        
        for ln in lines:
            raw = ln
            if raw.strip().startswith("#"):
                # 处理标题行
                flush_buf(char_pos)
                level = len(raw) - len(raw.lstrip('#'))
                title = raw.lstrip('#').strip()
                
                if level <= 0:
                    level = 1
                if level <= len(heading_stack):
                    heading_stack = heading_stack[:level-1]
                heading_stack.append(title)
                
                char_pos += len(raw) + 1
                continue
            
            # 段落内容累积
            if raw.strip() == "":
                flush_buf(char_pos)
                buf = []
            else:
                buf.append(raw)
            char_pos += len(raw) + 1
        
        flush_buf(char_pos)
        
        if not paragraphs:
            paragraphs = [{"content": text, "heading_path": None, "start": 0, "end": len(text)}]
        
        return paragraphs


    def _enhanced_pdf_processing():
        pass

    def _fallback_text_reader():
        pass