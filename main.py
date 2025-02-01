# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui import GitDiffApp

def main() -> None:
    """
    アプリケーションのエントリーポイント。
    QApplication の初期化と GitDiffApp ウィジェットの表示を行う。
    """
    app = QApplication(sys.argv)
    window = GitDiffApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
