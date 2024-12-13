#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Transcription using OpenAI's Whisper model"""


import sys
import warnings
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from modules.gui import WhisperTranscriberApp


warnings.filterwarnings('ignore', category=FutureWarning)

ROOT_DIR = Path(__file__).resolve().parent


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WhisperTranscriberApp(ROOT_DIR)
    ex.show()
    sys.exit(app.exec())
    