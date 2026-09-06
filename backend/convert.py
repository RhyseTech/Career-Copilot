import os
import pymupdf as fitz

pdf_dir = r'R:\Company Portal\products\2.Carrer_Copilot\rendercv\examples'
out_dir = r'R:\Company Portal\products\2.Carrer_Copilot\frontend\public\templates'

os.makedirs(out_dir, exist_ok=True)

theme_map = {
    'ClassicTheme': 'classic',
    'EmberTheme': 'ember',
    'EngineeringclassicTheme': 'engineeringclassic',
    'EngineeringresumesTheme': 'engineeringresumes',
    'HarvardTheme': 'harvard',
    'InkTheme': 'ink',
    'ModerncvTheme': 'moderncv',
    'OpalTheme': 'opal',
    'Sb2novTheme': 'sb2nov'
}

for f in os.listdir(pdf_dir):
    if f.endswith('.pdf'):
        theme_id = None
        for key, val in theme_map.items():
            if key in f:
                theme_id = val
                break
        
        if theme_id:
            pdf_path = os.path.join(pdf_dir, f)
            try:
                doc = fitz.open(pdf_path)
                page = doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                out_path = os.path.join(out_dir, f'{theme_id}.png')
                pix.save(out_path)
                print(f'Saved {out_path}')
            except Exception as e:
                print(f'Failed {f}: {e}')
