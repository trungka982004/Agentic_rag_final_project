# 04. ĐẶC TẢ GIAO DIỆN LẬP TRÌNH (API & WEBSOCKET SPECS)
## Đặc tả Chi tiết các RESTful Endpoints và Giao thức WebSocket Đồng bộ Canvas thời gian thực

---

### 1. CÁC RESTFUL API MỚI (BACKEND FASTAPI)

Tất cả các endpoint đều yêu cầu xác thực JWT qua Header: `Authorization: Bearer <access_token>`.

#### 1.1. Nhóm Quản lý Dự án Bài báo (Project Management)

##### `POST /api/projects`
Tạo một dự án bài báo mới.
* **Request Body:**
  ```json
  {
    "title": "Adaptive Agentic RAG with Tiered Knowledge Routing",
    "template_type": "ieee_conference",
    "target_venue": "IEEE Transactions on AI",
    "primary_domain": "it",
    "abstract_text": "Retrieval-Augmented Generation (RAG) mitigates hallucination..."
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "id": "7a3f89e2-411a-4f51-b88a-9231f41d9c12",
    "title": "Adaptive Agentic RAG with Tiered Knowledge Routing",
    "template_type": "ieee_conference",
    "sections_count": 5,
    "created_at": "2026-11-04T08:00:00Z"
  }
  ```

##### `GET /api/projects/{id}`
Lấy chi tiết dự án, bao gồm danh sách các chương mục (sections) và danh mục tài liệu tham khảo (references).
* **Response (200 OK):**
  ```json
  {
    "id": "7a3f89e2-411a-4f51-b88a-9231f41d9c12",
    "title": "Adaptive Agentic RAG with Tiered Knowledge Routing",
    "sections": [
      {"id": "s1", "title": "1. Introduction", "slug": "introduction", "order_index": 1, "word_count": 450},
      {"id": "s2", "title": "2. Related Work", "slug": "related_work", "order_index": 2, "word_count": 820}
    ],
    "references": [
      {"id": "r1", "bibtex_key": "vaswani2017attention", "title": "Attention Is All You Need", "year": 2017}
    ]
  }
  ```

#### 1.2. Nhóm Quản lý Nội dung Chương mục (Paper Sections)

##### `PUT /api/projects/{id}/sections/{section_id}`
Lưu tự động nội dung bản thảo khi người dùng đang gõ (Auto-save).
* **Request Body:**
  ```json
  {
    "content_markdown": "# 1. Introduction\n\nRetrieval-Augmented Generation has emerged as...",
    "word_count": 520
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": "saved",
    "updated_at": "2026-11-04T08:05:22Z"
  }
  ```

#### 1.3. Nhóm Trích dẫn & Tọa độ Bounding Box (Citations & Coordinates)

##### `GET /api/documents/{domain}/{doc_name}/spans`
Lấy danh sách tọa độ bounding box của các đoạn văn trong file PDF để phục vụ việc bôi vàng đối chiếu.
* **Query Parameters:** `page` (tùy chọn).
* **Response (200 OK):**
  ```json
  {
    "document_name": "bge_m3_paper.pdf",
    "total_spans": 142,
    "spans": [
      {
        "id": "span_48",
        "page_number": 3,
        "bbox": [0.125, 0.442, 0.880, 0.495],
        "text_content": "BGE-M3 supports dense, sparse lexical, and multi-vector representations..."
      }
    ]
  }
  ```

##### `GET /api/documents/{domain}/{doc_name}/pdf`
Stream file nhị phân PDF để `react-pdf` ở Zone 3 tải về render trực tiếp.

#### 1.4. Nhóm Biên dịch & Xuất bản (Compile & Export)

##### `POST /api/projects/{id}/compile`
Kích hoạt trình biên dịch Tectonic/LaTeX cục bộ trên server.
* **Response (200 OK):**
  ```json
  {
    "compile_status": "success",
    "pdf_url": "/api/projects/7a3f89e2-411a-4f51-b88a-9231f41d9c12/download-pdf",
    "log_output": "Output written on main.pdf (6 pages, 420,123 bytes)..."
  }
  ```

##### `GET /api/projects/{id}/export-overleaf`
Tải về tệp `.zip` đầy đủ mã nguồn TeX, file `.bib`, hình ảnh 300 DPI sẵn sàng import lên Overleaf.

---

### 2. GIAO THỨC WEBSOCKET ĐỒNG BỘ TRỢ LÝ AI (CANVAS COPILOT WEBSOCKET)

* **Endpoint:** `WS /api/ws/studio/{project_id}`
* **Xác thực:** Token truyền qua query param: `?token=<jwt_access_token>`.

#### 2.1. Client Gửi Yêu cầu (Client Events)

##### A. Gợi ý Trích dẫn Thông minh (Action: `suggest_citation`)
Gửi câu khẳng định đang viết để tìm bài báo minh chứng trong 618 bài:
```json
{
  "action": "suggest_citation",
  "section_id": "s1",
  "context_text": "Traditional dense retrievers suffer from cross-domain lexical mismatch when handling technical keywords.",
  "domain": "it"
}
```

##### B. Chuốt Văn phong Học thuật (Action: `refine_tone`)
Yêu cầu viết lại đoạn văn bản đã bôi đen:
```json
{
  "action": "refine_tone",
  "raw_text": "We ran experiments and our system is way faster than CRAG.",
  "tone_target": "academic_formal"
}
```

##### C. Lập Ma trận So sánh Bài báo (Action: `generate_review_matrix`)
Yêu cầu lập bảng so sánh đối đầu giữa các bài báo:
```json
{
  "action": "generate_review_matrix",
  "selected_papers": [
    "bge_m3_paper.pdf",
    "crag_corrective_rag.pdf",
    "self_rag_framework.pdf"
  ]
}
```

#### 2.2. Server Stream Kết quả Về (Server Telemetry & Payload Events)

##### A. Trả về Tiến trình Suy luận của LangGraph (Event: `node_update`)
Cập nhật huy hiệu trạng thái lên giao diện:
```json
{
  "event": "node_update",
  "current_node": "citation_suggest_node",
  "status": "Searching across 130 Computer Science papers for exact evidence..."
}
```

##### B. Trả về Kết quả Gợi ý Trích dẫn (Event: `citation_match`)
Trả về bài báo phù hợp kèm tọa độ chính xác:
```json
{
  "event": "citation_match",
  "bibtex_key": "chen2024bge",
  "document_name": "bge_m3_paper.pdf",
  "title": "BGE-M3: Multi-Functionality, Multi-Granularity for Information Retrieval",
  "page_number": 3,
  "matched_excerpt": "...sparse lexical matching ensures exact terminology preservation across domains...",
  "bbox": [0.125, 0.442, 0.880, 0.495],
  "confidence_score": 0.94
}
```

##### C. Trả về Văn bản đã Chuốt (Event: `refine_complete`)
```json
{
  "event": "refine_complete",
  "original_text": "We ran experiments and our system is way faster than CRAG.",
  "refined_text": "Empirical evaluations substantiate that the proposed architecture demonstrates statistically significant latency reduction compared to the CRAG baseline.",
  "improvements": [
    "Replaced informal phrasing 'way faster' with 'demonstrates statistically significant latency reduction'",
    "Adopted third-person academic passive tone"
  ]
}
```

