import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Yêu cầu cài thư viện:
# pip install -r requirements.txt

from agent import MultiMemoryAgent

def run_benchmark():
    print("Khởi chạy Agent với Multi-Memory Stack Gemini...")
    agent = MultiMemoryAgent()
    
    # --- KỊCH BẢN BENCHMARK MULTI-TURN 10 TÌNH HUỐNG ---
    
    # Kịch bản 1: Cung cấp thông tin ban đầu (Profile)
    print("\n\n=== BENCHMARK 1: PROFILE INJECTION ===")
    agent.chat("Chào bạn, tôi tên là Trí, tôi là sinh viên IT.")

    # Kịch bản 2: Ghi nhớ Sở thích (Conflict Test - Giai đoạn 1)
    print("\n\n=== BENCHMARK 2: PROFILE UPDATE (CONFLICT TEST 1) ===")
    agent.chat("Tôi rất thích uống cà phê đen vào buổi sáng.")

    # Kịch bản 3: Sửa đổi Sở thích -> Sinh ra mâu thuẫn (Conflict Test - Giai đoạn 2)
    print("\n\n=== BENCHMARK 3: THAY ĐỔI DỮ LIỆU ĐỂ TEST CONFLICT ===")
    agent.chat("À tôi đổi ý rồi, dạo này tôi bị mất ngủ nên tôi chuyển sang uống nước cam vào buổi sáng rồi, quên vụ cà phê đi nhé.")

    # Kịch bản 4: Truy xuất Semantic Memory (Tri thức tĩnh)
    print("\n\n=== BENCHMARK 4: SEMANTIC RETRIEVAL ===")
    agent.chat("Bạn có biết langgraph state hoạt động như thế nào không?")

    # Kịch bản 5: Ngắt quãng ngữ cảnh bằng các lượt đi vòng vo
    print("\n\n=== BENCHMARK 5: LÀM NHIỄU NGỮ CẢNH (TRÔI TOKEN BẰNG SHORT-TERM CHAT) ===")
    agent.chat("Bỏ qua mấy chuyện đó đi! Kể cho tôi một câu chuyện cười ngắn.")
    
    print("\n\n=== BENCHMARK 6: LÀM NHIỄU TIẾP TỤC ===")
    agent.chat("Chuyện đó cũng vui đó, thế thời tiết trưa nay ở Hà Nội ra sao?")

    print("\n\n=== BENCHMARK 7: LÀM NHIỄU TIẾP TỤC LẦN 3 ===")
    agent.chat("Tôi vừa học xong một khóa khá đau đầu, bạn làm vài bài toán đố vui đi.")

    # Kịch bản 8: Kiểm tra Profile Recall sau thời gian dài (vượt qua giới hạn Short-term Memory window=3)
    print("\n\n=== BENCHMARK 8: PROFLE RECALL (SAU KHI TRÔI SHORT-TERM) ===")
    agent.chat("Bây giờ, bạn còn nhớ tôi là ai và tôi thích uống nước gì vào buổi sáng không?")

    # Kịch bản 9: Giao việc lớn để kích hoạt log vào Episodic Memory
    print("\n\n=== BENCHMARK 9: GIAO TASK ĐỂ GHI EPISODIC LOG ===")
    agent.chat("Bạn giúp tôi tóm tắt lại kế hoạch code game Rắn Săn Mồi hôm qua đi.")

    # Kịch bản 10: Episodic Recall - Lục lại hành động lớn đã xảy ra 
    print("\n\n=== BENCHMARK 10: EPISODIC RECALL ===")
    agent.chat("Nãy giờ tôi và bạn đã trải qua những chuyện gì? Liệt kê ngắn gọn những chủ đề mình đã nói/tìm kiếm giúp tôi.")

    print("\n\n=> HOÀN THÀNH 10 KỊCH BẢN CHUẨN ĐÁNH GIÁ CỦA RUBRIC.")

if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ or len(os.environ["GOOGLE_API_KEY"]) < 5:
         print("\n⚠️[ERROR LUỒNG PHỤ]: BẠN CẦN SET BIẾN MÔI TRƯỜNG 'GOOGLE_API_KEY' TỪ GEMINI TRƯỚC KHI CHẠY THỬ!")
         print("Cách thực hiện: set GOOGLE_API_KEY=YOUR_KEY (hoặc export) ở terminal.\n")
    else:
         run_benchmark()
