# SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

CACHE_DIR = Path(".cache")
OUTPUT_DIR = Path("output")
MODEL_NAME = ["htdemucs", "htdemucs_ft", "htdemucs_6s", "hdemucs_mmi", "mdx"]
ALLOWED_EXTENSIONS = ("mp3", "wav")
MAX_FILE_SIZE_MB = 200
LOG_BUFFER_SIZE = 50
ICON_PATH = str(Path(__file__).parent.absolute() / "static" / "icon.svg")
FAVICON_PATH = str(Path(__file__).parent.absolute() / "static" / "favicon.svg")
LOGO_PATH = str(Path(__file__).parent.absolute() / "static" / "logo.svg")
APP_NAME = "Sol Audio Stem Splitter"
APP_VERSION = "0.0.1"
PAGE_TITLE = "Sol"
ABOUT_TEXT = f"""
### About {APP_NAME}

{APP_NAME} is a professional-grade audio separation solution leveraging cutting-edge machine learning 
to isolate vocal and instrumental tracks with studio-quality results. Built as an individual research project, 
it combines state-of-the-art algorithms with production-grade engineering.

**Key Features:**
- 🎵 AI-powered stem separation
- 🎙️ Multi-stem isolation
- 🚀 GPU-accelerated processing via CUDA (when available)
- 🔒 Local processing - files never leave your machine
- 📊 Real-time progress monitoring

**Core Technologies:**
- 🧠 AI Engine: Facebook Research's Demucs architecture
- 🌐 Web Interface: Streamlit with custom component integration

**Technical Highlights:**
- Powered by {', '.join(MODEL_NAME).upper()} variant model
- Supports {', '.join(ALLOWED_EXTENSIONS).upper()} formats up to {MAX_FILE_SIZE_MB}MB
- Multiple output formats with metadata preservation

**Developer Information:**
- Sole Creator: [Peyman Farahani (@PFarahani)](https://github.com/PFarahani)
- Project Repository: [GitHub](https://github.com/PFarahani/sol-audio-stem-splitter)
- License: Apache 2.0 Open Source
- Version: {APP_VERSION}

*Ethical AI Statement:  
This application uses only properly licensed models and respects intellectual property rights.  
All processing occurs locally without cloud dependencies.*
"""