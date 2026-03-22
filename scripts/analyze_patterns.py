#!/usr/bin/env python3
"""AI Text Slop 16パターン分析スクリプト"""

import json, os, re, glob
from collections import Counter, defaultdict
import statistics

DATA_DIR = os.path.expanduser("~/repos/iris-lab/009-ai-text-slop/data")
MODELS = ["claude-sonnet-4", "gpt-4o", "qwen3.5-4b", "qwen3.5-9b", "swallow-20b", "llama3.2-1b"]

# === AI頻出語彙パターン ===
AI_FREQ_WORDS_JA = [
    "重要です", "不可欠", "についてご紹介", "についてご説明", "を活用する",
    "それでは", "いかがでしたでしょうか", "まとめると", "最後に",
    "さまざまな", "効果的な", "効率的な", "適切な", "包括的な", "具体的な",
    "重要な役割", "大きなメリット", "大幅に向上", "飛躍的に",
    "〜することが可能です", "〜が期待できます", "〜と言えるでしょう",
    "注目すべき", "見逃せない", "押さえておきたい",
    "ぜひ", "活用してみてください", "参考にしてみてください",
    "本記事では", "この記事では", "今回は",
]

# emダッシュ
EM_DASH_PATTERN = re.compile(r'[—–]')

# ヘッジング表現
HEDGE_WORDS = [
    "かもしれません", "と思われます", "と考えられます", "可能性があります",
    "場合があります", "ことがあります", "傾向があります", "一般的に",
    "基本的に", "概ね", "おおむね", "ある程度",
]

# 追従トーン（読者への過度な同意・共感）
SYCOPHANCY_PATTERNS = [
    "素晴らしい", "非常に有益", "画期的な", "革新的な",
    "ご存知の通り", "皆さんもご存じ", "当然ながら",
]

# 定型結論パターン
BOILERPLATE_CONCLUSIONS = [
    "いかがでしたでしょうか", "いかがでしたか", "まとめ",
    "以上、", "ぜひ.*活用してみてください", "ぜひ.*試してみてください",
    "参考になれば幸いです", "お役に立てれば",
    "最後までお読みいただき", "ご覧いただきありがとう",
]

# 三点セット（メリット/デメリット/まとめ の定型構成）
THREE_SET = ["メリット", "デメリット", "まとめ"]

# 太字の機械的多用
BOLD_PATTERN = re.compile(r'\*\*[^*]+\*\*')

# リスト記号パターン
LIST_PATTERN = re.compile(r'^[\s]*[-・✅🔹▶️●◆►※★☆▪️]', re.MULTILINE)

# 見出しパターン
HEADING_PATTERN = re.compile(r'^#{1,4}\s', re.MULTILINE)

# 絵文字パターン
EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001F9FF\U00002702-\U000027B0\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF\U0000FE00-\U0000FE0F\U0001F000-\U0001F02F]"
)

def load_samples(model):
    """モデルのサンプルを読み込み"""
    d = os.path.join(DATA_DIR, model)
    samples = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        data = json.load(open(f))
        text = data.get("response", "") or data.get("text", "")
        if text:
            samples.append({"file": os.path.basename(f), "text": text, **data})
    return samples

def count_pattern(text, patterns):
    """パターンリストの出現回数"""
    count = 0
    for p in patterns:
        count += len(re.findall(p, text))
    return count

def analyze_sample(text):
    """1サンプルの16パターン分析"""
    lines = text.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    
    # 文の分割（。！？で区切り）
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    
    # 文長のリスト
    sent_lengths = [len(s) for s in sentences]
    
    results = {}
    
    # 1. AI頻出語彙数
    results["ai_freq_words"] = count_pattern(text, AI_FREQ_WORDS_JA)
    
    # 2. emダッシュ数
    results["em_dash"] = len(EM_DASH_PATTERN.findall(text))
    
    # 3. ヘッジング表現数
    results["hedging"] = count_pattern(text, HEDGE_WORDS)
    
    # 4. 追従トーン数
    results["sycophancy"] = count_pattern(text, SYCOPHANCY_PATTERNS)
    
    # 5. 定型結論パターン数
    results["boilerplate_conclusion"] = count_pattern(text, BOILERPLATE_CONCLUSIONS)
    
    # 6. 三点セット（メリット/デメリット/まとめ）の有無
    three_count = sum(1 for t in THREE_SET if t in text)
    results["three_set"] = three_count
    
    # 7. 太字の使用数
    results["bold_count"] = len(BOLD_PATTERN.findall(text))
    
    # 8. リスト記号使用数
    results["list_markers"] = len(LIST_PATTERN.findall(text))
    
    # 9. 見出し数
    results["headings"] = len(HEADING_PATTERN.findall(text))
    
    # 10. 文長の均一性（標準偏差 / 平均）→ 小さいほど均一
    if len(sent_lengths) >= 3:
        mean_len = statistics.mean(sent_lengths)
        std_len = statistics.stdev(sent_lengths)
        results["sent_length_cv"] = round(std_len / mean_len, 3) if mean_len > 0 else 0
    else:
        results["sent_length_cv"] = 0
    
    # 11. 平均文長
    results["avg_sent_length"] = round(statistics.mean(sent_lengths), 1) if sent_lengths else 0
    
    # 12. 絵文字使用数
    results["emoji_count"] = len(EMOJI_PATTERN.findall(text))
    
    # 13. 総文字数
    results["char_count"] = len(text)
    
    # 14. 文数
    results["sentence_count"] = len(sentences)
    
    # 15. 段落数
    results["paragraph_count"] = len([l for l in text.split('\n\n') if l.strip()])
    
    # 16. 「〜することが重要です」系の結び文パターン
    important_endings = len(re.findall(r'(?:重要です|不可欠です|必要です|大切です)[。]?$', text, re.MULTILINE))
    results["important_endings"] = important_endings
    
    return results

# === メイン分析 ===
print("=" * 70)
print("AI Text Slop 16パターン分析結果")
print("6モデル × 10テーマ × 3試行 = 180サンプル")
print("=" * 70)

all_results = {}
for model in MODELS:
    samples = load_samples(model)
    if not samples:
        continue
    
    model_results = []
    for s in samples:
        r = analyze_sample(s["text"])
        model_results.append(r)
    all_results[model] = model_results

# === モデル別平均値テーブル ===
metrics = [
    ("ai_freq_words", "AI頻出語彙"),
    ("em_dash", "emダッシュ"),
    ("hedging", "ヘッジング"),
    ("sycophancy", "追従トーン"),
    ("boilerplate_conclusion", "定型結論"),
    ("three_set", "三点セット"),
    ("bold_count", "太字使用"),
    ("list_markers", "リスト記号"),
    ("headings", "見出し数"),
    ("emoji_count", "絵文字"),
    ("important_endings", "重要です系結び"),
    ("sent_length_cv", "文長変動係数"),
    ("avg_sent_length", "平均文長(字)"),
    ("char_count", "平均文字数"),
]

print(f"\n{'指標':<16}", end="")
for m in MODELS:
    print(f"{m:>14}", end="")
print()
print("-" * (16 + 14 * len(MODELS)))

for key, label in metrics:
    print(f"{label:<16}", end="")
    for model in MODELS:
        vals = [r[key] for r in all_results.get(model, [])]
        avg = statistics.mean(vals) if vals else 0
        print(f"{avg:>14.2f}", end="")
    print()

# === AI Text Slop Score 算出 ===
print("\n" + "=" * 70)
print("AI Text Slop Score（複合スコア）")
print("=" * 70)

# 正規化用: 各指標のmax
maxes = {}
for key, _ in metrics:
    all_vals = []
    for model in MODELS:
        all_vals.extend([r[key] for r in all_results.get(model, [])])
    maxes[key] = max(all_vals) if all_vals else 1

# スコア構成（重み付き）
score_weights = {
    "ai_freq_words": 3.0,
    "boilerplate_conclusion": 2.5,
    "sycophancy": 2.0,
    "hedging": 1.5,
    "three_set": 1.5,
    "bold_count": 1.0,
    "list_markers": 1.0,
    "important_endings": 2.0,
    "emoji_count": 1.0,
}

# 文長均一性はCVが低いほどAIっぽい → (1 - CV)で逆転
# 注: CVは通常0-1の範囲

for model in MODELS:
    scores = []
    for r in all_results.get(model, []):
        score = 0
        total_weight = 0
        for key, weight in score_weights.items():
            val = r[key]
            mx = maxes.get(key, 1) or 1
            normalized = min(val / mx, 1.0)
            score += normalized * weight
            total_weight += weight
        # 文長均一性ボーナス（CVが低い = AIっぽい）
        cv = r.get("sent_length_cv", 0.5)
        uniformity_score = max(0, 1.0 - cv)  # CV=0→1.0, CV=1→0
        score += uniformity_score * 1.5
        total_weight += 1.5
        
        final = (score / total_weight) * 100
        scores.append(final)
    
    avg_score = statistics.mean(scores) if scores else 0
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0
    print(f"{model:<20} Score: {avg_score:>6.1f} ± {std_score:.1f}")

# === JSONで詳細結果保存 ===
output = {
    "experiment": "AI Text Slop 16-pattern analysis",
    "models": MODELS,
    "sample_count": {m: len(all_results.get(m, [])) for m in MODELS},
    "averages": {},
    "raw": {}
}
for model in MODELS:
    avgs = {}
    for key, _ in metrics:
        vals = [r[key] for r in all_results.get(model, [])]
        avgs[key] = round(statistics.mean(vals), 3) if vals else 0
    output["averages"][model] = avgs
    output["raw"][model] = all_results.get(model, [])

outpath = os.path.expanduser("~/repos/iris-lab/009-ai-text-slop/results/analysis_results.json")
os.makedirs(os.path.dirname(outpath), exist_ok=True)
with open(outpath, "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n詳細結果保存: {outpath}")

