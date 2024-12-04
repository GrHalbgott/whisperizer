#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functions to call Whisper"""


import whisper
from whisper.tokenizer import LANGUAGES
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


class TranscriberThread(QThread):
    progress = pyqtSignal(int)
    message_box = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path, model_name, output_file):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name
        self.output_file = output_file

    def run(self):
        try:
            model = whisper.load_model(self.model_name)
            audio = whisper.load_audio(str(self.file_path))
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
            _, probs = model.detect_language(mel)
            self.message_box.emit(f'Detected language: {LANGUAGES[max(probs, key=probs.get)].title()}')
            options = whisper.DecodingOptions()
            result = whisper.decode(model, mel, options)

            with open(self.output_file, 'w', encoding='utf-8') as f:
                text = result.text.replace('.', '.\n')
                f.write(text)
            self.finished.emit(f'Success! Transcription saved to {self.output_file}')
        except Exception as e:
            self.error.emit(f'ERROR! An error occurred during execution:\n{e}')


class Transcriber:
    def __init__(self, progress_bar, message_box_callback):
        self.progress_bar = progress_bar
        self.message_box_callback = message_box_callback
        self.thread = None

    def whisper_transcribe(self, file_path: Path, model_name: str, output_file: Path):
        self.thread = TranscriberThread(file_path, model_name, output_file)
        self.thread.progress.connect(self.update_progress)
        self.thread.message_box.connect(self.message_box_callback)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self, message):
        self.progress_bar.setValue(100)
        self.message_box_callback(message)

    def on_error(self, message):
        self.message_box_callback(message)
