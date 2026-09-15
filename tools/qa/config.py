"""Explicit configuration. QA never writes over historical evidence or user profiles."""
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Config:
    root: Path
    output: Path
    browser: str | None = None
    timeout: float = 600
    origin: str = 'fixture'
    headed: bool = False
    display: str | None = None

    def validate(self):
        root, output = self.root.resolve(), self.output.resolve()
        if not (root/'index.html').is_file() or not (root/'src').is_dir():
            raise ValueError('Root must contain index.html and src/.')
        # Compare to the lexical artifact directory too, rejecting symlink escapes.
        base = root/'artifacts'
        if output == base or not output.is_relative_to(base):
            raise ValueError('Output must be a NEW child of <root>/artifacts/.')
        if base.resolve() != base:
            raise ValueError('Artifact root must not escape through a symlink.')
        if self.origin not in ('fixture', 'http'):
            raise ValueError('Origin must be fixture or http.')
        if not 0 < self.timeout <= 3600:
            raise ValueError('Timeout must be in (0, 3600] seconds.')
        if self.browser and (not Path(self.browser).is_file() or not os.access(self.browser,os.X_OK)):
            raise ValueError('Browser must be an executable path, or omitted for Playwright bundled Chromium.')
        return self
