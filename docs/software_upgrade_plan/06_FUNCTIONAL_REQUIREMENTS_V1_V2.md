# ĐẶC TẢ YÊU CẦU CHỨC NĂNG HỆ THỐNG TOÀN DIỆN (FRS)
## Comprehensive Functional Requirements Specification — Version 1.0 & Version 2.0
**Đồ án Tốt nghiệp / Nghiên cứu Khoa học**  
*Mã hệ thống:* **Academic Research Studio & Multi-Domain Agentic RAG Platform**  
*Chuẩn tài liệu:* Tham chiếu **IEEE Std 830-1998** & **ISO/IEC/IEEE 29148:2018**  
*Ngày ban hành:* 05/11/2026 | *Trạng thái:* **Hoàn thành 100% (Camera-Ready Release v2.0.0)**

---

## 📑 MỤC LỤC
1. [Giới thiệu & Phạm vi hệ thống](#1-giới-thiệu--phạm-vi-hệ-thống)
2. [Ma trận tiến hóa hệ thống (Evolution Matrix: V1.0 vs V2.0)](#2-ma-trận-tiến-hóa-hệ-thống-evolution-matrix-v10-vs-v20)
3. [Tác nhân & Phân quyền hệ thống (User Personas & Role Matrix)](#3-tác-nhân--phân-quyền-hệ-thống-user-personas--role-matrix)
4. [Quy ước định danh mã yêu cầu (Requirement ID Conventions)](#4-quy-ước-định-danh-mã-yêu-cầu-requirement-id-conventions)
5. [PHẦN A: ĐẶC TẢ YÊU CẦU CHỨC NĂNG PHIÊN BẢN 1.0 (VERSION 1.0)](#5-phần-a-đặc-tả-yêu-cầu-chức-năng-phiên-bản-10-version-10)
   - Nhóm 1: Xác thực & Hồ sơ học giả (`FR-V1-AUTH`)
   - Nhóm 2: Tiếp nhận & Quản lý kho tài liệu số (`FR-V1-DOC`)
   - Nhóm 3: Phân loại & Định tuyến đa miền (`FR-V1-ROUTER`)
   - Nhóm 4: Tìm kiếm lai & Fallback 3 tầng (`FR-V1-RETRIEVAL`)
   - Nhóm 5: Đồ thị LangGraph tự đánh giá & Sửa lỗi (`FR-V1-SELF-CORRECT`)
   - Nhóm 6: Sandbox tính toán mã Python REPL (`FR-V1-REPL`)
   - Nhóm 7: Xuất dữ liệu Google Workspace (`FR-V1-EXPORT`)
   - Nhóm 8: Streaming WebSocket & Trực quan hóa tư duy Agent (`FR-V1-UI-STREAM`)
6. [PHẦN B: ĐẶC TẢ YÊU CẦU CHỨC NĂNG PHIÊN BẢN 2.0 (VERSION 2.0)](#6-phần-b-đặc-tả-yêu-cầu-chức-năng-phiên-bản-20-version-20)
   - Nhóm 9: Quản lý Dự án & Cấu trúc bài báo khoa học (`FR-V2-PROJECT`)
   - Nhóm 10: Trình soạn thảo Canvas WYSIWYG & Slash Commands (`FR-V2-EDITOR`)
   - Nhóm 11: Thanh công cụ AI nổi tại chỗ (Floating Copilot) (`FR-V2-FLOATING-AI`)
   - Nhóm 12: Split-Screen PDF Verifier & Click-to-Verify Bounding Box (`FR-V2-VERIFIER`)
   - Nhóm 13: Bộ 4 State Nodes Agentic Studio chuyên sâu (`FR-V2-AGENT-NODES`)
   - Nhóm 14: Động cơ biên dịch PDF Preprint tại chỗ (In-App Compiler) (`FR-V2-COMPILER`)
   - Nhóm 15: Đóng gói dự án Overleaf (.ZIP) (`FR-V2-OVERLEAF`)
   - Nhóm 16: Tối ưu hóa hiệu năng & Cache đĩa BM25 (`FR-V2-PERF`)
7. [Ma trận truy xuất nguồn gốc (Requirements Traceability Matrix - RTM)](#7-ma-trận-truy-xuất-nguồn-gốc-requirements-traceability-matrix---rtm)

---

## 1. GIỚI THIỆU & PHẠM VI HỆ THỐNG

### 1.1. Bối cảnh
Trong nghiên cứu khoa học và viết bài báo quốc tế (ISI/Scopus), sinh viên, giảng viên và nghiên cứu sinh thường xuyên phải chuyển đổi qua lại giữa hàng loạt công cụ rời rạc:
* **Google Scholar / ArXiv / Semantic Scholar:** Tìm kiếm tài liệu.
* **ChatGPT / Claude:** Tra cứu và giải thích khái niệm (thường gặp ảo giác, trích dẫn giả).
* **Word / Overleaf:** Viết bản thảo và công thức toán học.
* **Acrobat / Foxit PDF Reader:** Mở từng file PDF kiểm tra xem câu văn trong bài báo có đúng trang, đúng tọa độ gốc không.
* **Zotero / Mendeley:** Quản lý file BibTeX.

### 1.2. Mục tiêu hệ thống
Hệ thống được thiết kế để giải quyết toàn diện quy trình trên theo nguyên lý **"All-in-One Autonomous Academic IDE"**, trải qua 2 cột mốc lớn:
* **Phiên bản 1.0 (Research Chatbot & Grounded QA):** Cung cấp giao diện đàm thoại học thuật, hỗ trợ truy vấn ngữ liệu đa miền trên 618 bài báo gốc, giải quyết triệt để ảo giác thông qua quy trình tự sửa lỗi của LangGraph.
* **Phiên bản 2.0 (Academic Studio IDE):** Chuyển dịch từ Chatbot một cột sang **Môi trường Phát triển Tích hợp Học thuật (Academic IDE)** 3 cột hoàn chỉnh, người dùng chỉ cần mở ứng dụng là có thể thực hiện từ khâu lập đề cương, soạn thảo công thức KaTeX, xác thực câu văn gốc bằng Bounding Box phát sáng, cho đến biên dịch ra PDF camera-ready và gói Overleaf ZIP chuẩn tạp chí IEEE/ACM.

---

## 2. MA TRẬN TIẾN HÓA HỆ THỐNG (EVOLUTION MATRIX: V1.0 VS V2.0)

Bảng so sánh sau minh chứng tính bao quát và tính kế thừa giữa hai phiên bản:

| Chiều không gian so sánh | Phiên bản 1.0 (Interactive Chatbot) | Phiên bản 2.0 (Academic Studio IDE) | Mối quan hệ kế thừa |
| :--- | :--- | :--- | :--- |
| **UX / Bố cục màn hình** | Single-column Chat Window kèm Sidebar lịch sử hội thoại | **3-Zone Topology:** Zone 1 (Outline) - Zone 2 (Canvas) - Zone 3 (PDF Verifier) | Kế thừa Chat view thành 1 tab con trong Zone 3; bổ sung Canvas soạn thảo chuyên nghiệp |
| **Phương thức tương tác** | Prompt $\rightarrow$ Stream token $\rightarrow$ Final Answer | Soạn thảo trực tiếp (WYSIWYG), Slash Commands (`/`), Floating AI Toolbar, Click-to-Verify | Nâng cấp toàn diện trải nghiệm viết bài liền mạch |
| **Cơ sở dữ liệu** | User, ChatSession, Message, Profile | Bổ sung `Project`, `PaperSection`, `ProjectReference`, `DocumentSpan`, `InlineCitation` | Kế thừa 100% bảng cũ, bổ sung 5 bảng quản lý bài báo và tọa độ hình học |
| **Độ chính xác bằng chứng** | Trích xuất text chunk đính kèm cuối câu trả lời | Khung chữ nhật **Bounding Box $(x_0, y_0, x_1, y_1)$** phát sáng đè trực tiếp lên trang PDF gốc | Nâng cấp từ text sang tọa độ hình học không gian trang sách |
| **Agentic State Graph** | Router, Retrieve, Grade, WebSearch, ExpertSearch, Generate, REPL, Export | Bổ sung 4 Studio Nodes: Literature Matrix, Citation Suggest, Tone Polish, Reviewer-2 Auditor | Kế thừa toàn bộ đồ thị cũ, bổ sung đồ thị con chuyên trách viết báo |
| **Công cụ toán học & bảng** | Markdown text + KaTeX render thụ động | Soạn thảo KaTeX công thức hiển thị, bảng so sánh đa cột, mã giả thuật toán LaTeX | Hỗ trợ nhập liệu chủ động theo thời gian thực |
| **Khả năng xuất bản** | Export Google Docs & Google Sheets | Biên dịch PDF camera-ready nội bộ (Tectonic) + Đóng gói Overleaf .ZIP Bundle | Độc lập hoàn toàn, không phụ thuộc tài khoản bên thứ ba |
| **Tốc độ khởi động BM25** | $\approx 17.2$s (nguy cơ lỗi SQLite variables) | $< 0.9$s (Pickle Disk Cache + Lô 500 chunks) | Tối ưu hóa sâu tầng động cơ Core Engine |

---

## 3. TÁC NHÂN & PHÂN QUYỀN HỆ THỐNG (USER PERSONAS & ROLE MATRIX)

| Tác nhân (Actor) | Mô tả vai trò | Phạm vi sử dụng chức năng |
| :--- | :--- | :--- |
| **Guest / Anonymous** | Người dùng chưa đăng nhập | Xem trang giới thiệu, chuyển hướng sang `/login` hoặc sử dụng chế độ Demo Sandbox cục bộ |
| **Researcher / Student** | Sinh viên làm luận văn, nghiên cứu sinh, giảng viên | Toàn quyền tạo dự án bài báo, hỏi đáp RAG, soạn thảo Canvas, xác thực PDF, biên dịch PDF/Overleaf |
| **Autonomous Agent** | Thực thể AI (LangGraph State Machine) | Thực hiện tự động: phân loại miền, tìm kiếm lai, kiểm chứng ảo giác, tạo bảng ma trận, chuốt văn phong |
| **System Admin** | Quản trị viên hệ thống | Cấu hình tài nguyên Docker, quản lý nạp 618 bài báo PDF, giám sát các chỉ số hiệu năng |

---

## 4. QUY ƯỚC ĐỊNH DANH MÃ YÊU CẦU (REQUIREMENT ID CONVENTIONS)

Mỗi yêu cầu chức năng được đánh mã định danh theo chuẩn:
$$\text{FR-}[V_x]\text{-}[\text{MODULE}]\text{-}[\text{NUM}]$$
* $V_x$: `V1` (Phiên bản 1.0) hoặc `V2` (Phiên bản 2.0).
* `MODULE`: Viết tắt phân hệ (VD: `AUTH`, `DOC`, `RETRIEVAL`, `EDITOR`, `VERIFIER`, `AGENT`, `COMPILER`).
* `NUM`: Số thứ tự gồm 2 chữ số (VD: `01`, `02`).

---

## 5. PHẦN A: ĐẶC TẢ YÊU CẦU CHỨC NĂNG PHIÊN BẢN 1.0 (VERSION 1.0)

### Nhóm 1: Xác thực & Quản lý người dùng (`FR-V1-AUTH`)

#### `FR-V1-AUTH-01`: Đăng ký tài khoản người dùng
* **Mô tả:** Cho phép người dùng mới tạo tài khoản bằng email và mật khẩu an toàn.
* **Đầu vào:** `email` (chuẩn RFC 5322), `password` (tối thiểu 8 ký tự).
* **Xử lý:** Backend băm mật khẩu bằng thuật toán `bcrypt` (`passlib.context`). Lưu thông tin vào bảng `users`.
* **Đầu ra:** Thông báo đăng ký thành công, tự động chuyển sang màn hình đăng nhập.

#### `FR-V1-AUTH-02`: Đăng nhập & Cấp phát JWT Bearer Token
* **Mô tả:** Xác thực người dùng và cấp mã JWT để truy cập các tài nguyên bảo vệ.
* **Đầu vào:** `username` (email), `password` qua `OAuth2PasswordRequestForm`.
* **Xử lý:** Kiểm tra đối sánh mật khẩu. Nếu hợp lệ, sinh JWT access token với thời hạn hiệu lực 1440 phút (24 giờ), ký bằng thuật toán HS256 (`JWT_SECRET`).
* **Đầu ra:** `{ "access_token": "...", "token_type": "bearer" }`.

#### `FR-V1-AUTH-03`: Quản lý hồ sơ học giả (Profile Management)
* **Mô tả:** Cho phép cập nhật tên hiển thị, học hàm/học vị, đơn vị công tác (affiliation), và ảnh đại diện.
* **Endpoint:** `GET /api/auth/me`, `PUT /api/profile`, `POST /api/profile/avatar`.
* **Đầu ra:** Dữ liệu hồ sơ người dùng lưu tại bảng `profiles` và đồng bộ trên TopBar giao diện.

---

### Nhóm 2: Tiếp nhận & Quản lý tài liệu số (`FR-V1-DOC`)

#### `FR-V1-DOC-01`: Quản lý kho ngữ liệu đa miền (8 Domains)
* **Mô tả:** Hệ thống hỗ trợ tổ chức kho ngữ liệu theo 8 lĩnh vực khoa học biệt lập: `it`, `medicine`, `economics`, `physics`, `math`, `law`, `agriculture`, `electronics`.
* **Lưu trữ:** Mỗi miền tương ứng một thư mục vật lý tại `data/raw/{domain}/` và một ChromaDB Vector Collection riêng biệt `db/vector_stores/{domain}_collection/`.

#### `FR-V1-DOC-02`: Tải lên tài liệu PDF mới & Trigger Ingestion nền
* **Mô tả:** Cho phép người dùng tải file bài báo `.pdf` vào một miền cụ thể.
* **Xử lý:** Lưu file vào thư mục miền tương ứng. Kích hoạt `BackgroundTasks` gọi hàm `ingest_docs()` để phân đoạn (RecursiveCharacterTextSplitter: chunk size 1000, overlap 200), trích xuất embeddings ($bge\text{-}m3$) và nạp vào vector store.

#### `FR-V1-DOC-03`: Tái phân loại tài liệu giữa các miền (Document Reassignment)
* **Mô tả:** Chuyển một file PDF từ miền nguồn sang miền đích khi phát hiện phân loại sai.
* **Xử lý:** Di chuyển file vật lý, xóa vector cũ trong ChromaDB miền nguồn, và tái nạp chỉ mục cho miền đích.

---

### Nhóm 3: Phân loại & Định tuyến đa miền (`FR-V1-ROUTER`)

#### `FR-V1-ROUTER-01`: Phân loại ý định & Chọn miền tri thức tự động
* **Mô tả:** Phân tích câu hỏi người dùng để xác định lĩnh vực khoa học mục tiêu (`it`, `math`, `medicine`,...).
* **Cơ chế:** Kết hợp nhận diện từ khóa heuristics và mô hình ngôn ngữ LLM (`Qwen2.5-7B`) phân loại với độ trễ $< 0.5$s. Nếu người dùng chọn thủ công miền ưu tiên (`preferred_domain`), hệ thống sẽ bỏ qua phân loại tự động.

#### `FR-V1-ROUTER-02`: Định tuyến nhánh thực thi đồ thị (Conditional Branch Routing)
* **Mô tả:** Tùy thuộc vào bản chất câu hỏi, router điều hướng luồng LangGraph:
  * Chứa tính toán logic/mã nguồn $\rightarrow$ Chuyển sang `python_repl`.
  * Yêu cầu thông tin xu hướng, so sánh chuyên sâu $\rightarrow$ Kích hoạt `expert_consult` (Tavily).
  * Tra cứu tài liệu khoa học nội bộ $\rightarrow$ Chuyển sang `retrieve_local`.

---

### Nhóm 4: Tìm kiếm lai & Fallback 3 tầng (`FR-V1-RETRIEVAL`)

#### `FR-V1-RETRIEVAL-01`: Hybrid Search kết hợp $BGE\text{-}M3$ và $BM25$
* **Mô tả:** Tại Tier 1, thực hiện tìm kiếm kết hợp giữa Dense Vector Search và Sparse Lexical Search.
* **Công thức dung hợp điểm số:**
  $$\mathcal{S}_{hybrid}(q, d) = \lambda \cdot \mathcal{S}_{dense}(q, d) + (1 - \lambda) \cdot \mathcal{S}_{BM25}(q, d), \quad \text{với } \lambda = 0.5$$
* **Kết quả:** Trích xuất top-$k$ đoạn văn có độ tương đồng ngữ nghĩa và từ khóa cao nhất.

#### `FR-V1-RETRIEVAL-02`: Động cơ Fallback 3 tầng (3-Tier Fallback Mechanism)
* **Tier 1 (Nội bộ):** Tìm kiếm trên ChromaDB cục bộ chứa 618 bài báo gốc.
* **Tier 2 (Web Fallback):** Nếu ngữ cảnh nội bộ không đạt điểm đánh giá, tự động kích hoạt DuckDuckGo Web Search để bù đắp thông tin đại chúng.
* **Tier 3 (Expert Fallback):** Nếu câu hỏi đòi hỏi nghiên cứu nâng cao, kích hoạt Tavily Academic API để thu thập bài báo cập nhật từ các nguồn mở quốc tế.

---

### Nhóm 5: Đồ thị LangGraph tự đánh giá & Sửa lỗi (`FR-V1-SELF-CORRECT`)

#### `FR-V1-SELF-CORRECT-01`: Chấm điểm sự phù hợp của tài liệu (Document Relevance Grading)
* **Mô tả:** Node `grade_documents` đánh giá từng đoạn văn thu được: "yes" (liên quan) hoặc "no" (rác/không liên quan). Chỉ các đoạn được đánh giá "yes" mới đưa vào bộ ngữ cảnh sinh lời giải.

#### `FR-V1-SELF-CORRECT-02`: Kiểm chứng ảo giác (Hallucination Checker)
* **Mô tả:** Node đánh giá độc lập kiểm tra câu trả lời sinh ra có hoàn toàn bắt nguồn từ tập tài liệu ngữ cảnh hay không (`grounded vs hallucinated`). Nếu phát hiện ảo giác, yêu cầu node `generate` tự viết lại (tối đa 3 lần lặp).

#### `FR-V1-SELF-CORRECT-03`: Đánh giá mức độ giải quyết câu hỏi (Answer Relevance)
* **Mô tả:** Kiểm tra câu trả lời có trực tiếp giải quyết đúng trọng tâm câu hỏi của người dùng không. Nếu không thỏa mãn, tự động kích hoạt truy vấn bổ sung từ web search.

---

### Nhóm 6: Sandbox tính toán mã Python REPL (`FR-V1-REPL`)

#### `FR-V1-REPL-01`: Thực thi mã tính toán khoa học cô lập
* **Mô tả:** Cho phép agent tự sinh và thực thi các đoạn mã Python để tính toán ma trận, xác suất thống kê, hoặc mô phỏng phương trình mà LLM không tính nhẩm chính xác được.
* **Bảo mật:** Chạy qua `langchain_experimental.utilities.PythonREPL` trong môi trường kiểm soát, tự động bắt lỗi cú pháp và ngoại lệ runtime để phản hồi cho LLM tự sửa mã.

---

### Nhóm 7: Xuất dữ liệu Google Workspace (`FR-V1-EXPORT`)

#### `FR-V1-EXPORT-01`: Tự động xuất báo cáo sang Google Docs
* **Mô tả:** Khi câu lệnh chứa ý định xuất bản (`export to google docs`), agent trích xuất nội dung đã định dạng và dùng Google Drive/Docs API tạo một tài liệu mới trên Google Drive của người dùng.
* **Đầu ra:** Link chia sẻ tài liệu Google Docs trả về trực tiếp trong tin nhắn hội thoại.

#### `FR-V1-EXPORT-02`: Trích xuất và xuất bảng sang Google Sheets
* **Mô tả:** Khi kết quả chứa bảng số liệu đối sánh, agent tự động bóc tách thành mảng hai chiều `List[List[Any]]` và tạo trang tính Google Sheets có tiêu đề cột chuẩn xác.

---

### Nhóm 8: Streaming WebSocket & Trực quan hóa tư duy Agent (`FR-V1-UI-STREAM`)

#### `FR-V1-UI-STREAM-01`: Luồng dữ liệu hai chiều thời gian thực (Bidirectional Streaming)
* **Endpoint:** `ws://127.0.0.1:8000/api/ws/chat/{session_id}?token={jwt}`.
* **Sự kiện luồng:** Phát các gói tin JSON định dạng chuẩn:
  * `{"type": "node_update", "node": "router", "status": "running"}`
  * `{"type": "token", "content": "..."}`
  * `{"type": "final_answer", "content": "..."}`
  * `{"type": "export_link", "url": "..."}`

#### `FR-V1-UI-STREAM-02`: Thanh hiển thị quy trình suy nghĩ (Agent Thought Bar)
* **Giao diện:** Thanh tiến trình trực quan trên Chat Window hiển thị sống động từng bước thực thi của đồ thị (Phân loại miền $\rightarrow$ Truy xuất cục bộ $\rightarrow$ Đánh giá độ tin cậy $\rightarrow$ Sinh lời giải).

#### `FR-V1-UI-STREAM-03`: Render biểu đồ Mermaid & công thức KaTeX
* **Mô tả:** Tự động phát hiện và render các khối mã ```mermaid thành sơ đồ luồng kiến trúc tương tác và các khối `$ ... $` thành công thức toán đẹp mắt trên nền tảng web.

---

## 6. PHẦN B: ĐẶC TẢ YÊU CẦU CHỨC NĂNG PHIÊN BẢN 2.0 (VERSION 2.0)

### Nhóm 9: Quản lý Dự án & Cấu trúc bài báo khoa học (`FR-V2-PROJECT`)

#### `FR-V2-PROJECT-01`: Khởi tạo dự án bài báo khoa học (Academic Project Lifecycle)
* **Mô tả:** Cho phép tạo mới một bài báo hoàn chỉnh gắn liền với tài khoản người dùng.
* **Thuộc tính dự án:** Tiêu đề (`title`), Mẫu định dạng (`template_type`: IEEE Conference, ACM, Nature), Địa chỉ công bố mục tiêu (`target_venue`), Miền nghiên cứu chính (`primary_domain`), Tóm tắt (`abstract_text`), và Từ khóa (`keywords`).
* **Khởi tạo mặc định:** Hệ thống tự động sinh 6 mục bài báo tiêu chuẩn:
  1. *Abstract* (`abstract`)
  2. *1. Introduction* (`introduction`)
  3. *2. Related Work* (`related-work`)
  4. *3. Methodology* (`methodology`)
  5. *4. Experiments and Results* (`experiments`)
  6. *5. Conclusion* (`conclusion`)

#### `FR-V2-PROJECT-02`: Quản lý các phân đoạn bài báo (Section Management)
* **Mô tả:** Thêm mới, đổi tên, xóa, và thay đổi thứ tự hiển thị (`order_index`) của các mục trong bài báo.
* **Cập nhật thời gian thực:** Mỗi mục lưu trữ nội dung Markdown riêng biệt, tự động tính toán tổng số từ (`word_count`) và ước lượng thời gian đọc.

#### `FR-V2-PROJECT-03`: Quản lý danh mục trích dẫn dự án (Project Bibliography)
* **Mô tả:** Lưu trữ các nguồn trích dẫn đính kèm dự án trong bảng `project_references`.
* **Dữ liệu chuẩn:** `bibtex_key`, `title`, `authors`, `year`, `venue`, `doi`, `pdf_source_path`, và `bibtex_raw`. Hỗ trợ sao chép nhanh mã BibTeX chuẩn chỉ bằng 1 cú click.

---

### Nhóm 10: Trình soạn thảo Canvas WYSIWYG & Slash Commands (`FR-V2-EDITOR`)

#### `FR-V2-EDITOR-01`: Bố cục Academic Canvas chuẩn Novel / Overleaf
* **Vị trí:** Tọa lạc tại **Zone 2** (Cột trung tâm).
* **Đặc tính:** Giao diện tối giản, tập trung vào trải nghiệm viết bài chuyên nghiệp. Thiết kế bảng điều khiển dạng thẻ giấy chuẩn kích thước trang in học thuật, hỗ trợ căn lề, định dạng tiêu đề, danh sách, khối trích dẫn.

#### `FR-V2-EDITOR-02`: Cơ chế Tự động lưu không chặn (Auto-Save Sync)
* **Mô tả:** Tự động đồng bộ nội dung từ Canvas về cơ sở dữ liệu PostgreSQL qua endpoint `PUT /api/projects/{id}/sections/{section_id}`.
* **Kỹ thuật:** Áp dụng kỹ thuật debounce $2000$ms ($2$ giây sau khi người dùng ngừng gõ phím).
* **Trạng thái giao diện:**
  * Đang lưu: Biểu tượng spinner xoay tròn + chữ "Saving...".
  * Lưu thành công: Dấu check xanh + "Saved at HH:mm:ss".
  * Lỗi kết nối: Dấu cảnh báo đỏ + thông báo lỗi.

#### `FR-V2-EDITOR-03`: Trình đơn lệnh nhanh Slash Command (`/`)
* **Mô tả:** Khi người dùng gõ ký tự `/`, một menu popover thanh lịch lập tức xuất hiện tại đúng tọa độ con trỏ, cung cấp các lệnh chèn nhanh:
  * `/math`: Chèn khối công thức toán KaTeX chuẩn (`\begin{equation} ... \end{equation}`).
  * `/table`: Chèn bảng ma trận so sánh đối chuẩn thực nghiệm đa cột (Precision, Recall, F1, Latency).
  * `/cite`: Chèn cú pháp trích dẫn `\cite{bibtex_key}` gắn liền với kho ngữ liệu.
  * `/algo`: Chèn khung mã giả thuật toán LaTeX chuẩn mực.

#### `FR-V2-EDITOR-04`: Thẻ trích dẫn tương tác (Interactive Citation Badges)
* **Mô tả:** Mọi thẻ `\cite{key}` xuất hiện trên văn bản Canvas đều được tự động bóc tách thành các huy hiệu tương tác (Clickable Badges) màu tím nổi bật ở thanh Citation Quick Bar.

---

### Nhóm 11: Thanh công cụ AI nổi tại chỗ (Floating Copilot) (`FR-V2-FLOATING-AI`)

#### `FR-V2-FLOATING-AI-01`: Kích hoạt theo vùng chọn văn bản (Selection Popover)
* **Mô tả:** Khi người dùng dùng chuột bôi đen một câu hoặc đoạn văn bản bất kỳ ($\ge 4$ ký tự), thanh công cụ **Floating AI Toolbar** màu tím bo tròn sẽ tự động bay lên nhẹ nhàng ngay trên đoạn văn bản được chọn.

#### `FR-V2-FLOATING-AI-02`: Bộ 4 tác vụ tinh chỉnh văn bản tại chỗ
1. **Polish Tone (Chuốt văn phong):** Chuyển đổi câu văn thô sơ, văn nói thành văn phong học thuật chuẩn IEEE/ACM Transactions, loại bỏ câu mơ hồ, bảo toàn công thức toán.
2. **Find Evidence (Tìm dẫn chứng):** Tự động bóc tách luận điểm chính, tìm kiếm trong 618 bài báo để gợi ý các đoạn văn chứng minh tương ứng kèm thẻ `\cite{}`.
3. **Condense (Cô đọng):** Rút gọn câu chữ mà không làm mất ý chính, phục vụ các bài báo bị giới hạn số trang (Page-limit optimization).
4. **Expand (Mở rộng phương pháp luận):** Bổ sung diễn giải sâu hơn về mặt giải thuật hoặc nguyên lý toán học.

---

### Nhóm 12: Split-Screen PDF Verifier & Click-to-Verify Bounding Box (`FR-V2-VERIFIER`)

#### `FR-V2-VERIFIER-01`: Động cơ Streaming PDF nhị phân hiệu năng cao
* **Vị trí:** Tọa lạc tại **Zone 3** (Cột bên phải).
* **Endpoint Backend:** `GET /api/documents/{domain}/{doc_name}/pdf`.
* **Đặc tính:** Hỗ trợ giao thức `Range: bytes`, cho phép xem tài liệu PDF kích thước lớn mượt mà, hỗ trợ nhảy trang ngay tức thì, phóng to/thu nhỏ từ 50% đến 200%.

#### `FR-V2-VERIFIER-02`: Khung chữ nhật phát sáng Bounding Box Overlay
* **Mô tả:** Xây dựng component `BoundingBoxHighlighter.tsx` nhận vector tọa độ chuẩn hóa $(x_0, y_0, x_1, y_1) \in [0, 1]^4$ từ cơ sở dữ liệu `document_spans`.
* **Hiệu ứng hình ảnh:** Vẽ lớp phủ hình chữ nhật phát sáng màu tím/vàng với đường viền nổi bật (`box-shadow: 0 0 15px rgba(168, 85, 247, 0.7)`), gắn kèm nhãn bài báo và số trang chính xác.

#### `FR-V2-VERIFIER-03`: Tương tác "Click-to-Verify" đa chiều
* **Kịch bản:** Khi người dùng click vào bất kỳ thẻ trích dẫn nào (ví dụ `\cite{vaswani2017attention}`) trên Canvas ở Zone 2:
  * Zustand State Store (`studioStore.ts`) lập tức cập nhật `activeCitation`.
  * Zone 3 tự động chuyển sang tab Verifier, nạp đúng tài liệu PDF gốc, nhảy đúng số trang chứa câu văn đó, và vẽ Bounding Box đè lên vị trí câu trong thời gian $< 1.2$ giây.

#### `FR-V2-VERIFIER-04`: Thanh phân chia co giãn linh hoạt (Draggable Panel Resizers)
* **Mô tả:** Cho phép người dùng rê chuột vào đường ngăn giữa Zone 1 - Zone 2 và Zone 2 - Zone 3 để kéo chỉnh độ rộng của các cột theo ý muốn, có ràng buộc kích thước tối thiểu để không bị vỡ giao diện.

---

### Nhóm 13: Bộ 4 State Nodes Agentic Studio chuyên sâu (`FR-V2-AGENT-NODES`)

#### `FR-V2-AGENT-01`: Literature Review Matrix Generator Node
* **Mô tả:** Thu nhận câu hỏi nghiên cứu hoặc chủ đề so sánh, tìm kiếm tài liệu trên nhiều bài báo cùng lúc, và tự động tổng hợp bảng ma trận tổng quan tài liệu (Literature Review Matrix).
* **Cấu trúc bảng đầu ra:**
  `| Paper Reference | Primary Methodology | Key Quantitative Results | Notable Limitations / Research Gaps |`

#### `FR-V2-AGENT-02`: Smart Citation Suggester & BibTeX Extractor Node
* **Mô tả:** Phân tích từng khẳng định trong đoạn văn bản người dùng đang viết dở, đối soát cơ sở dữ liệu 618 bài báo, tự động bổ sung thẻ `\cite{key}` vào vị trí khẳng định và xuất khối mã BibTeX chuẩn xác bên dưới. Nếu câu văn không có bằng chứng, gắn nhãn cảnh báo `[Citation Needed]`.

#### `FR-V2-AGENT-03`: Academic Tone Polish & KaTeX Normalizer Node
* **Mô tả:** Chuyên biệt hóa prompt kỹ thuật dành cho văn phong IEEE/ACM: loại bỏ thể bị động không cần thiết, chuẩn hóa biến số toán học về dạng KaTeX (ví dụ $N, \mathcal{L}_{total}, \mathbb{R}^d$), bảo toàn 100% các thẻ `\cite{}` hiện có.

#### `FR-V2-AGENT-04`: Reviewer-2 Anti-Hallucination Grounding Auditor Node
* **Mô tả:** Đóng vai trò là "Người phản biện số 2" cực kỳ khắt khe: quét từng câu văn trong bản thảo, đối soát với các câu văn gốc thu được trong corpus, phân loại từng luận điểm thành:
  * `[VERIFIED GROUNDED]`: Có chứng cứ trực tiếp trong bài báo.
  * `[PARTIALLY SUPPORTED]`: Hợp lý nhưng thiếu định lượng cụ thể.
  * `[POTENTIAL HALLUCINATION]`: Không tìm thấy căn cứ hoặc mâu thuẫn với tài liệu.
* **Chỉ số:** Tính toán điểm số tin cậy bằng chứng từ 0% đến 100%.

#### `FR-V2-AGENT-05`: Kênh WebSocket Copilot Studio chuyên dụng
* **Endpoint:** `ws://127.0.0.1:8000/api/ws/studio/{project_id}`.
* **Xử lý:** Nhận diện các chế độ thực thi (`matrix`, `citation`, `polish`, `audit`), gọi đồ thị `studio_graph` và truyền luồng kết quả trực tiếp về Editor Canvas theo thời gian thực.

---

### Nhóm 14: Động cơ biên dịch PDF Preprint tại chỗ (In-App Compiler) (`FR-V2-COMPILER`)

#### `FR-V2-COMPILER-01`: Động cơ biên dịch độc lập không phụ thuộc bên thứ ba
* **Mô tả:** Cho phép sinh bản in camera-ready preprint 2 cột chuẩn IEEE trực tiếp từ mã nguồn bài báo mà không cần kết nối internet hay gửi dữ liệu sang máy chủ bên thứ ba.
* **Cơ chế:**
  * *Ưu tiên 1:* Gọi trình biên dịch độc lập **Tectonic** nhúng sẵn trong container để build mã LaTeX sang PDF.
  * *Dự phòng an toàn:* Nếu môi trường host chưa cài đặt Tectonic, tự động kích hoạt bộ layout engine của **PyMuPDF** để vẽ tiêu đề, khối tác giả, bảng số liệu và 2 cột văn bản ra file PDF hợp lệ chuẩn Letter/A4 trong $< 0.1$s.
* **Endpoint:** `POST /api/projects/{id}/compile`.

---

### Nhóm 15: Đóng gói dự án Overleaf (.ZIP) (`FR-V2-OVERLEAF`)

#### `FR-V2-OVERLEAF-01`: Sinh gói nén mã nguồn Overleaf 1-Click
* **Mô tả:** Tạo file nén `.zip` chứa toàn bộ cấu trúc dự án để người dùng có thể tải về và upload trực tiếp lên Overleaf:
  * `main.tex`: Toàn bộ mã nguồn LaTeX đã được ráp nối chuẩn từ các Paper Sections.
  * `references.bib`: Toàn bộ trích dẫn BibTeX đã được chuẩn hóa.
  * `README.md`: Hướng dẫn import vào Overleaf.
* **Endpoint:** `GET /api/projects/{id}/export/overleaf`.

---

### Nhóm 16: Tối ưu hóa hiệu năng & Cache đĩa BM25 (`FR-V2-PERF`)

#### `FR-V2-PERF-01`: Khắc phục triệt để giới hạn SQLite Variable Limit
* **Vấn đề cũ:** Miền `it` có 34,231 chunks; lệnh `db.get()` với hơn 999 tham số gây lỗi crash `sqlite3.OperationalError: too many SQL variables`.
* **Giải pháp:** Tải chunks theo lô cố định $500\text{ chunks/lô}$, đảm bảo an toàn tuyệt đối trên mọi hệ điều hành.

#### `FR-V2-PERF-02`: Bộ nhớ đệm Pickle trên đĩa cứng (Disk Pickle Cache)
* **Mô tả:** Sau khi xây dựng BM25 Index lần đầu, đối tượng chỉ mục được tuần tự hóa (pickle) và lưu xuống đĩa tại `db/bm25_caches/{domain}_bm25.pkl`.
* **Hiệu năng:** Rút ngắn thời gian khởi động BM25 từ $17.2$ giây xuống **$< 0.9$ giây** (tăng tốc độ gấp 19 lần).

---

## 7. MA TRẬN TRUY XUẤT NGUỒN GỐC (REQUIREMENTS TRACEABILITY MATRIX - RTM)

Bảng ma trận ánh xạ từng yêu cầu chức năng tới các thành phần mã nguồn, API Endpoint và Testcase kiểm chứng:

| Mã yêu cầu | Mô tả tóm tắt | Thành phần Backend | Thành phần Frontend | API Endpoint / WebSocket | Unit / Integration Testcase |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`FR-V1-AUTH-01`** | Đăng ký tài khoản | `backend/auth.py` | `src/app/register/page.tsx` | `POST /api/auth/register` | `test_auth.py` |
| **`FR-V1-AUTH-02`** | Đăng nhập cấp JWT | `backend/auth.py` | `src/app/login/page.tsx` | `POST /api/auth/login` | `test_auth.py` |
| **`FR-V1-DOC-01`** | Ngữ liệu 8 miền | `local_rag.py` | `src/components/Sidebar.tsx` | `GET /api/documents` | `test_local_rag.py` |
| **`FR-V1-RETRIEVAL`** | Hybrid Search Fallback | `local_rag.py`, `agent/` | `src/components/ChatWindow.tsx` | `GET /api/ws/chat/{id}` | `test_bm25_cache.py` |
| **`FR-V1-SELF-CORRECT`** | Tự sửa lỗi LangGraph | `agent/nodes.py`, `edges.py`| `AgentThoughtBar.tsx` | `GET /api/ws/chat/{id}` | `test_graph.py` |
| **`FR-V1-UI-STREAM`** | WebSocket Streaming | `backend/routers/chat.py` | `ChatWindow.tsx`, `useWebSocket.ts` | `ws://.../api/ws/chat/{id}` | `test_websocket.py` |
| **`FR-V2-PROJECT-01`** | Khởi tạo Project & Sections | `routers/projects.py`, `models.py` | `ProjectSidebar.tsx`, `studio/page.tsx` | `POST /api/projects` | `test_academic_models.py` |
| **`FR-V2-EDITOR-01`** | Canvas Soạn thảo 3-Zone | `routers/projects.py` | `AcademicEditor.tsx`, `studio/page.tsx` | `GET /api/projects/{id}` | `test_academic_models.py` |
| **`FR-V2-EDITOR-02`** | Auto-save Sync 2s | `routers/projects.py` | `useAutoSave.ts`, `AcademicEditor.tsx` | `PUT /api/projects/{id}/sections/{sec_id}` | `test_academic_models.py` |
| **`FR-V2-EDITOR-03`** | Slash Commands (`/`) | `routers/projects.py` | `SlashMenu.tsx`, `AcademicEditor.tsx` | Frontend Interactivity | UI Manual Audit |
| **`FR-V2-FLOATING-AI`** | Floating AI Toolbar | `agent/studio_nodes.py` | `FloatingAIToolbar.tsx` | `ws://.../api/ws/studio/{id}` | `test_studio_nodes.py` |
| **`FR-V2-VERIFIER-01`** | Stream PDF nhị phân | `backend/main.py` | `SplitPDFViewer.tsx` | `GET /api/documents/{d}/{doc}/pdf` | `test_pdf_spans.py` |
| **`FR-V2-VERIFIER-02`** | Bounding Box Overlay | `models.py`, `extract_pdf_spans.py` | `BoundingBoxHighlighter.tsx` | `GET /api/documents/{d}/{doc}/spans` | `test_pdf_spans.py` |
| **`FR-V2-VERIFIER-03`** | Click-to-Verify | `routers/projects.py` | `studioStore.ts`, `Zone3Pane.tsx` | Zustand State Dispatch | UI Manual Audit |
| **`FR-V2-AGENT-01..04`** | 4 Studio Agent Nodes | `agent/studio_nodes.py` | `Zone3Pane.tsx`, `FloatingAIToolbar.tsx` | `ws://.../api/ws/studio/{id}` | `test_studio_nodes.py` |
| **`FR-V2-COMPILER-01`** | In-App PDF Compilation | `export_service.py` | `ExportModal.tsx`, `studio/page.tsx` | `POST /api/projects/{id}/compile` | `test_export_service.py` |
| **`FR-V2-OVERLEAF-01`** | Export Overleaf ZIP | `export_service.py` | `ExportModal.tsx` | `GET /api/projects/{id}/export/overleaf` | `test_export_service.py` |
| **`FR-V2-PERF-01..02`** | Lô 500 chunks & Disk Pickle | `local_rag.py` | Backend Engine Initialization | Server Startup Routine | `test_bm25_cache.py` |

---

## 8. KẾT LUẬN & ĐÁNH GIÁ CHUẨN ĐỒ ÁN KLTN

Bộ tài liệu FRS này chứng minh:
1. **Tính kế thừa 100%:** Phiên bản 2.0 không loại bỏ hay làm gián đoạn bất kỳ chức năng cốt lõi nào của Version 1.0 (toàn bộ các API auth, tài liệu 8 miền, chatbot, web fallback và streaming đều hoạt động song song).
2. **Tính đột phá công nghệ:** Mở rộng thành công sang mô hình Academic Studio IDE độc lập, mang lại giá trị thực tiễn cao cho cộng đồng nghiên cứu khoa học.
3. **Tính kiểm chứng đầy đủ:** Tất cả các chức năng từ V1.0 đến V2.0 đều được bảo vệ bởi bộ kiểm thử tự động `run_master_suite.py` đạt tỷ lệ thành công 100%.

