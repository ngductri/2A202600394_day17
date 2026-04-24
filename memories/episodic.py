import json
import os
from datetime import datetime

"""
3. Episodic Memory
Vai trò: Lưu trữ diễn biến chuỗi hoạt động quan trọng trong quá khứ như 1 tập tin logs.
Ví dụ: Lưu lại các đoạn summary của 1 câu hỏi/đáp lớn hoặc kết quả từ 1 hành động hoàn thiện.
"""
class EpisodicMemory:
    def __init__(self, file_path="log/episodic_log.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.episodes = []
        self._load()
        
    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.episodes = json.load(f)

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.episodes, f, ensure_ascii=False, indent=2)
            
    def add_episode(self, question: str, answer: str):
        episode_data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "answer": answer
        }
        print(f"      [*] [Episodic Memory] Lưu log sự kiện lúc {episode_data['time']}")
        self.episodes.append(episode_data)
        self._save() # Lưu thực tế xuống log file
        
    def retrieve(self) -> str:
        if not self.episodes:
            return "Trống."
        # Chỉ load snippet ngắn vào prompt để tránh tràn token
        lines = []
        for e in self.episodes[-3:]:
            if isinstance(e, dict):
                lines.append(f"- Event ({e.get('time', 'N/A')}): Hỏi: '{e.get('question', '')}' -> Đáp: '{str(e.get('answer', ''))[:100]}...'")
            else:
                # Fallback xử lý log cũ dạng string
                lines.append(f"- Event: {e}")
        return "\n".join(lines)
