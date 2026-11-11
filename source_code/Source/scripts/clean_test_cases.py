import json
import re

TEST_CASES_PATH = "source_code/Source/test_cases.json"

with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)

hardware_fixed = 0
ground_truth_cleaned = 0

for item in cases:
    q = item.get("question", "")
    domain = item.get("domain", "").lower()
    
    # 1. Fix mismatched hardware design template
    match = re.search(r"What are the hardware design methodologies and challenges described in ['\"](.*?)['\"]", q)
    if match:
        paper_name = match.group(1).strip()
        if domain == "it":
            item["question"] = f"What are the algorithmic methodologies, model architectures, and technical challenges described in '{paper_name}'?"
        elif domain == "math":
            item["question"] = f"What are the mathematical formulations, analytical proofs, and theoretical principles described in '{paper_name}'?"
        elif domain == "physics":
            item["question"] = f"What are the physical principles, theoretical frameworks, and experimental methods described in '{paper_name}'?"
        elif domain == "electronics":
            item["question"] = f"What are the circuit design methodologies, hardware architectures, and implementation challenges described in '{paper_name}'?"
        hardware_fixed += 1
        
    # 2. Clean ground_truth
    gt = item.get("ground_truth", "")
    if gt:
        cleaned_gt = gt
        # Remove template prefix
        if cleaned_gt.startswith("Based on academic resources, "):
            cleaned_gt = cleaned_gt[len("Based on academic resources, "):].strip()
        elif cleaned_gt.startswith("Based on academic resources,"):
            cleaned_gt = cleaned_gt[len("Based on academic resources,"):].strip()
            
        # Fix hyphenated word breaks (e.g. "differ-\nent" -> "different")
        cleaned_gt = re.sub(r'([a-zA-Z]+)-\s*\n\s*([a-zA-Z]+)', r'\1\2', cleaned_gt)
        
        # Replace single newlines within text with a space (preserving paragraphs)
        cleaned_gt = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned_gt)
        cleaned_gt = re.sub(r'[ \t]+', ' ', cleaned_gt).strip()
        
        if cleaned_gt != gt:
            item["ground_truth"] = cleaned_gt
            ground_truth_cleaned += 1

with open(TEST_CASES_PATH, "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=4, ensure_ascii=False)

print(f"Fixed {hardware_fixed} mismatched hardware design questions.")
print(f"Cleaned {ground_truth_cleaned} ground truth reference excerpts.")

