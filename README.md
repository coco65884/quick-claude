# quick-claude

プロジェクトに Claude Code 用のテンプレート（`CLAUDE.md` + `.claude/`）を追加する CLI ツール。

## テンプレートの内容

| ファイル | 説明 |
|---|---|
| `CLAUDE.md` | 開発ルール・Git運用・品質チェックの指示書 |
| `.claude/settings.json` | セキュリティ deny ルール・hooks 設定・環境変数 |
| `.claude/hooks/deny-check.py` | 危険なコマンドを動的にブロックする PreToolUse hook |

## インストール

```bash
# uv（推奨）
uv tool install git+https://github.com/coco65884/quick-claude.git

# pipx
pipx install git+https://github.com/coco65884/quick-claude.git
```

ローカルにクローンしてインストールする場合:

```bash
git clone https://github.com/coco65884/quick-claude.git
cd quick-claude
uv tool install .
```

## 使い方

```bash
# 任意のプロジェクトディレクトリで実行
cd ~/my-project
quick-claude          # CLAUDE.md と .claude/ を追加
quick-claude -f       # 既存ファイルがあっても上書き
```

## 動作要件

- Python 3.9+
- macOS / Linux
