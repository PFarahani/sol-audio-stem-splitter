# SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
# SPDX-License-Identifier: Apache-2.0

import os
import time
from pathlib import Path
import streamlit as st
from config import CACHE_DIR, OUTPUT_DIR

class StreamlitTqdm:
    def __init__(
        self, iterable=None, total=None, disable=False, desc=None, unit=None, **kwargs
    ):
        self.iterable = iterable
        self.total = total or (len(iterable) if iterable else 100)
        self.disable = disable
        self.n = 0
        self.start_time = time.time()
        self.desc = desc or "Processing"
        self.unit = unit or "it"

        # Get containers from session state
        self.progress_container = st.session_state.get("progress_bar")
        self.text_container = st.session_state.get("progress_text")

        if not self.progress_container or not self.text_container:
            raise ValueError("Progress containers not initialized")

    def update(self, n=1):
        if self.disable:
            return

        self.n += n
        elapsed = time.time() - self.start_time
        progress = self.n / self.total if self.total else 0
        eta = (elapsed / (progress) - elapsed) if progress > 0 else 0

        self.progress_container.progress(progress)
        self.text_container.text(
            f"{self.desc}: {int(progress*100)}% | "
            f"Elapsed: {elapsed:.1f}s | "
            f"ETA: {eta:.1f}s | "
            f"{self.unit}/s: {self.n/(elapsed+1e-8):.1f}"
        )

    def __iter__(self):
        if self.iterable is None:
            raise ValueError("Iterable not provided")

        for item in self.iterable:
            yield item
            self.update()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass


def replace_tqdm():
    """Apply custom patch to tqdm"""
    from demucs import apply, repo

    apply.tqdm.tqdm = StreamlitTqdm
    repo.torch.hub.tqdm = StreamlitTqdm


def resolve_path(path: str) -> str:
    return os.path.abspath(os.path.join(os.getcwd(), path))


def load_js(file_name: str = "main.js") -> str:
    """Load JavaScript content from file and wrap in <script> tags"""
    js_dir = Path(__file__).parent / "frontend/scripts"
    js_file = js_dir / file_name

    if not js_file.exists():
        st.error(f"JavaScript file not found: {js_file}")
        return ""

    with open(js_file, "r") as f:
        js_content = f.read()

    return f"<script>\n{js_content}\n</script>"


def load_css(file_name: str = "main.css") -> str:
    """Load CSS content from file and wrap in <style> tags"""
    css_dir = Path(__file__).parent / "frontend/styles"
    css_file = css_dir / file_name

    if not css_file.exists():
        st.error(f"CSS file not found: {css_file}")
        return ""

    with open(css_file, "r") as f:
        css_content = f.read()

    return f"<style>\n{css_content}\n</style>"


def setup_environment():
    """Initialize required directories and environment variables"""
    CACHE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    os.environ["TORCH_HOME"] = str(CACHE_DIR)
