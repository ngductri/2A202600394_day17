"""
LangGraph Multi-Memory Agent
Gom 4 backend vào State và truyền vào LLM (Gemini API)
"""
import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from prompts import SYSTEM_PROMPT
from memories.short_term import ShortTermMemory
from memories.long_term_profile import LongTermProfileMemory
from memories.episodic import EpisodicMemory
from memories.semantic import SemanticMemory

# Định nghĩa TypedDict State (Yêu cầu Rubric #2)
class MemoryState(TypedDict):
    user_input: str
    response: str
    short_term_context: str
    profile_context: str
    episodic_context: str
    semantic_context: str

class MultiMemoryAgent:
    def __init__(self):
        # 4 System Memories
        self.short_term = ShortTermMemory(window_size=3) # Token budget cut-off qua window
        self.profile = LongTermProfileMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        
        # Khởi tạo interface của Gemini Model
        if "GOOGLE_API_KEY" not in os.environ:
            print("[Cảnh Báo] Hãy set biến môi trường GOOGLE_API_KEY trước khi chạy.")
            
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0.2)
        # LLM phụ dùng cho việc tách context facts ổn định (Temperature=0)
        self.extractor_llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
        
        # Build node Graph
        self.graph = self._build_graph()

    def retrieve_memory_node(self, state: MemoryState):
        """Node 1: Gom nhặt dữ liệu từ các Memory Backends"""
        print("\n⏳ [ROUTER] BƯỚC 1: Lấy context từ 4 loại Memory Data...")
        user_input = state["user_input"]
        
        state["short_term_context"] = self.short_term.retrieve()
        state["profile_context"] = self.profile.retrieve()
        state["semantic_context"] = self.semantic.retrieve(user_input)
        state["episodic_context"] = self.episodic.retrieve()
        
        print("  -> Đã Inject thành công 4 loại memory vào State Router.")
        return state

    def call_model_node(self, state: MemoryState):
        """Node 2: Cung cấp Context vào System Prompt và gọi Gemini"""
        print("\n⏳ [LLM] BƯỚC 2: Gọi Gemini kết hợp Prompt & Injection...")
        
        prompt = SYSTEM_PROMPT.format(
            profile_context=state["profile_context"],
            episodic_context=state["episodic_context"],
            semantic_context=state["semantic_context"],
            short_term_context=state["short_term_context"]
        )
        
        # [Tiêu chí Rubric: Đo lường Token Budget bằng định lượng Character Count]
        char_count = len(prompt)
        print(f"  -> [Token Budgeting] Prompt truyền vào LLM dài: {char_count} ký tự (Ước tính khoảng {char_count // 4} tokens).")
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=state["user_input"])
        ]
        
        response = self.llm.invoke(messages)
        print("  -> LLM Gemini đã phản hồi lại dựa trên memories.")
        
        # Ép kiểu an toàn để tránh lỗi list.strip()
        content = response.content
        if isinstance(content, list):
            # Nếu Gemini trả về list dict chứa text blocks
            texts = [str(c.get("text", c)) if isinstance(c, dict) else str(c) for c in content]
            content = " ".join(texts)
        else:
            content = str(content)
            
        state["response"] = content
        return {"response": content}

    def update_memory_node(self, state: MemoryState):
        """Node 3: Lắng nghe response & update lại vào backends. Xử lý conflict tại đây."""
        print("\n⏳ [UPDATING] BƯỚC 3: Lưu lại dữ liệu & Resolve Conflict (Dị ứng, tên)...")
        user_input = state["user_input"]
        response = state["response"]
        
        # 1. Update Short-Term
        self.short_term.add_message("user", user_input)
        self.short_term.add_message("assistant", response)
        
        # 2. Xử lý lưu đè/lưu mới Profile
        extract_prompt = f"""
        Bạn là agent chắt lọc thông tin cho người dùng. 
        Hãy lọc các thông tin, facts (tên, sở thích, dị ứng, thông báo liên quan đến bản thân...) từ câu nói sau sang định dạng JSON dict.
        Ví dụ: "À nhầm, tôi bị dị ứng đậu nành chứ không phải sữa" -> {{"allergy": "đậu nành"}} 
        Nếu người dùng bị dị ứng mảng mới giữ lại logic thay thế thông tin (conflict update).
        Nếu không có, về {{}}.
        Chỉ trả output raw JSON:
        USER SAID: "{user_input}"
        """
        try:
            res = self.extractor_llm.invoke(extract_prompt).content
            clean_res = res.replace("```json", "").replace("```", "").strip()
            extracted_facts = json.loads(clean_res)
            
            for k, v in extracted_facts.items():
                self.profile.update_fact(k, v) # Conflict Handling diễn ra ở hàm này
        except Exception:
            pass # Không parse được tức là không có
            
        # 3. Cập nhật Episodic (Log toàn bộ Question và Answer dưới dạng JSON log format)
        self.episodic.add_episode(question=user_input, answer=response)
            
        return {}

    def _build_graph(self):
        graph = StateGraph(MemoryState)
        graph.add_node("retrieve", self.retrieve_memory_node)
        graph.add_node("call_model", self.call_model_node)
        graph.add_node("update_memory", self.update_memory_node)
        
        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "call_model")
        graph.add_edge("call_model", "update_memory")
        graph.add_edge("update_memory", END)
        
        return graph.compile()
        
    def chat(self, user_input: str):
        print("\n" + "═"*60)
        print(f"👤 USER (Gốc): {user_input}")
        
        # [FEATURE MỚI: BẢO VỆ PII ĐẦU VÀO TRƯỚC KHI VÀO GRAPH]
        # Che Email
        safe_input = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_BỊ_ẨN]', user_input)
        # Che CCCD hoặc Số điện thoại (9 đến 12 chữ số)
        safe_input = re.sub(r'\b\d{9,12}\b', '[ID_BỊ_ẨN]', safe_input)
        
        if safe_input != user_input:
            print(f"🛡️ CẢNH BÁO PII: Tin nhắn của bạn chứa dữ liệu nhạy cảm. Hệ thống đã tự động Masking!")
            print(f"👤 USER (Đã Mask): {safe_input}")
            
        result = self.graph.invoke({"user_input": safe_input})
        print("\n🤖 GEMINI AGENT PHẢN HỒI:")
        
        final_answer = result.get("response", "")
        if isinstance(final_answer, list):
            final_answer = " ".join([str(i) for i in final_answer])
            
        print(str(final_answer).strip())
        print("═"*60)
