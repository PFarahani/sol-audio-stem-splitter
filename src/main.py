# SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
# SPDX-License-Identifier: Apache-2.0

import streamlit_config
streamlit_config.apply_streamlit_patches()

import sys
import os
from pathlib import Path
import streamlit as st
import streamlit.web.cli as stcli
from config import OUTPUT_DIR
from frontend.ui import (
    render_header_section,
    render_file_uploader,
    render_processing_expander,
    render_output,
    config_page,
    render_advanced_config,
)
from utils import setup_environment, resolve_path
from audio_processor import execute_demucs, process_audio



def main_flow():

    render_header_section()

    config = render_advanced_config()
    uploaded_file = render_file_uploader()

    # Export Format Configuration
    export_cfg = config["EXPORT_FORMAT"]
    format_args = []
    if export_cfg["format"]:
        format_args.append(export_cfg["format"])
        if export_cfg["format"] == "--mp3" and export_cfg["mp3_bitrate"]:
            format_args += ["--mp3-bitrate", str(export_cfg["mp3_bitrate"])]
    elif export_cfg["wav_bit_depth"]:
        if export_cfg["wav_bit_depth"] == 32:
            format_args.append("--float32")
        elif export_cfg["wav_bit_depth"] == 24:
            format_args.append("--int24")

    if not uploaded_file:
        return

    # Update session state
    if (
        config != st.session_state.config
        or uploaded_file != st.session_state.uploaded_file
    ):
        st.session_state.submitted = False  # Reset submission on config/file change
    st.session_state.config = config
    st.session_state.uploaded_file = uploaded_file

    if st.button("Submit for Processing", disabled=not uploaded_file):
        st.session_state.submitted = True


    # Execute only when submitted
    if st.session_state.submitted and uploaded_file:

        try:
            setup_environment()

            with st.spinner("Processing..."):
                output_dir = OUTPUT_DIR / uploaded_file.name
                output_dir.mkdir(parents=True, exist_ok=True)
                input_path = output_dir / uploaded_file.name

                if not input_path.exists():
                    input_path.write_bytes(uploaded_file.getvalue())
                output_container = render_processing_expander()
                execute_demucs(
                    [
                        (
                            "demucs"
                            if not getattr(sys, "frozen", False)
                            else str(Path(sys._MEIPASS) / "demucs.exe")
                        ),
                        *config["STEM_MODE"],
                        "-n", config["MODEL_NAME"],
                        "-o", str(output_dir),
                        "--filename", "{stem}.{ext}",
                        *format_args, "-d",
                        config["DEVICE"], str(input_path),
                    ],
                    output_container,
                )

                # Determine stems based on configuration
                if config["STEM_MODE"] and config["STEM_MODE"][0] == "--two-stems":
                    stems = ["vocals", "no_vocals"]
                elif not config["STEM_MODE"] and config["MODEL_NAME"] == "htdemucs_6s":
                    stems = ["vocals", "drums", "bass", "guitar", "piano", "other"]
                else:
                    stems = ["vocals", "drums", "bass", "other"]

                output_paths = process_audio(
                    config["MODEL_NAME"], output_dir, stems, extension="mp3"
                )

                render_output(output_paths, channels=len(output_paths))

        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            st.exception(e)
            st.session_state.submitted = False


def main():
    """Main application entry point"""
    # Initialize session state

    if "submitted" not in st.session_state:
        st.session_state.submitted = False
        st.session_state.config = {}
        st.session_state.uploaded_file = None

    # Ensure package metadata is accessible [PyInstaller]
    if getattr(sys, "frozen", False):
        os.environ["PYTHONPATH"] = os.pathsep.join(
            [
                os.path.join(sys._MEIPASS, "importlib_metadata"),
                os.path.join(sys._MEIPASS, "streamlit"),
                os.environ.get("PYTHONPATH", ""),
            ]
        )

    config_page()

    main_flow()


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        # Splash Screen
        try:
            import pyi_splash
            pyi_splash.close()
        except:
            pass

    if st.runtime.exists():
        main()

    else:
        sys.argv = [
            "streamlit",
            "run",
            resolve_path(__file__),
            "--global.developmentMode=false",
            "--browser.gatherUsageStats=false"
        ]
        sys.exit(stcli.main())