# 05. LỘ TRÌNH TRIỂN KHAI KỸ THUẬT (IMPLEMENTATION ROADMAP)
## Phân bổ Công việc theo 5 Sprints, Tiêu chuẩn Nghiệm thu & Quản trị Rủi ro

---

### 1. TỔNG QUAN TIẾN ĐỘ THEO MÔ HÌNH AGILE (5 SPRINTS)

Lộ trình triển khai được chia thành **5 Sprint** (mỗi Sprint dự kiến 1–2 tuần) đảm bảo tính kế thừa từ mã nguồn hiện tại và kiểm thử cuốn chiếu:

```
[Sprint 1: Core Engine & DB] ──> [Sprint 2: Academic Canvas] ──> [Sprint 3: Split-PDF Verifier]
                                                                            │
[Sprint 5: Docker & Delivery] <── [Sprint 4: Agent Studio Workflows] ◄──────┘
```

---

### 2. CHI TIẾT CÁC HẠNG MỤC THEO TỪNG SPRINT

#### SPRINT 1: NỀN TẢNG CƠ SỞ DỮ LIỆU & SỬA LỖI CORE RETRIEVAL ENGINE
* **Mục tiêu:** Khắc phục triệt để lỗi BM25, nâng cấp DB schema mới trên PostgreSQL và trích xuất tọa độ 618 bài báo.
* **Danh sách công việc (Task Breakdown):**
  - [ ] **Task 1.1:** Viết lại module `backend/retrieval/bm25_cache_manager.py` với cơ chế Batch Loading ($500\text{ chunks}$) và Disk-based Pickle Caching, chấm dứt hoàn toàn lỗi `too many SQL variables`.
  - [ ] **Task 1.2:** Tạo migration script Alembic cho PostgreSQL: tạo các bảng `projects`, `paper_sections`, `project_references`, `document_spans`, `inline_citations`.
  - [ ] **Task 1.3:** Viết script `scripts/extract_pdf_spans.py` dùng `PyMuPDF` (`fitz`) để nạp toàn bộ text spans kèm tọa độ Bounding Box của 618 PDFs vào bảng `document_spans`.
  - [ ] **Task 1.4:** Viết các Unit Test kiểm thử tốc độ khởi động BM25 và độ chính xác của tọa độ trích xuất.
* **Tiêu chuẩn nghiệm thu (Acceptance Criteria):**
  - Khởi tạo BM25 cho domain `it` mất $< 0.1$s từ cache (thay vì crash như trước).
  - Bảng `document_spans` có đầy đủ dữ liệu tọa độ của 618 bài báo với tỷ lệ parse thành công $\ge 98\%$.

---

#### SPRINT 2: TÍCH HỢP ACADEMIC CANVAS & TRÌNH SOẠN THẢO WYSIWYG
* **Mục tiêu:** Xây dựng Zone 2 (Academic Canvas) thay thế khung chat cũ bằng trình soạn thảo rich-text chuẩn học thuật.
* **Danh sách công việc (Task Breakdown):**
  - [ ] **Task 2.1:** Cài đặt các gói Tiptap / Novel.sh vào `frontend/`: `@tiptap/react`, `@tiptap/pm`, `@tiptap/extension-table`, `@tiptap/extension-mathematics` (KaTeX).
  - [ ] **Task 2.2:** Xây dựng component `AcademicEditor.tsx` hỗ trợ tự động lưu nháp (Auto-save) sau mỗi $2$ giây không gõ phím.
  - [ ] **Task 2.3:** Tích hợp Slash Command Menu (`/`): hỗ trợ chèn công thức toán LaTeX, tạo bảng biểu, và chèn trích dẫn.
  - [ ] **Task 2.4:** Xây dựng `FloatingAIToolbar.tsx`: khi người dùng bôi đen câu văn, xuất hiện menu "Make Academic Tone", "Find Evidence", "Translate to En".
* **Tiêu chuẩn nghiệm thu (Acceptance Criteria):**
  - Người dùng gõ công thức toán học (ví dụ: `\mathcal{L}_{total}`) hiển thị đẹp mắt theo chuẩn KaTeX.
  - Thao tác gõ mượt mà không bị giật lag, nội dung tự động đồng bộ xuống bảng `paper_sections`.

---

#### SPRINT 3: HIỆN THỰC HÓA BỘ ĐỐI CHIẾU PDF SONG SONG (CLICK-TO-VERIFY)
* **Mục tiêu:** Xây dựng Zone 3 (Split-Screen Evidence Verifier) mang lại trải nghiệm tra cứu minh chứng của SciSpace.
* **Danh sách công việc (Task Breakdown):**
  - [ ] **Task 3.1:** Tích hợp thư viện `react-pdf` vào component `SplitPDFViewer.tsx`.
  - [ ] **Task 3.2:** Xây dựng lớp phủ `BoundingBoxHighlighter.tsx`: nhận tọa độ $(x_0, y_0, x_1, y_1)$ và vẽ khung chữ nhật màu vàng nổi bật trên trang PDF.
  - [ ] **Task 3.3:** Thiết lập Zustand Store liên kết tương tác: khi click vào thẻ trích dẫn `\cite{}` trên Canvas Zone 2 $\rightarrow$ Zone 3 tự động mở file PDF, cuộn tới đúng trang và kích hoạt khung vàng.
  - [ ] **Task 3.4:** Viết API `GET /api/documents/{domain}/{doc_name}/pdf` phục vụ stream file nhị phân tốc độ cao.
* **Tiêu chuẩn nghiệm thu (Acceptance Criteria):**
  - Độ trễ từ lúc click vào thẻ trích dẫn đến khi câu văn gốc trong PDF được bôi vàng $< 1.2$ giây.
  - Khung bôi vàng khớp chính xác $100\%$ với vị trí câu văn trên file PDF.

---

#### SPRINT 4: ĐỒ THỊ LANGGRAPH HỌC THUẬT & TRỢ LÝ COPILOT ĐỒNG TÁC GIẢ
* **Mục tiêu:** Tích hợp các State Node học thuật mới vào LangGraph và kết nối WebSocket với Canvas.
* **Danh sách công việc (Task Breakdown):**
  - [ ] **Task 4.1:** Xây dựng node `review_matrix_node`: đọc 3–5 file PDF được chọn và tự động sinh bảng đối sánh Markdown/LaTeX.
  - [ ] **Task 4.2:** Xây dựng node `citation_suggest_node`: phân tích câu văn người dùng đang viết, truy xuất bài báo liên quan nhất trong 618 bài và trả về mã BibTeX.
  - [ ] **Task 4.3:** Xây dựng node `academic_polish_node`: tinh chỉnh văn phong học thuật qua mô hình local Qwen2.5 7B.
  - [ ] **Task 4.4:** Xây dựng node `integrity_auditor_node`: rà soát toàn bộ section, phát hiện các nhận định thiếu trích dẫn và gắn cờ cảnh báo trên giao diện Zone 3.
  - [ ] **Task 4.5:** Hoàn thiện giao thức WebSocket `WS /api/ws/studio/{project_id}` đồng bộ streaming mượt mà.
* **Tiêu chuẩn nghiệm thu (Acceptance Criteria):**
  - Trợ lý AI phản hồi gợi ý câu văn học thuật và trích dẫn trong $< 2.5$ giây.
  - Bảng rà soát phát hiện chính xác các câu nhận định không có trích dẫn nguồn.

---

#### SPRINT 5: BIÊN DỊCH NỘI BỘ, ĐÓNG GÓI DOCKER & BÀN GIAO SẢN PHẨM
* **Mục tiêu:** Đóng gói xuất bản bài báo và chuẩn hóa Docker 1-Click Run.
* **Danh sách công việc (Task Breakdown):**
  - [ ] **Task 5.1:** Tích hợp engine biên dịch TeX cục bộ (Tectonic) vào container Backend: biên dịch trực tiếp toàn bộ các section ra file `paper.pdf`.
  - [ ] **Task 5.2:** Xây dựng tính năng xuất bản `Export Overleaf ZIP`: nén toàn bộ mã nguồn TeX, file `.bib`, hình ảnh thành tệp `.zip` đạt chuẩn nộp bài.
  - [ ] **Task 5.3:** Cập nhật `docker-compose.yml` và `Dockerfile` đa giai đoạn (multi-stage build), tối ưu dung lượng ảnh Docker.
  - [ ] **Task 5.4:** Viết kịch bản kiểm thử toàn diện End-to-End từ lúc tạo dự án, viết bài, đối soát PDF đến xuất bản.
* **Tiêu chuẩn nghiệm thu (Acceptance Criteria):**
  - Lệnh `docker compose up -d` kích hoạt thành công toàn bộ hệ thống trên máy mới chỉ sau 1 lệnh duy nhất.
  - File PDF biên dịch và file ZIP Overleaf mở ra đạt chuẩn định dạng IEEE Conference mà không có bất kỳ lỗi cú pháp nào.

---

### 3. MA TRẬN QUẢN TRỊ RỦI RO KỸ THUẬT (RISK MANAGEMENT MATRIX)

| Rủi ro Kỹ thuật | Xác suất | Tác động | Giải pháp Phòng ngừa & Dự phòng |
| :--- | :---: | :---: | :--- |
| **Tràn VRAM GPU khi chạy đồng thời Editor + Qwen2.5** | Trung bình | Cao | Duy trì cơ chế Dynamic GPU/CPU Fallback (`OLLAMA_NUM_GPU=8`), giới hạn ngữ cảnh `num_ctx=3072` tokens. |
| **Lệch tọa độ Bounding Box khi render trên các độ phân giải** | Cao | Trung bình | Chuẩn hóa tọa độ Bounding Box theo tỷ lệ phần trăm $(0.0 \rightarrow 1.0)$ thay vì lưu pixel tuyệt đối. |
| **Trình biên dịch TeX thiếu font hoặc style package** | Thấp | Cao | Sử dụng Tectonic (tự động tải font thiếu) hoặc đóng gói sẵn toàn bộ `IEEEtran.cls` và các gói thông dụng vào Docker image. |

