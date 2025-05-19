# SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
# SPDX-License-Identifier: Apache-2.0

import os
from threading import Thread
import http.server
import socketserver
import time
from typing import List
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html
from config import (
    APP_NAME,
    PAGE_TITLE,
    FAVICON_PATH,
    LOGO_PATH,
    ALLOWED_EXTENSIONS,
    ABOUT_TEXT,
    MODEL_NAME,
)
from utils import load_css, load_js, replace_tqdm


def inject_custom_scripts(height: int = 0, **kwargs):
    """Inject cached JavaScript into Streamlit app"""
    js = load_js()
    if js:
        html(js, height=height, **kwargs)


def inject_custom_styles():
    """Inject cached custom CSS into Streamlit app"""
    css = load_css()
    if css:
        st.markdown(css, unsafe_allow_html=True)


class ShutdownHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_shutdown_request()

    def do_POST(self):
        self.handle_shutdown_request()

    def handle_shutdown_request(self):
        if self.path == "/shutdown":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b"Terminating server...")
            os.kill(os.getpid(), 9)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()


def run_shutdown_server():
    from streamlit import config

    port = config.get_option("server.port")
    # Different port for shutdown server
    shutdown_port = port + 1
    with socketserver.TCPServer(("", shutdown_port), ShutdownHandler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()


def render_shutdown_button():
    """Render and handle shutdown functionality"""
    if st.button("Shut Down", key="shutdown_button"):
        handle_shutdown()


def handle_shutdown():
    """Perform shutdown sequence with a real-time countdown in the warning message."""
    # Inject JavaScript to update the countdown message
    js_code = """
    <script>
    (function() {
        const countdownElement = window.parent.document.querySelector('.stAlertContainer p');
        // To update only the shutdown message
        if (countdownElement.textContent.startsWith('Shutting down the application in')) {
            let countdown = 5;
            const timer = setInterval(() => {
                countdown--;
                countdownElement.textContent = `Shutting down the application in ${countdown} seconds...`;
                if (countdown <= 0) {
                    clearInterval(timer);
                    countdownElement.textContent = 'Shutting down the application...';
                }
            }, 1000);
        }
    })();
    </script>
    """
    st.components.v1.html(js_code, height=0)

    # Display initial warning (will be updated by JavaScript)
    placeholder = st.empty()
    placeholder.warning("Shutting down the application in 5 seconds...")
    time.sleep(5)
    st.info("Please manually close this browser tab.")
    time.sleep(1)
    os.kill(os.getpid(), 9)


def config_page():
    """Configure and customize the UI"""
    st.set_page_config(
        page_title=PAGE_TITLE, page_icon=FAVICON_PATH, menu_items={"About": ABOUT_TEXT}
    )

    inject_custom_scripts()

    inject_custom_styles()

    render_shutdown_button()

    replace_tqdm()

    # Only start the shutdown server once per session
    if "shutdown_server_started" not in st.session_state:
        shutdown_thread = Thread(target=run_shutdown_server, daemon=True)
        shutdown_thread.start()
        st.session_state.shutdown_server_started = True


def render_header_section():
    """Render core elements in the header section of the app"""
    st.image(LOGO_PATH)
    st.title(APP_NAME)
    st.markdown(
        f"""
        ### AI-Powered Stem Separation

        Upload a mixed audio track ({"/".join(ALLOWED_EXTENSIONS)}) to separate audio stems.
    """
    )


def render_advanced_config() -> dict:
    """Renders an expandable advanced configuration panel and returns user-selected values"""
    from audio_processor import cuda_enabled

    with st.expander("Advanced optional configurations", expanded=False):
        st.markdown("#### Core Separation Parameters")
        model_options = MODEL_NAME
        model = st.selectbox(
            "Model Name",
            options=model_options,
            index=0,
            help="""
                ### **Model Descriptions**  
                1. **`htdemucs`**: 
                Default model for separating audio into **4 stems** (vocals, drums, bass, other). 
                Ideal for general-purpose use with balanced speed and quality.

                2. **`htdemucs_ft`**: 
                Fine-tuned version of `htdemucs` for slightly improved separation accuracy, 
                especially for vocals and instruments.

                3. **`htdemucs_6s`**: 
                Separates audio into **6 stems**: vocals, drums, bass, guitar, piano, and other. 
                Best for detailed instrumental extraction.

                4. **`hdemucs_mmi`**: 
                Uses mixture-invariant training to handle overlapping sounds better. 
                Good for complex tracks with dense instrumentation.

                5. **`mdx`**: 
                Hybrid model combining spectral and time-domain methods. 
                Focuses on vocal separation but works for other stems.
                """,
        )

        stem_mode = st.radio("Stem Mode", ["Two Stems (Vocals)", "All Stems"])
        if stem_mode == "Two Stems (Vocals)":
            stem_config = ["--two-stems", "vocals"]
        else:
            stem_config = []

        st.markdown("#### Output Format Configuration")
        col1, col2 = st.columns(2)
        with col1:
            export_format = st.selectbox(
                "Output Format", ["MP3", "WAV", "FLAC"], index=0
            )
        with col2:
            wav_bit_depth = None
            mp3_bitrate = None

            if export_format == "MP3":
                mp3_bitrate = st.selectbox(
                    "MP3 Bitrate", [320, 256, 192, 128, 96], index=0
                )
            elif export_format == "WAV":
                wav_bit_depth = st.selectbox(
                    "WAV Bit Depth",
                    options=["32-bit float", "24-bit int", "None"],
                    index=2,
                )
            else:
                None

        st.markdown("#### Hardware Configuration")

        gpu_accelerator = st.checkbox(
            "GPU accelerator",
            value=True if cuda_enabled() else False,
            disabled=not cuda_enabled(),
            help="Enable GPU acceleration (only available if CUDA is detected)",
        )
        device = "cuda" if gpu_accelerator else "cpu"
        st.info(f"Using device: {device}")

        return {
            "MODEL_NAME": model,
            "STEM_MODE": stem_config,
            "EXPORT_FORMAT": {
                "format": (
                    "--mp3"
                    if export_format == "MP3"
                    else "--flac" if export_format == "FLAC" else None
                ),
                "mp3_bitrate": (mp3_bitrate if export_format == "MP3" else None),
                "wav_bit_depth": (
                    "--float32"
                    if wav_bit_depth == "32-bit float"
                    else "--int24" if wav_bit_depth == "24-bit int" else None
                ),
            },
            "DEVICE": device,
        }


def render_file_uploader():
    """Render file uploader"""
    return st.file_uploader(
        "Choose Audio File", type=ALLOWED_EXTENSIONS, accept_multiple_files=False
    )


def render_output(stem_paths: List[Path], channels: int = 2) -> None:
    """Render audio output section with dynamic stem visualization

    Args:
        stem_paths: List of paths to separated audio stems
        channels: Number of audio channels (2, 4, or 6)
    """
    VALID_CHANNELS = (2, 4, 6)
    if channels not in VALID_CHANNELS:
        raise ValueError(f"Channels must be one of {VALID_CHANNELS}")

    stem_config = {
        2: [("🎤", "vocals"), ("🎵", "accompaniment")],
        4: [("🎤", "vocals"), ("🥁", "drums"), ("🎸", "bass"), ("🎹", "other")],
        6: [
            ("🎤", "vocals"),
            ("🥁", "drums"),
            ("🎚️", "bass"),
            ("🎸", "guitar"),
            ("🎹", "piano"),
            ("🎵", "other"),
        ],
    }

    # Validate stem count matches channel configuration
    expected_stems = channels
    if len(stem_paths) != expected_stems:
        st.error(f"Expected {expected_stems} stems, found {len(stem_paths)}")
        return

    # Render stems with error handling
    cols = st.columns(2)

    for idx, (path, (emoji, label)) in enumerate(
        zip(stem_paths, stem_config[channels])
    ):
        with cols[idx % 2]:
            if path and path.exists():
                file_format = f"audio/{path.suffix.lstrip('.')}"
                st.markdown(f"#### {emoji} {label.title()}")
                st.audio(str(path), format=file_format)
            else:
                st.error(f"{label.title()} extraction failed")


def render_processing_expander():
    """Render processing details expander"""
    with st.expander("Processing Details", expanded=False, icon="📜"):
        output_container = st.empty()

        if "progress_bar" not in st.session_state:
            st.session_state.progress_bar = st.empty()
        if "progress_text" not in st.session_state:
            st.session_state.progress_text = st.empty()

        return output_container
