# git_utils.py
from typing import List
import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError

class GitRepository:
    """
    Git リポジトリに対する操作をまとめたクラス。
    リポジトリの検証、フェッチ、ブランチ一覧の取得、diff の生成などを行う。
    """
    def __init__(self, path: str) -> None:
        self.path = path
        self.repo = self._validate_repo(path)

    def _validate_repo(self, path: str) -> git.Repo:
        """
        指定されたパスが有効な Git リポジトリか検証する。
        """
        try:
            return git.Repo(path)
        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            raise ValueError("Invalid Git repository") from e

    def fetch(self) -> None:
        """
        リモートから最新の情報をフェッチする。
        """
        self.repo.git.fetch()

    def get_branches(self) -> List[str]:
        """
        リポジトリ内のブランチ一覧を取得する。
        """
        return [branch.name for branch in self.repo.branches]

    def get_diff(self, branch1: str, branch2: str) -> str:
        """
        指定した2ブランチ間の diff を取得する。
        三点比較（three-dot diff）を用いて、共通の祖先からの差分を出す。
        """
        self.fetch()
        return self.repo.git.diff(f"{branch1}...{branch2}", "--stat", "--patch")
