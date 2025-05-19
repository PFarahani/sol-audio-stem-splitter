# utils/error_handler.py

import threading
import traceback
from utils import log_error

def global_thread_excepthook(args):
    print(f"[Thread Exception] Unhandled exception in {args.thread.getName()}:")
    traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)
    log_error(args.exc_value)

def setup_global_exception_hook():
    """Call this once during app startup"""
    threading.excepthook = global_thread_excepthook