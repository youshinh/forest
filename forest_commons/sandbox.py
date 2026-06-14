import os
import subprocess
import re

class SandboxRunner:
    def __init__(self, workspace_dir=None):
        if workspace_dir is None:
            # デフォルトで本ファイルの2つ上のディレクトリ（プロジェクトルート）を指定
            workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.image_tag = "forestgram-python-runner:latest"

    def build_sandbox_image(self):
        """サンドボックス用のDockerイメージをビルドします。"""
        dockerfile_dir = os.path.join(self.workspace_dir, ".forestgram", "sandbox")
        if not os.path.exists(dockerfile_dir):
            raise FileNotFoundError(f"Sandbox directory not found: {dockerfile_dir}")

        print(f"[*] Building Docker image {self.image_tag}...")
        result = subprocess.run(
            ["docker", "build", "-t", self.image_tag, "."],
            cwd=dockerfile_dir,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise subprocess.SubprocessError(
                f"Docker build failed.\nStdout: {result.stdout}\nStderr: {result.stderr}"
            )
        print(f"[+] Docker image {self.image_tag} built successfully.")

    def _validate_path(self, target_path):
        """パスがワークスペース内にあるか厳格にチェックします。"""
        abs_path = os.path.abspath(target_path)
        try:
            common = os.path.commonpath([self.workspace_dir, abs_path])
            if common != self.workspace_dir:
                raise PermissionError(f"Security Violation: Target path is outside workspace: {target_path}")
        except ValueError as e:
            raise PermissionError(f"Security Violation: Invalid path resolution: {str(e)}")
        return abs_path

    def run_in_sandbox(self, project_id, script_relative_path, memory_limit="512m", cpu_limit="1.0"):
        """Dockerコンテナ内で指定されたスクリプトを安全に実行します。
        
        - ネットワーク遮断 (--network none)
        - メモリ制限 (--memory)
        - CPU制限 (--cpus)
        - 読み取り専用マウント (:ro)
        """
        # 入力値バリデーション
        if not re.match(r"^[a-zA-Z0-9_\-\./]+$", project_id):
            raise ValueError(f"Invalid project ID: {project_id}")

        temp_dir = os.path.join(self.workspace_dir, "projects", project_id, "temporary")
        deliverables_dir = os.path.join(self.workspace_dir, "projects", project_id, "deliverables")

        # ディレクトリ存在確保とパスチェック
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(deliverables_dir, exist_ok=True)
        abs_temp = self._validate_path(temp_dir)
        abs_deliv = self._validate_path(deliverables_dir)

        # 実行スクリプトの物理パスチェック
        script_path = os.path.join(abs_temp, script_relative_path)
        abs_script = self._validate_path(script_path)
        if not os.path.exists(abs_script):
            raise FileNotFoundError(f"Script not found in temporary folder: {script_relative_path}")

        # コンテナ内のパス構成:
        # temporary/ は /workspace に読み取り専用でマウント
        # deliverables/ は /output に書き込み許可でマウント
        container_script = os.path.join("/workspace", script_relative_path).replace("\\", "/")

        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            f"--memory={memory_limit}",
            f"--cpus={cpu_limit}",
            "-v", f"{abs_temp}:/workspace:ro",
            "-v", f"{abs_deliv}:/output:rw",
            self.image_tag,
            "python3", container_script
        ]

        print(f"[*] Running sandbox command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
