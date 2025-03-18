#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Whisper Transcriber"""


import whisper
from whisper.tokenizer import LANGUAGES
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


class TranscriberThread(QThread):
    message_box = pyqtSignal(str)

    def __init__(self, file_path, model_name, language, output_file, mode, keep_orig):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name
        self.language = language
        self.output_file = output_file
        self.mode = mode
        self.keep_orig = keep_orig

    def run(self):
        try:
            model = whisper.load_model(self.model_name)
            audio = whisper.load_audio(str(self.file_path))
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
            _, probs = model.detect_language(mel)
            detected_language = LANGUAGES[max(probs, key=probs.get)]
            self.message_box.emit(f"Detected language: {detected_language.title()}")

            if self.mode == "transcribe" or self.keep_orig:
                self.message_box.emit("Transcribing, please wait...")
                result = model.transcribe(str(self.file_path), task="transcribe")
                self.write_to_file(result, self.output_file)
                self.message_box.emit(f"Success! Transcription saved to {self.output_file}.")
            if self.mode == "translate":
                self.message_box.emit("Transcribing and translating, please wait...")
                result = model.transcribe(str(self.file_path), task="translate", language=self.language)
                output_file = self.output_file.with_stem(f"{self.output_file.stem}_{self.language}")
                self.write_to_file(result, output_file)
                self.message_box.emit(f"Success! Translated transcription saved to {output_file}.")

        except Exception as e:
            self.message_box.emit(f"ERROR! An error occurred during execution:\n{e}")

    def write_to_file(self, result, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            text = result["text"].replace(".", ".\n")
            f.write(text)


class Transcriber:
    def __init__(self, message_box_callback):
        self.message_box_callback = message_box_callback
        self.thread = None

    def whisper_transcribe(
        self, file_path: Path, model_name: str, language: str, output_file: Path, mode: str, keep_orig: bool
    ):
        self.thread = TranscriberThread(file_path, model_name, language, output_file, mode, keep_orig)
        self.thread.message_box.connect(self.message_box_callback)
        self.thread.start()
