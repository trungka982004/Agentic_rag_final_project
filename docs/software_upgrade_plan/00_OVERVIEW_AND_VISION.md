# 00. TỔNG QUAN SẢN PHẨM & TẦM NHÌN KIẾN TRÚC
## Chuyển dịch từ "Single-column Chatbot" sang "Academic IDE & Research Studio"

---

### 1. BỐI CẢNH & ĐỘNG LỰC TÁI THIẾT KẾ

Hệ thống hiện tại vận hành theo mô hình **Single-column Chatbot** (FastAPI + WebSocket + Next.js UI). Dù đã giải quyết được việc phân chia 8 miền tri thức (618 PDFs) và cơ chế tự sửa lỗi phân tầng (LangGraph), mô hình này bộc lộ những rào cản UX nghiêm trọng đối với đối tượng người dùng mục tiêu (Nhà nghiên cứu, Giảng viên, Sinh viên làm luận văn/bài báo):

| Đặc điểm | Mô hình Hiện tại (Chatbot) | Hạn chế thực tế đối với Nhà nghiên cứu |
| :--- | :--- | :--- |
| **Bản chất giao diện** | Bong bóng hội thoại hỏi - đáp dạng tuyến tính. | Không thể trực tiếp viết bài; phải liên tục copy-paste văn bản ra Word hoặc Overleaf. |
| **Tính xác thực trích dẫn** | Báo `Citations (0)` hoặc chỉ liệt kê tên file PDF đơn thuần. | Không thể kiểm chứng nhanh xem trích dẫn đó nằm ở trang mấy, câu văn nào; nguy cơ bị đạo văn hoặc ảo giác. |
| **Định dạng đầu ra** | Markdown thô hoặc xuất sang Google Docs / Google Sheets. | Không phù hợp với cộng đồng nghiên cứu STEM/CS (vốn sử dụng 100% LaTeX, BibTeX và Overleaf). |
| **Sự phụ thuộc công cụ** | Người dùng vẫn phải mở Zotero (quản lý file), Overleaf (soạn thảo), Grammarly (chuốt văn phong). | Phân mảnh luồng công việc (context switching), tốn nhiều thời gian chuyển đổi định dạng. |

---

### 2. TẦM NHÌN SẢN PHẨM: "ALL-IN-ONE ACADEMIC STUDIO"

Mục tiêu cốt lõi của bản nâng cấp là biến hệ thống thành một **Môi trường Phát triển Tích hợp Học thuật (Academic IDE)** khép kín 100%, tích hợp trọn vẹn vòng đời nghiên cứu:

$$\text{Khảo sát \& Tìm Gap} \longrightarrow \text{Lập Blueprint} \longrightarrow \text{Soạn thảo có Căn cứ} \longrightarrow \text{Chuốt Văn phong \& LaTeX} \longrightarrow \text{Audit \& Xuất bản}$$

#### 3 Trụ Cột Triết Lý:
1. **Local-First & Quyền riêng tư Tuyệt đối (Zero Cloud Leak):**
   * Mọi bản thảo, ý tưởng nghiên cứu, dữ liệu thí nghiệm và trích dẫn được lưu trữ và xử lý hoàn toàn cục bộ trên máy chủ nội bộ thông qua **Qwen2.5 7B** và **bge-m3**. Không bao giờ rò rỉ dữ liệu nghiên cứu chưa công bố lên bất kỳ bên thứ ba nào.
2. **Căn cứ Học thuật Tuyệt đối (100% Grounded & Traceable):**
   * Triệt tiêu hoàn toàn hiện tượng trích dẫn ma (ghost citation). Bất kỳ câu khẳng định nào trong bài báo đều có thể click vào để mở đúng file PDF và bôi vàng câu văn gốc trong vòng 1 giây.
3. **Môi trường Soạn thảo Tích hợp (Canvas as Core):**
   * Bản thảo bài báo là trung tâm của màn hình làm việc. Trợ lý AI đóng vai trò là một đồng tác giả (Co-author) thông minh, hỗ trợ viết tiếp, tra cứu số liệu, chuốt câu từ và sinh công thức toán/bảng biểu tại chỗ.

---

### 3. KIẾN TRÚC PHÂN VÙNG MỚI: 3-ZONE ACADEMIC WORKSPACE

Giao diện làm việc chính của ứng dụng được tổ chức thành 3 phân vùng tương tác song song (Split-View):

```
+------------------------------------------------------------------------------------------------------------------------+
| [LOGO] ACADEMIC STUDIO  |  Project: "Adaptive Multi-Domain Agentic RAG"               [Compile PDF] [Export Overleaf]  |
+------------------------------------+-------------------------------------------+---------------------------------------+
| ZONE 1: KNOWLEDGE & PROJECT HUB    | ZONE 2: ACADEMIC CANVAS                   | ZONE 3: EVIDENCE & VERIFIER           |
| (Quản lý dự án & Kho 8 miền)       | (Môi trường soạn thảo bài báo chính)      | (Kiểm chứng PDF & Đọc tài liệu gốc)   |
|                                    |                                           |                                       |
| [Tab 1: Paper Structure]           | Section: 1. Introduction                  | [Tab 1: Original PDF] [Tab 2: Audit]  |
|  ├── 00_Abstract.tex               |                                           |                                       |
|  ├── 01_Introduction.tex  <Active> | Retrieval-Augmented Generation (RAG)      | +-----------------------------------+ |
|  ├── 02_Related_Work.tex           | has become a foundational paradigm...     | | BGE-M3 Technical Report (Page 3)  | |
|  ├── 03_Methodology.tex            | \cite{chen2024bge}. However, cross-domain | |                                   | |
|  ├── 04_Experiments.tex            | semantic confusion degrades precision     | | "...bge-m3 supports multi-vector  | |
|  └── references.bib                | in multi-disciplinary scenarios.          | | retrieval and cross-lingual..."   | |
|                                    |                                           | | [HIGHLIGHTED IN YELLOW BOX]       | |
| [Tab 2: 8-Domain KB (618 PDFs)]    | [ + Generate Comparison Table ]           | +-----------------------------------+ |
|  ├── CS/IT (130 files)             | [ /math: Insert KaTeX Formula ]           | Grounding Integrity Status:           |
|  ├── Mathematics (97 files)        | [ Inline AI: Make Academic Tone ]         | • [v] Claim 1: Verified (Page 3)      |
|  └── Electronics (121 files)       |                                           | • [!] Claim 2: Missing Citation       |
+------------------------------------+-------------------------------------------+---------------------------------------+
| Status: Qwen2.5 7B Ready (Local VRAM) | Word Count: 3,420 words | Citations: 19 Verified | Compile Status: Passed (0 err) |
+------------------------------------------------------------------------------------------------------------------------+
```

---

### 4. SỰ KHÁC BIỆT KỸ THUẬT: HIỆN TẠI VS. NÂNG CẤP

| Tiêu chí Kỹ thuật | Trạng thái Hiện tại (v1.0) | Trạng thái Sau Nâng cấp (v2.0 - Studio) |
| :--- | :--- | :--- |
| **Giao diện cốt lõi** | Danh sách tin nhắn chat dạng bong bóng. | **Rich-text Canvas (Tiptap / Novel.sh)** với Slash commands, KaTeX math blocks và Markdown tables. |
| **Mô hình Dữ liệu** | Lưu vết Chat sessions rời rạc. | **Mô hình Dự án Học thuật (Projects $\rightarrow$ Sections $\rightarrow$ BibTeX $\rightarrow$ Citations).** |
| **Cơ chế Trích dẫn** | Hiển thị chuỗi tên file PDF trong thanh chat. | **Smart Citation Engine:** Lưu trữ tọa độ Bounding Box, click vào thẻ mở trực tiếp PDF bôi vàng câu gốc. |
| **Retrieval Engine** | BM25 sinh lỗi SQLite khi vượt quá 999 biến. | **Batched Indexing + Disk-based Pickle Cache** giúp khởi động và truy xuất tức thì $< 0.05$s. |
| **Tác vụ Hỗ trợ AI** | Trả lời câu hỏi chung (General QA). | **5 Agent Nodes chuyên biệt:** Lập ma trận so sánh, Lập dàn ý bài báo, Gợi ý trích dẫn `\cite{}`, Chuốt văn phong học thuật, và Audit lỗi logic. |
| **Biên dịch & Xuất bản**| Xuất Google Docs / Google Sheets. | **Tích hợp Compiler nội bộ:** Tự động biên dịch ra PDF chuẩn IEEE/Springer và đóng gói ZIP cho Overleaf. |

