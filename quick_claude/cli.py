#!/usr/bin/env python3
"""quick-claude: Claude Code テンプレートをカレントディレクトリに追加する CLI"""

import argparse
import json
import shutil
import stat
import subprocess
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

IGNORE_PATTERNS = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc")


def copy_file(src: Path, dst: Path, *, force: bool) -> bool:
    """ファイルをコピーする。既存ファイルがあれば force 時のみ上書き。"""
    if dst.exists() and not force:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def copy_dir(src: Path, dst: Path, *, force: bool) -> bool:
    """ディレクトリを再帰的にコピーする。既存なら force 時のみ上書き。"""
    if dst.exists() and not force:
        return False
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=IGNORE_PATTERNS)
    return True


def ensure_hooks_executable(claude_dir: Path) -> None:
    """hooks/ 内のファイルに実行権限を付与する。"""
    hooks_dir = claude_dir / "hooks"
    if not hooks_dir.exists():
        return
    for hook in hooks_dir.iterdir():
        if hook.is_file():
            hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def get_repo_fullname() -> str | None:
    """gh CLI から owner/repo を取得する。"""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def setup_auto_merge(repo: str) -> bool:
    """GitHub リポジトリの auto-merge と branch protection を設定する。"""
    # auto-merge を有効化
    try:
        subprocess.run(
            ["gh", "api", f"repos/{repo}", "-X", "PATCH", "-f", "allow_auto_merge=true"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"  error: auto-merge の有効化に失敗しました: {e.stderr.strip()}")
        return False

    # branch protection rule を設定
    protection = {
        "required_status_checks": {
            "strict": True,
            "checks": [
                {"context": "lint"},
                {"context": "test"},
            ],
        },
        "enforce_admins": False,
        "required_pull_request_reviews": None,
        "restrictions": None,
    }
    try:
        subprocess.run(
            ["gh", "api", f"repos/{repo}/branches/main/protection", "-X", "PUT", "--input", "-"],
            input=json.dumps(protection),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"  error: branch protection の設定に失敗しました: {e.stderr.strip()}")
        return False

    return True


def patch_claude_md_for_auto_merge(claude_md: Path) -> None:
    """CLAUDE.md の作業フローに auto-merge ステップを追加する。"""
    content = claude_md.read_text()
    old = (
        '# 4. push → PR → merge\n'
        'git push -u origin feature/<TASK-ID>-<description>\n'
        'gh pr create --title "..." --body "Closes #<NUMBER>" --base main'
    )
    new = (
        '# 4. push → PR → auto-merge\n'
        'git push -u origin feature/<TASK-ID>-<description>\n'
        'gh pr create --title "..." --body "Closes #<NUMBER>" --base main\n'
        'gh pr merge --auto --squash'
    )
    if old in content:
        claude_md.write_text(content.replace(old, new))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="quick-claude",
        description="Claude Code テンプレートをカレントディレクトリに追加する",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="既存ファイルを上書きする",
    )
    parser.add_argument(
        "--no-ci",
        action="store_true",
        help="GitHub Actions CI workflow を追加しない",
    )
    parser.add_argument(
        "--auto-merge",
        action="store_true",
        help="auto-merge と branch protection rule を設定する",
    )
    args = parser.parse_args()

    cwd = Path.cwd()

    # --- CLAUDE.md ---
    src_md = TEMPLATES_DIR / "CLAUDE.md"
    dst_md = cwd / "CLAUDE.md"
    if copy_file(src_md, dst_md, force=args.force):
        print("  added: CLAUDE.md")
    else:
        print("  skip:  CLAUDE.md  (already exists, use -f to overwrite)")

    # --- .claude/ (パッケージ内では dot-claude/ として格納) ---
    src_dir = TEMPLATES_DIR / "dot-claude"
    dst_dir = cwd / ".claude"
    if copy_dir(src_dir, dst_dir, force=args.force):
        ensure_hooks_executable(dst_dir)
        print("  added: .claude/")
    else:
        print("  skip:  .claude/   (already exists, use -f to overwrite)")

    # --- pyproject.toml + .github/workflows/ (Python CI セット) ---
    if not args.no_ci:
        src_pyproject = TEMPLATES_DIR / "pyproject.toml"
        dst_pyproject = cwd / "pyproject.toml"
        if copy_file(src_pyproject, dst_pyproject, force=args.force):
            print("  added: pyproject.toml")
        else:
            print("  skip:  pyproject.toml (already exists, use -f to overwrite)")

        src_gh = TEMPLATES_DIR / "dot-github"
        dst_gh = cwd / ".github"
        if copy_dir(src_gh, dst_gh, force=args.force):
            print("  added: .github/workflows/ci.yml")
        else:
            print("  skip:  .github/  (already exists, use -f to overwrite)")

    # --- auto-merge 設定 ---
    if args.auto_merge:
        repo = get_repo_fullname()
        if repo is None:
            print("  error: gh CLI が見つからないか、GitHub リポジトリが設定されていません")
            print("         リポジトリ作成後に quick-claude --auto-merge を再実行してください")
        else:
            if setup_auto_merge(repo):
                print(f"  added: auto-merge + branch protection ({repo})")
                patch_claude_md_for_auto_merge(dst_md)
                print("  added: CLAUDE.md に auto-merge ステップを追記")

    print()
    print("Done! Run 'claude' to start.")


if __name__ == "__main__":
    main()
