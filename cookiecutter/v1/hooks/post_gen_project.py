import shutil
from pathlib import Path

project_dir = Path("{{ cookiecutter.import_name }}").absolute()

framework = "{{ cookiecutter.framework }}"
if framework == "React + Typescript":
    shutil.move(str(project_dir / "frontend-react"), str(project_dir / "frontend"))
    shutil.rmtree(str(project_dir / "frontend-reactless"))
elif framework == "Pure Typescript":
    shutil.move(str(project_dir / "frontend-reactless"), str(project_dir / "frontend"))
    shutil.rmtree(str(project_dir / "frontend-react"))
else:
    raise Exception(f"Unsupported option: {framework!r}")
