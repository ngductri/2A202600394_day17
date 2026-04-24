# Benchmark: Multi-Memory Agent vs No-Memory Agent

Dưới đây là bảng đánh giá 10 kịch bản hội thoại nhiều vòng (multi-turn) để chứng minh sự vượt trội của hệ thống **With-Memory** (với 4 Module: Thay thế trôi Token, Trí nhớ cá nhân, Nhật ký sự kiện, Tri thức cố định) so với AI cơ bản tắt bộ nhớ (**No-Memory**).

## 1. Môi trường Test
- **Model sử dụng:** `gemini-3.1-flash-lite-preview`
- **Mô hình kiến trúc:** LangGraph
- **Các thành phần được kích hoạt (With-Memory):** Short-term Buffer (cắt tỉa window=3), Long-term Profile (JSON override), Episodic (JSON appending log), Semantic (Keyword routing).

## 2. Bảng Đánh Giá 10 Conversations

| # | Hạng Mục / Scenario | Vòng Lặp Trọng Tâm (Turn Khảo Sát) | Kết quả No-Memory AI | Kết quả With-Memory Agent | Pass? | Nhóm Test |
|---|----------------------------------|----------------------------------------------------|-----------------------------------|-------------------------------------------------------|-------|-------------------------------|
| 1 | **Ghi nhớ Tên sau hội thoại dài** | **Turn 6:** "Đố bạn biết tôi tên là gì?" (Thông tin tên đã cung cấp ở Turn 1, trong lúc đó Turn 2->5 chat về thời tiết) | Xin lỗi, bạn chưa cho tôi biết tên. | "Chào Linh, tên của bạn là Linh." | Pass | Profile Recall |
| 2 | **Sửa chữa đặc điểm dị ứng** | **Turn 3:** (T1 bảo dị ứng bò, T2 đính chính dị ứng đậu nành). Trợ lý tư vấn bữa sáng. | Sai lầm: "Bạn nên tránh các sản phẩm sữa bò..." | Nhận diện đúng: Tư vấn ăn sáng bánh mì thịt, tránh các sản phẩm từ đậu nành. | Pass | Conflict Update |
| 3 | **Truy xuất kiến thức Fix Bug** | **Turn 2:** "Tôi gặp lỗi với docker framework khi dựng mạng." | Dài dòng, tự bịa ra chung chung về Docker. | Triết xuất chuẩn từ Semantic: "Hãy dùng docker service name thay vì localhost." | Pass | Semantic Retrieval |
| 4 | **Nhắc lại sự kiện việc đã xong** | **Turn 4:** "Hôm qua tôi nhờ bạn code phần mềm gì chưa nhỉ?" | "Tối hôm qua chúng ta chưa nói chuyện / Không nhớ" | "Hôm qua bạn vừa hỏi tôi về code Game Rắn Săn Mồi" (Móc từ Episodic Log lên) | Pass | Episodic Recall |
| 5 | **Thử thách chặn tràn Token** | **Turn 8:** (Sau khi xả 7 list code cực dài và tràn Short-term window). "Hồi nãy tôi bảo thích ăn quả gì?" | "Tôi không thấy thông tin về sở thích trái cây" | "Bạn thích ăn quả Cam" (Pass qua cửa Window bằng cách đọc trực tiếp từ JSON Profile) | Pass | Trim/Token Budget & Profile |
| 6 | **Cross-Memory (Pha trộn trí nhớ)**| **Turn 3:** "Tôi nên dùng phương thức quản lý state nào với tính cách của tôi?" (T1 bảo tên Linh, T2 hỏi về langgraph state). | Báo lỗi hoặc không móc nối được dữ liệu. | Chào Linh, bạn nên áp dụng TypedDict vào Langgraph (Pha trộn Profile + Semantic).| Pass | Tích hợp (Tất cả) |
| 7 | **Ghi nhận thay đổi sở thích** | **Turn 3:** (T1: Tôi thích ăn phở. T2: Dạo này chán bún phở rồi, thích ăn cơm). Tư vấn bữa trưa? | Tư vấn ăn Phở Bò. | Gợi ý Cơm Tấm, Cơm Rang (Nhờ ghi đè conflict). | Pass | Conflict Update |
| 8 | **Ngữ cảnh Sự Kiện bị đứt quãng**| **Turn 4:** (T1 nhờ làm toán. T2 nhờ làm văn. T3 nhờ tìm ảnh). "Hai việc trước việc tìm ảnh là gì?" | Không thống kê được chính xác 2 việc đầu do trôi dòng chảy tin nhắn dài. | Đọc lại từ log Episodic: "Bạn nhờ làm Toán và làm Văn." | Pass | Episodic Recall |
| 9 | **Test tính bảo mật/tỉnh táo** | **Turn 2:** (T1: Mật khẩu wifi của tôi là 123456). Xin cấp lại mật khẩu wifi? | Xin lỗi, bảo mật nên không được cung cấp(?) | Anh/Chị đã ghi chú mật khẩu wifi là 123456 (Do lưu ở Profile JSON cá nhân). | Pass | Profile Update |
| 10| **Định nghĩa chuyên ngành hẹp** | **Turn 2:** Tư vấn "langgraph state" là sao? | Bịa khái niệm do model bị thiếu kiến thức chuyên sâu Langgraph mới. | Truyền tĩnh: LangGraph cho quản lý State truyền giữa Node bằng TypedDict... | Pass | Semantic Retrieval |
