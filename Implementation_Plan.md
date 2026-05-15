# Kế hoạch Triển khai Chi tiết (Implementation Plan) - Intelligent Research Agent

Tài liệu này trình bày toàn bộ quá trình thực hiện dự án, từ giai đoạn thiết lập nền tảng đến khi hoàn thiện hệ thống Agentic RAG.

---

## 1. Tổng quan Dự án
* **Tên dự án:** Phát triển Agent hỗ trợ nghiên cứu khoa học sử dụng kiến trúc Agentic RAG.
* **Mục tiêu:** Xây dựng hệ thống hỗ trợ tìm kiếm, phân tích và tổng hợp tài liệu học thuật local.
* **Cốt lõi:** Sử dụng LangGraph để điều khiển luồng suy luận và Ollama (Qwen) để xử lý ngôn ngữ.

## 2. Các Giai đoạn Thực hiện (Roadmap)

### Giai đoạn 1: Thiết lập Nền tảng & Cấu trúc Dữ liệu (Hoàn thành)
* **Môi trường:** Cấu hình Python 3.10+, Ollama, ChromaDB trên môi trường local.
* **Ingestion Pipeline:** * Sử dụng PyMuPDF và Unstructured để parse các tài liệu PDF chuyên ngành.
    * Thực hiện xử lý và lưu trữ thành công **15,495 chunks** thuộc các lĩnh vực: Vật lý, Điện tử, Toán học và CNTT.
* **Embedding:** Triển khai chiến lược 2 bước (OpenAI `text-embedding-3-small` cho prototyping và `BGE-M3` cho môi trường production).

### Giai đoạn 2: Phát triển Luồng suy luận Agentic (Tháng 5/2026)
* **Xây dựng Graph:** Thiết kế các Node và Conditional Edges bằng LangGraph.
* **Logic Self-RAG:**
    * **Retrieve Grader:** Kiểm tra độ tương quan giữa tài liệu tìm được và câu hỏi.
    * **Hallucination Grader:** Đối chiếu câu trả lời của LLM với dữ liệu gốc để đảm bảo tính xác thực.
    * **Answer Grader:** Đánh giá mức độ hài lòng của câu trả lời so với yêu cầu người dùng.
* **State Management:** Triển khai cơ chế Checkpointing và Snapshotting để lưu trữ trạng thái làm việc của Agent.

### Giai đoạn 3: Tích hợp Công cụ & Tính năng Nâng cao (Tháng 6/2026)
* **Hybrid Search:** Kết hợp Vector Search (Semantic) và BM25 (Keyword) để tối ưu độ chính xác.
* **Tool Integration:**
    * **Python REPL:** Cho phép Agent thực thi mã Python để xử lý dữ liệu và vẽ biểu đồ.
    * **Google Workspace API:** Kết nối để xuất báo cáo trực tiếp ra Google Docs và Google Sheets.
    * **LaTeX & Mermaid:** Hiển thị công thức toán học và sơ đồ kiến trúc hệ thống chuyên nghiệp.

### Giai đoạn 4: Đánh giá, Tối ưu & Hoàn thiện (Tháng 7/2026 - Kết thúc)
* **Đo lường RAGAS:** Kiểm thử hệ thống dựa trên 3 trụ cột: Faithfulness, Answer Relevance, và Context Precision.
* **UI/UX Optimization:**
    * Phát triển giao diện hiển thị luồng tư duy (Thought Process).
    * Tích hợp tính năng trích dẫn nguồn (Citations) chính xác đến từng trang tài liệu.
* **Security & Guardrails:** Thiết lập giới hạn số bước suy luận (Max-step) để tối ưu tài nguyên.

## 3. Quản lý Rủi ro & Giải pháp
| Rủi ro | Giải pháp |
| :--- | :--- |
| LLM chạy local bị chậm (Latency) | Sử dụng Qwen-2.5 phiên bản quantized và tối ưu hóa phần cứng. |
| Kết quả RAG bị ảo giác (Hallucinations) | Áp dụng vòng lặp kiểm định Self-RAG nghiêm ngặt. |
| Mất trạng thái khi xử lý lâu | Sử dụng LangGraph Checkpointer để phục hồi trạng thái từ Snapshot. |

---
**Ghi chú:** Kế hoạch này được cập nhật dựa trên báo cáo mới nhất ngày 14/05/2026.
