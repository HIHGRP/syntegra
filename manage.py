#!/usr/bin/env python3
"""Syntegra management entry point."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "syntegra.settings.dev")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
