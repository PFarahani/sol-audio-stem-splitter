# SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import warnings


def _disable_streamlit_telemetry():
    """Nuclear approach to disable all Streamlit data collection"""
    # Silence warnings about missing config
    warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")


def _override_config_paths():
    """Force all Streamlit paths to use current directory"""
    from streamlit import file_util, config

    # Patch config/credentials paths
    def patched_get_path(*path_segments):
        return str(Path.cwd() / ".streamlit" / Path(*path_segments))

    file_util.get_streamlit_file_path = patched_get_path

    # Create local config directory
    local_config = Path.cwd() / ".streamlit"
    local_config.mkdir(exist_ok=True)

    # Force empty credentials
    cred_file = local_config / "credentials.toml"
    if not cred_file.exists():
        cred_file.write_text('[general]\nemail = ""\n')


def apply_streamlit_patches():
    """Apply all necessary patches before Streamlit imports"""
    # Must be called before ANY Streamlit imports
    _disable_streamlit_telemetry()

    # Mock critical modules
    with patch.dict("sys.modules", {"streamlit.runtime.credentials": MagicMock()}):
        from streamlit.runtime import credentials

        credentials._send_email = lambda *a, **k: None
        credentials.Credentials = MagicMock()
        credentials.Credentials.get_current.return_value.activation.is_valid = True

    _override_config_paths()
