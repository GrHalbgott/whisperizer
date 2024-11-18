#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Uses Whisper AI for transcription"""


import os
import sys
import whisper
from pathlib import Path


def main(file: str=None):
    '''Transcribe audio files using Whisper AI'''

    # Preliminaries
    in_dir = Path("audiofiles")
    out_dir = Path("transcriptions")
    model = whisper.load_model("turbo")

    # Finding files to transcribe
    files_to_transcribe = [file] if file else os.listdir(in_dir)

    # Transcribe    
    for file in files_to_transcribe:
        result = model.transcribe(str(in_dir / file), verbose=False)
        
        with open(out_dir / f"{file}.txt", "w", encoding="utf-8") as f:
            result["text"] = result["text"].replace(".", ".\n")
            f.write(result["text"])

    sys.exit("FINISHED.")

if __name__ == "__main__":

    file = input("Enter the file name you want to transcribe: ")

    main(file)

    
