import importlib
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()
modules_dir = Path(__file__).parent
for f in sorted(modules_dir.glob("*.py")):
    if f.stem == "__init__":
        continue
    module = importlib.import_module(f".{f.stem}", package=__name__)
    if hasattr(module, "router") and isinstance(getattr(module, "router"), APIRouter):
        router.include_router(module.router)
