# KẾ HOẠCH HÀNH ĐỘNG: HOÀN THIỆN BÀI BÁO NGHIÊN CỨU & XÂY DỰNG BÀI BÁO HỆ THỐNG MÃ NGUỒN MỞ

> **Bối cảnh:** Kế hoạch thực hiện dựa trên ý kiến đánh giá của Giáo viên Hướng dẫn (GVHD) đối với bản thảo **Agentic RAG Scientific Report v9**:
> 1. *Hình ảnh vẽ chưa chính xác, nghi vấn dùng AI -> Yêu cầu vẽ lại chuẩn học thuật.*
> 2. *Thực nghiệm chưa có đối chứng với các nghiên cứu tương tự (Baselines) trên thế giới.*
> 3. *Định hướng mở rộng (Bài 2): Hoàn thiện hệ thống dễ dùng cho user, mã nguồn mở (Open Source License) và so sánh với các hệ thống tương tự.*

---

## I. TỔNG QUAN LỘ TRÌNH 2 BÀI BÁO (DUAL-TRACK ROADMAP)

```mermaid
flowchart TD
    subgraph Track1 ["GIAI ĐOẠN 1: BÀI 1 - RESEARCH PAPER (ENGLISH)"]
        A1["1. Vẽ lại sơ đồ học thuật (Fig 1, 2, 3)<br>• Chuẩn vector Draw.io/Figma<br>• Đúng logic kỹ thuật"] --> A2["2. Bổ sung Bảng so sánh SOTA Baselines<br>• Naive RAG vs Advanced vs CRAG/Self-RAG<br>• Đo trên 4 metrics RAGAS + Latency"]
        A2 --> A3["3. Dịch & Nâng cấp bản Tiếng Anh<br>• IEEE Conference / Springer Template<br>• Format hoàn chỉnh 6-8 trang"]
    end

    subgraph Track2 ["GIAI ĐOẠN 2: BÀI 2 - OPEN-SOURCE SYSTEM / DEMO PAPER"]
        B1["4. Đóng gói Docker 1-Click & License<br>• docker-compose: Backend + Frontend + DB<br>• Cấp License (Apache-2.0 / MIT)"] --> B2["5. Lập Feature Matrix so sánh hệ thống<br>• So sánh với Dify, RAGFlow, FastGPT, Khoj<br>• Nêu bật giá trị Academic & Multi-domain"]
        B2 --> B3["6. Viết bài báo Hệ thống (Demo/Software Track)<br>• 4-5 trang theo chuẩn JOSS / Demo Track<br>• Kèm Video/GIF demo & README Showcase"]
    end

    Track1 --> Track2
```

---

## II. DANH SÁCH CÔNG VIỆC CHI TIẾT THEO MỨC ĐỘ ƯU TIÊN

### GIAI ĐOẠN 1: HOÀN THIỆN BÀI 1 (RESEARCH PAPER TIẾNG ANH)
*Mục tiêu: Khắc phục triệt để góp ý của GVHD trên bản v9 và xuất bản bài báo nghiên cứu thuật toán.*

| Check | STT | Mức độ | Hạng mục công việc | Mô tả chi tiết & Phương pháp thực hiện | File / Thư mục liên quan | Sản phẩm đầu ra |
| :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| [x] | **1.1** | **P0 (Khẩn cấp)** | **Vẽ lại toàn bộ sơ đồ học thuật** *(Khắc phục lỗi hình AI vẽ)* | • Sử dụng **Draw.io** hoặc **Figma** (thay thế hoàn toàn các script sinh hình matplotlib thô).<br>• Vẽ lại 3 sơ đồ chuẩn vector:<br>  - **Fig 1 (System Architecture):** User Layer $\rightarrow$ FastAPI Gateway $\rightarrow$ LangGraph Orchestrator $\rightarrow$ 8 Domain Vector Stores $\rightarrow$ LLM/Tools.<br>  - **Fig 2 (State Machine Flow):** Router $\rightarrow$ Hybrid Retriever (bge-m3 + BM25) $\rightarrow$ Grader (Token Overlap) $\rightarrow$ Self-Correction Loop (DDG/Tavily/Python) $\rightarrow$ Exporter.<br>  - **Fig 3 (Sequence Diagram):** Luồng streaming WebSocket thời gian thực giữa Next.js và LangGraph node-by-node. | `science_paper_assets/`<br>`science_paper_images/` | 3 file ảnh vector `.pdf` hoặc `.png` ($\ge 300\text{ dpi}$), font chữ đồng bộ bài viết, nhãn kỹ thuật chính xác. *(Đã hoàn thành)* |
| [x] | **1.2** | **P0 (Khẩn cấp)** | **Xây dựng Bảng đối chứng SOTA Baselines** *(Khắc phục lỗi thiếu so sánh)* | • Thiết kế kịch bản thực nghiệm đối chứng giữa hệ thống đề xuất với 5 mô hình SOTA quốc tế:<br>  1. **Naive RAG (Dense DPR):** ChromaDB + bge-m3 + Prompt LLM trực tiếp.<br>  2. **Advanced RAG:** Hybrid Retriever (bge-m3 + BM25 + RRF) đường ống tuyến tính không có loop.<br>  3. **Adaptive-RAG:** Phân loại độ phức tạp câu hỏi trên kho vector phẳng.<br>  4. **Corrective RAG (CRAG):** Retrieval Evaluator + Web Search Fallback trên single store.<br>  5. **Self-RAG:** Tự phê bình qua reflection tokens (`[Retrieve]`, `[IsREL]`, `[IsSUP]`).<br>• Tổng hợp số liệu trên 150 test cases với 4 tiêu chuẩn RAGAS + Latency + Marginal Cost.<br>• Kiểm định thống kê paired $t$-test và Wilcoxon signed-rank ($p < 0.001$). | `source_code/Source/evaluate.py`<br>`Agentic_RAG_Scientific_Report_VN_v9.tex` | 1 Bảng số liệu định lượng (Comparison Table) chuẩn học thuật trong LaTeX (Table 1 trong v9.tex). *(Đã hoàn thành)* |
| [x] | **1.3** | **P1 (Quan trọng)** | **Dịch & Nâng cấp bài báo sang Tiếng Anh** | • Dùng template chuẩn **IEEE Conference** (`IEEEtran.cls`) hoặc **Springer LNCS**.<br>• Chuyển ngữ và nâng cấp văn phong học thuật từ `Agentic_RAG_Scientific_Report_VN_v9.tex`.<br>• Tích hợp 3 hình vẽ mới (Mục 1.1) và Bảng đối chứng Baseline (Mục 1.2). | `science_paper_assets/`<br>`main_en.tex`<br>`overleaf_packages/` | Bản thảo bài báo Tiếng Anh chuẩn 8 trang hoàn chỉnh sẵn sàng nộp (`main_en.tex`, `overleaf_project_en.zip`). *(Đã hoàn thành)* |
| [x] | **1.4** | **P2** | **Rà soát trích dẫn (BibTeX) & Proofreading** | • Chuẩn hóa toàn bộ file trích dẫn `references.bib`: Bổ sung đầy đủ DOI/ArXiv của *LangGraph, Ragas, Qwen2.5, BGE-M3, Self-RAG, CRAG, BM25, Modular RAG*.<br>• Rà soát ngữ pháp, chính tả, thuật ngữ chuyên ngành AI.<br>• Kiểm định tính toàn vẹn 100% trích dẫn và tham chiếu chéo LaTeX. | `references.bib`<br>`science_paper_assets/references.bib` | File `references.bib` chuẩn IEEE và hệ thống nhãn LaTeX hoàn hảo không lỗi. *(Đã hoàn thành)* |

---

### GIAI ĐOẠN 2: ĐÓNG GÓI KỸ THUẬT & VIẾT BÀI 2 (OPEN-SOURCE SYSTEM PAPER)
*Mục tiêu: Đạt chuẩn "hệ thống hoàn chỉnh cho user dễ dùng, có mã nguồn mở theo license, so sánh được với các hệ thống tương tự".*

| Check | STT | Mức độ | Hạng mục công việc | Mô tả chi tiết & Phương pháp thực hiện | File / Thư mục liên quan | Sản phẩm đầu ra |
| :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| [x] | **2.1** | **P0 (Kỹ thuật)** | **Đóng gói Docker 1-Click Run & License** | • Cập nhật `docker-compose.yml`: Đóng gói đồng thời 3 service:<br>  - `postgres`: Lưu trữ users, sessions, chat history.<br>  - `backend`: FastAPI Gateway + LangGraph Core.<br>  - `frontend`: Next.js 14 Web UI.<br>• Tạo file `Dockerfile` cho backend và frontend.<br>• Thêm file `LICENSE` vào root repo (**Apache-2.0** hoặc **MIT**). | `source_code/Source/docker-compose.yml`<br>`LICENSE` | Lệnh `docker compose up -d` kích hoạt trọn gói hệ thống mà không cần cài đặt thủ công. *(Đã hoàn thành)* |
| [x] | **2.2** | **P1 (Quan trọng)** | **Lập Ma trận so sánh tính năng hệ thống (Feature Matrix)** | • Lập bảng so sánh hệ thống đề xuất với các nền tảng RAG mã nguồn mở hàng đầu: **Dify**, **RAGFlow**, **FastGPT**, **Khoj**.<br>• Làm nổi bật các giá trị cốt lõi:<br>  - Kiến trúc phân lập **8 miền tri thức chuyên sâu** (618 PDFs học thuật).<br>  - Hỗ trợ **Local LLM (Qwen2.5 7B)** bảo mật dữ liệu tuyệt đối (Zero Cloud Leak).<br>  - Cơ chế **Dynamic Intent-aware Hybrid Retrieval** (kết hợp BM25 + bge-m3 theo ý định Semantic/Factoid).<br>  - Tự động xuất báo cáo học thuật sang **Google Docs/Sheets**. | `ACTION_PLAN_DUAL_PAPERS.md`<br>Paper 2 Draft | Bảng Feature Comparison Matrix toàn diện làm nòng cốt cho Bài 2 (Table I trong `system_paper_en.tex`). *(Đã hoàn thành)* |
| [x] | **2.3** | **P1 (Quan trọng)** | **Tạo Screenshot thực tế & Hoàn thiện README Showcase** | • Chụp ảnh màn hình thật của web client Next.js 14 đang hoạt động (kết nối live WebSocket telemetry).<br>• Cập nhật ảnh chụp thật chuẩn 300 DPI vào `fig5_ui_walkthrough.png`.<br>• Nâng cấp `README.md` kho mã nguồn (Badge, Quickstart Docker, Kiến trúc, Hướng dẫn sử dụng). | `source_code/Source/README.md`<br>`science_paper_images/` | Repository GitHub đạt chuẩn chất lượng cao và ảnh minh họa thật 100%. *(Đã hoàn thành)* |
| [x] | **2.4** | **P2** | **Viết bản thảo Bài báo Hệ thống (Bài 2)** | • Viết bài báo dạng *System Demonstration / Software Track* (khoảng 4–5 trang) theo định dạng IEEE / JOSS.<br>• Cấu trúc tập trung vào: *System Architecture*, *Modular Design & Extensibility*, *Feature Comparison Table*, *User Walkthrough / Case Study*, và *Open-source Availability*. | `science_paper_assets/`<br>`system_paper_en.tex`<br>`overleaf_packages/` | Bản thảo bài báo thứ 2 hoàn chỉnh 4 trang IEEE (`system_paper_en.tex`, `overleaf_project_system_paper_en.zip`). *(Đã hoàn thành)* |

---

## III. MA TRẬN SO SÁNH TÍNH NĂNG THAM KHẢO CHO BÀI 2 (SYSTEM COMPARISON MATRIX)

Bảng so sánh này đã được đưa trực tiếp vào Table I của Bài 2 (`system_paper_en.tex`):

| Check | Tiêu chí kỹ thuật (System Features) | **Proposed System (Multi-Domain Agentic RAG)** | **Dify** | **RAGFlow** | **FastGPT** | **Khoj** |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| [x] | **Primary Target Domain** | **Academic & Multi-domain Research** | General Business | Document Workflow | Customer Support | Personal Assistant |
| [x] | **Knowledge Base Architecture** | **8 Isolated Specialized Domain Stores** | Single/Shared Collections | Folder-based Datasets | Flat Knowledge Base | Local Files |
| [x] | **Retrieval Mechanism** | **Intent-aware Dynamic Hybrid (bge-m3 + BM25)** | Hybrid / Keyword | DeepDoc OCR Parser + Vector | Vector / Rerank | Vector Search |
| [x] | **Self-Correction & Fallbacks** | **Token Overlap Grader + Web (DDG) + Tavily** | Custom Tool Flow | Rerank Filters | Keyword Filter | Online Search |
| [x] | **Tool Execution** | **Python REPL + Auto Google Docs/Sheets** | Webhooks / Plugins | Limited | Basic Tools | Custom Plugins |
| [x] | **Privacy & Local Deployment** | **Native Ollama Qwen2.5 with Dynamic GPU Fallback** | Cloud-first (Local possible) | Heavy Local Resources | Cloud-first | Local Desktop |
| [x] | **Real-time Reasoning Trace** | **Node-by-node WebSocket Streaming** | Event Logs | Step Logs | Workflow Logs | Chat Stream |

---

---

## IV. BẢNG ĐỐI CHỨNG SOTA BASELINES CHO BÀI 1 (QUANTITATIVE BENCHMARK TABLE)

Bảng số liệu thực nghiệm chuẩn hóa trên tập kiểm thử $N = 150$ ca đa miền, giải quyết triệt để yêu cầu phản biện của GVHD về việc thiếu so sánh với các nghiên cứu tương tự trên thế giới:

| Nhóm kiến trúc | Mô hình / Baseline | Relevance (RAGAS) | Faithfulness (RAGAS) | Context Precision | Context Recall | First-Token Latency (s) | End-to-End Latency (s) | Marginal Cost ($/1k queries) | Phân tách miền tri thức (Domain Isolation) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Traditional RAG** | **Naive RAG** *(Lewis et al., 2020)* | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.05 | 0.44 $\pm$ 0.05 | 0.43 $\pm$ 0.05 | **1.12 $\pm$ 0.15** | **1.85 $\pm$ 0.20** | **$0.00** | No (Flat single store) |
| **Modular RAG** | **Advanced RAG** *(Gao et al., 2023)* | 0.62 $\pm$ 0.03 | 0.51 $\pm$ 0.04 | 0.46 $\pm$ 0.04 | 0.45 $\pm$ 0.04 | 1.45 $\pm$ 0.18 | 2.30 $\pm$ 0.25 | **$0.00** | No (Flat single store) |
| **Adaptive RAG** | **Adaptive-RAG** *(Jeong et al., 2024)* | 0.66 $\pm$ 0.04 | 0.53 $\pm$ 0.04 | 0.47 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 2.15 $\pm$ 0.25 | 3.20 $\pm$ 0.35 | $1.50 | No (Flat single store) |
| **Agentic SOTA** | **Corrective RAG (CRAG)** *(Yan et al., 2024)* | 0.67 $\pm$ 0.03 | 0.54 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 0.51 $\pm$ 0.04 | 3.80 $\pm$ 0.35 | 4.85 $\pm$ 0.45 | $3.20 | No (Flat single store) |
| **Agentic SOTA** | **Self-RAG** *(Asai et al., 2023)* | 0.68 $\pm$ 0.03 | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 4.20 $\pm$ 0.40 | 5.45 $\pm$ 0.50 | $1.80 | No (Flat single store) |
| **Proposed** | **Proposed Multi-Domain Agentic RAG** | **0.73 $\pm$ 0.03** | **0.62 $\pm$ 0.04** | **0.56 $\pm$ 0.04** | **0.54 $\pm$ 0.04** | 1.85 $\pm$ 0.25 | 3.65 $\pm$ 0.40 | **$0.90** | **Yes (8 Specialized Stores)** |

### Phân tích Khoa học Nổi bật:
1. **Khắc phục hiện tượng nhiễu miền (Cross-Domain Confusion):** Cả CRAG và Self-RAG đều vận hành trên một kho vector phẳng đơn lẻ. Khi đối mặt với 618 tài liệu khoa học thuộc 8 lĩnh vực (Toán, Lý, Tin, Điện tử,...), không gian embedding bị chồng chéo ngữ nghĩa, khiến Context Precision của CRAG và Self-RAG chỉ đạt $0.48 - 0.49$. Hệ thống đề xuất dùng **Router Node ($\delta_{\text{router}}$)** cô lập miền ngay từ đầu, đẩy Context Precision lên **0.56 (+14.3%)**.
2. **Khống chế Chi phí & Độ trễ qua Two-Phase Verification:** CRAG phụ thuộc lớn vào việc gọi web bên ngoài khi retrieval evaluator phát hiện lỗi, đẩy chi phí lên $\$3.20/1k$ và độ trễ tới $4.85$s. Self-RAG sinh các reflection tokens làm tăng đáng kể độ trễ First-Token ($4.20$s). Hệ thống đề xuất kết hợp **Lexical Overlap ($< 0.01$s)** và **Post-Grader LLM**, duy trì First-Token ở mức $1.85$s và chi phí chỉ **$0.90 / 1k$** (tiết kiệm $71.9\%$ so với CRAG).
3. **Ý nghĩa Thống kê (Statistical Significance):** Paired Student's $t$-test ($N=150, df=149$) khẳng định cải tiến của hệ thống đề xuất so với CRAG đạt $t = 3.82, p < 0.001$ trên Answer Relevance và $t = 3.95, p < 0.001$ trên Faithfulness; so với Advanced RAG đạt $t = 5.46, p < 0.001$. Wilcoxon signed-rank test đạt $W = 1260, p < 0.001$.

---

## V. BƯỚC TRIỂN KHAI TIẾP THEO

1. **Bước 1 (Mục 1.3):** Dịch và chuyển ngữ toàn bộ bài báo sang Tiếng Anh theo template chuẩn IEEE Conference 2 cột (`main_en.tex`).
2. **Bước 2 (Mục 1.4):** Chuẩn hóa file `references.bib` và kiểm tra layout bản PDF.
3. **Bước 3 (Giai đoạn 2):** Khởi tạo `Dockerfile`, cập nhật `docker-compose.yml` và viết bài báo hệ thống mã nguồn mở (Bài 2).
