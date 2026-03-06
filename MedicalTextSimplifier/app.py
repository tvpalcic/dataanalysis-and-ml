import openai
import sys
import json
import PyPDF2
from docx import Document
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QIcon
import os

# API ключ
openai.api_key = 'key'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")  
    return os.path.join(base_path, relative_path)

# функция упрощения текста через модель
def simplify_text_with_chat_model(input_text):
    if not input_text.strip():
        return "Error: Input text is empty."
    try:
        response = openai.ChatCompletion.create(
            model="ft:gpt-3.5-turbo-0125:personal:try1:BIGSWBhw",
            messages=[
                {"role": "system", "content": "You simplify complex medical texts for non-experts without losing meaning."},
                {"role": "user", "content": input_text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

class SimplifierApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Medical Text Simplifier")
        self.setGeometry(100, 100, 1200, 700)

        icon_file = resource_path("tsicon.ico")
        if os.path.exists(icon_file):
            self.setWindowIcon(QIcon(icon_file))

       
        self.set_background()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        widget_style = """
            QTextEdit, QListWidget {
                background-color: rgba(255,255,255,230);
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """
        button_style = """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """
        simplify_button_style = """
            QPushButton {
                background-color: #50C878;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40A360;
            }
        """
        clear_button_style = """
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E55A5A;
            }
        """

        # ===== History =====
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.setStyleSheet(widget_style)
        self.history_list.clicked.connect(self.load_from_history)
        history_layout.addWidget(self.history_list)

        self.clear_history_button = QPushButton("🗑 Clear History")
        self.clear_history_button.setStyleSheet(clear_button_style)
        self.clear_history_button.clicked.connect(self.clear_history)
        history_layout.addWidget(self.clear_history_button)

        main_layout.addLayout(history_layout, 2)

        # ===== Input =====
        input_layout = QVBoxLayout()
        self.input_text_edit = QTextEdit()
        self.input_text_edit.setPlaceholderText("Enter text or load a file...")
        self.input_text_edit.setStyleSheet(widget_style)
        input_layout.addWidget(self.input_text_edit)

        upload_layout = QHBoxLayout()
        self.upload_txt_button = QPushButton("📄 TXT")
        self.upload_txt_button.setStyleSheet(button_style)
        self.upload_txt_button.clicked.connect(self.handle_upload_txt)
        upload_layout.addWidget(self.upload_txt_button)

        self.upload_pdf_button = QPushButton("📕 PDF")
        self.upload_pdf_button.setStyleSheet(button_style)
        self.upload_pdf_button.clicked.connect(self.handle_upload_pdf)
        upload_layout.addWidget(self.upload_pdf_button)

        self.upload_docx_button = QPushButton("📋 Word")
        self.upload_docx_button.setStyleSheet(button_style)
        self.upload_docx_button.clicked.connect(self.handle_upload_docx)
        upload_layout.addWidget(self.upload_docx_button)

        input_layout.addLayout(upload_layout)

        self.simplify_button = QPushButton("Simplify Text")
        self.simplify_button.setMinimumHeight(50)
        self.simplify_button.setStyleSheet(simplify_button_style)
        self.simplify_button.clicked.connect(self.handle_simplify)
        input_layout.addWidget(self.simplify_button)

        main_layout.addLayout(input_layout, 4)

        # ===== Output =====
        output_layout = QVBoxLayout()
        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setStyleSheet(widget_style)
        output_layout.addWidget(self.output_text_edit)

        self.save_button = QPushButton("💾 Save Result")
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_simplified_text)
        output_layout.addWidget(self.save_button)

        main_layout.addLayout(output_layout, 4)

        # ===== History data =====
        self.history = self.load_history()
        self.update_history()
        self.setLayout(main_layout)

    # ===== Background =====
    def set_background(self):
        background_file = resource_path("background.jpg")
        if os.path.exists(background_file):
            self.background = QPixmap(background_file)
            palette = QPalette()
            scaled = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
            palette.setBrush(QPalette.Window, QBrush(scaled))
            self.setPalette(palette)

    def resizeEvent(self, event):
        if hasattr(self, "background"):
            palette = QPalette()
            scaled = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
            palette.setBrush(QPalette.Window, QBrush(scaled))
            self.setPalette(palette)

    # ===== Actions =====
    def handle_simplify(self):
        text = self.input_text_edit.toPlainText()
        if not text.strip():
            self.output_text_edit.setText("Error: empty input")
            return
        result = simplify_text_with_chat_model(text)
        self.output_text_edit.setText(result)
        if not result.startswith("Error"):
            self.history.append((text, result))
            self.save_history()
            self.update_history()

    def handle_upload_txt(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open TXT", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as f:
                self.input_text_edit.setText(f.read())

    def handle_upload_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_name:
            text = ""
            with open(file_name, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            self.input_text_edit.setText(text)

    def handle_upload_docx(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Word", "", "Word Files (*.docx)")
        if file_name:
            doc = Document(file_name)
            text = "\n".join(p.text for p in doc.paragraphs)
            self.input_text_edit.setText(text)

    def save_simplified_text(self):
        text = self.output_text_edit.toPlainText()
        if not text.strip():
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(text)

    # ===== History =====
    def update_history(self):
        self.history_list.clear()
        for i, (q, r) in enumerate(self.history):
            self.history_list.addItem(f"{i+1}: {q[:40]}...")

    def load_from_history(self):
        idx = self.history_list.currentRow()
        if idx >= 0:
            q, r = self.history[idx]
            self.input_text_edit.setText(q)
            self.output_text_edit.setText(r)

    def load_history(self):
        path = resource_path("history.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def save_history(self):
        path = resource_path("history.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def clear_history(self):
        self.history = []
        self.save_history()
        self.update_history()

# ===== Main =====
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = SimplifierApp()
    window.show()
    sys.exit(app.exec_())