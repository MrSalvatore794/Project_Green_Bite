"""Pytest configuration.

Ensures the ``server`` directory is importable no matter which directory
pytest is run from, so tests can ``import app`` / ``import config`` reliably.
"""

import os
import sys

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)
