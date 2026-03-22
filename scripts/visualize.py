#!/usr/bin/env python3
"""AI Text Slop 分析結果の可視化"""

import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 日本語フォント
font_path = None
for p in ["/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"]:
    if os.path.exists(p):
        font_path = p; break
if font_path:
    fp = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = fp.get_name()
else:
    plt.rcParams['font.family'] = 'DejaVu Sans'

RESULTS_PATH = os.path.expanduser("~/repos/iris-lab/009-ai-text-slop/results/analysis_results.json")
OUT_DIR = os.path.expanduser("~/repos/iris-lab/009-ai-text-slop/results")

with open(RESULTS_PATH) as f:
    data = json.load(f)

models = data["models"]
model_labels = {
    "claude-sonnet-4": "Claude\nSonnet 4",
    "gpt-4o": "GPT-4o",
    "qwen3.5-4b": "Qwen3.5\n4B",
    "qwen3.5-9b": "Qwen3.5\n9B",
    "swallow-20b": "Swallow\n20B",
    "llama3.2-1b": "Llama3.2\n1B"
}
colors = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]

# === 1. AI Text Slop Score 棒グラフ ===
fig, ax = plt.subplots(figsize=(10, 6))
scores_data = {}
for model in models:
    raw = data["raw"].get(model, [])
    if not raw: continue
    # Recalculate scores
    score_weights = {
        "ai_freq_words": 3.0, "boilerplate_conclusion": 2.5,
        "sycophancy": 2.0, "hedging": 1.5, "three_set": 1.5,
        "bold_count": 1.0, "list_markers": 1.0, "important_endings": 2.0, "emoji_count": 1.0,
    }
    # Get maxes
    maxes = {}
    for key in score_weights:
        all_vals = []
        for m in models:
            all_vals.extend([r.get(key, 0) for r in data["raw"].get(m, [])])
        maxes[key] = max(all_vals) if all_vals else 1
    
    scores = []
    for r in raw:
        score = 0; tw = 0
        for key, w in score_weights.items():
            val = r.get(key, 0)
            mx = maxes.get(key, 1) or 1
            score += min(val/mx, 1.0) * w; tw += w
        cv = r.get("sent_length_cv", 0.5)
        score += max(0, 1-cv) * 1.5; tw += 1.5
        scores.append((score/tw)*100)
    scores_data[model] = scores

x = np.arange(len(models))
means = [np.mean(scores_data.get(m, [0])) for m in models]
stds = [np.std(scores_data.get(m, [0])) for m in models]
bars = ax.bar(x, means, yerr=stds, color=colors, capsize=5, edgecolor='white', linewidth=1.5)
ax.set_xticks(x)
ax.set_xticklabels([model_labels.get(m, m) for m in models], fontsize=11)
ax.set_ylabel("AI Text Slop Score", fontsize=13)
ax.set_title("AI Text Slop Score by Model", fontsize=15, fontweight='bold')
ax.set_ylim(0, 40)
for bar, mean in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5, f'{mean:.1f}', ha='center', fontsize=12, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "slop_score_comparison.png"), dpi=150)
print("Saved: slop_score_comparison.png")
plt.close()

# === 2. レーダーチャート（主要6指標） ===
radar_keys = ["ai_freq_words", "boilerplate_conclusion", "hedging", "bold_count", "list_markers", "three_set"]
radar_labels = ["AI Vocabulary", "Boilerplate\nConclusion", "Hedging", "Bold Usage", "List Markers", "Three-Set\nPattern"]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
angles = np.linspace(0, 2*np.pi, len(radar_keys), endpoint=False).tolist()
angles += angles[:1]

for i, model in enumerate(models):
    avgs = data["averages"].get(model, {})
    values = [avgs.get(k, 0) for k in radar_keys]
    # Normalize to 0-1 range
    maxes_radar = {}
    for k in radar_keys:
        all_v = [data["averages"].get(m, {}).get(k, 0) for m in models]
        maxes_radar[k] = max(all_v) if all_v else 1
    values_norm = [v / (maxes_radar[k] or 1) for v, k in zip(values, radar_keys)]
    values_norm += values_norm[:1]
    ax.plot(angles, values_norm, 'o-', linewidth=2, label=model_labels.get(model, model), color=colors[i])
    ax.fill(angles, values_norm, alpha=0.1, color=colors[i])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(radar_labels, fontsize=10)
ax.set_ylim(0, 1.1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
ax.set_title("AI Text Slop Pattern Radar", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "slop_radar_chart.png"), dpi=150)
print("Saved: slop_radar_chart.png")
plt.close()

# === 3. 箱ひげ図（モデル間文字数比較） ===
fig, ax = plt.subplots(figsize=(10, 6))
char_data = []
for model in models:
    chars = [r.get("char_count", 0) for r in data["raw"].get(model, [])]
    char_data.append(chars)
bp = ax.boxplot(char_data, labels=[model_labels.get(m, m) for m in models], patch_artist=True)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel("Character Count", fontsize=13)
ax.set_title("Text Length Distribution by Model", fontsize=15, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "char_count_boxplot.png"), dpi=150)
print("Saved: char_count_boxplot.png")
plt.close()

# === 4. ヒートマップ（モデル×指標） ===
heatmap_keys = ["ai_freq_words", "boilerplate_conclusion", "hedging", "sycophancy", 
                "bold_count", "list_markers", "headings", "three_set", "important_endings"]
heatmap_labels = ["AI Vocab", "Boilerplate", "Hedging", "Sycophancy",
                  "Bold", "Lists", "Headings", "3-Set", "Important"]

fig, ax = plt.subplots(figsize=(12, 5))
matrix = []
for model in models:
    avgs = data["averages"].get(model, {})
    row = [avgs.get(k, 0) for k in heatmap_keys]
    matrix.append(row)

matrix = np.array(matrix)
# Normalize columns
col_max = matrix.max(axis=0)
col_max[col_max == 0] = 1
matrix_norm = matrix / col_max

im = ax.imshow(matrix_norm, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(heatmap_labels)))
ax.set_xticklabels(heatmap_labels, fontsize=11, rotation=45, ha='right')
ax.set_yticks(range(len(models)))
ax.set_yticklabels([model_labels.get(m, m).replace('\n', ' ') for m in models], fontsize=11)

for i in range(len(models)):
    for j in range(len(heatmap_keys)):
        ax.text(j, i, f'{matrix[i,j]:.1f}', ha='center', va='center', fontsize=9,
                color='white' if matrix_norm[i,j] > 0.6 else 'black')

ax.set_title("AI Text Slop Pattern Heatmap", fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax, label="Normalized Intensity")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "slop_heatmap.png"), dpi=150)
print("Saved: slop_heatmap.png")
plt.close()

print("\n=== All visualizations saved ===")
