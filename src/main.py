#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Transcription using OpenAI's Whisper model"""


import os
import sys
from PyQt6.QtWidgets import QApplication

from modules.ui import WhisperTranscriberApp


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = WhisperTranscriberApp(ROOT_DIR)
    ex.show()
    sys.exit(app.exec())