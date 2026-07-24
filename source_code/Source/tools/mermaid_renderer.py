import subprocess
import os
import uuid
from typing import Optional

def render_mermaid_to_image(mmd_code: str, output_dir: str = "temp_assets") -> Optional[str]:
    """
    Render Mermaid code to a PNG image using mermaid-cli (mmdc).
    
    Args:
        mmd_code: The raw mermaid diagram code.
        output_dir: Directory to save the temporary image.
        
    Returns:
        Path to the generated PNG file, or None if failed.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_id = str(uuid.uuid4())[:8]
    mmd_file = os.path.join(output_dir, f"diagram_{file_id}.mmd")
    png_file = os.path.join(output_dir, f"diagram_{file_id}.png")
    
    # Clean up mermaid code
    mmd_code = mmd_code.replace("```mermaid", "").replace("```", "").strip()
    
    # Self-healing: if there is no 'subgraph' in the flowchart, any standalone 'end' is a syntax error
    lines = mmd_code.splitlines()
    cleaned_lines = []
    has_subgraph = any("subgraph" in line.lower() for line in lines)
    for line in lines:
        stripped = line.strip()
        if not has_subgraph and (stripped.lower() == "end" or stripped.lower() == "end;"):
            continue
        cleaned_lines.append(line)
    mmd_code = "\n".join(cleaned_lines)
    
    # Write mermaid code to temp file
    with open(mmd_file, "w", encoding="utf-8") as f:
        f.write(mmd_code)
        
    try:
        # Check if local node_modules mmdc exists
        local_mmdc = os.path.join("node_modules", ".bin", "mmdc.cmd")
        if os.path.exists(local_mmdc):
            mmdc_path = f'"{os.path.abspath(local_mmdc)}"'
        else:
            mmdc_path = "mmdc" # fallback to global
            
        # Execute mmdc
        cmd = f'{mmdc_path} -i "{os.path.abspath(mmd_file)}" -o "{os.path.abspath(png_file)}" -b white'
        print(f"[Mermaid Renderer] Executing: {cmd}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        
        if os.path.exists(png_file):
            # Clean up the .mmd file
            os.remove(mmd_file)
            return os.path.abspath(png_file)
            
    except Exception as e:
        print(f"[Mermaid Renderer] Error: {e}")
        if os.path.exists(mmd_file):
            os.remove(mmd_file)
            
    return None
