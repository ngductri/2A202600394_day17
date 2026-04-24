# Reflection: Privacy & Technical Limitations (Multi-Memory Agent)

Dưới đây là phần tự đánh giá (Reflection) về hệ thống Multi-Memory Agent vừa được xây dựng, nhằm phân tích các rủi ro về quyền riêng tư (Privacy) và những hạn chế về mặt kỹ thuật (Technical Limitations) theo đúng yêu cầu của hệ thống Agentic AI hiện đại.

## 1. Rủi ro về Quyền riêng tư (Privacy & PII Risks)

**1.1. Nhận diện Memory nhạy cảm nhất**
Trong 4 backend được xây dựng, **Long-term Profile Memory** là thành phần nhạy cảm và tiềm ẩn nhiều rủi ro nhất. 
Lý do: Nó trực tiếp lưu trữ các thông tin định danh cá nhân (PII - Personally Identifiable Information) như: Tên tuổi, sở thích, thông tin y tế (dị ứng), đôi khi là cả địa chỉ nhà hoặc thông tin nhạy cảm vô tình bị trích xuất từ câu chat của người dùng.

**1.2. Rủi ro của việc Truy xuất sai (Retrieval Errors)**
Nếu quá trình phân giải ngữ cảnh bị lỗi, Agent có thể vô tình lấy thông tin của "User A" trộn lẫn vào phiên hội thoại của "User B" (đặc biệt trong các kiến trúc dùng chung một Vector Database mà chưa thiết lập Row-Level Security chuẩn). Việc rò rỉ chéo này là một vi phạm quyền riêng tư cực kỳ nghiêm trọng.

**1.3. Phương án xử lý (Consent, TTL, Deletion)**
Để hệ thống tuân thủ các quy tắc bảo vệ dữ liệu (VD: GDPR), kiến trúc cần sớm được bổ sung các tính năng:
- **Xóa bộ nhớ (Right to be Forgotten):** Cần có endpoint cho phép user yêu cầu "Xóa toàn bộ trí nhớ về tôi". Khi đó, hệ thống phải quét và xóa toàn bộ dữ liệu ứng với User ID trong file `profile_kv.json` và `episodic_log.json`.
- **TTL (Time-To-Live):** Các thông tin Semantic hoặc Short-term nên có thời hạn lưu trữ. Định kỳ tự động dọn dẹp các log Episodic quá 30 ngày để giảm thiểu rủi ro tích tụ dữ liệu hành vi.
- **Consent:** Chỉ kích hoạt Extractor LLM (Lưu Profile) khi có sự đồng ý ban đầu từ người sử dụng.

---

## 2. Hạn chế Kỹ thuật (Technical Limitations) của System

Dù hệ thống đã xử lý được tình trạng tràn Token bằng cửa sổ Sliding Window và cơ chế Override Key-Value, mô hình hiện tại vẫn tồn tại các giới hạn khi mở rộng (Scaling):

1. **Vấn đề đồng thời (Concurrency) của JSON Store:** 
   Hiện tại `LongTermProfileMemory` và `EpisodicMemory` đang ghi trực tiếp xuống file text (JSON). Nếu hệ thống Server đón nhận cùng lúc hàng trăm người dùng gửi tin nhắn, việc mở khóa/ghi file (File I/O lock) sẽ dẫn đến lỗi Race Condition (ghi đè mất dữ liệu của nhau). 
   *Giải pháp:* Cập nhật lên các Database thực thụ như Redis, PostgreSQL.

2. **Chi phí Extractor LLM gấp đôi (Cost Overhead):**
   Trong kiến trúc hiện tại, cứ mỗi lượt chat, hệ thống không chỉ phải chạy LLM chính để phát sinh câu trả lời, mà còn phải chạy một LLM phụ (Extractor) bằng prompt phụ để soi tìm các "Facts" cập nhật Profile. Ở quy mô lớn, điều này sẽ dội chi phí Token API lên gấp đôi.
   *Giải pháp:* Chuyển sang mô hình Extractor chạy Asynchronous (bất đồng bộ) theo dạng Background Job, hoặc dùng các mô hình BERT/Spacy siêu nhẹ chuyên dụng cho trích xuất thực thể (NER) thay vì gọi Gemini.

3. **Keyword Fallback cho Semantic Memory còn thô sơ:**
   Kiến trúc Semantic hiện tại đang dùng string matching (`if word in query`). Điều này dẫn đến sự cứng nhắc (không hiểu được từ đồng nghĩa).
   *Giải pháp:* Thay thế bằng ChromaDB hoặc FAISS với công nghệ Vector Embedding để tra cứu độ tương đồng ngữ nghĩa thực sự.
