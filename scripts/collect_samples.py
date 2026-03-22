#!/usr/bin/env python3
"""
AI Text Slop — データ収集スクリプト
6モデル × 10テーマ × 3試行 = 180サンプル
"""

import json
import os
import sys
import time
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

# === 設定 ===
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

PROMPT_TEMPLATE = "以下のテーマについて、技術ブログ記事を800字程度で書いてください。マークダウン形式で、見出し・箇条書き・コード例を適宜使ってください。\n\nテーマ: {theme}"

THEMES = [
    "Reactのパフォーマンス最適化",
    "Docker入門 — コンテナ化のメリットと始め方",
    "REST APIの設計ベストプラクティス",
    "GitHubActionsでCI/CDを構築する方法",
    "TypeScriptの型システムを活かした安全な開発",
    "データベースインデックスの仕組みと最適化",
    "WebSocketを使ったリアルタイム通信の実装",
    "セキュリティを考慮したJWT認証の設計",
    "マイクロサービスアーキテクチャの利点と課題",
    "AIを活用したコードレビューの自動化",
]

# === モデル定義 ===
MODELS = {
    # 商用API
    "claude-sonnet-4": {"type": "anthropic", "model": "claude-sonnet-4-20250514"},
    "gpt-4o": {"type": "openai", "model": "gpt-4o"},
    # ローカルOSS (autocrew-wsl Ollama)
    "qwen3.5-4b": {"type": "ollama", "model": "qwen3.5:4b"},
    "qwen3.5-9b": {"type": "ollama", "model": "qwen3.5:9b"},
    "swallow-20b": {"type": "ollama", "model": "gpt-oss:20b"},
    "llama3.2-1b": {"type": "ollama", "model": "llama3.2:1b"},
}

TRIALS = 3

# === API呼び出し ===
def call_anthropic(model: str, prompt: str) -> str:
    import urllib.request
    api_key = os.environ["ANTHROPIC_API_KEY"]
    data = json.dumps({
        "model": model,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    return result["content"][0]["text"]


def call_openai(model: str, prompt: str) -> str:
    import urllib.request
    api_key = os.environ["OPENAI_API_KEY"]
    data = json.dumps({
        "model": model,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def call_ollama(model: str, prompt: str) -> str:
    """autocrew-wsl の Ollama API を SSH経由で呼び出す"""
    escaped_prompt = prompt.replace('"', '\\"').replace("'", "'\\''")
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False})
    # ローカルからcurlで直接叩く（Tailscale経由）
    cmd = [
        "sshpass", "-p", "Ken096906261",
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
        "autocrew_user@100.72.192.8",
        f"curl -s http://localhost:11434/api/generate -d '{json.dumps({'model': model, 'prompt': prompt, 'stream': False})}'"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Ollama error: {result.stderr}")
    resp = json.loads(result.stdout)
    return resp["response"]


def generate(model_key: str, prompt: str) -> str:
    config = MODELS[model_key]
    if config["type"] == "anthropic":
        return call_anthropic(config["model"], prompt)
    elif config["type"] == "openai":
        return call_openai(config["model"], prompt)
    elif config["type"] == "ollama":
        return call_ollama(config["model"], prompt)
    else:
        raise ValueError(f"Unknown type: {config['type']}")


def main():
    # .envから環境変数読み込み
    env_path = Path.home() / "repos/sns-operations/.env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key, val)

    # 特定モデルだけ実行する場合
    target_models = sys.argv[1:] if len(sys.argv) > 1 else list(MODELS.keys())

    total = len(target_models) * len(THEMES) * TRIALS
    done = 0
    errors = 0

    for model_key in target_models:
        if model_key not in MODELS:
            print(f"[SKIP] Unknown model: {model_key}")
            continue

        model_dir = DATA_DIR / model_key
        model_dir.mkdir(exist_ok=True)

        for t_idx, theme in enumerate(THEMES):
            for trial in range(1, TRIALS + 1):
                done += 1
                filename = f"theme{t_idx:02d}_trial{trial}.json"
                filepath = model_dir / filename

                # 既存スキップ
                if filepath.exists():
                    print(f"[SKIP] {done}/{total} {model_key}/{filename} (exists)")
                    continue

                prompt = PROMPT_TEMPLATE.format(theme=theme)
                print(f"[{done}/{total}] {model_key} | theme{t_idx:02d} | trial{trial}...", end=" ", flush=True)

                try:
                    start = time.time()
                    text = generate(model_key, prompt)
                    elapsed = time.time() - start

                    record = {
                        "model": model_key,
                        "model_id": MODELS[model_key]["model"],
                        "model_type": MODELS[model_key]["type"],
                        "theme_index": t_idx,
                        "theme": theme,
                        "trial": trial,
                        "prompt": prompt,
                        "response": text,
                        "char_count": len(text),
                        "elapsed_sec": round(elapsed, 2),
                        "timestamp": datetime.now().isoformat(),
                    }
                    with open(filepath, "w") as f:
                        json.dump(record, f, ensure_ascii=False, indent=2)
                    print(f"OK ({len(text)}字, {elapsed:.1f}s)")

                except Exception as e:
                    errors += 1
                    print(f"ERROR: {e}")
                    # エラーログ
                    with open(DATA_DIR / "errors.log", "a") as f:
                        f.write(f"{datetime.now().isoformat()} | {model_key} | theme{t_idx:02d} | trial{trial} | {e}\n")

                # API制限回避
                if MODELS[model_key]["type"] in ("anthropic", "openai"):
                    time.sleep(2)
                else:
                    time.sleep(1)

    print(f"\n=== Complete: {done} tasks, {errors} errors ===")


if __name__ == "__main__":
    main()
