# SỔ TAY THEO DÕI THI CÔNG & RÀ SOÁT COMMIT THEO TỪNG PHASE
## Master Execution & Continuous Audit Tracker — Academic Studio Upgrade

> **Mục đích tài liệu:** Tài liệu này được thiết lập làm "Bảng điều khiển kiểm soát chất lượng" (Quality & Audit Dashboard) theo dõi tiến độ thi công thực tế theo từng bước của 5 Phase nâng cấp, quản lý chặt chẽ từng Commit trên 5 Feature Branches để đảm bảo tính minh bạch, chuẩn mực Git công nghiệp và thuận tiện rà soát nghiệm thu liên tục.

---

### I. SƠ ĐỒ ĐIỀU HƯỚNG NHÁNH (GIT BRANCH TOPOLOGY)

```text
[origin/main] ───────► v1.0.0 (Release Ổn định Baseline)
       │
[origin/develop] ────► Nhánh tích hợp chính (Active Working Base)
       │
       ├──► [feature/core-db-retrieval]   (Phase 1: Sprint 1 - Core Engine & DB)
       ├──► [feature/canvas-editor]        (Phase 2: Sprint 2 - Academic Canvas)
       ├──► [feature/split-pdf-verifier]   (Phase 3: Sprint 3 - Split-PDF Verifier)
       ├──► [feature/agent-studio-nodes]   (Phase 4: Sprint 4 - LangGraph Nodes)
       └──► [feature/export-compile-docker](Phase 5: Sprint 5 - Compiler & Docker)
```

---

### II. NGUYÊN TẮC QUẢN TRỊ COMMIT CHUẨN MỰC (COMMIT PROTOCOL)

1. **Chuẩn đặt tên Commit (Conventional Commits):**
   `<type>(<scope>): <subject>`
   * `feat`: Thêm tính năng mới.
   * `fix`: Sửa lỗi kỹ thuật (bug fix).
   * `refactor`: Tái cấu trúc code nhưng không đổi logic bên ngoài.
   * `chore`: Cấu hình build, dependencies, Docker, script phụ trợ.
   * `test`: Bổ sung kiểm thử đơn vị hoặc tích hợp.
   * `docs`: Cập nhật tài liệu kỹ thuật.
2. **Quy tắc Atomic Commit:** Mỗi commit giải quyết trọn vẹn **1 vấn đề kỹ thuật duy nhất**. Không gom nhiều module khác nhau vào chung một commit.
3. **Cơ chế rà soát:** Sau khi hoàn thành một commit, điền mã Hash (`git rev-parse --short HEAD`), cập nhật trạng thái `[x] DONE` và ngày thực hiện vào bảng dưới đây.

---

### III. BẢNG THEO DÕI THI CÔNG CHI TIẾT THEO 5 PHASES

---

#### PHASE 1: CORE ENGINE & DATABASE FOUNDATION
* **Nhánh làm việc:** `feature/core-db-retrieval`
* **Lệnh kích hoạt nhánh:** `git checkout feature/core-db-retrieval`
* **Mục tiêu kỹ thuật:** Khắc phục triệt để lỗi SQLite của BM25, tạo schema PostgreSQL mới cho bài báo và trích xuất Bounding Box của 618 bài báo PDF.

##### 1. Danh sách Commit Audit Log:
| STT | Commit Type & Scope | Tiêu đề Commit Chuẩn | Trạng thái | Commit Hash | Ngày rà soát | Người phụ trách |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **C1.1** | `fix(retrieval)` | `fix(retrieval): fix sqlite variable limit in bm25 with batching and disk pickle cache` | `[x] DONE` | `edb1653` | 2026-11-05 | Backend Dev |
| **C1.2** | `feat(database)` | `feat(database): define sqlalchemy models and alembic migrations for academic projects` | `[x] DONE` | `7e63cfb` | 2026-11-05 | DB / Backend |
| **C1.3** | `feat(ingestion)` | `feat(ingestion): extract text bounding boxes from 618 pdfs using pymupdf` | `[x] DONE` | `bf18ea7` | 2026-11-05 | Data / RAG Dev |
| **C1.4** | `test(core)` | `test(core): add unit tests for bm25 cache retrieval and span coordinate accuracy` | `[x] DONE` | `971472d` | 2026-11-05 | QA / Dev |

##### 2. Các bước thực hiện chi tiết (Step-by-step checklist):
* [x] **Bước 1.1:** Tối ưu `source_code/Source/local_rag.py`: Áp dụng chunk loading theo lô $500\text{ chunks}$ và lưu cache đĩa vào `db/bm25_caches/{domain}_bm25.pkl`.
* [x] **Bước 1.2:** Kiểm tra truy vấn domain `it` (34,231 chunks) và viết unit test `test_bm25_cache.py` chứng minh lỗi SQLite `too many SQL variables` đã triệt tiêu 100%.
* [x] **Bước 1.3:** Định nghĩa các models SQLAlchemy trong `backend/models.py` và `backend/schemas.py`: `Project`, `PaperSection`, `ProjectReference`, `DocumentSpan`, `InlineCitation`. Đã migrate và kiểm thử vòng đời thành công trên PostgreSQL (`test_academic_models.py`).
* [x] **Bước 1.4:** Viết script `scripts/extract_pdf_spans.py` dùng `fitz` (`PyMuPDF`) quét 618 PDFs trong `data/raw/`, tính toán tọa độ chuẩn hóa $(x_0, y_0, x_1, y_1)$ và nạp vào bảng `document_spans`.
* [x] **Bước 1.5:** Chạy test kiểm thử tốc độ khởi động BM25 đạt $< 0.1$s và số lượng spans nạp thành công đạt $\ge 98\%$. Chạy master test suite `run_core_suite.py` hoàn thành $4/4$ tests xuất sắc.

---

#### PHASE 2: ACADEMIC CANVAS & TRÌNH SOẠN THẢO WYSIWYG
* **Nhánh làm việc:** `feature/canvas-editor`
* **Lệnh kích hoạt nhánh:** `git checkout feature/canvas-editor`
* **Mục tiêu kỹ thuật:** Thay thế giao diện chat đơn bằng Academic Canvas (Tiptap / Novel.sh) hỗ trợ KaTeX, công thức toán và menu lệnh Slash (`/`).

##### 1. Danh sách Commit Audit Log:
| STT | Commit Type & Scope | Tiêu đề Commit Chuẩn | Trạng thái | Commit Hash | Ngày rà soát | Người phụ trách |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **C2.1** | `feat(editor)` | `feat(editor): integrate tiptap wysiwyg canvas editor with auto-save sync` | `[ ] PENDING` | - | - | Frontend Dev |
| **C2.2** | `feat(editor)` | `feat(editor): implement slash commands for math blocks and academic tables` | `[ ] PENDING` | - | - | Frontend Dev |
| **C2.3** | `feat(ui)` | `feat(ui): add floating ai toolbar for in-place tone refinement and evidence search` | `[ ] PENDING` | - | - | Frontend Dev |
| **C2.4** | `refactor(frontend)` | `refactor(frontend): reorganize studio page layout to 3-zone topology` | `[ ] PENDING` | - | - | Frontend Dev |

##### 2. Các bước thực hiện chi tiết (Step-by-step checklist):
* [ ] **Bước 2.1:** Cài đặt các thư viện `@tiptap/react`, `@tiptap/pm`, `@tiptap/extension-mathematics` (KaTeX), `@tiptap/extension-table` vào `frontend/`.
* [ ] **Bước 2.2:** Xây dựng component `frontend/src/components/studio/Zone2_Canvas/AcademicEditor.tsx`.
* [ ] **Bước 2.3:** Thiết lập hook `useAutoSave` tự động đẩy nội dung Markdown cập nhật về endpoint `PUT /api/projects/{id}/sections/{section_id}` sau $2$s không gõ.
* [ ] **Bước 2.4:** Hiện thực hóa Slash Command: khi người dùng gõ `/math` thì sinh khối KaTeX; gõ `/table` thì mở bảng so sánh; gõ `/cite` thì mở popup gợi ý trích dẫn.
* [ ] **Bước 2.5:** Xây dựng `FloatingAIToolbar.tsx` hiện ra khi bôi đen văn bản để gọi tính năng chuốt câu hoặc tìm bằng chứng.

---

#### PHASE 3: SPLIT-SCREEN PDF VERIFIER & CLICK-TO-VERIFY
* **Nhánh làm việc:** `feature/split-pdf-verifier`
* **Lệnh kích hoạt nhánh:** `git checkout feature/split-pdf-verifier`
* **Mục tiêu kỹ thuật:** Xây dựng Zone 3 nhúng `react-pdf`, hỗ trợ click vào thẻ `\cite{}` trên Canvas thì PDF gốc tự mở và bôi vàng câu văn gốc.

##### 1. Danh sách Commit Audit Log:
| STT | Commit Type & Scope | Tiêu đề Commit Chuẩn | Trạng thái | Commit Hash | Ngày rà soát | Người phụ trách |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **C3.1** | `feat(pdf-viewer)` | `feat(pdf-viewer): embed react-pdf viewer in zone 3 with high-performance stream` | `[ ] PENDING` | - | - | Fullstack Dev |
| **C3.2** | `feat(pdf-viewer)` | `feat(pdf-viewer): build bounding-box highlight overlay for grounded text` | `[ ] PENDING` | - | - | Frontend Dev |
| **C3.3** | `feat(sync)` | `feat(sync): implement click-to-verify interaction linking canvas citations to pdf viewer` | `[ ] PENDING` | - | - | Frontend Dev |
| **C3.4** | `style(ui)` | `style(ui): ensure responsive split-screen panel resizing with zustand state` | `[ ] PENDING` | - | - | Frontend Dev |

##### 2. Các bước thực hiện chi tiết (Step-by-step checklist):
* [ ] **Bước 3.1:** Thêm endpoint Backend `GET /api/documents/{domain}/{doc_name}/pdf` phục vụ streaming file nhị phân.
* [ ] **Bước 3.2:** Tích hợp `react-pdf` trong `frontend/src/components/studio/Zone3_Verifier/SplitPDFViewer.tsx`.
* [ ] **Bước 3.3:** Xây dựng lớp phủ `BoundingBoxHighlighter.tsx` render khung chữ nhật phát sáng đè lên tọa độ $(x_0, y_0, x_1, y_1)$ của trang PDF tương ứng.
* [ ] **Bước 3.4:** Kết nối tương tác qua Zustand Store (`studioStore.ts`): khi user click thẻ trích dẫn `\cite{key}` $\rightarrow$ State cập nhật `activeCitation` $\rightarrow$ Zone 3 tự cuộn trang và vẽ khung vàng trong $< 1.2$s.

---

#### PHASE 4: ACADEMIC AGENT NODES & WEBSOCKET COPILOT
* **Nhánh làm việc:** `feature/agent-studio-nodes`
* **Lệnh kích hoạt nhánh:** `git checkout feature/agent-studio-nodes`
* **Mục tiêu kỹ thuật:** Mở rộng đồ thị LangGraph với 4 State Nodes phục vụ trực tiếp việc viết bài và đồng bộ WebSocket streaming.

##### 1. Danh sách Commit Audit Log:
| STT | Commit Type & Scope | Tiêu đề Commit Chuẩn | Trạng thái | Commit Hash | Ngày rà soát | Người phụ trách |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **C4.1** | `feat(agent)` | `feat(agent): implement literature review matrix node for multi-paper comparison` | `[ ] PENDING` | - | - | AI / Agent Dev |
| **C4.2** | `feat(agent)` | `feat(agent): implement smart in-text citation suggest node with bibtex extractor` | `[ ] PENDING` | - | - | AI / Agent Dev |
| **C4.3** | `feat(agent)` | `feat(agent): implement academic tone polish and grammar refinement node` | `[ ] PENDING` | - | - | AI / Agent Dev |
| **C4.4** | `feat(agent)` | `feat(agent): implement reviewer-2 grounding auditor node for hallucination detection` | `[ ] PENDING` | - | - | AI / Agent Dev |
| **C4.5** | `feat(api)` | `feat(api): expand websocket endpoint /api/ws/studio for real-time canvas copilot` | `[ ] PENDING` | - | - | Backend Dev |

##### 2. Các bước thực hiện chi tiết (Step-by-step checklist):
* [ ] **Bước 4.1:** Định nghĩa `AcademicStudioState` trong `agent/state.py` chứa `draft_content`, `target_papers`, `citations`.
* [ ] **Bước 4.2:** Viết hàm `review_matrix_node` đọc nhiều tài liệu và xuất bảng so sánh định dạng LaTeX `booktabs`.
* [ ] **Bước 4.3:** Viết hàm `citation_suggest_node` phân tích câu khẳng định và đối soát tìm bài báo tương ứng trong 618 bài.
* [ ] **Bước 4.4:** Viết hàm `academic_polish_node` dùng prompt học thuật chuyên sâu trên Qwen2.5 7B.
* [ ] **Bước 4.5:** Viết hàm `integrity_auditor_node` quét câu văn không có chứng cứ và gắn nhãn cảnh báo.
* [ ] **Bước 4.6:** Nâng cấp WebSocket router tại `backend/routers/studio.py` stream trực tiếp phản hồi về Canvas.

---

#### PHASE 5: COMPILER, OVERLEAF EXPORT & DOCKER PACKAGING
* **Nhánh làm việc:** `feature/export-compile-docker`
* **Lệnh kích hoạt nhánh:** `git checkout feature/export-compile-docker`
* **Mục tiêu kỹ thuật:** Biên dịch PDF tại chỗ không phụ thuộc bên thứ ba, đóng gói Overleaf ZIP và hoàn thiện Docker 1-Click.

##### 1. Danh sách Commit Audit Log:
| STT | Commit Type & Scope | Tiêu đề Commit Chuẩn | Trạng thái | Commit Hash | Ngày rà soát | Người phụ trách |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **C5.1** | `feat(compiler)` | `feat(compiler): integrate local tectonic engine for 1-click in-app pdf compilation` | `[ ] PENDING` | - | - | DevOps / Backend |
| **C5.2** | `feat(export)` | `feat(export): add 1-click overleaf zip packager with bibtex and assets` | `[ ] PENDING` | - | - | Backend Dev |
| **C5.3** | `chore(docker)` | `chore(docker): update docker-compose and dockerfile with multi-stage build` | `[ ] PENDING` | - | - | DevOps Dev |
| **C5.4** | `docs(spec)` | `docs(spec): finalize technical upgrade blueprint and api documentation` | `[ ] PENDING` | - | - | Tech Lead |
| **C5.5** | `chore(release)` | `chore(release): bump version to v2.0.0-academic-studio` | `[ ] PENDING` | - | - | Tech Lead |

##### 2. Các bước thực hiện chi tiết (Step-by-step checklist):
* [ ] **Bước 5.1:** Cài đặt Tectonic CLI trong container Backend; viết endpoint `POST /api/projects/{id}/compile` ghép nối các sections và trả về file `main.pdf`.
* [ ] **Bước 5.2:** Viết endpoint `GET /api/projects/{id}/export-overleaf` tự động đóng gói `main.tex`, `references.bib`, `IEEEtran.cls` và thư mục `figures/` thành tệp `.zip`.
* [ ] **Bước 5.3:** Cập nhật `docker-compose.yml` đảm bảo cả 3 container (`postgres`, `backend`, `frontend`) khởi chạy đồng bộ với 1 lệnh `docker compose up -d`.
* [ ] **Bước 5.4:** Chạy kiểm thử toàn trình (End-to-End Test): Tạo bài báo mới $\rightarrow$ Soạn thảo $\rightarrow$ Gợi ý trích dẫn $\rightarrow$ Đối soát PDF $\rightarrow$ Biên dịch PDF thành công.

---

### IV. HƯỚNG DẪN THAO TÁC GIT & QUY TRÌNH HỢP NHẤT (MERGE PROTOCOL)

Khi hoàn thành toàn bộ commit trong một Phase, thực hiện quy trình Review & Merge vào nhánh `develop`:

```bash
# 1. Đảm bảo toàn bộ thay đổi đã commit sạch sẽ
git status

# 2. Chuyển về nhánh develop và cập nhật mới nhất
git checkout develop
git pull origin develop

# 3. Merge nhánh feature vào develop (tạo merge commit rõ ràng)
git merge --no-ff feature/core-db-retrieval -m "Merge branch 'feature/core-db-retrieval' into develop (Phase 1 Complete)"

# 4. Khi hoàn thành toàn bộ 5 Phase, merge develop vào main và gắn thẻ release
git checkout main
git merge --no-ff develop -m "Release v2.0.0: Academic Studio Platform"
git tag -a v2.0.0-academic-studio -m "Official Release of Academic Studio IDE"
```

---
*Sổ tay theo dõi tiến độ thi công đã sẵn sàng. Cập nhật bảng này sau mỗi commit để kiểm soát chất lượng 100%.*

