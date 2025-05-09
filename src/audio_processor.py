# SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path
from typing import List
import torch
from config import LOG_BUFFER_SIZE
from demucs.separate import main as demucs_main

torch.classes.__path__ = []

def execute_demucs(command: list[str], log_container) -> None:
    """
    Executes the Demucs audio separation tool with specified arguments,
    redirecting stdout/stderr to a log container for real-time monitoring.
    """
    args = command[1:]  # Skip executable path/name

    # Redirect stdout/stderr to log container (keep for non-progress logs)
    class Logger:
        def __init__(self, log_container):
            self.log_container = log_container
            self.log_buffer = []

        def write(self, data):
            for line in data.strip().split("\n"):
                self.log_buffer.append(line)
                self.log_container.text("\n".join(self.log_buffer[-LOG_BUFFER_SIZE:]))

        def flush(self):
            pass

    logger = Logger(log_container)
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout = logger
    sys.stderr = logger

    try:
        sys.argv = ["demucs"] + args
        demucs_main()
    finally:
        sys.stdout, sys.stderr = original_stdout, original_stderr


def process_audio(
    model_name: str, output_dir: Path, stems: List[str], extension: str = "mp3"
) -> List[Path]:
    """
    Generates output paths for separated audio stems.

    Args:
        model_name: Name of the separation model
        output_dir: Base directory for output files
        stems: List of stem names produced by the model
        extension: File format extension (default: 'mp3')

    Returns:
        List of paths where separated stems will be saved
    """
    model_dir = output_dir / model_name
    return [model_dir / f"{stem}.{extension}" for stem in stems]


def get_compute_device():
    """Return available compute device with CUDA priority"""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def cuda_enabled() -> bool:
    if torch.cuda.is_available():
        return True
    else:
        return False


def create_device_status():
    """Create status message about compute resources"""
    if cuda_enabled():
        return f"GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB)"
    return (
        "CPU: Using hardware acceleration"
        if torch.backends.mps.is_available()
        else "CPU: Basic processing"
    )
