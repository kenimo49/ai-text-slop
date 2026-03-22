# AI Text Slop

**AI-generated Japanese text has a detectable "style fingerprint". This repo quantifies it.**

[![Paper](https://img.shields.io/badge/Paper-PDF-red)](paper/main.pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data](https://img.shields.io/badge/Data-190_samples-green)](data/)

---

## Try It

```bash
python scripts/analyze_patterns.py

# Output:
# ======================================================================
# AI Text Slop Score（複合スコア）
# ======================================================================
# claude-sonnet-4      Score:   21.5 ± 4.5
# gpt-4o               Score:   19.8 ± 6.3
# qwen3.5-4b           Score:   16.7 ± 5.8
# qwen3.5-9b           Score:   15.6 ± 4.2
# swallow-20b          Score:   15.2 ± 6.3
# llama3.2-1b          Score:   10.3 ± 8.8
```

## The Surprising Finding

> **Human-written Qiita articles score MORE "AI-like" (28.5) than any LLM output (max 21.5).**

This reveals that what we think of as "AI-like" writing — heavy headings, bullet lists, bold formatting — is actually **standard practice in Japanese technical blog culture**. The real AI fingerprints are in **vocabulary patterns**, not structure.

| Source | Slop Score | AI Vocabulary | Lists | Headings |
|--------|-----------|---------------|-------|----------|
| **Human (Qiita)** | **28.5** | 2.70 | **31.8** | **22.4** |
| Claude Sonnet 4 | 21.5 | **3.43** | 14.6 | 14.7 |
| GPT-4o | 19.8 | 3.33 | 7.6 | 9.9 |
| Swallow-20B | 15.2 | 0.80 | 10.1 | 6.3 |
| Llama 3.2-1B | 10.3 | 1.83 | 3.3 | 9.5 |

→ Structural patterns are **culturally biased**, not AI-specific.

## Key Findings

🔥 **RLHF makes text MORE "AI-like"** — Commercial models (Claude, GPT) score significantly higher than open-source (Kruskal–Wallis *p* < 10⁻⁹, Cohen's *d* = 1.01)

🧪 **The Swallow Paradox** — Japanese-specialized Swallow-20B has the *lowest* AI vocabulary (0.80) but the *highest* boilerplate conclusions (1.17). Vocabulary and structure dissociate.

📏 **Scale ≠ Convergence** — 4B scores higher than 9B and 20B. Alignment intensity, not parameter count, drives stylistic convergence.

🤖 **Each model has a fingerprint** — Claude over-structures, GPT hedges, Swallow uses boilerplate endings, Llama can't follow length instructions.

## How It Works

180 samples (6 models × 10 topics × 3 trials) + 10 human baseline articles, measured across **16 pattern indicators**:

**Vocabulary** — AI-frequent phrases, hedging, sycophancy, "important" endings
**Structure** — Boilerplate conclusions, three-set pattern, headings, bold, lists
**Rhythm** — Sentence-length CV, average sentence length, sentence count
**Surface** — Em-dashes, emoji, character count, paragraphs

These are combined into a weighted **AI Text Slop Score** (0–100).

## Repository Structure

```
├── data/
│   ├── claude-sonnet-4/     # 30 samples
│   ├── gpt-4o/              # 30 samples
│   ├── qwen3.5-4b/          # 30 samples
│   ├── qwen3.5-9b/          # 30 samples
│   ├── swallow-20b/         # 30 samples
│   ├── llama3.2-1b/         # 30 samples
│   └── human-qiita/         # 10 human baseline articles
├── scripts/
│   ├── collect_samples.py   # API sample collection
│   ├── analyze_patterns.py  # 16-pattern analysis + Slop Score
│   └── visualize.py         # Chart generation (matplotlib)
├── results/
│   ├── analysis_results.json
│   ├── human_baseline.json
│   └── *.png                # Visualization charts
├── paper/
│   ├── main.tex             # LaTeX source
│   ├── main.pdf             # Compiled paper (13 pages)
│   └── figures/
└── README.md
```

## Quick Start

```bash
git clone https://github.com/kenimo49/ai-text-slop.git
cd ai-text-slop

# Run analysis
python scripts/analyze_patterns.py

# Generate visualizations
pip install matplotlib
python scripts/visualize.py
```

## Statistical Validation

| Test | Statistic | *p*-value |
|------|-----------|-----------|
| Kruskal–Wallis (all 6 models) | *H* = 49.87 | *p* = 1.47 × 10⁻⁹ |
| Mann–Whitney U (commercial vs. OSS) | *U* = 5530 | *p* = 2.38 × 10⁻⁹ |
| Cohen's *d* (effect size) | *d* = 1.01 | Large effect |

## Experiment Configuration

- **Prompt**: `[Topic]についての技術ブログ記事を800字程度で書いてください。`
- **Topics**: React, Docker, REST API, GitHub Actions, TypeScript, DB Index, WebSocket, JWT, Microservices, AI Code Review
- **Trials**: 3 per model-topic pair (fresh session each)
- **Commercial**: Claude Sonnet 4 (API), GPT-4o (API)
- **Open-source**: Qwen 3.5-4B/9B, Swallow-20B, Llama 3.2-1B (Ollama, RTX 4070)

## Citation

```bibtex
@article{imoto2026aitextslop,
  title={AI Text Slop: A Quantitative Study of Stylistic Convergence
         Across Six Language Models in Japanese Technical Writing},
  author={Imoto, Ken},
  year={2026},
  url={https://github.com/kenimo49/ai-text-slop}
}
```

## Related Work

- [AI Blue: Color Recognition Bias in VLMs](https://github.com/kenimo49/ai-blue-color-bias) — Zenodo DOI: 10.5281/zenodo.19159702
- [AI Slop Escape Guide](https://zenn.dev/kenimo49/books/ai-slop-escape-guide) — Practical guide to avoiding AI text patterns (Japanese, Zenn Book)

## License

MIT
