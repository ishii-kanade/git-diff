import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QComboBox, QMessageBox
import git
import os

class GitDiffApp(QWidget):
    def __init__(self):
        super().__init__()
        self.repo_path = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Git Branch Diff Tool')
        self.setGeometry(100, 100, 600, 200)

        layout = QVBoxLayout()

        self.repo_path_label = QLabel('Repository Path:')
        layout.addWidget(self.repo_path_label)
        
        self.repo_path_button = QPushButton('Select Repository')
        self.repo_path_button.clicked.connect(self.select_repo)
        layout.addWidget(self.repo_path_button)
        
        self.branch1_label = QLabel('Branch 1 (Base):')
        layout.addWidget(self.branch1_label)
        
        self.branch1_combo = QComboBox()
        layout.addWidget(self.branch1_combo)
        
        self.branch2_label = QLabel('Branch 2 (Feature):')
        layout.addWidget(self.branch2_label)
        
        self.branch2_combo = QComboBox()
        layout.addWidget(self.branch2_combo)
        
        self.load_branches_button = QPushButton('Load Branches')
        self.load_branches_button.clicked.connect(self.load_branches)
        layout.addWidget(self.load_branches_button)
        
        self.generate_diff_button = QPushButton('Generate Diff')
        self.generate_diff_button.clicked.connect(self.generate_diff)
        layout.addWidget(self.generate_diff_button)
        
        self.diff_summary_label = QLabel('')
        layout.addWidget(self.diff_summary_label)
        
        self.setLayout(layout)

    def select_repo(self):
        self.repo_path = QFileDialog.getExistingDirectory(self, 'Select Repository')
        if self.repo_path and os.path.isdir(self.repo_path):
            self.repo_path_label.setText(f'Repository Path: {self.repo_path}')
        else:
            self.repo_path = ""
            QMessageBox.critical(self, 'Error', 'Invalid repository path')

    def load_branches(self):
        if not self.repo_path:
            QMessageBox.critical(self, 'Error', 'Please select a repository first')
            return
        
        try:
            branches = self.get_branches(self.repo_path)
            self.branch1_combo.clear()
            self.branch2_combo.clear()
            self.branch1_combo.addItems(branches)
            self.branch2_combo.addItems(branches)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error loading branches: {e}')

    def get_branches(self, repo_path):
        repo = git.Repo(repo_path)
        return [branch.name for branch in repo.branches]

    def generate_diff(self):
        branch1 = self.branch1_combo.currentText()
        branch2 = self.branch2_combo.currentText()

        if not branch1 or not branch2:
            QMessageBox.critical(self, 'Error', 'Please select both branches')
            return

        try:
            diff = self.get_diff(self.repo_path, branch1, branch2)
            self.display_diff_result(diff)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error during diff: {e}')

    def get_diff(self, repo_path, branch1, branch2):
        repo = git.Repo(repo_path)
        
        # Fetch latest changes
        repo.git.fetch()

        # Use three-dot diff to compare the two branches based on their common ancestor
        return repo.git.diff(f'{branch1}...{branch2}', '--stat', '--patch')

    def display_diff_result(self, diff):
        if not diff.strip():
            QMessageBox.information(self, 'No Differences', 'No differences found between the selected branches.')
        else:
            output_file = os.path.join(self.repo_path, 'diff.txt')
            self.save_diff_to_file(diff, output_file)
            QMessageBox.information(self, 'Success', f'Diff saved to {output_file}')
            self.diff_summary_label.setText(f'Diff saved to {output_file}')

    def save_diff_to_file(self, diff, file_path):
        with open(file_path, 'w') as file:
            file.write(diff)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GitDiffApp()
    ex.show()
    sys.exit(app.exec_())
