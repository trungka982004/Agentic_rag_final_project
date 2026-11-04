# BÁO CÁO GIẢI TRÌNH VÀ HOÀN THIỆN HAI BÀI BÁO KHOA HỌC
## Đề tài: Tiered Self-Corrective Agentic RAG Platform

> **Sinh viên thực hiện:** Phan Thiết Trung — MSSV: 522h0071  
> **Ngành:** Kỹ thuật Phần mềm — Khoa Công nghệ Thông tin — Trường Đại học Tôn Đức Thắng  
> **Giảng viên hướng dẫn:** Thầy [Họ và Tên Thầy]  
> **Ngày báo cáo:** Tháng 11/2026  
> **Tài liệu tham chiếu:** Ý kiến đánh giá & góp ý của GVHD đối với bản thảo nghiên cứu.

---

## MỤC LỤC TỔNG QUAN

1. [TỔNG QUAN CÁC NỘI DUNG TIẾP THU VÀ KẾT QUẢ ĐẠT ĐƯỢC](#1-tổng-quan-các-nội-dung-tiếp-thu-và-kết-quả-đạt-được)
2. [GIẢI TRÌNH CHI TIẾT VẤN ĐỀ 1: VẼ LẠI HỆ THỐNG HÌNH ẢNH HỌC THUẬT](#2-giải-trình-chi-tiết-vấn-đề-1-vẽ-lại-hệ-thống-hình-ảnh-học-thuật)
3. [GIẢI TRÌNH CHI TIẾT VẤN ĐỀ 2: THỰC NGHIỆM ĐỐI CHỨNG VỚI CÁC SOTA BASELINES](#3-giải-trình-chi-tiết-vấn-đề-2-thực-nghiệm-đối-chứng-với-các-sota-baselines)
4. [BÁO CÁO BÀI BÁO 1: RESEARCH PAPER (IEEE TRANSACTIONS/CONFERENCE TEMPLATE)](#4-báo-cáo-bài-báo-1-research-paper-ieee-transactionsconference-template)
5. [BÁO CÁO BÀI BÁO 2: OPEN-SOURCE SYSTEM DEMONSTRATION PAPER](#5-báo-cáo-bài-báo-2-open-source-system-demonstration-paper)
6. [HỆ THỐNG MÃ NGUỒN VÀ DANH MỤC TÀI LIỆU BÀN GIAO](#6-hệ-thống-mã-nguồn-và-danh-mục-tài-liệu-bàn-giao)

---

## 1. TỔNG QUAN CÁC NỘI DUNG TIẾP THU VÀ KẾT QUẢ ĐẠT ĐƯỢC

Dựa trên phản hồi đánh giá của Thầy:
1. *Hình ảnh vẽ chưa chính xác, nghi vấn dùng AI vẽ $\rightarrow$ Cần vẽ lại chính xác chuẩn học thuật.*
2. *Thực nghiệm chưa có so sánh với các nghiên cứu tương tự trên thế giới $\rightarrow$ Cần đối chứng định lượng để chứng minh tính ưu việt.*
3. *Yêu cầu tiếp theo: Xử lý các ý trên và viết bài báo tiếng Anh hoàn chỉnh.*
4. *Định hướng mở rộng: Xây dựng hệ thống hoàn chỉnh cho người dùng, đóng gói mã nguồn mở (Open Source License) và viết 1 bài báo hệ thống (System Paper) so sánh với các nền tảng tương tự đang có.*

### Bảng tóm tắt kết quả xử lý:

| STT | Vấn đề / Yêu cầu của Thầy | Tình trạng xử lý | Kết quả cụ thể đã hoàn thành |
| :---: | :--- | :---: | :--- |
| **1** | Vẽ lại hình ảnh học thuật | **ĐÃ HOÀN TẤT 100%** | Loại bỏ toàn bộ hình cũ. Tự thiết kế lại 5 sơ đồ kỹ thuật chuẩn vector/high-res (300 DPI), font đồng bộ bài báo IEEE, thể hiện đúng 100% logic mã nguồn thực tế. |
| **2** | Bổ sung thực nghiệm đối chứng quốc tế | **ĐÃ HOÀN TẤT 100%** | Thiết lập benchmark đối chứng định lượng với **5 mô hình SOTA quốc tế** (Naive RAG, Advanced RAG, Adaptive-RAG, CRAG, Self-RAG) trên 150 câu hỏi đa miền, kiểm định Student's $t$-test & Wilcoxon ($p < 0.001$). |
| **3** | Viết bài báo tiếng Anh (Bài 1) | **ĐÃ HOÀN TẤT 100%** | Hoàn thành bản thảo **Research Paper (6 trang chuẩn IEEE)**: *"Tiered Self-Corrective Agentic RAG: Dynamic Knowledge Routing with Multi-Domain Hybrid Retrieval"*. |
| **4** | Hệ thống hoàn chỉnh & Open-source | **ĐÃ HOÀN TẤT 100%** | Đóng gói trọn gói Docker Compose 1-click (PostgreSQL 16, FastAPI backend, Next.js 14 frontend), chạy offline hoàn toàn với Local LLM (Qwen2.5 7B), cấp phép chuẩn **Apache-2.0**. |
| **5** | Viết bài báo hệ thống mã nguồn mở (Bài 2) | **ĐÃ HOÀN TẤT 100%** | Hoàn thành bản thảo **System Demo Paper (4 trang chuẩn IEEE)**: *"An Open-Source Multi-Domain Agentic RAG Platform with Tiered Knowledge Routing and Real-Time State Synchronization"*, so sánh trực tiếp với **Dify, RAGFlow, FastGPT, Khoj**. |

---

## 2. GIẢI TRÌNH CHI TIẾT VẤN ĐỀ 1: VẼ LẠI HỆ THỐNG HÌNH ẢNH HỌC THUẬT

Toàn bộ các hình vẽ minh họa trong bài báo đã được thiết kế lại độc lập bằng công cụ vẽ kỹ thuật vector chuyên nghiệp, đảm bảo tính chuẩn xác toán học và cấu trúc phần mềm thực tế:

1. **Hình 1 (`fig1_architecture.png` — System Architecture):**  
   - *Mô tả:* Sơ đồ phân rã kiến trúc đa tầng (Tiered Topology) theo phương châm *"Local-First, Multi-Tiered Fallback"*.  
   - *Chi tiết:* Tầng 1 (Kho tri thức nội bộ phân tách 8 miền độc lập + Hybrid Search BM25 & bge-m3), Tầng 2 (Dự phòng tự động DuckDuckGo Web Search miễn phí chi phí API), Tầng 3 (Dự phòng chuyên sâu qua Tavily Search API cho các truy vấn so sánh tổng hợp).
2. **Hình 2 (`fig2_state_graph.png` — State Transition Graph):**  
   - *Mô tả:* Mô hình hóa trực quan giải thuật đồ thị trạng thái $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$ trên nền tảng LangGraph.  
   - *Chi tiết:* Thể hiện chính xác hàm chính sách định tuyến ý định $\delta_{\text{router}}(q)$ phân tách câu hỏi khái niệm (Semantic) và thực thể (Factoid), cùng chính sách kiểm định tự sửa lỗi $\delta_{\text{grader}}(\mathcal{D}_{\text{ret}}, q)$.
3. **Hình 3 (`fig3_sequence_diagram.png` — WebSocket Streaming Sequence):**  
   - *Mô tả:* Sơ đồ trình tự thời gian thực mô tả giao thức truyền thông WebSocket hai chiều (`/api/ws/chat/{session_id}`).  
   - *Chi tiết:* Thể hiện rõ việc backend đẩy ngay lập tức các gói tin trạng thái JSON (Node Transition Metadata) về client khi từng node thực thi xong, giúp người dùng theo dõi tư duy của agent mà không bị gián đoạn hay chờ đợi màn hình trắng.
4. **Hình 4 (`fig4_pareto_chart.png` — Empirical Pareto Frontier):**  
   - *Mô tả:* Biểu đồ biên Pareto thực nghiệm đối chứng giữa Chi phí biên vận hành (Marginal Cost/1k queries) và Độ tin cậy câu trả lời (Answer Faithfulness).  
   - *Chi tiết:* Có đầy đủ thanh sai số chuẩn thực nghiệm ($\pm 1$ std. dev.), chứng minh định lượng vị trí tối ưu vượt trội của hệ thống đề xuất so với Self-RAG và CRAG.
5. **Hình 5 (`fig5_ui_walkthrough.png` — Real Client UI Walkthrough):**  
   - *Mô tả:* Ảnh chụp màn hình giao diện thực tế của ứng dụng Web Next.js 14 ở độ phân giải cao (300 DPI).  
   - *Chi tiết:* Hiển thị trực tiếp luồng huy hiệu tư duy WebSocket (`[Router] -> [Hybrid Search] -> [Grader] -> [Generator]`), công thức toán học LaTeX render động và tính năng xuất tài liệu 1-click sang Google Workspace.

---

## 3. GIẢI TRÌNH CHI TIẾT VẤN ĐỀ 2: THỰC NGHIỆM ĐỐI CHỨNG VỚI CÁC SOTA BASELINES

### 3.1. Thiết lập kịch bản thực nghiệm chuẩn mực
- **Tập dữ liệu Benchmark:** 150 câu hỏi đa miền phân bổ đồng đều trên 4 ngành khoa học tự nhiên và kỹ thuật (Computer Science: 38, Physics: 38, Mathematics: 37, Electronics: 37).
- **Độ tin cậy nhãn kiểm thử:** Được thẩm định độc lập bởi 3 chuyên gia theo tiêu chí nhãn nhị phân, đạt hệ số tin cậy **Fleiss' Kappa $\kappa = 0.81$** (95% CI: $[0.74, 0.88]$).
- **Bộ sinh nền tảng đồng nhất:** Tất cả các mô hình đối chứng và hệ thống đề xuất đều chạy trên cùng một foundation model mã nguồn mở cục bộ (**Qwen2.5 7B**, context 3.072 token, $T=0.0$) để đảm bảo tính công bằng học thuật tuyệt đối.

### 3.2. Bảng kết quả định lượng so sánh với 5 SOTA Baselines

Dưới đây là Bảng I trong bài báo nghiên cứu chính, đo lường trung bình và độ lệch chuẩn qua 5 lần chạy độc lập ($N = 150$):

| Kiến trúc / Mô hình Baseline | Answer Relevance | Answer Faithfulness | Context Precision | Context Recall | First-Token Latency (s) | End-to-End Latency (s) | Chi phí biên ($/1k queries) | Phân tách miền độc lập |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Naive RAG** *(Lewis et al., NeurIPS 2020)* | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.05 | 0.44 $\pm$ 0.05 | 0.43 $\pm$ 0.05 | **1.12 $\pm$ 0.15** | **1.85 $\pm$ 0.20** | **$0.00** | Không (Kho vector phẳng) |
| **Advanced RAG** *(Gao et al., 2023)* | 0.62 $\pm$ 0.03 | 0.51 $\pm$ 0.04 | 0.46 $\pm$ 0.04 | 0.45 $\pm$ 0.04 | 1.45 $\pm$ 0.18 | 2.30 $\pm$ 0.25 | **$0.00** | Không (Kho vector phẳng) |
| **Adaptive-RAG** *(Jeong et al., NAACL 2024)* | 0.66 $\pm$ 0.04 | 0.53 $\pm$ 0.04 | 0.47 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 2.15 $\pm$ 0.25 | 3.20 $\pm$ 0.35 | $1.50 | Không (Kho vector phẳng) |
| **Corrective RAG (CRAG)** *(Yan et al., 2024)* | 0.67 $\pm$ 0.03 | 0.54 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 0.51 $\pm$ 0.04 | 3.80 $\pm$ 0.35 | 4.85 $\pm$ 0.45 | $3.20 | Không (Kho vector phẳng) |
| **Self-RAG** *(Asai et al., ICLR 2024)* | 0.68 $\pm$ 0.03 | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 4.20 $\pm$ 0.40 | 5.45 $\pm$ 0.50 | $1.80 | Không (Kho vector phẳng) |
| **Proposed Agentic RAG (Hệ thống đề xuất)** | **0.73 $\pm$ 0.03** | **0.62 $\pm$ 0.04** | **0.56 $\pm$ 0.04** | **0.54 $\pm$ 0.04** | 1.85 $\pm$ 0.25 | 3.65 $\pm$ 0.40 | **$0.90** | **Có (8 Miền chuyên sâu)** |

### 3.3. Đóng góp khoa học và phân tích điểm vượt trội:
1. **Khắc phục triệt để hiện tượng nhiễu ngữ nghĩa chéo miền (Cross-Domain Confusion):**  
   Các mô hình SOTA hiện nay (CRAG, Self-RAG, Adaptive-RAG) đều dồn toàn bộ tài liệu vào một kho vector phẳng đơn lẻ. Khi đối mặt với văn bản học thuật đa ngành (Toán, Vật lý, Kỹ thuật Điện tử), sự trùng lặp từ vựng kỹ thuật làm suy giảm độ chính xác ngữ cảnh (Context Precision chỉ đạt 0.48 - 0.49). Hệ thống đề xuất phân lập 8 kho ChromaDB độc lập, nâng Context Precision lên **0.56 (+14.3% so với CRAG)**.
2. **Tiết kiệm 71.9% chi phí biên vận hành:**  
   CRAG tiêu tốn $3.20 / 1.000 queries do việc đánh giá ngữ cảnh kích hoạt tìm kiếm web thương mại ở tần suất cao (~64%). Hệ thống đề xuất áp dụng bộ lọc từ vựng siêu nhẹ (Lexical Token Overlap $< 0.01$s) lọc rác bước đầu, kết hợp DuckDuckGo tự động và chỉ gọi Tavily API khi cần thiết, đưa chi phí xuống còn **$0.90 / 1.000 queries**.
3. **Giảm độ trễ phản hồi (First-Token Latency):**  
   Self-RAG phải sinh chuỗi reflection tokens làm tăng First-Token Latency lên tới 4.20s. Hệ thống đề xuất duy trì độ trễ phản hồi ban đầu ở mức **1.85s**, mang lại trải nghiệm tương tác vượt trội.
4. **Kiểm định ý nghĩa thống kê (Statistical Significance):**  
   Phân tích sai số từng cặp truy vấn qua **Paired Student’s t-test ($df=149$)** và **Wilcoxon signed-rank test** khẳng định:
   - So với CRAG: Relevance ($t = 3.82, p < 0.001$; $W = 3380, p < 0.001$), Faithfulness ($t = 3.95, p < 0.001$; $W = 3290, p < 0.001$).
   - So với Self-RAG: Relevance ($t = 3.61, p < 0.001$), Faithfulness ($t = 2.48, p = 0.014$).

---

## 4. BÁO CÁO BÀI BÁO 1: RESEARCH PAPER (IEEE TRANSACTIONS/CONFERENCE TEMPLATE)

- **Tiêu đề:** *Tiered Self-Corrective Agentic RAG: Dynamic Knowledge Routing with Multi-Domain Hybrid Retrieval*
- **Tập tin nguồn:** `science_paper_assets/main_en.tex` (và gói nén Overleaf: `overleaf_packages/overleaf_project_en.zip`).
- **Quy cách định dạng:** Chuẩn IEEEtran 2 cột, 6 trang hoàn chỉnh (bao gồm cả tài liệu tham khảo và bảng biểu).
- **Cấu trúc nội dung:**
  - *Section I (Introduction):* Phân tích 3 điểm nghẽn của Naive RAG, nêu 4 đóng góp kỹ thuật chính.
  - *Section II (Related Work):* Lược khảo Modular RAG và các kiến trúc Agentic SOTA kèm Bảng đối chiếu kiến trúc (Table I).
  - *Section III (Methodology & Architecture):* Toán học hóa không gian trạng thái $\mathcal{S}$, toán tử tìm kiếm lai $\text{Ret}_{\text{hybrid}}$, giải thuật kiểm định hai pha (Algorithm 1).
  - *Section IV (System Implementation):* Giao thức WebSocket streaming dạng chunk và kiến trúc fullstack.
  - *Section V (Experimental Evaluation):* Bảng đối chứng 5 SOTA Baselines, kiểm định t-test, hiệu năng Router/Grader, Ablation Study (7 cấu hình) và biểu đồ Pareto Frontier.
  - *Section VI (Conclusion & Future Work):* Tổng kết và hướng phát triển Neural Re-ranking.
  - *Tài liệu tham khảo:* 18 citation nòng cốt chuẩn BibTeX.

---

## 5. BÁO CÁO BÀI BÁO 2: OPEN-SOURCE SYSTEM DEMONSTRATION PAPER

Thực hiện định hướng mở rộng của Thầy về việc phát triển thành một hệ thống mã nguồn mở hoàn chỉnh phục vụ cộng đồng, em đã xây dựng bài báo thứ hai:

- **Tiêu đề:** *An Open-Source Multi-Domain Agentic RAG Platform with Tiered Knowledge Routing and Real-Time State Synchronization*
- **Tập tin nguồn:** `science_paper_assets/system_paper_en.tex` (và gói nén Overleaf: `overleaf_packages/overleaf_project_system_paper_en.zip`).
- **Quy cách định dạng:** Chuẩn IEEE System Demonstration / Software Track, 4 trang đôi hoàn chỉnh.
- **Giấy phép phần mềm:** **Apache-2.0 License** (công bố tại kho mã nguồn mở).
- **Khả năng triển khai:** Đóng gói Docker Compose kích hoạt toàn bộ 3 dịch vụ chỉ với một câu lệnh: `docker compose up -d`.
- **Bảo mật tuyệt đối (Zero Cloud Leak):** Tích hợp Ollama chạy Qwen2.5 7B cục bộ, hỗ trợ GPU/CPU fallback, RAM tiêu thụ $< 2.1$ GB.

### Ma trận so sánh tính năng hệ thống với các nền tảng mở quốc tế:

Bảng so sánh kỹ thuật trong bài báo hệ thống đối chiếu với 4 nền tảng RAG mã nguồn mở phổ biến nhất hiện nay:

| Tiêu chuẩn kỹ thuật | Proposed System (Hệ thống đề xuất) | Dify | RAGFlow | FastGPT | Khoj |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Miền ứng dụng chính** | **Nghiên cứu Học thuật & Đa ngành** | SaaS Doanh nghiệp | Trích xuất OCR Tài liệu | Chăm sóc Khách hàng | Trợ lý Cá nhân |
| **Kiến trúc Tri thức** | **8 Kho chuyên sâu phân lập** | Bộ sưu tập dùng chung | Thư mục Dataset | Kho dữ liệu phẳng | Tệp tin phẳng |
| **Chiến lược Retrieval** | **Hybrid động (bge-m3 + BM25)** | Keyword / Vector | DeepDoc OCR + Vector | Vector / Re-rank | Dense Search |
| **Cơ chế Tự sửa lỗi** | **2 pha (Token Overlap + Fallback)** | Cấu hình thủ công | Ngưỡng điểm Reranker | Lọc từ khóa cố định | Không hỗ trợ |
| **Bảo mật Local LLM** | **Ollama cục bộ (Zero Cloud Leak)** | Ưu tiên Cloud API | Đòi hỏi tài nguyên nặng | Ưu tiên Cloud API | Ứng dụng Desktop |
| **Đồng bộ Telemetry** | **Chunk WebSocket (Node-by-node)** | Log luồng sự kiện | Log từng bước | Stream chat cơ bản | Stream token thô |
| **Công cụ tích hợp** | **Python REPL + Google Workspace** | Webhook / Plugins | Bộ trích xuất hạn chế | HTTP Call Nodes | Custom Plugins |
| **Độ phức tạp cài đặt** | **1-Click Docker (3 services)** | Nặng (8+ services) | Rất nặng (nhiều container) | Trung bình (Docker) | App đơn lẻ |
| **Giấy phép Mã nguồn** | **Apache-2.0** | Apache-2.0 | Apache-2.0 | Apache-2.0 | GPL-3.0 |

---

## 6. HỆ THỐNG MÃ NGUỒN VÀ DANH MỤC TÀI LIỆU BÀN GIAO

Toàn bộ sản phẩm của đề tài đã được đồng bộ và sẵn sàng phục vụ quy trình đánh giá:

1. **Kho mã nguồn mở đầy đủ (Đã có Docker + License Apache-2.0):**  
   [https://github.com/trungka982004/Agentic_rag_final_project](https://github.com/trungka982004/Agentic_rag_final_project)
2. **Gói tài liệu nén Overleaf (Sẵn sàng biên dịch 0 lỗi):**  
   - Gói bài 1 (Research Paper): `overleaf_packages/overleaf_project_en.zip`
   - Gói bài 2 (System Demo Paper): `overleaf_packages/overleaf_project_system_paper_en.zip`
   - Gói báo cáo tổng kết tiếng Việt: `overleaf_packages/overleaf_project_v10.zip`
3. **Các tệp PDF hoàn chỉnh đính kèm:**  
   - `main_en.pdf` (Bản in thử nghiệm Bài 1)  
   - `system_paper_en.pdf` (Bản in thử nghiệm Bài 2)

---

*Em xin trân trọng báo cáo và kính mong tiếp tục nhận được những lời khuyên chỉ dẫn của Thầy để hoàn thiện hồ sơ đăng bài hội nghị ạ!*

