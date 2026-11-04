# 03. THIẾT KẾ GIAO DIỆN & TRẢI NGHIỆM NGƯỜI DÙNG (FRONTEND & UX)
## Bố cục 3 Phân vùng (3-Zone Studio), Trình soạn thảo Canvas AI & Trình đọc PDF Đối chiếu

---

### 1. BỐ CỤC KHÔNG GIAN LÀM VIỆC 3 PHÂN VÙNG (3-ZONE LAYOUT)

Giao diện trang `/studio/[project_id]` được thiết kế tối ưu hóa cho màn hình từ 1080p trở lên, chia thành 3 cột cố định có khả năng co giãn kích thước (Resizable Panels):

```
+-------------------------------------------------------------------------------------------------------------------------+
| TOPBAR: Tên dự án | Template: IEEE Conference | Trạng thái: Đã lưu | [Xuất BibTeX] [Biên dịch PDF] [Tải Overleaf ZIP]  |
+------------------------------+-------------------------------------------+----------------------------------------------+
| ZONE 1: PROJECT & KB HUB     | ZONE 2: ACADEMIC CANVAS                   | ZONE 3: EVIDENCE & VERIFIER                  |
| (Chiều rộng: 20% - 25%)      | (Chiều rộng: 45% - 50%)                   | (Chiều rộng: 30% - 35%)                      |
|                              |                                           |                                              |
| ── Cấu trúc Bài báo ──       | [Heading 1] 1. INTRODUCTION               | [Tab: PDF Gốc]   [Tab: Báo cáo Kiểm chứng]   |
| • 00_Abstract                |                                           |                                              |
| • 01_Introduction  <Active>  | Large Language Models (LLMs) have gained  | Document: bge_m3_paper.pdf (Trang 3/12)      |
| • 02_Related_Work            | widespread adoption across various        | +------------------------------------------+ |
| • 03_Methodology             | academic disciplines \cite{vaswani2017}.  | | ...dense representation captures semantic| |
| • 04_Experiments             | However, linear RAG pipelines suffer from | | context, while sparse retrieval ensures  | |
| • references.bib             | cross-domain semantic confusion           | | exact terminology matching...            | |
|                              | \cite{chen2024bge}.                       | | [KHUNG BÔI VÀNG CÂU VĂN ĐỐI CHIẾU]       | |
| ── Thư viện 8 Miền ──        |                                           | +------------------------------------------+ |
| [x] CS / IT (130)            | [ Gõ / để chèn lệnh AI, Công thức, Bảng ] | Điểm tương quan: 94% (Đã kiểm chứng)        |
| [ ] Mathematics (97)         |                                           |                                              |
| [ ] Physics (72)             | $$Score(D, Q) = \sum_{i=1}^{n} IDF(q_i)...| Danh sách Nhận định cần kiểm chứng:          |
|                              |                                           | • [v] Câu 1: Khớp trang 3 (bge-m3)           |
| [+ Nạp thêm PDF mới]         | [ Thanh công cụ nổi: Make Formal | Copy ] | • [!] Câu 3: Thiếu số liệu thực nghiệm       |
+------------------------------+-------------------------------------------+----------------------------------------------+
| FOOTER: Từ: 1,840 | Trích dẫn: 12 bài | VRAM: 3.8/4.0 GB (Ollama Qwen2.5 7B) | WebSocket: Đã kết nối                      |
+-------------------------------------------------------------------------------------------------------------------------+
```

---

### 2. CẤU TRÚC THÀNH PHẦN FRONTEND (COMPONENT HIERARCHY)

Hệ thống thư mục component mới trong `frontend/src/`:

```text
frontend/src/
├── app/
│   ├── studio/
│   │   ├── page.tsx                           # Danh sách dự án (Project Dashboard)
│   │   └── [project_id]/
│   │       ├── page.tsx                       # Màn hình 3-Zone Workspace chính
│   │       └── layout.tsx
├── components/
│   ├── studio/
│   │   ├── Topbar/
│   │   │   ├── ProjectHeader.tsx              # Tên dự án, trạng thái lưu tự động
│   │   │   └── ActionButtons.tsx              # Nút Compile PDF, Export Overleaf
│   │   ├── Zone1_ProjectNav/
│   │   │   ├── SectionList.tsx                # Danh sách cây thư mục các chương mục bài báo
│   │   │   ├── BibtexDrawer.tsx               # Ngăn kéo quản lý danh mục trích dẫn @article
│   │   │   └── DomainQuickFilter.tsx          # Bộ lọc 8 miền tài liệu khoa học
│   │   ├── Zone2_Canvas/
│   │   │   ├── AcademicEditor.tsx             # Novel.sh / Tiptap WYSIWYG core
│   │   │   ├── SlashCommandExtension.ts       # Menu lệnh gõ phím '/'
│   │   │   ├── KaTeXBlock.tsx                 # Render công thức toán học thời gian thực
│   │   │   ├── FloatingAIToolbar.tsx          # Thanh công cụ nổi (Make Academic, Find Evidence)
│   │   │   └── ComparisonTableBuilder.tsx     # Bảng so sánh baseline Markdown/LaTeX
│   │   └── Zone3_Verifier/
│   │       ├── SplitPDFViewer.tsx             # Wrapper hiển thị PDF bằng react-pdf
│   │       ├── BoundingBoxHighlighter.tsx     # Lớp vẽ khung vàng phát sáng đè lên trang PDF
│   │       ├── ClaimAuditPanel.tsx            # Bảng kiểm tra chống ảo giác & cảnh báo thiếu trích dẫn
│   │       └── CompiledPDFPreview.tsx         # Tab xem trực tiếp file PDF sau khi biên dịch
├── hooks/
│   ├── useStudioProject.ts                    # Hook quản lý trạng thái dự án, lưu tự động
│   ├── useCitationVerifier.ts                 # Hook đồng bộ giữa click thẻ trích dẫn và PDF Viewer
│   └── useStudioWebSocket.ts                  # Hook WebSocket streaming trạng thái Copilot
└── store/
    └── studioStore.ts                         # Zustand Store quản lý trạng thái toàn cục 3 vùng
```

---

### 3. ĐẶC TẢ CHI TIẾT TỪNG PHÂN VÙNG TƯƠNG TÁC

#### 3.1. Zone 1: Quản lý Cây Thư mục & Thư viện Tri thức (Left Hub)
* **Quản lý Chương mục (Section Tree):** Người dùng có thể kéo thả thay đổi thứ tự các phần (`Abstract` $\rightarrow$ `Introduction` $\rightarrow$ `Methodology`). Bấm vào chương nào thì Canvas Zone 2 lập tức mở nội dung chương đó.
* **Tích hợp Danh mục BibTeX:** Hiển thị toàn bộ các thẻ `@article{key, ...}` đang được dùng trong bài. Người dùng có thể bấm copy 1 click hoặc xóa thẻ không dùng.

#### 3.2. Zone 2: Trình Soạn thảo Bài báo Học thuật (Academic Canvas)
Được xây dựng trên nền tảng **Novel.sh / Tiptap**:
1. **Slash Commands Menu (Gõ `/`):**
   * `/ai-section`: Kích hoạt Agent tự động sinh dàn ý hoặc bản nháp cho section hiện tại.
   * `/math`: Chèn khối công thức toán LaTeX (render bằng KaTeX ngay tại chỗ).
   * `/table`: Mở giao diện tạo bảng so sánh thực nghiệm.
   * `/cite`: Mở popup tìm kiếm nhanh trong kho 618 bài báo để chèn thẻ `\cite{...}`.
2. **Thanh công cụ AI nổi khi bôi đen (Floating AI Toolbar):**
   * Khi người dùng bôi đen một câu hoặc một đoạn văn bản:
     * **Make Formal:** Chuyển câu sang phong cách tiếng Anh học thuật trang trọng.
     * **Find Evidence:** Agent tìm ngay trong 618 bài báo xem có số liệu nào chứng minh cho câu khẳng định này không.
     * **Fix Grammar & Flow:** Sửa lỗi ngữ pháp và tăng tính liên kết câu văn (coherence).

#### 3.3. Zone 3: Kiểm chứng Trích dẫn & Trình đọc PDF Đối chiếu (Right Verifier)
1. **Cơ chế Click-to-Verify (Trải nghiệm SciSpace):**
   * Khi người dùng click chuột vào thẻ `\cite{chen2024bge}` trên Canvas Zone 2:
     * Cột Zone 3 lập tức tải tệp `bge_m3_paper.pdf`.
     * Tự động nhảy đến đúng **Trang 3**.
     * Component `BoundingBoxHighlighter.tsx` vẽ một khung chữ nhật màu vàng viền xanh dạ quang ôm trọn câu văn mà tác giả bài báo đã đề cập.
   * Người dùng nhìn thấy ngay tài liệu gốc để kiểm tra tính chính xác, không còn nỗi sợ "ảo giác".
2. **Bảng Báo cáo Liêm chính Học thuật (Claim Audit Panel):**
   * Tự động phân tích toàn bộ văn bản trong Canvas và đánh dấu màu theo mức độ tin cậy:
     * 🟢 **Xanh lá (Verified):** Khẳng định đã được chứng minh bằng tài liệu trong kho nội bộ.
     * 🟡 **Vàng (Missing Citation):** Câu văn đưa ra số liệu/kết luận nhưng chưa gắn thẻ trích dẫn `\cite{}`.
     * 🔴 **Đỏ (Hallucination Alert):** Thông tin mâu thuẫn với nội dung tài liệu trích dẫn.

---

### 4. QUẢN LÝ TRẠNG THÁI TOÀN CỤC (ZUSTAND STORE SPECIFICATION)

```typescript
// File: frontend/src/store/studioStore.ts
import { create } from 'zustand';

interface StudioState {
  // Project Info
  projectId: string | null;
  activeSectionId: string | null;
  selectedDomain: string;
  
  // Verification & PDF Sync
  activeCitation: {
    bibtexKey: string;
    pdfPath: string;
    pageNumber: number;
    bbox: [number, number, number, number] | null;
  } | null;
  
  // View Modes
  rightPanelTab: 'pdf_viewer' | 'audit_report' | 'compiled_preview';
  isCompiling: boolean;
  
  // Actions
  setActiveSection: (id: string) => void;
  jumpToCitation: (citationData: StudioState['activeCitation']) => void;
  setRightPanelTab: (tab: StudioState['rightPanelTab']) => void;
}

export const useStudioStore = create<StudioState>((set) => ({
  projectId: null,
  activeSectionId: null,
  selectedDomain: 'it',
  activeCitation: null,
  rightPanelTab: 'pdf_viewer',
  isCompiling: false,

  setActiveSection: (id) => set({ activeSectionId: id }),
  jumpToCitation: (citationData) => set({ activeCitation: citationData, rightPanelTab: 'pdf_viewer' }),
  setRightPanelTab: (tab) => set({ rightPanelTab: tab }),
}));
```

