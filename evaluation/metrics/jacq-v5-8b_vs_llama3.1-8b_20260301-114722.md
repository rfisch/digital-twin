# Evaluation Report

**Fine-tuned model**: jacq-v5:8b
**Baseline model**: llama3.1:8b
**Test examples**: 10

---

## Embedding Similarity (nomic-embed-text)

Cosine similarity — higher = text lives in the same semantic space as Jacq's writing.

| Metric | Fine-tuned | Baseline | Better |
|--------|-----------|----------|--------|
| Similarity to reference | 0.7 | 0.69 | FT |
| Similarity to corpus centroid | 0.79 | 0.82 | Base |

## Style Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Avg sentence length | 15.97 words | 17.49 words | 17.09 words |
| Vocabulary overlap | — | 0.23 | 0.2 |
| ROUGE-1 F1 | — | 0.44 | 0.39 |

## Structural Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Dashes/1k words | 9.28 | 12.89 | 14.25 |
| Parentheses/1k words | 3.0 | 3.59 | 1.89 |
| Questions/1k words | 13.6 | 17.16 | 20.0 |
| Fragment % | 15.79% | 9.89% | 15.4% |

## Failure Mode Analysis (Gemini)

| Metric | Fine-tuned | Baseline | Better |
|--------|-----------|----------|--------|
| Avg buzzwords | 5.1 | 6.3 | FT |
| Flagged as generic AI | 1/10 | 0/10 | Base |
| Avg specificity (count) | 5.2 | 4.0 | FT |
| Avg directness (1-5) | 4.1 | 4.3 | Base |

## Per-Example Results

### Example 1
**Prompt**: Write about a recent retreat or getaway where you were able to focus on writing or another creative pursuit....

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4747 | 0.3591 |
| Vocab overlap | 0.2319 | 0.1742 |
| Word count | 1376 | 433 |
| Embed sim (ref) | 0.8793 | 0.7692 |
| Embed sim (corpus) | 0.8309 | 0.7941 |
| Buzzwords | 0 | 6 |
| Specificity | 14 | 9 |
| Directness | 4/5 | 4/5 |

### Example 2
**Prompt**: Write a blog post titled "Jacqueline Fisch - Wishbeads Guest Blog post"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4 | 0.3897 |
| Vocab overlap | 0.1993 | 0.1793 |
| Word count | 527 | 502 |
| Embed sim (ref) | 0.6189 | 0.5822 |
| Embed sim (corpus) | 0.8128 | 0.8283 |
| Buzzwords | 1 | 9 |
| Specificity | 9 | 11 |
| Directness | 4/5 | 5/5 |

### Example 3
**Prompt**: Describe the writing process as a journey of intentional motion and growth, where one's body of work is carefully curate...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4369 | 0.3851 |
| Vocab overlap | 0.1952 | 0.1828 |
| Word count | 466 | 445 |
| Embed sim (ref) | 0.7712 | 0.7811 |
| Embed sim (corpus) | 0.8329 | 0.8606 |
| Buzzwords | 14 | 3 |
| Specificity | 0 | 1 |
| Directness | 4/5 | 4/5 |

### Example 4
**Prompt**: Describe the strategies you use to manage your thoughts and emotions when faced with negative self-talk or criticism fro...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3521 | 0.3807 |
| Vocab overlap | 0.2128 | 0.216 |
| Word count | 273 | 352 |
| Embed sim (ref) | 0.7487 | 0.7305 |
| Embed sim (corpus) | 0.7459 | 0.7846 |
| Buzzwords | 6 | 6 |
| Specificity | 0 | 0 |
| Directness | 4/5 | 4/5 |

### Example 5
**Prompt**: Write a blog post about inspiring astrology writing prompts for creative businesses...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4876 | 0.3703 |
| Vocab overlap | 0.2362 | 0.1954 |
| Word count | 744 | 554 |
| Embed sim (ref) | 0.8601 | 0.8688 |
| Embed sim (corpus) | 0.8191 | 0.846 |
| Buzzwords | 6 | 19 |
| Specificity | 0 | 6 |
| Directness | 4/5 | 4/5 |

### Example 6
**Prompt**: Write a blog post titled "What if it was easy"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4694 | 0.445 |
| Vocab overlap | 0.2126 | 0.2057 |
| Word count | 354 | 341 |
| Embed sim (ref) | 0.761 | 0.7969 |
| Embed sim (corpus) | 0.7426 | 0.7787 |
| Buzzwords | 7 | 7 |
| Specificity | 0 | 0 |
| Directness | 4/5 | 4/5 |

### Example 7
**Prompt**: Write a blog post titled "Finding your way"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4871 | 0.4447 |
| Vocab overlap | 0.2767 | 0.225 |
| Word count | 637 | 377 |
| Embed sim (ref) | 0.6897 | 0.6979 |
| Embed sim (corpus) | 0.7642 | 0.8305 |
| Buzzwords | 10 | 4 |
| Specificity | 11 | 5 |
| Directness | 4/5 | 5/5 |

### Example 8
**Prompt**: Write about why women should stop waiting for permission to write...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.394 | 0.3709 |
| Vocab overlap | 0.2529 | 0.2166 |
| Word count | 423 | 364 |
| Embed sim (ref) | 0.8705 | 0.8514 |
| Embed sim (corpus) | 0.8134 | 0.8344 |
| Buzzwords | 5 | 4 |
| Specificity | 4 | 3 |
| Directness | 4/5 | 4/5 |

### Example 9
**Prompt**: Write a blog post about crisis comms...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.4896 | 0.3489 |
| Vocab overlap | 0.2322 | 0.1951 |
| Word count | 869 | 315 |
| Embed sim (ref) | 0.7971 | 0.7935 |
| Embed sim (corpus) | 0.7084 | 0.7791 |
| Buzzwords | 0 | 3 |
| Specificity | 13 | 5 |
| Directness | 5/5 | 5/5 |

### Example 10
**Prompt**: Write a blog post titled "Writing with astrology - days of the week"...

| | Fine-tuned | Baseline |
|---|---|---|
| ROUGE-1 | 0.3862 | 0.3621 |
| Vocab overlap | 0.2275 | 0.213 |
| Word count | 713 | 674 |
| Embed sim (ref) | 0.0 | 0.0 |
| Embed sim (corpus) | 0.7966 | 0.8545 |
| Buzzwords | 2 | 2 |
| Specificity | 1 | 0 |
| Directness | 4/5 | 4/5 |
