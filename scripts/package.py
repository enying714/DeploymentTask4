"""Package only intended source files; exclude local secrets, data and runtimes."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
destination = root.parent / 'output' / 'task4-handoff' / 'Task4-Full-Code-and-Guide.zip'
destination.parent.mkdir(parents=True, exist_ok=True)
excluded = {'.venv', '__pycache__', '.git', 'artifacts', 'evidence', 'local-data'}
with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in excluded for part in relative.parts):
            continue
        if path.name == '.env' or path.suffix in {'.pyc', '.db', '.pem', '.key'} or '.db-' in path.name:
            continue
        archive.write(path, Path('task4') / relative)
print(destination)
