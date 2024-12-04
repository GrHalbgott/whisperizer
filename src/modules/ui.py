#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GUI for the Whisperizer application"""


from pathlib import Path
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtWidgets import *

from modules.transcriber import Transcriber


class WhisperTranscriberApp(QWidget):
    def __init__(self, ROOT_DIR):
        super().__init__()
        self.root_dir = ROOT_DIR
        self.transcriber = Transcriber()
        self.supported_file_types = ('.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma', '.webm')
        self.valid_extensions = ('', '.txt', '.md', '.html', '.log', '.xml')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Whisperizer')
        self.setMinimumSize(500, 500)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }
            QLabel#subtitle {
                font-size: 14px;
                color: #666;
            }
            QLabel#message {
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                padding: 10px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton:hover:!disabled {
                background-color: #0056b3;
            }
            QPushButton:pressed:!disabled {
                background-color: #004494;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)

        # Title label
        self.title_label = QLabel('Whisperizer', objectName='title')
        layout.addWidget(self.title_label)

        # Subtitle label
        self.subtitle_label = QLabel('Transcribe your audio files with OpenAI Whisper', objectName='subtitle')
        layout.addWidget(self.subtitle_label)

        ### Add responsive whitespace
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # File selection
        self.file_label = QLabel('Select Audio File:')
        layout.addWidget(self.file_label)
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.textChanged.connect(self.check_fields)
        file_layout.addWidget(self.file_path)
        self.file_button = QPushButton('Browse')
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_button)
        layout.addLayout(file_layout)

        ### Add static whitespace
        layout.addSpacing(10)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_container = QWidget()
        model_container_layout = QHBoxLayout()
        model_container.setLayout(model_container_layout)

        self.model_label = QLabel('Select Whisper Model:')
        model_container_layout.addWidget(self.model_label)
        info_icon = QLabel()
        icon_path = Path(self.root_dir).parent / 'assets' / 'tooltip.png'
        info_icon.setPixmap(QPixmap(icon_path.as_posix()).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        info_icon.setToolTip('Get more information and a list of available models.')
        info_icon.mousePressEvent = self.openWebPage
        model_container_layout.addWidget(info_icon)

        model_layout.addWidget(model_container)
        model_layout.addStretch()
        layout.addLayout(model_layout)

        ## Dropdown model selection
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(['tiny', 'base', 'small', 'medium', 'large', 'turbo'])
        self.model_dropdown.setCurrentIndex(5)
        self.model_dropdown.currentIndexChanged.connect(self.check_fields)
        layout.addWidget(self.model_dropdown)

        # Output directory selection
        self.output_label = QLabel('Select Output Directory:')
        layout.addWidget(self.output_label)
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.textChanged.connect(self.check_fields)
        output_layout.addWidget(self.output_path)
        self.output_button = QPushButton('Browse')
        self.output_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_button)
        layout.addLayout(output_layout)

        ### Add static whitespace
        layout.addSpacing(10)

        # Output file name
        self.output_file_label = QLabel('Output File Name:')
        layout.addWidget(self.output_file_label)
        self.output_file_name = QLineEdit()
        self.output_file_name.textChanged.connect(self.check_fields)
        layout.addWidget(self.output_file_name)

        ### Add static whitespace
        layout.addSpacing(10)

        # Message label
        self.message_label = QLabel('', objectName='message')
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.message_label)
        layout.addWidget(self.scroll_area)

        # Add responsive whitespace
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Transcribe button
        self.transcribe_button = QPushButton('Transcribe')
        self.transcribe_button.clicked.connect(self.transcribe)
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.setToolTip('Please select a file, output directory, and specify an output file name.')
        layout.addWidget(self.transcribe_button)

        # Exit button
        # TODO: either should be clickable when executing to halt the process or add a "Cancel" button
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)


    def openWebPage(self, event):
            QDesktopServices.openUrl(QUrl('https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages'))


    # TODO: first path to open should be script path (of main) rather than working directory - try packaged version
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Select Audio File', 
            '', 
            f'Audio Files (*{" *".join(self.supported_file_types)});;All Files (*)'
        )
        if file_path:
            self.file_path.setText(file_path)
            default_output_name = Path(file_path).stem
            self.output_file_name.setText(default_output_name)


    def select_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if output_dir:
            self.output_path.setText(output_dir)


    def check_fields(self):
        if self.file_path.text() and self.output_path.text() and self.output_file_name.text():
            self.transcribe_button.setEnabled(True)
        else:
            self.transcribe_button.setEnabled(False)

    
    # TODO: append to this widget rather than overwriting (to be able to see what happened) 
    def show_message(self, msg: str):
        self.message_label.setText(msg)
        self.scroll_area.verticalScrollBar()
        self.scroll_area.horizontalScrollBar()
        QApplication.processEvents()
    

    def transcribe(self):
        file_path = Path(self.file_path.text())
        model_name = self.model_dropdown.currentText()
        output_dir = Path(self.output_path.text())
        output_file_name = self.output_file_name.text()

        self.show_message('Transcribing...')
    
    # TODO: also check if suffix exists in the first place
        output_file_path = Path(output_file_name)
        if output_file_path.suffix.lower() not in self.valid_extensions:
            output_file_path = output_file_path.with_suffix('.txt')
            self.show_message('Invalid extension provided. Defaulting to .txt')
    
        output_file = output_dir / output_file_path
    
        try:
            self.transcriber.transcribe(file_path, model_name, output_file)
            self.show_message(f'Success! Transcription saved to {output_file}')
        except Exception as e:
            self.show_message(f'ERROR! An error occurred during execution:\n\n{e}')

