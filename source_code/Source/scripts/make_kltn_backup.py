import os
import sys
import zipfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKUP_DIR = ROOT / "BACKUP_KLTN_TO_USB"
BACKUP_DIR.mkdir(exist_ok=True)

print(f"=== KLTN BACKUP TOOL ===")
print(f"Root: {ROOT}")
print(f"Backup destination: {BACKUP_DIR}")

# -----------------------------------------------------------------------------
# 1. Package 1: Manuscripts, Feedback, Paper Assets, Docs & .env
# -----------------------------------------------------------------------------
pkg1_path = BACKUP_DIR / "1_KLTN_MANUSCRIPTS_FEEDBACK_CONFIG.zip"
print(f"\n[1/3] Creating {pkg1_path.name}...")

targets_pkg1 = [
    ("manuscripts", ROOT / "manuscripts"),
    ("feedback", ROOT / "feedback"),
    ("science_paper_assets", ROOT / "science_paper_assets"),
    ("overleaf_packages", ROOT / "overleaf_packages"),
    ("docs", ROOT / "docs"),
    ("env_backend.env", ROOT / "source_code/Source/.env"),
    ("env_frontend.env.local", ROOT / "source_code/Source/frontend/.env.local"),
]

with zipfile.ZipFile(pkg1_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for arc_prefix, target in targets_pkg1:
        if not target.exists():
            print(f"  Skipping (not found): {target}")
            continue
        if target.is_file():
            zf.write(target, arc_prefix)
            print(f"  Added file: {arc_prefix}")
        else:
            count = 0
            for file_path in target.rglob("*"):
                if file_path.is_file():
                    rel = file_path.relative_to(target)
                    zf.write(file_path, f"{arc_prefix}/{rel}")
                    count += 1
            print(f"  Added directory {arc_prefix}: {count} files")

pkg1_size_mb = pkg1_path.stat().st_size / (1024 * 1024)
print(f"  -> Done! Size: {pkg1_size_mb:.2f} MB")

# -----------------------------------------------------------------------------
# 2. Package 2: Vector DB & BM25 Caches
# -----------------------------------------------------------------------------
pkg2_path = BACKUP_DIR / "2_KLTN_VECTOR_DATABASE_CHROMA_BM25.zip"
print(f"\n[2/3] Creating {pkg2_path.name}...")
db_dir = ROOT / "source_code/Source/db"

with zipfile.ZipFile(pkg2_path, "w", zipfile.ZIP_DEFLATED) as zf:
    count = 0
    # Include bm25 caches, chroma.sqlite3, and vector stores
    for file_path in db_dir.rglob("*"):
        if file_path.is_file():
            # If vector_stores.zip exists, we can still include all files
            rel = file_path.relative_to(db_dir)
            zf.write(file_path, f"db/{rel}")
            count += 1
    print(f"  Added {count} files from db/")

pkg2_size_mb = pkg2_path.stat().st_size / (1024 * 1024)
print(f"  -> Done! Size: {pkg2_size_mb:.2f} MB")

# -----------------------------------------------------------------------------
# 3. Package 3: Raw Research PDFs
# -----------------------------------------------------------------------------
pkg3_path = BACKUP_DIR / "3_KLTN_RAW_PAPERS_PDFS.zip"
print(f"\n[3/3] Creating {pkg3_path.name}...")
data_dir = ROOT / "source_code/Source/data"

with zipfile.ZipFile(pkg3_path, "w", zipfile.ZIP_DEFLATED) as zf:
    count = 0
    for file_path in data_dir.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(data_dir)
            zf.write(file_path, f"data/{rel}")
            count += 1
    print(f"  Added {count} files from data/")

pkg3_size_mb = pkg3_path.stat().st_size / (1024 * 1024)
print(f"  -> Done! Size: {pkg3_size_mb:.2f} MB")

# -----------------------------------------------------------------------------
# 4. Instructions for Restoration
# -----------------------------------------------------------------------------
readme_path = BACKUP_DIR / "README_HUONG_DAN_KHOI_PHUC.txt"
with open(readme_path, "w", encoding="utf-8") as f:
    f.write("""================================================================================
HƯỚNG DẪN KHÔI PHỤC TOÀN BỘ DỰ ÁN KHÓA LUẬN TỐT NGHIỆP (KLTN) VÀ BÀI BÁO
================================================================================

Sau khi máy tính được sửa hoặc cài lại hệ điều hành, hãy làm theo các bước sau để khôi phục:

BƯỚC 1: KHÔI PHỤC MÃ NGUỒN VÀ LỊCH SỬ GIT
--------------------------------------------------------------------------------
Bạn có thể khôi phục mã nguồn bằng 1 trong 2 cách:
- CÁCH 1 (Nếu máy tính có mạng và GitHub):
    git clone https://github.com/trungka982004/Agentic_rag_final_project.git
    cd Agentic_rag_final_project
    git checkout develop

- CÁCH 2 (Dùng file KLTN_Git_Full_Repository.bundle offline không cần mạng):
    git clone KLTN_Git_Full_Repository.bundle Agentic_rag_final_project
    cd Agentic_rag_final_project
    git checkout develop

BƯỚC 2: GIẢI NÉN CÁC GÓI SAO LƯU VÀO ĐÚNG VỊ TRÍ
--------------------------------------------------------------------------------
1. Giải nén '1_KLTN_MANUSCRIPTS_FEEDBACK_CONFIG.zip' ngay tại thư mục gốc:
   - Thư mục 'manuscripts/' (2 bài báo Springer & Elsevier, file .drawio, .tex, .bib)
   - Thư mục 'feedback/' (nhận xét của Thầy)
   - Thư mục 'science_paper_assets/' (KLTN tiếng Việt v1-v10)
   - Thư mục 'overleaf_packages/' (các gói zip nộp Overleaf)
   - Thư mục 'docs/' (lộ trình và biên bản nghiệm thu)
   - File 'env_backend.env' -> Đổi tên thành: source_code/Source/.env
   - File 'env_frontend.env.local' -> Đổi tên thành: source_code/Source/frontend/.env.local

2. Giải nén '2_KLTN_VECTOR_DATABASE_CHROMA_BM25.zip':
   - Copy toàn bộ nội dung trong thư mục 'db' vào: source_code/Source/db/

3. Giải nén '3_KLTN_RAW_PAPERS_PDFS.zip':
   - Copy toàn bộ nội dung trong thư mục 'data' vào: source_code/Source/data/

BƯỚC 3: CÀI ĐẶT LẠI MÔI TRƯỜNG CHẠY (VENV & NODE)
--------------------------------------------------------------------------------
1. Backend Python:
   cd source_code/Source
   python -m venv venv
   .\\venv\\Scripts\\activate
   pip install -r requirements.txt

2. Frontend Vue.js:
   cd ../../source_code/Source/frontend
   npm install
   npm run dev

CHÚC BẠN BẢO VỆ KHÓA LUẬN VÀ XUẤT BẢN BÀI BÁO THÀNH CÔNG RỰC RỠ!
================================================================================
""")

print("\n=== SUMMARY OF BACKUP PACKAGES CREATED IN BACKUP_KLTN_TO_USB ===")
for p in BACKUP_DIR.iterdir():
    size_mb = p.stat().st_size / (1024 * 1024)
    print(f"  * {p.name:<45} : {size_mb:>8.2f} MB")
print("==================================================================")
