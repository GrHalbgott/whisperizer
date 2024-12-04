#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Function to call Whisper"""


import whisper
from pathlib import Path


class Transcriber:
    def transcribe(self, file_path: Path, model_name: str, output_file: Path):
        model = whisper.load_model(model_name)
        result = model.transcribe(str(file_path), verbose=False)

        with open(output_file, "w", encoding="utf-8") as f:
            result["text"] = result["text"].replace(".", ".\n")
            f.write(result["text"])