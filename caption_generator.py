import sys
import os
import random
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit, QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

# ── Data Pools ────────────────────────────────────────────────────────────────

categories = {
    "Tech": {
        "hooks": [
            "You won't believe this new...",
            "Finally, the tool we needed:",
            "Stop doing this manually!",
        ],
        "bodies": [
            "This AI tool is changing the game.",
            "Level up your workflow with this.",
            "This is a total lifesaver for devs.",
        ],
        "hashtags": "#tech #coding #ai #innovation #python",
    },
    "Education": {
        "hooks": [
            "Quick lesson on...",
            "Boost your grades with...",
            "The secret to understanding...",
        ],
        "bodies": [
            "Let's break this down simply.",
            "Master this concept in 60 seconds.",
            "Study smarter, not harder.",
        ],
        "hashtags": "#learning #students #stem #education #tips",
    },
    "Video Editing": {
        "hooks": [
            "Bring your creativity into editing...",
            "Video Editing is a power through which you can create anything you want.",
            "This editing trick will blow your mind!",
        ],
        "bodies": [
            "Only basic knowledge is enough to start editing.",
            "Master keyframe animation as a beginner.",
            "This one technique makes your cuts look cinematic.",
        ],
        "hashtags": "#editing #visuals #motiongraphics #skill #videoediting",
    },
}

# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Social Media Architect")
        self.setFixedSize(520, 520)
        self._last_caption = ""
        self._build_ui()
        self._connect_signals()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)

        self.titleLabel = QLabel("Caption &amp; Hashtag Generator")
        self.titleLabel.setTextFormat(Qt.RichText)
        self.titleLabel.setText("Caption & Hashtag Generator")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 15px; font-weight: bold; color: #222222;")

        self.subtitleLabel = QLabel("YouTube & TikTok")
        self.subtitleLabel.setAlignment(Qt.AlignCenter)
        self.subtitleLabel.setStyleSheet("font-size: 12px; color: #666666;")

        header.addWidget(self.titleLabel)
        header.addWidget(self.subtitleLabel)
        root.addLayout(header)

        # Niche group
        nicheGroup = QGroupBox("Select Your Niche")
        nicheGroup.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                color: #555555;
                border: 0.5px solid #cccccc;
                border-radius: 6px;
                background-color: #ffffff;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 4px;
            }
        """)
        nicheLayout = QVBoxLayout(nicheGroup)
        nicheLayout.setSpacing(8)
        nicheLayout.setContentsMargins(10, 10, 10, 10)

        self.nicheCombo = QComboBox()
        self.nicheCombo.addItems(["Tech", "Education", "Video Editing"])
        self.nicheCombo.setStyleSheet("""
            QComboBox {
                border: 1px solid #aaaaaa;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                color: #222222;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }
            QComboBox::after {
                content: "▼";
            }
            QComboBox QAbstractItemView {
                border: 1px solid #aaaaaa;
                selection-background-color: #5a8dee;
                selection-color: white;
            }
        """)
        nicheLayout.addWidget(self.nicheCombo)
        root.addWidget(nicheGroup)

        # Generate button
        self.generateBtn = QPushButton("✨  Generate Caption")
        self.generateBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.generateBtn.setMinimumHeight(38)
        self.generateBtn.setStyleSheet("""
            QPushButton {
                background-color: #5a8dee;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4a7dde; }
            QPushButton:pressed { background-color: #3a6dce; }
        """)
        root.addWidget(self.generateBtn)

        # Output group
        outputGroup = QGroupBox("Generated Output")
        outputGroup.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                color: #555555;
                border: 0.5px solid #cccccc;
                border-radius: 6px;
                background-color: #ffffff;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 4px;
            }
        """)
        outputLayout = QVBoxLayout(outputGroup)
        outputLayout.setSpacing(8)
        outputLayout.setContentsMargins(10, 10, 10, 10)

        self.outputBox = QTextEdit()
        self.outputBox.setReadOnly(True)
        self.outputBox.setPlaceholderText("Your generated caption will appear here...")
        self.outputBox.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: #fafafa;
                font-size: 12px;
                color: #333333;
                padding: 8px;
                line-height: 1.7;
            }
        """)

        self.hashtagsLabel = QLabel("")
        self.hashtagsLabel.setWordWrap(True)
        self.hashtagsLabel.setStyleSheet("font-size: 11px; color: #3a5bb5;")

        outputLayout.addWidget(self.outputBox)
        outputLayout.addWidget(self.hashtagsLabel)
        root.addWidget(outputGroup)

        # Bottom buttons
        bottomLayout = QHBoxLayout()
        bottomLayout.setSpacing(10)

        self.regenerateBtn = QPushButton("🔄  Regenerate")
        self.regenerateBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.regenerateBtn.setMinimumHeight(34)
        self.regenerateBtn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #f0f0f0; }
            QPushButton:pressed { background-color: #e0e0e0; }
        """)

        self.saveBtn = QPushButton("💾  Save to .txt")
        self.saveBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.saveBtn.setMinimumHeight(34)
        self.saveBtn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219a52; }
            QPushButton:pressed { background-color: #1a7a42; }
        """)

        bottomLayout.addWidget(self.regenerateBtn)
        bottomLayout.addWidget(self.saveBtn)
        root.addLayout(bottomLayout)

    # ── Signal Connections ────────────────────────────────────────────────────

    def _connect_signals(self):
        self.generateBtn.clicked.connect(self._generate)
        self.regenerateBtn.clicked.connect(self._generate)
        self.saveBtn.clicked.connect(self._save)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _generate(self):
        choice = self.nicheCombo.currentText()
        data = categories[choice]

        hook = random.choice(data["hooks"])
        body = random.choice(data["bodies"])
        tags = data["hashtags"]

        caption = f"{hook}\n\n{body}"
        self._last_caption = f"{caption}\n\n{tags}"

        self.outputBox.setPlainText(caption)
        self.hashtagsLabel.setText(tags)

    def _save(self):
        if not self._last_caption:
            QMessageBox.warning(self, "Nothing to Save", "Generate a caption first!")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Caption", "caption.docx", "Text Files (*.docx)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._last_caption)
            QMessageBox.information(self, "Saved", f"Caption saved to:\n{path}")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())