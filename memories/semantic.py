"""
4. Semantic Memory
Vai trò: Kiến thức, FAQ tĩnh. Lưu trữ và thực hiện vector/keyword retrieval.
Để đơn giản hóa theo rubic "Có thể backend giả lập / keyword search fallback", ta dùng dictionary có keyword matching.
"""
class SemanticMemory:
    def __init__(self):
        # Giả lập kiến thức về debug Docker (Phục vụ phần đánh giá - Test Recall)
        self.knowledge = {
            "docker framework": "Giải pháp: Khi debug mạng ở môi trường multi-container thì dùng docker service name thay vì localhost.",
            "langgraph state": "LangGraph cho phép quản lý State truyền giữa các Node bằng TypedDict, hỗ trợ chu trình AI lặp lại.",
        }
        
    def retrieve(self, query: str) -> str:
        # Keyword search matching cơ bản thay Vector FAISS
        results = []
        query_lower = query.lower()
        print(f"      [*] [Semantic Memory] Đang search kiến thức cho query liên quan: '{query_lower}'")
        for key, info in self.knowledge.items():
            # Nếu key (VD docker, langgraph) xuất hiện trong user prompt thì nhặt bài ra
            if any(word in query_lower for word in key.split()):
                results.append(info)
                
        if not results:
            return "Không có kiến thức Semantic liên quan được tìm thấy."
        return "\n".join([f"- Kiến thức hệ thống: {r}" for r in results])
