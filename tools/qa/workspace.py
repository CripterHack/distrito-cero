"""Copy development code without historical evidence or user/dependency caches."""
from pathlib import Path
import shutil

def stage_workspace(root, destination):
    root=Path(root).resolve()
    ignored=shutil.ignore_patterns('.git','.worktrees','artifacts','__pycache__','.venv','node_modules','.env','.env.*')
    def select(directory,names):
        excluded=set(ignored(directory,names))
        # qa/ at repository root is history. tools/qa and legitimate src/qa are code.
        if Path(directory).resolve()==root:
            excluded.add('qa')
        return excluded
    return shutil.copytree(root,destination,ignore=select,symlinks=False)
