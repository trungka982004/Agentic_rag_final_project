import json
import os
import re
import time
import sys

# Force sys.stdout and sys.stderr to use UTF-8 to prevent encoding errors on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add parent directory to sys.path to allow importing local_rag
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_rag import retrieve_context

def clean_name(name):
    # remove extension and clean underscores/hyphens/parentheses
    name = re.sub(r'\.pdf$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[\-_()\'\"]', ' ', name)
    return ' '.join(name.split()).lower()

def find_pdf_for_question(question, domain):
    domain_path = os.path.join("data/raw", domain)
    if not os.path.exists(domain_path):
        return []
    
    question_clean = question.lower()
    matches = []
    
    # Try finding exact titles in quotes or match by title words
    for file in os.listdir(domain_path):
        if not file.endswith(".pdf"):
            continue
        c_name = clean_name(file)
        # Check if the cleaned file name is in the question
        if c_name in question_clean:
            matches.append(file)
            
    # Fallback: if no direct match, check if any word from file is in question (for short/fuzzy names)
    if not matches:
        for file in os.listdir(domain_path):
            if not file.endswith(".pdf"):
                continue
            c_name = clean_name(file)
            # if c_name is long enough and contains at least 3 words, check if it partially matches
            words = c_name.split()
            if len(words) >= 3:
                phrase = " ".join(words[:3]) # match first 3 words
                if phrase in question_clean:
                    matches.append(file)
                    
    return matches

def clean_context_for_ground_truth(context):
    if not context or "No database found" in context or "No relevant information" in context or "Error occurred" in context:
        return None
    # Strip the "--- Source: ... ---" headers
    cleaned = re.sub(r'--- Source:.*?\n', '', context)
    cleaned = cleaned.strip()
    # Take the first 2-3 sentences or first 250 characters
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    selected_sentences = []
    char_count = 0
    for s in sentences:
        if char_count > 250:
            break
        selected_sentences.append(s)
        char_count += len(s)
    
    result = " ".join(selected_sentences).strip()
    if len(result) > 300:
        result = result[:297] + "..."
    return result

def main():
    input_file = "test_cases.json"
    output_file = "test_cases.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print("[*] Reading test cases...")
    with open(input_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    # Check if already migrated
    if cases and "test_case_id" in cases[0]:
        print("[*] test_cases.json is already migrated!")
        return

    print(f"[*] Migrating {len(cases)} test cases with fast retrieval...")
    migrated_cases = []
    
    for i, case in enumerate(cases):
        cid = case.get("id", i + 1)
        domain = case.get("domain", "physics")
        question = case.get("question", "")
        
        # 1. Determine type
        # Alternate Simple RAG and Agentic Reflection
        run_type = "Simple RAG" if cid % 2 != 0 else "Agentic Reflection"
        
        # 2. Determine test_case_id prefix
        prefix = "TC_SIM" if run_type == "Simple RAG" else "TC_AGT"
        test_case_id = f"{prefix}_{str(cid).zfill(3)}"
        
        # 3. Find expected source document
        matches = find_pdf_for_question(question, domain)
        expected_source_document = matches
        
        # 4. Fast ground truth extraction from vector DB
        context = ""
        if expected_source_document:
            context = retrieve_context(question, domain, k=1, target_file=expected_source_document[0])
        else:
            context = retrieve_context(question, domain, k=1)
            
        gt_snippet = clean_context_for_ground_truth(context)
        if gt_snippet:
            ground_truth = f"Based on academic resources, {gt_snippet}"
        else:
            ground_truth = f"Ground truth answer regarding: {question}"

        # 5. Define evaluation_criteria
        if expected_source_document:
            evaluation_criteria = f"The system must accurately retrieve information from file {expected_source_document[0]} and return a precise and complete answer."
        else:
            evaluation_criteria = "The system must correctly route to the appropriate domain and return an accurate response based on the retrieved context."

        migrated_cases.append({
            "test_case_id": test_case_id,
            "type": run_type,
            "question": question,
            "ground_truth": ground_truth,
            "expected_source_document": expected_source_document,
            "evaluation_criteria": evaluation_criteria,
            # Keep domain as helper hidden field
            "domain": domain
        })
        
        # Print with unicode characters handled (encoded to string to avoid errors on Windows cmd)
        try:
            print(f"[{i+1}/{len(cases)}] Migrated {test_case_id} | Type: {run_type} | PDF: {expected_source_document}")
        except Exception:
            # Fallback print if encoding still fails
            print(f"[{i+1}/{len(cases)}] Migrated {test_case_id} | Type: {run_type}")
        
        # Save progress incrementally to a temp file, then rename at the end to be safe
        if (i + 1) % 10 == 0 or (i + 1) == len(cases):
            with open("test_cases_temp.json", "w", encoding="utf-8") as out:
                json.dump(migrated_cases, out, ensure_ascii=False, indent=4)
            print(f"[*] Saved progress to test_cases_temp.json")

    # Rename temp file to output_file
    if os.path.exists("test_cases_temp.json"):
        if os.path.exists(output_file):
            os.remove(output_file)
        os.rename("test_cases_temp.json", output_file)
        print(f"[*] Successfully wrote final output to {output_file}")
    
    print("[*] Migration completed successfully!")

if __name__ == "__main__":
    main()
