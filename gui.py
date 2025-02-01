# gui.py
import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QComboBox,
    QMessageBox,
    QPlainTextEdit,
)
from git_utils import GitRepository

class GitDiffApp(QWidget):
    """
    GitDiffApp クラスは、Git リポジトリのブランチ間差分（diff）を生成するための GUI を実装しています。
    ユーザーがリポジトリを選択し、ブランチを指定すると、差分を画面上に表示しファイルにも保存します。
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.repo: GitRepository | None = None
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Git Branch Diff Tool")
        self.setGeometry(100, 100, 800, 400)

        # レイアウトの初期化
        self.main_layout = QVBoxLayout(self)

        # リポジトリ選択ウィジェット
        self.repo_path_label = QLabel("Repository Path:")
        self.main_layout.addWidget(self.repo_path_label)

        self.repo_path_button = QPushButton("Select Repository")
        self.repo_path_button.clicked.connect(self.select_repo)
        self.main_layout.addWidget(self.repo_path_button)

        # ブランチ選択ウィジェット
        self.branch1_label = QLabel("Branch 1 (Base):")
        self.main_layout.addWidget(self.branch1_label)

        self.branch1_combo = QComboBox()
        self.branch1_combo.setEnabled(False)
        self.main_layout.addWidget(self.branch1_combo)

        self.branch2_label = QLabel("Branch 2 (Feature):")
        self.main_layout.addWidget(self.branch2_label)

        self.branch2_combo = QComboBox()
        self.branch2_combo.setEnabled(False)
        self.main_layout.addWidget(self.branch2_combo)

        # ブランチ読み込みボタン
        self.load_branches_button = QPushButton("Load Branches")
        self.load_branches_button.setEnabled(False)
        self.load_branches_button.clicked.connect(self.load_branches)
        self.main_layout.addWidget(self.load_branches_button)

        # diff 生成ボタン
        self.generate_diff_button = QPushButton("Generate Diff")
        self.generate_diff_button.setEnabled(False)
        self.generate_diff_button.clicked.connect(self.generate_diff)
        self.main_layout.addWidget(self.generate_diff_button)

        # diff 表示ウィジェット
        self.diff_summary_label = QLabel("")
        self.main_layout.addWidget(self.diff_summary_label)

        self.diff_text_area = QPlainTextEdit()
        self.diff_text_area.setReadOnly(True)
        self.diff_text_area.setVisible(False)
        self.main_layout.addWidget(self.diff_text_area)

        self.setLayout(self.main_layout)

    def select_repo(self) -> None:
        """
        リポジトリのディレクトリをユーザーに選択させ、GitRepository クラスのインスタンスを生成する。
        """
        selected_path = QFileDialog.getExistingDirectory(self, "Select Repository")
        if selected_path and os.path.isdir(selected_path):
            try:
                self.repo = GitRepository(selected_path)
                self.repo_path_label.setText(f"Repository Path: {selected_path}")
                self.load_branches_button.setEnabled(True)
            except ValueError:
                QMessageBox.critical(
                    self, "Error", "The selected directory is not a valid Git repository."
                )
                self.repo = None
                self.repo_path_label.setText("Repository Path:")
                self.load_branches_button.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "Invalid repository path.")

    def load_branches(self) -> None:
        """
        選択したリポジトリからブランチ一覧を取得し、コンボボックスにセットする。
        """
        if self.repo is None:
            QMessageBox.critical(self, "Error", "Please select a repository first.")
            return

        try:
            branches = self.repo.get_branches()
            if not branches:
                QMessageBox.information(self, "No Branches", "No branches found in the repository.")
                return

            self.branch1_combo.clear()
            self.branch2_combo.clear()
            self.branch1_combo.addItems(branches)
            self.branch2_combo.addItems(branches)
            self.branch1_combo.setEnabled(True)
            self.branch2_combo.setEnabled(True)
            self.generate_diff_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading branches: {e}")

    def generate_diff(self) -> None:
        """
        選択された2つのブランチ間で diff を生成し、結果を表示・保存する。
        """
        if self.repo is None:
            QMessageBox.critical(self, "Error", "Please select a repository first.")
            return

        branch1 = self.branch1_combo.currentText()
        branch2 = self.branch2_combo.currentText()
        if not branch1 or not branch2:
            QMessageBox.critical(self, "Error", "Please select both branches.")
            return

        try:
            diff = self.repo.get_diff(branch1, branch2)
            self.display_diff_result(diff)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during diff generation: {e}")

    def display_diff_result(self, diff: str) -> None:
        # self.repoがNoneの場合はエラーメッセージを表示して早期リターンする
        if self.repo is None:
            QMessageBox.critical(self, "Error", "Repository is not set.")
            return

        if not diff.strip():
            QMessageBox.information(
                self, "No Differences", "No differences found between the selected branches."
            )
            self.diff_summary_label.setText("No differences found.")
            self.diff_text_area.setVisible(False)
        else:
            output_file = os.path.join(self.repo.path, "diff.txt")
            self.save_diff_to_file(diff, output_file)
            QMessageBox.information(self, "Success", f"Diff saved to {output_file}")
            self.diff_summary_label.setText(f"Diff saved to {output_file}")
            self.diff_text_area.setPlainText(diff)
            self.diff_text_area.setVisible(True)


    def save_diff_to_file(self, diff: str, file_path: str) -> None:
        """
        生成した diff を指定されたファイルに保存する。
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(diff)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving diff to file: {e}")
