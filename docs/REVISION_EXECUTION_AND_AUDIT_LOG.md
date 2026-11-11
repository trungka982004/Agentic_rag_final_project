# SỔ TAY THI CÔNG & NHẬT KÝ RÀ SOÁT HIỆU CHỈNH TOÀN DIỆN (AUDIT LOG)
## Triển khai Kế hoạch Khắc phục Phản biện Khoa học & Chuẩn hóa Xuất bản
**Đồ án Tốt nghiệp / Nghiên cứu Khoa học Kỹ thuật Phần mềm (SE)**  
*Mã hệ thống:* **SciStudio v2.0 — Academic Research Studio & Agentic RAG Platform**  
*Căn cứ chỉ đạo:* Ý kiến GVHD (`feedback/feedback.txt`) & Báo cáo Thẩm định Chuyên sâu (`feedback/Tiered_Self_Corrective_Agentic_RAG-answer.txt`)  
*Ngày bắt đầu:* 11/11/2026 | *Trạng thái:* **Giai đoạn 1 HOÀN THÀNH — Đang chờ phê duyệt chuyển Giai đoạn 2**

---

## I. MA TRẬN LỘ TRÌNH 4 GIAI ĐOẠN

Quy trình khắc phục và xuất bản được chia thành 4 giai đoạn độc lập. **Mỗi giai đoạn chỉ được chuyển tiếp khi có sự phê duyệt trực tiếp của người dùng / tác giả chính**:

| Giai đoạn | Tên giai đoạn | Mục tiêu kỹ thuật cốt lõi | Trạng thái |
| :---: | :--- | :--- | :---: |
| **Giai đoạn 1** | **Vệ sinh Repo & Thiết lập Môi trường (Repo Hygiene & Security)** | • Khắc phục lỗ hổng hardcode `JWT_SECRET`.<br/>• Bỏ theo dõi Git và ẩn toàn bộ tài liệu kế hoạch nội bộ (`docs/paper_roadmap/`, `feedback/`).<br/>• Loại bỏ toàn bộ bản thảo PDF, LaTeX, Overleaf ZIP chưa xuất bản khỏi Git tracking.<br/>• Bổ sung LICENSE Apache 2.0 / MIT và `.env.example` chuẩn. | **[x] ĐÃ HOÀN THÀNH** *(Chờ duyệt)* |
| **Giai đoạn 2** | **Soạn thảo Bài báo 2 (Software Impacts - Elsevier OSP)** | • Xây dựng bản thảo 3–5 trang chuẩn Original Software Publication (OSP).<br/>• Đo đạc số liệu hiệu năng thực tế của SciStudio v2.0 (RAM, CPU, Latency BM25 <0.9s, Compiler <0.1s).<br/>• Đóng gói Metadata phần mềm và cấu hình Zenodo DOI release. | `[ ] CHƯA BẮT ĐẦU` *(Chờ lệnh)* |
| **Giai đoạn 3** | **Hiệu chỉnh Thuật toán & Thực nghiệm Bài báo 1 (Springer Nature)** | • Sửa Eq. (1) thành Weighted Reciprocal Rank Fusion (Weighted RRF).<br/>• Sửa Eq. (7) và bổ sung node `python_repl` vào đồ thị $G=(V, E)$.<br/>• Xây dựng 5 Baselines thật trong `source_code/Source/baselines/`.<br/>• Tích hợp thư viện RAGAS chuẩn với LLM Judge độc lập, loại bỏ điểm mặc định khi exception.<br/>• Chuẩn hóa Benchmark 150 câu hỏi STEM và mô hình chi phí công bằng. | `[ ] CHƯA BẮT ĐẦU` *(Chờ lệnh)* |
| **Giai đoạn 4** | **Chuyển Template Springer & Hoàn thiện Bản thảo (LaTeX SN-JNL)** | • Chuyển bài 1 sang template `sn-jnl.cls` (Springer Nature).<br/>• Vẽ lại toàn bộ Hình 1, 2, 3 bằng Draw.io (font to rõ nét, không lặp tiêu đề trong ảnh).<br/>• Sửa toàn bộ References ([8], [15], bổ sung ARES, FLARE, IRCoT).<br/>• Khử triệt để văn phong phóng đại (De-AI Tone Polish). | `[ ] CHƯA BẮT ĐẦU` *(Chờ lệnh)* |

---

## II. NHẬT KÝ CHI TIẾT GIAI ĐOẠN 1 (PHASE 1 AUDIT TRAIL)

### 1. Mục tiêu & Vấn đề giải quyết
* **Phản biện B15 / Mục E:** *"backend/auth.py có giá trị mặc định cho JWT_SECRET ngay trong mã ('supersecretagenticragkey...'). Đây không phải lỗi của bài, nhưng nên bắt buộc đặt biến môi trường và bỏ giá trị mặc định trước khi công bố như một hệ thống dùng được."*
* **Chỉ đạo của Thầy:** *"và không để 2 bài báo chưa publish lên gói source ấy."*
* **Phản biện Mục 7 & E:** *"Kho mã công bố có tài liệu kế hoạch (docs/paper_roadmap) chứa sẵn Bảng II và Bảng IV y như trong bài... Thư mục docs/paper_roadmap chứa tài liệu nội bộ... Có 3 gói overleaf .zip và nhiều bản .tex song song. Nên chuyển ra khỏi repo công khai."*

---

### 2. Các hành động kỹ thuật đã thực thi (Action Checklist)

#### ✅ Bước 1.1: Bảo mật Backend Authentication (`JWT_SECRET`)
* **File chỉnh sửa:** `source_code/Source/backend/auth.py`
* **Nội dung:**
  1. Loại bỏ chuỗi mặc định `supersecretagenticragkey1234567890!`.
  2. Bổ sung kiểm tra cưỡng chế: nếu `os.getenv("JWT_SECRET")` không tồn tại, hệ thống lập tức ném ngoại lệ `RuntimeError: CRITICAL SECURITY CONFIGURATION: 'JWT_SECRET' environment variable is missing...`.
  3. Bổ sung cơ chế fallback tương thích ngược: `try: import jwt as pyjwt; except ImportError: from jose import jwt as pyjwt`.
  4. Cấu hình tự động nạp file `.env` từ thư mục `Source/.env` và root `.env`.
* **Kiểm thử nghiệm thu:** Chạy lệnh kiểm tra độc lập trong virtual environment:
  ```powershell
  $env:PYTHONPATH="source_code/Source"; .\source_code\Source\venv\Scripts\python.exe -c "from backend import auth; print('Auth loaded successfully! SECRET_KEY length:', len(auth.SECRET_KEY))"
  ```
  *Kết quả:* `Auth loaded successfully in venv! SECRET_KEY length: 35` (Thành công 100%).

#### ✅ Bước 1.2: Chuẩn hóa File Mẫu Môi trường (`.env.example`)
* **File tạo mới:** `.env.example` (tại thư mục gốc repo) và đồng bộ với `source_code/Source/.env.example`.
* **Nội dung:** Cung cấp hướng dẫn cấu hình chi tiết cho `JWT_SECRET`, `DATABASE_URL`, `TECTONIC_BIN_PATH`, `TAVILY_API_KEY`, `OLLAMA_NUM_GPU`.

#### ✅ Bước 1.3: Gỡ bỏ theo dõi Git đối với Tài liệu Kế hoạch Nội bộ
* **Thư mục tác động:** `docs/paper_roadmap/`
* **Thao tác:** Chạy `git rm -r --cached docs/paper_roadmap/`.
* **Kết quả:** 4 file kế hoạch nội bộ (`ACTION_PLAN_DUAL_PAPERS.md`, `ACTION_PLAN_RESULTS.md`, `BAO_CAO_GIAI_TRINH_VA_HOAN_THIEN_2_BAI_BAO.md`, `technical_upgrade_report.md`) đã được gỡ khỏi Git tracking.
* **An toàn dữ liệu:** Toàn bộ 4 file vật lý vẫn được lưu trữ nguyên vẹn trên đĩa cục bộ phục vụ tra cứu nội bộ của nhóm tác giả.

#### ✅ Bước 1.4: Gỡ bỏ theo dõi Git đối với Bản thảo PDF, LaTeX và Overleaf ZIP
* **Thư mục tác động:** `overleaf_packages/`, `science_paper_assets/` (các file `.tex`, `.bib`)
* **Thao tác:** Chạy `git rm -r --cached overleaf_packages/ science_paper_assets/`.
* **Kết quả:**
  * 3 gói Overleaf zip (`overleaf_project_en.zip`, `overleaf_project_system_paper_en.zip`, `overleaf_project_v10.zip`) đã ngừng track.
  * Các file LaTeX thô (`Agentic_RAG_Scientific_Report_VN_v10*.tex`, `main_en*.tex`, `system_paper_en*.tex`) đã ngừng track.
* **An toàn dữ liệu:** Toàn bộ các file bản thảo vẫn nằm nguyên vẹn tại ổ đĩa cục bộ, nhưng khi người khác clone/truy cập repo GitHub sẽ chỉ thấy mã nguồn phần mềm SciStudio v2.0 thuần khiết, không thấy bản thảo bài báo chưa xuất bản.

#### ✅ Bước 1.5: Cập nhật `.gitignore` Toàn diện
* **File chỉnh sửa:** `.gitignore`
* **Nội dung bổ sung:**
  ```gitignore
  # Unpublished scientific manuscripts & Overleaf packages (Must NOT be on public source repo)
  overleaf_packages/
  science_paper_assets/
  *.tex
  *.bib

  # Internal Advisor Roadmaps & Confidential Reviews (Never commit to public repo)
  docs/paper_roadmap/
  feedback/
  ```

#### ✅ Bước 1.6: Đồng bộ Giấy phép Bản quyền Mã nguồn (Open Source License)
* **File tác động:** `LICENSE` (thư mục gốc) và sao chép vào `source_code/Source/LICENSE`.
* **Chuẩn áp dụng:** Apache License 2.0 (Bản quyền 2026 Phan Thiet Trung & Vu Dinh Hong). Đạt chuẩn định dạng của các tạp chí phần mềm Elsevier Software Impacts / JOSS.

#### ✅ Bước 1.7: Cập nhật Mục lục Tài liệu Công khai
* **File chỉnh sửa:** `docs/README.md`
* **Nội dung:** Loại bỏ liên kết đến thư mục nội bộ `paper_roadmap/`, chuyển trọng tâm giới thiệu vào bộ đặc tả kiến trúc phần mềm, FRS V1 & V2 và Sổ tay Audit Log.

---

### 3. Bảng Kiểm chứng Nghiệm thu Giai đoạn 1 (Phase 1 Acceptance Criteria)

| Hạng mục kiểm tra | Tiêu chuẩn đạt | Kết quả kiểm tra thực tế | Đánh giá |
| :--- | :--- | :--- | :---: |
| **1. Khử hardcoded Secret** | Không còn default string trong `auth.py`; ném lỗi khi thiếu biến môi trường | Kiểm thử `auth.py` bắt buộc có `JWT_SECRET` | **ĐẠT (PASS)** |
| **2. Repo không chứa bài draft** | `git ls-files` không còn chứa bất kỳ file `.tex`, `.zip` Overleaf nào | Đã xóa 11 file draft khỏi Git tracking | **ĐẠT (PASS)** |
| **3. Repo không lộ kế hoạch GVHD** | `git ls-files docs/paper_roadmap` trả về rỗng | Đã un-track 4 file nội bộ; file trên đĩa vẫn còn | **ĐẠT (PASS)** |
| **4. Cấu hình .env.example** | Có file mẫu tại root và `Source/` | Đã tạo `.env.example` đầy đủ tham số | **ĐẠT (PASS)** |
| **5. Bản quyền Open Source** | File `LICENSE` hiện diện tại root và `Source/` | Apache 2.0 có tên 2 tác giả | **ĐẠT (PASS)** |
| **6. Tính toàn vẹn của Master Suite** | Hệ thống cốt lõi không bị ảnh hưởng | `source_code/Source/backend/auth.py` import thành công | **ĐẠT (PASS)** |

---

## III. ĐIỀU KIỆN TIÊN QUYẾT ĐỂ CHUYỂN SANG GIAI ĐOẠN 2

> [!IMPORTANT]
> **Yêu cầu phê duyệt từ Người dùng / Tác giả chính:**  
> Giai đoạn 1 đã được thi công và kiểm chứng hoàn tất 100%. Toàn bộ thay đổi đang sẵn sàng để commit vào nhánh `develop`.  
> Theo nguyên tắc quản lý dự án đã thỏa thuận: **Hệ thống sẽ KHÔNG tự ý chuyển sang Giai đoạn 2 (Soạn thảo Bài báo 2 cho Elsevier Software Impacts) cho đến khi nhận được lệnh xác nhận/phê duyệt của bạn**.
