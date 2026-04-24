import json
import os

"""
2. Long-Term Profile Memory
Vai trò: Lưu trữ các facts/sự kiện/thông tin cá nhân của người dùng.
Ví dụ lưu Key-Value store. Khi đổi thuộc tính, thuộc tính cũ sẽ bị đè/cập nhật.
"""
class LongTermProfileMemory:
    def __init__(self, file_path="log/profile_kv.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.profile = {}
        self._load()
    
    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.profile = json.load(f)

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def update_fact(self, key: str, value: str):
        print(f"      [*] [Profile Memory] Update / Handle Conflict: '{key}' = '{value}'")
        self.profile[key] = value
        self._save() # Lưu thực tế xuống đĩa
        
    def retrieve(self) -> str:
        if not self.profile:
            return "Trống."
        return "\n".join([f"- {k}: {v}" for k, v in self.profile.items()])
