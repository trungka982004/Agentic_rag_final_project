import os
import zipfile
import glob

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(base_dir)
pkg_dir = os.path.join(root_dir, 'overleaf_packages')
os.makedirs(pkg_dir, exist_ok=True)

image_files = glob.glob(os.path.join(base_dir, 'science_paper_images', '*.*'))
ref_file = os.path.join(base_dir, 'references.bib')

projects = [
    {
        'zip_name': 'overleaf_project_en.zip',
        'tex_file': os.path.join(base_dir, 'main_en.tex')
    },
    {
        'zip_name': 'overleaf_project_v10.zip',
        'tex_file': os.path.join(base_dir, 'Agentic_RAG_Scientific_Report_VN_v10.tex')
    },
    {
        'zip_name': 'overleaf_project_system_paper_en.zip',
        'tex_file': os.path.join(base_dir, 'system_paper_en.tex')
    }
]

for p in projects:
    zip_path = os.path.join(pkg_dir, p['zip_name'])
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(p['tex_file'], arcname='main.tex')
        if os.path.exists(ref_file):
            z.write(ref_file, arcname='references.bib')
        for img in image_files:
            rel_name = os.path.join('science_paper_images', os.path.basename(img))
            z.write(img, arcname=rel_name)
    print(f"Repackaged: {zip_path}")
