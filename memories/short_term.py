"""
1. Short-Term Memory
Vai trò: Lưu trữ ngắn hạn các lượt hội thoại gần nhất (Conversation Buffer / Sliding Window).
"""
class ShortTermMemory:
    def __init__(self, window_size=5):
        self.messages = []
        self.window_size = window_size
        
    def add_message(self, role: str, content: str):
        # Lưu message theo cấu trúc dict
        self.messages.append({"role": role, "content": content})
        # Cơ chế sliding window (cắt tỉa để tránh quá tải tokens)
        if len(self.messages) > self.window_size * 2: # *2 vì mỗi window coi như gồm user và assistant
            self.messages.pop(0)
            
    def retrieve(self) -> str:
        if not self.messages:
            return "Trống."
        return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.messages])
