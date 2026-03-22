import json, statistics
import numpy as np
from scipy import stats

with open('/home/iris/repos/iris-lab/009-ai-text-slop/results/analysis_results.json') as f:
    data = json.load(f)

raw = data['raw']
models = data['models']

score_weights = {
    "ai_freq_words": 3.0, "boilerplate_conclusion": 2.5,
    "headings": 1.5, "sycophancy": 2.0, "hedging": 1.5,
    "three_set": 1.5, "bold_count": 1.0, "list_markers": 1.0,
    "important_endings": 2.0, "emoji_count": 1.0,
}

# Get maxes across all models
all_samples = [s for m in models for s in raw[m]]
maxes = {}
for key in score_weights:
    vals = [s.get(key, 0) for s in all_samples]
    maxes[key] = max(vals) if vals else 1

def calc_scores(samples, weights, custom_maxes=None):
    mx = custom_maxes or maxes
    scores = []
    for r in samples:
        score = 0
        total_weight = 0
        for key, weight in weights.items():
            val = r.get(key, 0)
            m = mx.get(key, 1) or 1
            normalized = min(val / m, 1.0)
            score += normalized * weight
            total_weight += weight
        cv = r.get("sent_length_cv", 0.5)
        uniformity_score = max(0, 1.0 - cv)
        score += uniformity_score * 1.5
        total_weight += 1.5
        final = (score / total_weight) * 100
        scores.append(final)
    return scores

# Vocabulary-only
vocab_w = {k: v for k, v in score_weights.items() if k in ['ai_freq_words', 'hedging', 'sycophancy', 'important_endings']}
struct_w = {k: v for k, v in score_weights.items() if k in ['boilerplate_conclusion', 'three_set', 'headings', 'list_markers', 'bold_count']}
equal_w = {k: 1.0 for k in score_weights}

print("=" * 70)
print("SENSITIVITY ANALYSIS (normalized scores, 0-100)")
print("=" * 70)

for label, w in [("Original", score_weights), ("Equal Weights", equal_w), 
                  ("Vocabulary Only", vocab_w), ("Structure Only", struct_w)]:
    print(f"\n--- {label} ---")
    mm = {}
    for model in models:
        sc = calc_scores(raw[model], w)
        mean = statistics.mean(sc)
        std = statistics.stdev(sc) if len(sc) > 1 else 0
        mm[model] = mean
        print(f"  {model:20s}  {mean:5.1f} ± {std:4.1f}")
    ranked = sorted(mm.items(), key=lambda x: -x[1])
    print(f"  Rank: {' > '.join([str(m[0][:10])+'('+str(round(m[1],1))+')' for m in ranked])}")

    # Commercial vs OSS
    comm_scores = []
    oss_scores = []
    for m in ['claude-sonnet-4', 'gpt-4o']:
        comm_scores.extend(calc_scores(raw[m], w))
    for m in ['qwen3.5-4b', 'qwen3.5-9b', 'swallow-20b', 'llama3.2-1b']:
        oss_scores.extend(calc_scores(raw[m], w))
    u, p = stats.mannwhitneyu(comm_scores, oss_scores, alternative='greater')
    pooled = np.sqrt((np.std(comm_scores)**2 + np.std(oss_scores)**2) / 2)
    d = (np.mean(comm_scores) - np.mean(oss_scores)) / pooled if pooled > 0 else 0
    print(f"  Commercial vs OSS: d={d:.2f}, p={p:.2e}")

# Feature-level effect sizes
print("\n" + "=" * 70)
print("FEATURE-LEVEL EFFECT SIZES (Commercial vs OSS)")
print("=" * 70)
print(f"  {'Feature':25s} {'Comm':>7s} {'OSS':>7s} {'d':>6s} {'p':>10s} {'sig':>4s}")
print(f"  {'-'*60}")

for feat in ['ai_freq_words', 'boilerplate_conclusion', 'hedging', 'sycophancy',
             'headings', 'list_markers', 'bold_count', 'sent_length_cv', 'three_set']:
    cv = [s.get(feat, 0) for m in ['claude-sonnet-4', 'gpt-4o'] for s in raw[m]]
    ov = [s.get(feat, 0) for m in ['qwen3.5-4b', 'qwen3.5-9b', 'swallow-20b', 'llama3.2-1b'] for s in raw[m]]
    cm, om = np.mean(cv), np.mean(ov)
    ps = np.sqrt((np.std(cv)**2 + np.std(ov)**2) / 2)
    d = (cm - om) / ps if ps > 0 else 0
    u, p = stats.mannwhitneyu(cv, ov, alternative='two-sided')
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    print(f"  {feat:25s} {cm:7.2f} {om:7.2f} {d:+6.2f} {p:10.2e} {sig:>4s}")

# Leave-one-feature-out
print("\n" + "=" * 70)
print("LEAVE-ONE-FEATURE-OUT")
print("=" * 70)
orig_rank = sorted([(m, statistics.mean(calc_scores(raw[m], score_weights))) for m in models], key=lambda x: -x[1])
print(f"  Original: {' > '.join([f'{r[0][:10]}' for r in orig_rank])}")
for dropped in score_weights:
    loo = dict(score_weights)
    del loo[dropped]
    mm = sorted([(m, statistics.mean(calc_scores(raw[m], loo))) for m in models], key=lambda x: -x[1])
    changed = "CHANGED" if [r[0] for r in mm[:2]] != [r[0] for r in orig_rank[:2]] else ""
    print(f"  Drop {dropped:25s}: {' > '.join([f'{r[0][:10]}' for r in mm])} {changed}")

