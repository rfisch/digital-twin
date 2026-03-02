# Evaluation Report

**Fine-tuned model**: jacq-v5:8b
**Baseline model**: llama3.1:8b
**Judge model**: gemini
**Test examples**: 10

---

## LLM-as-Judge Scores (1-10)

| Criterion | Fine-tuned | Baseline | Delta |
|-----------|-----------|----------|-------|
| Voice | 6.4 | 6.4 | 0.0 |
| Edge | 5.3 | 5.4 | -0.1 |
| Specificity | 5.6 | 6.2 | -0.6 |
| Authenticity | 5.9 | 6.1 | -0.2 |
| **Overall** | **5.9** | **6.2** | **-0.3** |

## Style Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Avg sentence length | 15.97 words | 16.96 words | 17.1 words |
| Vocabulary overlap | — | 0.2 | 0.2 |
| ROUGE-1 F1 | — | 0.4 | 0.38 |

## Structural Metrics (v5 targets: dashes 5+/1k, fragments 12%+)

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Dashes/1k words | 9.28 | 13.38 | 11.98 |
| Parentheses/1k words | 3.0 | 2.07 | 4.53 |
| Questions/1k words | 13.6 | 12.3 | 18.01 |
| Fragment % | 15.79% | 9.53% | 13.02% |

## Per-Example Results

### Example 1
**Prompt**: Write about a recent retreat or getaway where you were able to focus on writing or another creative pursuit....

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 5/10 |
| ROUGE-1 | 0.4244 | 0.3209 |
| Vocab overlap | 0.2083 | 0.1439 |
| Word count | 432 | 373 |

Judge notes (fine-tuned): Good on specific details and some grounded vocabulary, but lacks Jacq's distinctive brashness and directness. It leans too much into generic positive blogger/self-help phrasing and rhetorical questions, making it feel a bit too polished and less authentic to her unique voice.

### Example 2
**Prompt**: Write a blog post titled "Jacqueline Fisch - Wishbeads Guest Blog post"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 5/10 |
| ROUGE-1 | 0.3586 | 0.3642 |
| Vocab overlap | 0.1932 | 0.186 |
| Word count | 407 | 387 |

Judge notes (fine-tuned): Good attempt at structural elements and avoiding buzzwords, but the intro/outro and lack of deeply personal, brash anecdotes make it feel more like a generic friendly coach than Jacq.

### Example 3
**Prompt**: Describe the writing process as a journey of intentional motion and growth, where one's body of work is carefully curate...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 3/10 | 7/10 |
| ROUGE-1 | 0.497 | 0.333 |
| Vocab overlap | 0.2138 | 0.1845 |
| Word count | 532 | 333 |

Judge notes (fine-tuned): The AI attempts a friendly, conversational tone but misses Jacq's unique brashness, grounded vocabulary, and specific, real-life metaphors, leaning instead into generic self-help tropes and abstract language.

### Example 4
**Prompt**: Describe the strategies you use to manage your thoughts and emotions when faced with negative self-talk or criticism fro...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 4/10 | 7/10 |
| ROUGE-1 | 0.3402 | 0.3404 |
| Vocab overlap | 0.1938 | 0.1812 |
| Word count | 298 | 308 |

Judge notes (fine-tuned): The AI adopted a conversational tone and some structural habits (dashes, 'And' starts) but fundamentally missed Jacq's core voice. It heavily relies on generic self-help jargon and abstract concepts, lacking her grounded vocabulary, brash directness, and real-life specificity, making it sound like a generic coach rather than a friend.

### Example 5
**Prompt**: Write a blog post about inspiring astrology writing prompts for creative businesses...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 6/10 | 4/10 |
| ROUGE-1 | 0.0192 | 0.3039 |
| Vocab overlap | 0.0205 | 0.1675 |
| Word count | 12 | 477 |

Judge notes (fine-tuned): The AI-generated title is plausible and avoids generic AI pitfalls, capturing a conversational and direct tone. However, as a single title, it lacks the deeper specificity (niche vocabulary, personal references) and unique structural quirks (grammar breaks, dashes) that define Jacq's full writing style.

### Example 6
**Prompt**: Write a blog post titled "What if it was easy"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 7/10 |
| ROUGE-1 | 0.5599 | 0.5136 |
| Vocab overlap | 0.2585 | 0.2299 |
| Word count | 483 | 444 |

Judge notes (fine-tuned): The AI successfully incorporated specific references (Elizabeth Gilbert, wine) and conversational elements, but occasionally leaned into generic 'friendly blogger' tropes and lacked Jacq's full brashness.

### Example 7
**Prompt**: Write a blog post titled "Finding your way"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 7/10 |
| ROUGE-1 | 0.5275 | 0.4367 |
| Vocab overlap | 0.2895 | 0.2277 |
| Word count | 639 | 423 |

Judge notes (fine-tuned): The AI attempts a conversational tone and personal anecdotes, which is a good start. However, it frequently defaults to generic self-help phrasing ('clarity,' 'powerful tool,' 'trust your gut') and a more structured, advice-giving format (numbered list, 'Here are some things I've learned') that deviates from Jacq's raw, specific, and brash style. It lacks her unique vocabulary, deliberate grammar breaks, and the punchy directness that makes her voice so distinct.

### Example 8
**Prompt**: Write about why women should stop waiting for permission to write...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 7/10 |
| ROUGE-1 | 0.38 | 0.4436 |
| Vocab overlap | 0.2121 | 0.259 |
| Word count | 349 | 311 |

Judge notes (fine-tuned): The AI successfully adopted personal anecdotes and specific scenarios, and mimicked some structural habits. However, it lacked Jacq's signature brashness and raw, unpolished directness, feeling slightly more polished and less 'friend over wine' than the original.

### Example 9
**Prompt**: Write a blog post about crisis comms...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 4/10 | 7/10 |
| ROUGE-1 | 0.438 | 0.3759 |
| Vocab overlap | 0.1968 | 0.1888 |
| Word count | 547 | 377 |

Judge notes (fine-tuned): The AI captures the topic and a general conversational tone, but fundamentally misses Jacq's unique voice, brashness, and especially her deep personal specificity. It reads more like a generic, helpful blog post than an authentic piece by Jacq.

### Example 10
**Prompt**: Write a blog post titled "Writing with astrology - days of the week"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 6/10 |
| ROUGE-1 | 0.4434 | 0.3378 |
| Vocab overlap | 0.2267 | 0.2069 |
| Word count | 835 | 586 |

Judge notes (fine-tuned): The AI adopted some structural habits and a friendly tone, but missed Jacq's grounded vocabulary, brashness, and deep personal specificity, often defaulting to generic self-help phrasing.
