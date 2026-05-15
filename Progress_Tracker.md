# Bảng Theo Dõi Tiến Độ (Progress Tracker)

Dựa trên tài liệu `Implementation_Plan.md` và tình trạng thực tế của mã nguồn (cập nhật ngày 15/05/2026), dưới đây là các hạng mục cần thực hiện để hoàn thiện dự án Agentic RAG. Bạn có thể sử dụng file này để đánh dấu (check) các phần việc đã hoàn thành.

## Giai đoạn 1: Thiết lập Nền tảng & Cấu trúc Dữ liệu
- [x] Cấu hình môi trường Python 3.10+, Ollama, ChromaDB trên local.
- [x] Ingestion Pipeline: Parse PDF bằng PyMuPDF và Unstructured.
- [x] Vector Database: Tạo các collection theo domain (it, math, physics, electronics) với 15,495 chunks.
- [x] Embedding: Tích hợp mô hình embedding (Hiện tại đang sử dụng `bge-m3`).
  - [x] *(Tuỳ chọn)* Chuyển đổi mô hình embedding sang `BGE-M3` hoặc `text-embedding-3-small` theo đúng plan.

## Giai đoạn 2: Phát triển Luồng suy luận Agentic
- [x] Xây dựng bộ khung LangGraph: Các node router, retrieve, web_search, generate.
- [x] Node **Router Grader**: Phân loại domain của câu hỏi.
- [x] Logic Self-RAG - **Retrieve Grader**: Kiểm tra độ tương quan giữa tài liệu tìm được và câu hỏi (`grade_documents_node`).
- [x] Logic Self-RAG - **Hallucination Grader**: Node đối chiếu câu trả lời của LLM với dữ liệu gốc để chống ảo giác.
- [x] Logic Self-RAG - **Answer Grader**: Node đánh giá xem câu trả lời có thỏa mãn yêu cầu của người dùng hay chưa.
- [x] Cập nhật Conditional Edges trong `graph.py` để kết nối Hallucination Grader và Answer Grader.
- [x] **State Management**: Cấu hình Checkpointing/Snapshotting (vd: `MemorySaver`) trong quá trình compile LangGraph để lưu trữ trạng thái hội thoại.

## Giai đoạn 3: Tích hợp Công cụ & Tính năng Nâng cao
- [ ] **Hybrid Search**: Bổ sung BM25 (keyword search) và kết hợp với Vector Search hiện tại bằng `EnsembleRetriever`.
- [ ] Tích hợp **Python REPL Tool**: Cho phép Agent thực thi mã Python.
- [ ] Tích hợp **Google Workspace API Tool**: Hỗ trợ Agent xuất báo cáo ra Google Docs/Sheets.
- [ ] Xử lý **LaTeX & Mermaid**: Hỗ trợ Agent trả về kết quả chuẩn định dạng để hiển thị công thức/sơ đồ.

## Giai đoạn 4: Đánh giá, Tối ưu & Hoàn thiện
- [ ] Tích hợp framework đánh giá **RAGAS** (Faithfulness, Answer Relevance, Context Precision) vào file `evaluate.py`.
- [ ] **UI/UX**: Xây dựng giao diện cho phép hiển thị luồng tư duy (Thought Process) của Agent một cách trực quan.
- [ ] **Citations**: Tối ưu UI để hiển thị trích dẫn nguồn chi tiết và chính xác.
- [ ] **Security & Guardrails**: Cấu hình `recursion_limit` trong LangGraph để kiểm soát số vòng lặp tối đa của Agent.

---
**Hướng dẫn sử dụng:** 
Khi bạn hoàn thành một tính năng, hãy đổi `[ ]` thành `[x]` trong file này để dễ dàng theo dõi tiến độ công việc.
