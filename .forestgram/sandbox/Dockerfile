# Forest-gram Sandbox Runner Dockerfile
# Pythonベースの超軽量テスト検証イメージです。非特権ユーザー（sandbox）で実行されます。
FROM python:3.11-slim

# 非特権ユーザーの作成
RUN useradd -m -u 10001 sandbox

WORKDIR /workspace

# 必要最低限のPythonライブラリがあればここでインストールします
# RUN pip install --no-cache-dir pytest

# 非特権ユーザーに切り替え
USER sandbox

CMD ["python3"]
