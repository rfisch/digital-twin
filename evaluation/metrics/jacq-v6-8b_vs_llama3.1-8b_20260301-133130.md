# Evaluation Report

**Fine-tuned model**: jacq-v6:8b
**Baseline model**: llama3.1:8b
**Test examples**: 10

---

## Perplexity (MLX)

Lower perplexity = model better predicts Jacq's writing patterns.

| | Loss | Perplexity | Examples |
|---|---|---|---|
| Baseline | 2.6981 | 14.85 | 58 |


## Embedding Similarity (nomic-embed-text)

Cosine similarity — higher = text lives in the same semantic space as Jacq's writing.

| Metric | Fine-tuned | Baseline | Better |
|--------|-----------|----------|--------|
| Similarity to reference | 0.75 | 0.75 | Tie |
| Similarity to corpus centroid | 0.78 | 0.8 | Base |

## Style Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Avg sentence length | 18.11 words | 18.65 words | 18.08 words |
| Vocabulary overlap | — | 0.23 | 0.2 |
| ROUGE-1 F1 | — | 0.42 | 0.4 |

## Structural Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Dashes/1k words | 7.29 | 16.14 | 12.7 |
| Parentheses/1k words | 1.44 | 2.83 | 5.06 |
| Questions/1k words | 12.38 | 8.07 | 13.73 |
| Fragment % | 15.93% | 8.72% | 10.96% |

## Failure Mode Analysis (Gemini)

| Metric | Fine-tuned | Baseline | Better |
|--------|-----------|----------|--------|
| Avg buzzwords | 4.8 | 5.5 | FT |
| Flagged as generic AI | 0/10 | 0/10 | Tie |
| Avg specificity (count) | 5.1 | 4.7 | FT |
| Avg directness (1-5) | 4.1 | 4.3 | Base |

## Per-Example Results

### Example 1
**Prompt**: Write about a moment from your childhood where you felt belittled or criticized by an authority figure, and how that exp...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3887 | 0.3962 |
| Vocab overlap | 0.2057 | 0.2165 |
| Word count | 511 | 422 |
| Embed sim (ref) | 0.7005 | 0.7196 |
| Embed sim (corpus) | 0.718 | 0.7825 |
| Buzzwords | 4 | 6 |
| Specificity | 5 | 6 |
| Directness | 4/5 | 4/5 |

### Example 2
**Prompt**: Write a blog post titled "Language with meaning"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3898 | 0.3817 |
| Vocab overlap | 0.2212 | 0.2 |
| Word count | 611 | 405 |
| Embed sim (ref) | 0.5912 | 0.5737 |
| Embed sim (corpus) | 0.7755 | 0.8047 |
| Buzzwords | 4 | 7 |
| Specificity | 1 | 1 |
| Directness | 4/5 | 5/5 |

### Example 3
**Prompt**: Describe the benefits of being part of a writing community for entrepreneurs who want to grow their business through wri...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4267 | 0.4155 |
| Vocab overlap | 0.2129 | 0.1966 |
| Word count | 309 | 320 |
| Embed sim (ref) | 0.8526 | 0.8148 |
| Embed sim (corpus) | 0.8375 | 0.8117 |
| Buzzwords | 10 | 9 |
| Specificity | 1 | 0 |
| Directness | 4/5 | 4/5 |

### Example 4
**Prompt**: Write from the perspective of an adult reflecting on their most memorable experiences with younger siblings during famil...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4749 | 0.3494 |
| Vocab overlap | 0.222 | 0.167 |
| Word count | 713 | 357 |
| Embed sim (ref) | 0.7118 | 0.7393 |
| Embed sim (corpus) | 0.6954 | 0.6852 |
| Buzzwords | 0 | 2 |
| Specificity | 25 | 6 |
| Directness | 4/5 | 5/5 |

### Example 5
**Prompt**: Write a blog post titled "advice detox"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4841 | 0.3645 |
| Vocab overlap | 0.257 | 0.2147 |
| Word count | 732 | 251 |
| Embed sim (ref) | 0.7107 | 0.7291 |
| Embed sim (corpus) | 0.8157 | 0.8237 |
| Buzzwords | 4 | 7 |
| Specificity | 3 | 3 |
| Directness | 4/5 | 4/5 |

### Example 6
**Prompt**: Write a blog post titled "the one question trick to knowing when your work is _done_"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.5012 | 0.4715 |
| Vocab overlap | 0.2867 | 0.25 |
| Word count | 474 | 378 |
| Embed sim (ref) | 0.7633 | 0.7038 |
| Embed sim (corpus) | 0.7667 | 0.7784 |
| Buzzwords | 4 | 0 |
| Specificity | 0 | 1 |
| Directness | 4/5 | 5/5 |

### Example 7
**Prompt**: Write a blog post about getting serious...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3865 | 0.3633 |
| Vocab overlap | 0.25 | 0.1867 |
| Word count | 437 | 450 |
| Embed sim (ref) | 0.7983 | 0.7615 |
| Embed sim (corpus) | 0.8667 | 0.8806 |
| Buzzwords | 6 | 2 |
| Specificity | 0 | 10 |
| Directness | 5/5 | 4/5 |

### Example 8
**Prompt**: Write about homeschooling and creativity...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3543 | 0.4039 |
| Vocab overlap | 0.2157 | 0.1893 |
| Word count | 609 | 367 |
| Embed sim (ref) | 0.814 | 0.8768 |
| Embed sim (corpus) | 0.6942 | 0.7787 |
| Buzzwords | 0 | 5 |
| Specificity | 8 | 12 |
| Directness | 4/5 | 4/5 |

### Example 9
**Prompt**: Write about doing nothing is a decision. when it's time to move on._ for the blog...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3372 | 0.4526 |
| Vocab overlap | 0.1978 | 0.2 |
| Word count | 373 | 508 |
| Embed sim (ref) | 0.7058 | 0.7293 |
| Embed sim (corpus) | 0.8011 | 0.7752 |
| Buzzwords | 5 | 6 |
| Specificity | 0 | 4 |
| Directness | 4/5 | 4/5 |

### Example 10
**Prompt**: Write about a personal introduction from the author of a book that promises to help readers overcome their struggles wit...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4594 | 0.4229 |
| Vocab overlap | 0.2478 | 0.2178 |
| Word count | 394 | 379 |
| Embed sim (ref) | 0.8545 | 0.8034 |
| Embed sim (corpus) | 0.8731 | 0.8477 |
| Buzzwords | 11 | 11 |
| Specificity | 8 | 4 |
| Directness | 4/5 | 4/5 |
