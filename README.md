# AI Text Slop: A Quantitative Study of Stylistic Convergence Across Six Language Models in Japanese Technical Writing

## Overview

This repository contains the data, code, and paper for a quantitative analysis of AI-generated text stylistic patterns ("AI Text Slop") in Japanese technical blog writing.

We analyze **180 samples** from **6 LLMs** across **10 topics** with **16 pattern indicators**, and propose a composite **AI Text Slop Score** to measure stylistic convergence.

## Key Findings

| Model | Slop Score | AI Vocabulary | Boilerplate | Sent. CV |
|-------|-----------|---------------|-------------|----------|
| Claude Sonnet 4 | **21.5** | **3.43** | 1.03 | 0.56 |
| GPT-4o | 19.8 | 3.33 | 0.80 | 0.56 |
| Qwen 3.5-4B | 16.7 | 2.70 | 0.57 | 0.57 |
| Qwen 3.5-9B | 15.6 | 2.30 | 0.73 | 0.59 |
| Swallow-20B | 15.2 | 0.80 | **1.17** | 0.76 |
| Llama 3.2-1B | 10.3 | 1.83 | 0.07 | **1.08** |
| **Human (Qiita)** | **28.5** | 2.70 | 2.20 | 0.62 |

- **RLHF-aligned commercial models** score significantly higher than open-source alternatives (Kruskal–Wallis $H = 49.87$, $p < 10^{-9}$, Cohen's $d = 1.01$)
- **Swallow-20B Paradox**: Lowest AI vocabulary (0.80) but highest boilerplate conclusions (1.17) — vocabulary and structural patterns dissociate
- **Human baseline surprise**: Qiita authors score *higher* than AI on structural metrics, revealing cultural confounding in formatting-based indicators

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
│   ├── analyze_patterns.py  # 16-pattern analysis
│   └── visualize.py         # Chart generation
├── results/
│   ├── analysis_results.json
│   ├── human_baseline.json
│   └── *.png                # Visualization charts
├── paper/
│   ├── main.tex             # LaTeX source
│   ├── main.pdf             # Compiled paper
│   └── figures/             # Paper figures
└── README.md
```

## Quick Start

```bash
# Run analysis
python scripts/analyze_patterns.py

# Generate visualizations
pip install matplotlib
python scripts/visualize.py
```

## 16 Pattern Indicators

### Vocabulary Patterns
1. AI-frequent vocabulary count (30 Japanese phrases)
2. Hedging expressions
3. Sycophantic/exaggerative tone
4. "Important" sentence endings

### Structural Patterns
5. Boilerplate conclusions
6. Three-set pattern (merits/demerits/summary)
7. Heading count
8. Bold usage count
9. List marker count

### Rhythm Patterns
10. Sentence-length coefficient of variation (CV)
11. Average sentence length
12. Sentence count

### Surface Patterns
13. Em-dash count
14. Emoji count
15. Total character count
16. Paragraph count

## Experiment Configuration

- **Prompt**: `[Topic]についての技術ブログ記事を800字程度で書いてください。`
- **Topics**: 10 common technical blog themes (React, Docker, REST API, etc.)
- **Trials**: 3 per model-topic pair (new session each)
- **Commercial models**: Claude Sonnet 4 (API), GPT-4o (API)
- **Open-source models**: Qwen 3.5-4B/9B, Swallow-20B, Llama 3.2-1B (Ollama, RTX 4070)

## Citation

```bibtex
@article{imoto2026aitextslop,
  title={AI Text Slop: A Quantitative Study of Stylistic Convergence Across Six Language Models in Japanese Technical Writing},
  author={Imoto, Ken},
  year={2026},
  url={https://github.com/kenimo49/ai-text-slop}
}
```

## Related Work

- [AI Blue: Color Recognition Bias in VLMs](https://github.com/kenimo49/ai-blue-color-bias) (Zenodo DOI: 10.5281/zenodo.19159702)

## License

MIT License
