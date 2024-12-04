#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GUI for the Whisperizer application"""


from pathlib import Path
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtWidgets import *

from modules.transcriber_thread import Transcriber


class WhisperTranscriberApp(QWidget):
    def __init__(self, ROOT_DIR):
        super().__init__()
        self.root_dir = Path(ROOT_DIR)
        self.supported_file_types = ('.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma', '.webm')
        self.valid_extensions = ('.txt', '.md', '.html', '.log', '.xml')
        self.initUI()
        self.transcriber = Transcriber(self.progress_bar, self.show_message)

    def initUI(self):
        self.setWindowTitle('Whisperizer')
        self.setMinimumSize(500, 500)
        self.setAcceptDrops(True)

        with open(self.root_dir.parent / 'assets' / 'styles.css', 'r') as style_sheet:
            self.setStyleSheet(style_sheet.read())

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

        # TODO: multiple selection should be possible - if multiple files are selected, omit naming them in the output file name
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
        icon_path = self.root_dir.parent / 'assets' / 'tooltip.png'
        info_icon.setPixmap(QPixmap(icon_path.as_posix()).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        info_icon.setToolTip('Click to get more information and a list of available models.')
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

        # TODO: add language selection (empty for detect language automatically)

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

        # TODO: deactivate if multiple input files are chosen
        # Output file name
        self.output_file_label = QLabel('Output File Name:')
        layout.addWidget(self.output_file_label)
        self.output_file_name = QLineEdit()
        self.output_file_name.textChanged.connect(self.check_fields)
        layout.addWidget(self.output_file_name)

        # Add responsive whitespace
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Message box
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        # self.message_box = QLabel('', objectName='message')
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.message_box)
        self.scroll_area.setMinimumSize(400, 100)
        layout.addWidget(self.scroll_area)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # Transcribe button
        self.transcribe_button = QPushButton('Transcribe')
        self.transcribe_button.clicked.connect(self.transcribe)
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.setToolTip('Please select a file, output directory, and specify an output file name.')
        layout.addWidget(self.transcribe_button)

        # Cancel button
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.cancel_transcription)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)

        # Exit button
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    # TODO: add drag and drop functionality

    def openWebPage(self, event):
            QDesktopServices.openUrl(QUrl('https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages'))

    # TODO: terminate thread, not whole program
    def cancel_transcription(self):
        raise KeyboardInterrupt

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Select Audio File', 
            self.root_dir.parent.as_posix(), 
            f'Audio Files (*{" *".join(self.supported_file_types)});;All Files (*)'
        )
        if file_path:
            self.file_path.setText(file_path)
            default_output_name = Path(file_path).stem
            self.output_file_name.setText(default_output_name)

    def select_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory', self.root_dir.parent.as_posix())
        if output_dir:
            self.output_path.setText(output_dir)

    def check_fields(self):
        if self.file_path.text() and self.output_path.text() and self.output_file_name.text():
            self.transcribe_button.setEnabled(True)
        else:
            self.transcribe_button.setEnabled(False)

    def show_message(self, msg: str):
        self.message_box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.message_box.append(msg)
        self.scroll_area.verticalScrollBar()
        self.scroll_area.horizontalScrollBar()
        QApplication.processEvents()
    
    # TODO: add progress bar for multiple input files 
    def transcribe(self):
        file_path = Path(self.file_path.text())
        model_name = self.model_dropdown.currentText()
        output_dir = Path(self.output_path.text())
        output_file_name = self.output_file_name.text()
    
        output_file_path = Path(output_file_name)
        if not output_file_path.suffix:
            output_file_path = output_file_path.with_suffix('.txt')
        if output_file_path.suffix.lower() not in self.valid_extensions:
            output_file_path = output_file_path.with_suffix('.txt')
            self.show_message('Invalid extension provided as output file. Defaulting to .txt.')
    
        output_file = output_dir / output_file_path

        # TODO: while transcribing, disable transcribe button and enable cancel button. When finished, turn around
        self.cancel_button.setEnabled(True)
        self.transcribe_button.setEnabled(False)

        # TODO: make progressbar if possible (write to console output and show it here) or alternatively animation
        self.show_message('Transcribing, please wait...')
    
        try:
            self.transcriber.whisper_transcribe(file_path, model_name, output_file)
        except Exception as e:
            self.show_message(f'ERROR! An error occurred during execution:\n{e}')
