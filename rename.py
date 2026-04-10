import os
import fitz  # PyMuPDF library
import re

# --- CONFIGURATION ---
RAW_DATA_PATH = "data/raw"

def clean_filename(text):
    """
    Normalize text string to use as filename:
    - Remove special characters.
    - Replace spaces with underscores '_'.
    - Limit length to avoid system errors.
    """
    # 1. Remove invalid characters for filenames on Windows/Linux
    clean_name = re.sub(r'[\\/*?:"<>|]', "", text).strip()
    
    # 2. Replace spaces and separators with underscores
    clean_name = clean_name.replace(" ", "_").replace("-", "_")
    
    # 3. Remove consecutive underscores (e.g., A__B -> A_B)
    clean_name = re.sub(r'_+', "_", clean_name)
    
    # 4. Limit filename length (around 100 characters for safety)
    return clean_name[:100]

def get_pdf_title(file_path):
    """
    Extract title from the first page of the PDF file.
    """
    try:
        doc = fitz.open(file_path)
        if len(doc) == 0:
            return None
        
        # Get text blocks from page 1
        # Usually the title is in the first blocks and has a large font
        blocks = doc[0].get_text("blocks")
        
        # Sort blocks by y coordinate (top to bottom)
        blocks.sort(key=lambda b: b[1])

        for block in blocks:
            text = block[4].strip()
            # Skip strings that are too short, numbers only (page numbers), or special characters
            if len(text) > 15 and not text.isdigit():
                # Take the first line of the text block as the title
                title = text.split('\n')[0]
                return title
        return None
    except Exception as e:
        print(f"   ⚠️ Could not read PDF content: {e}")
        return None

def rename_documents():
    """
    Main function to scan and rename files in the data/raw directory.
    """
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Directory {RAW_DATA_PATH} does not exist!")
        return

    for domain in os.listdir(RAW_DATA_PATH):
        domain_path = os.path.join(RAW_DATA_PATH, domain)
        
        # Only process if it is a directory (it, math, physics, electronics)
        if not os.path.isdir(domain_path):
            continue
            
        print(f"\n--- 📂 Processing domain: {domain.upper()} ---")
        
        for filename in os.listdir(domain_path):
            if not filename.endswith(".pdf"):
                continue
                
            old_path = os.path.join(domain_path, filename)
            original_name_no_ext = filename.replace(".pdf", "")
            
            # VARIABLE TO STORE EXPECTED NEW NAME
            target_title = None

            # CASE 1: Filename starts with a number (e.g., 1706.03762v7.pdf)
            # We need to extract the actual title from inside.
            if re.match(r'^\d', filename):
                print(f"🔍 Extracting title for code: {filename}")
                extracted_title = get_pdf_title(old_path)
                target_title = extracted_title if extracted_title else original_name_no_ext
            
            # CASE 2: Filename is already text (e.g., A Survey of AI.pdf)
            # We only need to normalize underscores.
            else:
                target_title = original_name_no_ext

            # PERFORM NORMALIZATION AND RENAMING
            clean_name = clean_filename(target_title)
            new_filename = f"{clean_name}.pdf"
            new_path = os.path.join(domain_path, new_filename)

            # Check if the new name is actually different from the old name before renaming
            if filename != new_filename:
                # Handle duplicate names (add _alt suffix if file already exists)
                if os.path.exists(new_path):
                    new_path = os.path.join(domain_path, f"{clean_name}_alt.pdf")
                
                try:
                    os.rename(old_path, new_path)
                    print(f"   ✅ Renamed: {filename} -> {os.path.basename(new_path)}")
                except Exception as e:
                    print(f"   ❌ Renaming error: {e}")
            else:
                print(f"   👌 File is already in the correct format: {filename}")

if __name__ == "__main__":
    print("==============================================")
    print("   ACADEMIC FILENAME NORMALIZATION SCRIPT")
    print("==============================================")
    confirm = input("The script will batch rename files in 'data/raw'. Continue? (y/n): ")
    if confirm.lower() == 'y':
        rename_documents()
        print("\n✨ Done! Your data is ready for the Ingestion step.")
    else:
        print("❌ Operation cancelled.")