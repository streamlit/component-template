import shutil
from pathlib import Path
import subprocess

project_dir = Path("{{ cookiecutter.import_name }}").absolute()

framework = "{{ cookiecutter.framework }}"
frontend_dir = project_dir / "frontend"

if framework == "React + Typescript":
    shutil.move(str(project_dir / "frontend-react"), str(frontend_dir))
    shutil.rmtree(str(project_dir / "frontend-reactless"))
elif framework == "Pure Typescript":
    shutil.move(str(project_dir / "frontend-reactless"), str(frontend_dir))
    shutil.rmtree(str(project_dir / "frontend-react"))
else:
    raise Exception(f"Unsupported option: {framework!r}")

print("Compiling frontend")
subprocess.run(["npm", "install"], cwd=frontend_dir)


print()
print("Project is ready")
print("To starts development: ")
print("1. Go to new created project:")
print(f"   $ cd {project_dir.relative_to(Path.cwd().parent)}")
print()
print("2. Open two terminal and run commands:")
print("  Terminal 1: $ npm run start")
print(f"  Terminal 2: $ streamlit run {project_dir.relative_to(Path.cwd())}/__init__.py")
