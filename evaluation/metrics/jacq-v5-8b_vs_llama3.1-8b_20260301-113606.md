# Evaluation Report

**Fine-tuned model**: jacq-v5:8b + RAG
**Baseline model**: llama3.1:8b
**Test examples**: 10

---

## Embedding Similarity (nomic-embed-text)

Cosine similarity — higher = text lives in the same semantic space as Jacq's writing.

| Metric | Fine-tuned | Baseline | Better |
|--------|-----------|----------|--------|
| Similarity to reference | 0.67 | 0.7 | Base |
| Similarity to corpus centroid | 0.73 | 0.82 | Base |

## Style Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Avg sentence length | 15.97 words | 18.92 words | 18.14 words |
| Vocabulary overlap | — | 0.28 | 0.2 |
| ROUGE-1 F1 | — | 0.48 | 0.39 |

## Structural Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Dashes/1k words | 9.28 | 17.36 | 12.16 |
| Parentheses/1k words | 3.0 | 7.17 | 6.66 |
| Questions/1k words | 13.6 | 11.16 | 14.78 |
| Fragment % | 15.79% | 8.74% | 12.92% |

## Failure Mode Analysis (Gemini)

| Metric | Fine-tuned | Baseline | Better |
|--------|-----------|----------|--------|
| Avg buzzwords | 11.1 | 8.9 | Base |
| Flagged as generic AI | 1/10 | 0/10 | Base |
| Avg specificity (count) | 3.9 | 3.7 | FT |
| Avg directness (1-5) | 4.1 | 4.2 | Base |

## Per-Example Results

### Example 1
**Prompt**: Write about a recent retreat or getaway where you were able to focus on writing or another creative pursuit....

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4006 | 0.3202 |
| Vocab overlap | 0.2172 | 0.1598 |
| Word count | 410 | 353 |
| Embed sim (ref) | 0.8507 | 0.734 |
| Embed sim (corpus) | 0.8116 | 0.7796 |
| Buzzwords | 3 | 4 |
| Specificity | 14 | 2 |
| Directness | 4/5 | 4/5 |

### Example 2
**Prompt**: Write a blog post titled "Jacqueline Fisch - Wishbeads Guest Blog post"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4 | 0.4065 |
| Vocab overlap | 0.2283 | 0.1922 |
| Word count | 1706 | 470 |
| Embed sim (ref) | 0.0 | 0.7376 |
| Embed sim (corpus) | 0.0 | 0.8549 |
| Buzzwords | 8 | 10 |
| Specificity | 7 | 5 |
| Directness | 4/5 | 4/5 |

### Example 3
**Prompt**: Describe the writing process as a journey of intentional motion and growth, where one's body of work is carefully curate...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.511 | 0.3692 |
| Vocab overlap | 0.2459 | 0.1959 |
| Word count | 625 | 343 |
| Embed sim (ref) | 0.8001 | 0.7785 |
| Embed sim (corpus) | 0.8512 | 0.8403 |
| Buzzwords | 36 | 24 |
| Specificity | 0 | 2 |
| Directness | 4/5 | 5/5 |

### Example 4
**Prompt**: Describe the strategies you use to manage your thoughts and emotions when faced with negative self-talk or criticism fro...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.5219 | 0.392 |
| Vocab overlap | 0.2784 | 0.2138 |
| Word count | 609 | 415 |
| Embed sim (ref) | 0.8226 | 0.6871 |
| Embed sim (corpus) | 0.7851 | 0.8133 |
| Buzzwords | 4 | 8 |
| Specificity | 0 | 1 |
| Directness | 4/5 | 4/5 |

### Example 5
**Prompt**: Write a blog post about inspiring astrology writing prompts for creative businesses...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.6116 | 0.3636 |
| Vocab overlap | 0.5089 | 0.1952 |
| Word count | 733 | 507 |
| Embed sim (ref) | 0.9316 | 0.8443 |
| Embed sim (corpus) | 0.8313 | 0.8159 |
| Buzzwords | 10 | 9 |
| Specificity | 9 | 8 |
| Directness | 4/5 | 4/5 |

### Example 6
**Prompt**: Write a blog post titled "What if it was easy"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.5806 | 0.45 |
| Vocab overlap | 0.3254 | 0.2209 |
| Word count | 623 | 444 |
| Embed sim (ref) | 0.9082 | 0.822 |
| Embed sim (corpus) | 0.8211 | 0.8155 |
| Buzzwords | 6 | 10 |
| Specificity | 4 | 7 |
| Directness | 5/5 | 4/5 |

### Example 7
**Prompt**: Write a blog post titled "Finding your way"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4837 | 0.4426 |
| Vocab overlap | 0.2665 | 0.2335 |
| Word count | 666 | 503 |
| Embed sim (ref) | 0.7424 | 0.6949 |
| Embed sim (corpus) | 0.8354 | 0.8386 |
| Buzzwords | 25 | 9 |
| Specificity | 4 | 7 |
| Directness | 4/5 | 4/5 |

### Example 8
**Prompt**: Write about why women should stop waiting for permission to write...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3088 | 0.3831 |
| Vocab overlap | 0.2091 | 0.2117 |
| Word count | 627 | 334 |
| Embed sim (ref) | 0.8644 | 0.8716 |
| Embed sim (corpus) | 0.8287 | 0.7952 |
| Buzzwords | 11 | 2 |
| Specificity | 0 | 4 |
| Directness | 4/5 | 4/5 |

### Example 9
**Prompt**: Write a blog post about crisis comms...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4209 | 0.4357 |
| Vocab overlap | 0.2441 | 0.2181 |
| Word count | 1069 | 489 |
| Embed sim (ref) | 0.7594 | 0.7995 |
| Embed sim (corpus) | 0.7386 | 0.7791 |
| Buzzwords | 2 | 4 |
| Specificity | 0 | 1 |
| Directness | 4/5 | 5/5 |

### Example 10
**Prompt**: Write a blog post titled "Writing with astrology - days of the week"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.5463 | 0.3352 |
| Vocab overlap | 0.2985 | 0.1952 |
| Word count | 1143 | 636 |
| Embed sim (ref) | 0.0 | 0.0 |
| Embed sim (corpus) | 0.7933 | 0.8605 |
| Buzzwords | 6 | 9 |
| Specificity | 1 | 0 |
| Directness | 4/5 | 4/5 |
