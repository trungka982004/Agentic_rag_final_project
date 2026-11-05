# ACADEMIC STUDIO: BỘ TÀI LIỆU KẾ HOẠCH NÂNG CẤP TOÀN DIỆN PHẦN MỀM
## Tái thiết kế Hệ thống từ "Chatbot Tra cứu" thành "Academic IDE & Research Studio"

---

### MỤC LỤC TÀI LIỆU KỸ THUẬT

Bộ tài liệu này định nghĩa chi tiết toàn bộ kiến trúc phần mềm, cơ sở dữ liệu, backend, frontend, giao thức truyền thông và lộ trình triển khai để nâng cấp hệ thống Agentic RAG thành nền tảng nghiên cứu và soạn thảo khoa học khép kín:

| STT | Tài liệu chi tiết | Nội dung trọng tâm |
| :---: | :--- | :--- |
| **00** | [**00_OVERVIEW_AND_VISION.md**](./00_OVERVIEW_AND_VISION.md) | **Tầm nhìn sản phẩm & Kiến trúc tổng thể:** Chuyển đổi mô hình từ Chatbot sang Academic Studio 3-Zone (Zone 1: Quản lý dự án & Thư viện tri thức; Zone 2: Soạn thảo Canvas WYSIWYG; Zone 3: Kiểm chứng PDF & Bôi vàng trích dẫn). |
| **01** | [**01_DATABASE_ARCHITECTURE.md**](./01_DATABASE_ARCHITECTURE.md) | **Thiết kế Cơ sở Dữ liệu Mới:** Sơ đồ ERD, DDL SQL chuẩn cho PostgreSQL (`projects`, `paper_sections`, `project_references`, `document_spans`, `inline_citations`) và chiến lược migrate dữ liệu. |
| **02** | [**02_BACKEND_AND_RETRIEVAL.md**](./02_BACKEND_AND_RETRIEVAL.md) | **Tái thiết kế Backend & Retrieval Engine:** Khắc phục triệt để lỗi SQLite BM25 bằng Disk-based Pickle Caching; module trích xuất tọa độ Bounding Box PDF; các State Node học thuật mới của LangGraph; Engine biên dịch LaTeX nội bộ. |
| **03** | [**03_FRONTEND_AND_UX.md**](./03_FRONTEND_AND_UX.md) | **Thiết kế Giao diện & Trải nghiệm Người dùng:** Cấu trúc Component 3-Zone trên Next.js 14; tích hợp trình soạn thảo Novel.sh/Tiptap với Slash commands (`/math`, `/cite`, `/table`); bộ đọc PDF song song `react-pdf` với lớp phủ Bounding Box. |
| **04** | [**04_API_AND_WEBSOCKET_SPECS.md**](./04_API_AND_WEBSOCKET_SPECS.md) | **Đặc tả Giao diện Lập trình (API & WebSocket):** Chi tiết các RESTful Endpoints quản lý dự án, tài liệu, trích dẫn; cấu trúc Payload WebSocket Streaming cho tương tác Copilot thời gian thực. |
| **05** | [**05_IMPLEMENTATION_ROADMAP.md**](./05_IMPLEMENTATION_ROADMAP.md) | **Lộ trình Triển khai Kỹ thuật:** Phân bổ công việc chi tiết qua 5 Sprints (từ xử lý Core Engine/DB, tích hợp Canvas Editor, hoàn thiện Split-PDF Verifier, đến đóng gói Docker 1-Click). |
| **LOG** | [**PHASE_EXECUTION_AND_AUDIT_LOG.md**](./PHASE_EXECUTION_AND_AUDIT_LOG.md) | **Sổ tay Thi công & Rà soát Commit (Audit Tracker):** Quản lý chi tiết từng bước, checklist kiểm thử và 22 Commit chuẩn hóa qua 5 Feature Branches phục vụ nghiệm thu liên tục. |

---

### HƯỚNG DẪN ĐỌC TÀI LIỆU
* **Dành cho Tech Lead / Backend Engineer:** Bắt đầu từ [01_DATABASE_ARCHITECTURE.md](./01_DATABASE_ARCHITECTURE.md) và [02_BACKEND_AND_RETRIEVAL.md](./02_BACKEND_AND_RETRIEVAL.md).
* **Dành cho Frontend / Fullstack Engineer:** Tập trung vào [03_FRONTEND_AND_UX.md](./03_FRONTEND_AND_UX.md) và [04_API_AND_WEBSOCKET_SPECS.md](./04_API_AND_WEBSOCKET_SPECS.md).
* **Dành cho Quản lý dự án (PM / Scrum Master):** Theo dõi tiến độ tại [05_IMPLEMENTATION_ROADMAP.md](./05_IMPLEMENTATION_ROADMAP.md).

