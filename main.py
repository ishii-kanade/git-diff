import sys
import os
from typing import List
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QComboBox,
    QMessageBox,
    QPlainTextEdit,
)
import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError


class GitDiffApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.repo_path: str = ""
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Git Branch Diff Tool")
        self.setGeometry(100, 100, 800, 400)

        # Use a different attribute name instead of "layout"
        self.main_layout = QVBoxLayout(self)

        # Repository selection
        self.repo_path_label = QLabel("Repository Path:")
        self.main_layout.addWidget(self.repo_path_label)

        self.repo_path_button = QPushButton("Select Repository")
        self.repo_path_button.clicked.connect(self.select_repo)
        self.main_layout.addWidget(self.repo_path_button)

        # Branch selectors
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

        # Load branches button
        self.load_branches_button = QPushButton("Load Branches")
        self.load_branches_button.setEnabled(False)
        self.load_branches_button.clicked.connect(self.load_branches)
        self.main_layout.addWidget(self.load_branches_button)

        # Generate diff button
        self.generate_diff_button = QPushButton("Generate Diff")
        self.generate_diff_button.setEnabled(False)
        self.generate_diff_button.clicked.connect(self.generate_diff)
        self.main_layout.addWidget(self.generate_diff_button)

        # Diff output widgets
        self.diff_summary_label = QLabel("")
        self.main_layout.addWidget(self.diff_summary_label)

        self.diff_text_area = QPlainTextEdit()
        self.diff_text_area.setReadOnly(True)
        self.diff_text_area.setVisible(False)
        self.main_layout.addWidget(self.diff_text_area)

        # Set the layout for the widget (optional, as we already pass self to QVBoxLayout)
        self.setLayout(self.main_layout)

    def select_repo(self) -> None:
        selected_path = QFileDialog.getExistingDirectory(self, "Select Repository")
        if selected_path and os.path.isdir(selected_path):
            try:
                # Validate the repository
                git.Repo(selected_path)
                self.repo_path = selected_path
                self.repo_path_label.setText(f"Repository Path: {self.repo_path}")
                self.load_branches_button.setEnabled(True)
            except (InvalidGitRepositoryError, NoSuchPathError):
                QMessageBox.critical(
                    self, "Error", "The selected directory is not a valid Git repository."
                )
                self.repo_path = ""
                self.repo_path_label.setText("Repository Path:")
                self.load_branches_button.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "Invalid repository path.")

    def load_branches(self) -> None:
        if not self.repo_path:
            QMessageBox.critical(self, "Error", "Please select a repository first.")
            return

        try:
            branches: List[str] = self.get_branches(self.repo_path)
            if not branches:
                QMessageBox.information(
                    self, "No Branches", "No branches found in the repository."
                )
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

    def get_branches(self, repo_path: str) -> List[str]:
        repo = git.Repo(repo_path)
        return [branch.name for branch in repo.branches]

    def generate_diff(self) -> None:
        branch1 = self.branch1_combo.currentText()
        branch2 = self.branch2_combo.currentText()

        if not branch1 or not branch2:
            QMessageBox.critical(self, "Error", "Please select both branches.")
            return

        try:
            diff = self.get_diff(self.repo_path, branch1, branch2)
            self.display_diff_result(diff)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during diff generation: {e}")

    def get_diff(self, repo_path: str, branch1: str, branch2: str) -> str:
        repo = git.Repo(repo_path)
        # Update repository state
        repo.git.fetch()
        # Three-dot diff based on common ancestor
        return repo.git.diff(f"{branch1}...{branch2}", "--stat", "--patch")

    def display_diff_result(self, diff: str) -> None:
        if not diff.strip():
            QMessageBox.information(
                self, "No Differences", "No differences found between the selected branches."
            )
            self.diff_summary_label.setText("No differences found.")
            self.diff_text_area.setVisible(False)
        else:
            output_file = os.path.join(self.repo_path, "diff.txt")
            self.save_diff_to_file(diff, output_file)
            QMessageBox.information(self, "Success", f"Diff saved to {output_file}")
            self.diff_summary_label.setText(f"Diff saved to {output_file}")
            self.diff_text_area.setPlainText(diff)
            self.diff_text_area.setVisible(True)

    def save_diff_to_file(self, diff: str, file_path: str) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(diff)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving diff to file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitDiffApp()
    window.show()
    sys.exit(app.exec_())
