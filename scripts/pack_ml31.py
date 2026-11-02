import zipfile
from pathlib import Path

root = Path('build/ml31_breakthrough')
out_zip = Path('build/portfolios/submission_ml31_breakthrough.zip')
out_zip.parent.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file():
            arcname = p.relative_to(root).as_posix()
            z.write(p, arcname=arcname)
            print(f'Added {arcname}')

print('Done. Total size:', out_zip.stat().st_size)
