import subprocess
import re
import os

class GitOperations:
    def __init__(self, repo_dir):
        self.repo_dir = os.path.abspath(repo_dir)

    def _run_git(self, args):
        """Gitコマンドを安全に実行します。"""
        # セキュリティ対策: shell=Falseで引数をリスト形式で渡すことでインジェクションを防ぎます。
        cmd = ["git"] + args
        result = subprocess.run(
            cmd,
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise subprocess.SubprocessError(
                f"Git command failed: {' '.join(cmd)}\n"
                f"Stdout: {result.stdout}\n"
                f"Stderr: {result.stderr}"
            )
        return result.stdout.strip()

    def _validate_identifier(self, identifier):
        """ブランチ名やプロジェクトIDの不正文字混入を防ぐための検証。"""
        if not re.match(r"^[a-zA-Z0-9_\-\./]+$", identifier):
            raise ValueError(f"Invalid identifier: {identifier}")

    def init_repo(self):
        """リポジトリを初期化します（未初期化の場合のみ）。"""
        if not os.path.exists(os.path.join(self.repo_dir, ".git")):
            self._run_git(["init"])
            # 初回ダミーコミット
            dummy_file = os.path.join(self.repo_dir, ".gitkeep")
            if not os.path.exists(dummy_file):
                with open(dummy_file, "w") as f:
                    f.write("")
            self._run_git(["add", ".gitkeep"])
            self._run_git(["commit", "-m", "Initial commit"])

    def checkout_project_branch(self, project_id):
        """プロジェクト共有開発ブランチを作成またはチェックアウトします。"""
        self._validate_identifier(project_id)
        branch_name = f"project/{project_id}"
        
        # 既存ブランチ一覧を取得して存在確認
        branches = self._run_git(["branch", "--list", branch_name])
        if branch_name in branches:
            self._run_git(["checkout", branch_name])
        else:
            # mainから分岐作成
            self._run_git(["checkout", "main"])
            self._run_git(["checkout", "-b", branch_name])

    def create_work_branch(self, project_id, ticket_id):
        """Tree Agent用の個別チケット作業用ブランチを作成します。"""
        self._validate_identifier(project_id)
        self._validate_identifier(ticket_id)
        
        proj_branch = f"project/{project_id}"
        work_branch = f"agent-work/{ticket_id}"

        # 親ブランチの存在確認とチェックアウト
        self.checkout_project_branch(project_id)
        
        # 既存の作業ブランチがあれば一度削除
        branches = self._run_git(["branch", "--list", work_branch])
        if work_branch in branches:
            self._run_git(["branch", "-D", work_branch])

        # 新規作成して切り替え
        self._run_git(["checkout", "-b", work_branch])

    def commit_deliverable(self, file_path, agent_name, precision, message_details=""):
        """成果物をGitに追加し、年輪コミットを生成します。"""
        self._validate_identifier(agent_name)
        
        # 成果物ファイルをステージング
        self._run_git(["add", file_path])
        
        # コミットメッセージのフォーマットに準拠
        commit_msg = (
            f"feat({agent_name}): Lignified {os.path.basename(file_path)} - "
            f"Precision: {precision}. {message_details}".strip()
        )
        self._run_git(["commit", "-m", commit_msg])

    def merge_work_branch(self, project_id, ticket_id, agent_name):
        """作業ブランチをプロジェクトブランチにマージし、作業ブランチを削除（落葉）します。"""
        self._validate_identifier(project_id)
        self._validate_identifier(ticket_id)
        self._validate_identifier(agent_name)

        proj_branch = f"project/{project_id}"
        work_branch = f"agent-work/{ticket_id}"

        # プロジェクトブランチに切り替え
        self._run_git(["checkout", proj_branch])

        # --no-ff でマージ実行
        merge_msg = f"merge(system): Integrated {agent_name} output for {ticket_id}"
        self._run_git(["merge", "--no-ff", work_branch, "-m", merge_msg])

        # 作業ブランチの削除（落葉）
        self._run_git(["branch", "-d", work_branch])
