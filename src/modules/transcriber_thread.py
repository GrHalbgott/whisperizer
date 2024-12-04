#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functions to call Whisper"""


import whisper
from whisper.tokenizer import LANGUAGES
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


class TranscriberThread(QThread):
    message_box = pyqtSignal(str)

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
            self.message_box.emit(f'Success! Transcription saved to {self.output_file}')
        except Exception as e:
            self.message_box.emit(f'ERROR! An error occurred during execution:\n{e}')


class Transcriber:
    def __init__(self, message_box_callback):
        self.message_box_callback = message_box_callback
        self.thread = None

    def whisper_transcribe(self, file_path: Path, model_name: str, output_file: Path):
        self.thread = TranscriberThread(file_path, model_name, output_file)
        self.thread.message_box.connect(self.message_box_callback)
        self.thread.start()
