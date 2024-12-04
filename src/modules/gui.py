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
        self.transcriber = Transcriber(self.show_message)

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

        # File selection
        self.file_label = QLabel('Select Audio File(s):')
        layout.addWidget(self.file_label)
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.textChanged.connect(self.check_fields)
        file_layout.addWidget(self.file_path)
        self.file_button = QPushButton('Browse')
        self.file_button.clicked.connect(self.select_files)
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

        # Output file name
        self.output_file_label = QLabel('Output File Name:')
        layout.addWidget(self.output_file_label)
        self.output_file_name = QLineEdit()
        self.output_file_name.textChanged.connect(self.check_fields)
        layout.addWidget(self.output_file_name)
        self.output_file_label.setEnabled(False)
        self.output_file_name.setEnabled(False)

        # Add responsive whitespace
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Message box
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        self.message_box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.message_box)
        self.scroll_area.setMinimumSize(400, 100)
        self.scroll_area.verticalScrollBar()
        self.scroll_area.horizontalScrollBar()
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

    def select_files(self):
        self.selected_files, _ = QFileDialog.getOpenFileNames(
            self, 
            'Select Audio File', 
            self.root_dir.parent.as_posix(), 
            f'Audio Files (*{" *".join(self.supported_file_types)});;All Files (*)'
        )
        if self.selected_files:
            self.file_path.setText("; ".join(self.selected_files))

            if len(self.selected_files) == 1:
                default_output_name = Path(self.selected_files[0]).stem
                self.output_file_name.setText(default_output_name)
                self.output_file_label.setEnabled(True)
                self.output_file_name.setEnabled(True)
            else:
                self.output_file_name.setText('')
                self.output_file_label.setEnabled(False)
                self.output_file_name.setEnabled(False)
        
    def select_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory', self.root_dir.parent.as_posix())
        if output_dir:
            self.output_path.setText(output_dir)

    def check_fields(self):
        files_selected = bool(self.file_path.text())
        output_path_set = bool(self.output_path.text())
        output_file_name_set = bool(self.output_file_name.text())
    
        if len(self.selected_files) == 1:
            self.transcribe_button.setEnabled(files_selected and output_path_set and output_file_name_set)
        else:
            self.transcribe_button.setEnabled(files_selected and output_path_set)

    def show_message(self, msg: str):
        self.message_box.append(msg)
        QApplication.processEvents()

    def update_progressbar(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()

    def on_file_finished(self):
        self.completed_files += 1
        progress = int((self.completed_files / len(self.selected_files)) * 100)
        self.update_progressbar(progress)

        if self.completed_files < len(self.selected_files):
            self.transcribe_next_file()
        else:
            self.cancel_button.setEnabled(False)
            self.transcribe_button.setEnabled(True)
            self.update_progressbar(100)

    def transcribe_next_file(self):
        if self.current_file_index < len(self.selected_files):
            file_path = self.selected_files[self.current_file_index]
            model_name = self.model_dropdown.currentText()
            output_dir = Path(self.output_path.text())

            if len(self.selected_files) == 1:
                output_file_name = self.output_file_name.text()
                output_file_path = Path(output_file_name)
                if not output_file_path.suffix:
                    output_file_path = output_file_path.with_suffix('.txt')
                if output_file_path.suffix.lower() not in self.valid_extensions:
                    output_file_path = output_file_path.with_suffix('.txt')
                    self.show_message('Invalid extension provided as output file. Defaulting to .txt.')
                output_file = output_dir / output_file_path
            else:
                output_file = output_dir / Path(file_path).with_suffix('.txt').name

            try:
                self.transcriber.whisper_transcribe(Path(file_path), model_name, output_file)
                self.transcriber.thread.finished.connect(self.on_file_finished)
                self.current_file_index += 1
            except Exception as e:
                self.show_message(f'ERROR! An error occurred during execution:\n{e}')

    def transcribe(self):
        self.cancel_button.setEnabled(True)
        self.transcribe_button.setEnabled(False)

        self.show_message('Transcribing, please wait...')
        self.completed_files = 0
        self.current_file_index = 0

        self.update_progressbar(0)
        self.transcribe_next_file()
