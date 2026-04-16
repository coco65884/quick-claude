# quick-claude

プロジェクトに Claude Code 用のテンプレート（`CLAUDE.md` + `.claude/` + CI workflow）を追加する CLI ツール。

## テンプレートの内容

| ファイル | 説明 |
|---|---|
| `.gitignore` | Python, Claude Code, macOS, IDE 向けの除外設定 |
| `CLAUDE.md` | 開発ルール・Git運用・初期セットアップ・品質チェックの指示書 |
| `.claude/settings.json` | セキュリティ deny ルール・hooks 設定・環境変数 |
| `.claude/hooks/deny-check.py` | 危険なコマンドを動的にブロックする PreToolUse hook |
| `.github/workflows/ci.yml` | GitHub Actions CI（ruff + pytest / Python向け） |

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
quick-claude               # .gitignore + CLAUDE.md + .claude/ + pyproject.toml + .github/workflows/ を追加
quick-claude --auto-merge  # 上記 + auto-merge と branch protection rule を設定
quick-claude -f            # 既存ファイルがあっても上書き
quick-claude --no-ci       # CI workflow + pyproject.toml を追加しない（Python以外のプロジェクト向け）
```

## Auto-merge の設定

`--auto-merge` フラグを付けると、以下を自動で設定する:

- リポジトリの auto-merge を有効化
- `main` ブランチに branch protection rule を追加（`lint` と `test` を必須チェックに）
- `CLAUDE.md` の作業フローに `gh pr merge --auto --squash` を追記

```bash
quick-claude --auto-merge
```

手動で設定する場合は、リポジトリの Settings から "Allow auto-merge" の有効化と branch protection rule の追加を行う。

## 動作要件

- Python 3.9+
- macOS / Linux
