# Evaluation Report

**Fine-tuned model**: jacq-v5:8b + RAG
**Baseline model**: llama3.1:8b
**Judge**: gemini (head-to-head, randomized order)
**Test examples**: 10

---

## Head-to-Head Results

| | Wins | Avg Score |
|---|---|---|
| **Fine-tuned** | **4/10** | **5.8/10** |
| Baseline | 6/10 | 6.8/10 |
| Ties/errors | 0/10 | — |

## Style Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Avg sentence length | 15.97 words | 17.76 words | 17.44 words |
| Vocabulary overlap | — | 0.27 | 0.2 |
| ROUGE-1 F1 | — | 0.47 | 0.38 |

## Structural Metrics

| Metric | Reference (Jacq) | Fine-tuned | Baseline |
|--------|-----------------|-----------|----------|
| Dashes/1k words | 9.28 | 14.75 | 13.85 |
| Parentheses/1k words | 3.0 | 3.99 | 3.78 |
| Questions/1k words | 13.6 | 11.2 | 16.13 |
| Fragment % | 15.79% | 9.6% | 13.57% |

## Per-Example Results

### Example 1
**Prompt**: Write about a recent retreat or getaway where you were able to focus on writing or another creative pursuit....

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 5/10 |
| Winner | **WIN** |  |
| ROUGE-1 | 0.4791 | 0.3011 |
| Vocab overlap | 0.2273 | 0.1535 |
| Word count | 725 | 334 |

**Judge reason**: Response A maintains Jacq's grounded specificity and conversational tone without falling into the generic self-help buzzwords and rhetorical questions that appear in Response B's conclusion.

### Example 2
**Prompt**: Write a blog post titled "Jacqueline Fisch - Wishbeads Guest Blog post"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 6/10 | 8/10 |
| Winner |  | **WIN** |
| ROUGE-1 | 0.3863 | 0.3272 |
| Vocab overlap | 0.2004 | 0.173 |
| Word count | 486 | 361 |

**Judge reason**: Response B better captures Jacq's voice through its strong personal anecdotes, specific literary references (Elizabeth Gilbert, Julia Cameron), and vivid real-life metaphors. It also incorporates her directness and conversational tone more effectively than Response A.

### Example 3
**Prompt**: Describe the writing process as a journey of intentional motion and growth, where one's body of work is carefully curate...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 5/10 |
| Winner | **WIN** |  |
| ROUGE-1 | 0.3481 | 0.3829 |
| Vocab overlap | 0.1971 | 0.1629 |
| Word count | 333 | 424 |

**Judge reason**: Response B is more direct and specific, opening with a personal detail ('I've written about 1,000 words') and crucially reusing Jacq's signature charcuterie board metaphor. While both responses contain some self-help jargon, B's brashness and grounded references align more closely with Jacq's authentic voice than A's generic motivational tone.

### Example 4
**Prompt**: Describe the strategies you use to manage your thoughts and emotions when faced with negative self-talk or criticism fro...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 5/10 | 7/10 |
| Winner |  | **WIN** |
| ROUGE-1 | 0.4594 | 0.3779 |
| Vocab overlap | 0.2316 | 0.1871 |
| Word count | 443 | 347 |

**Judge reason**: Response A better captures Jacq's conversational, brash, and grounded tone, and avoids the pervasive self-help jargon that makes Response B sound like a generic coach. While Response B includes specific references, its overall language contradicts Jacq's anti-jargon style.

### Example 5
**Prompt**: Write a blog post about inspiring astrology writing prompts for creative businesses...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 3/10 | 7/10 |
| Winner |  | **WIN** |
| ROUGE-1 | 0.6307 | 0.2884 |
| Vocab overlap | 0.4186 | 0.1791 |
| Word count | 1263 | 362 |

**Judge reason**: Response A successfully generates new content that captures Jacq's specific, grounded, and conversational tone, including personal details and direct language. Response B largely copies the original text, and its own generated content is generic and lacks Jacq's distinct voice and specificity.

### Example 6
**Prompt**: Write a blog post titled "What if it was easy"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 9/10 | 7/10 |
| Winner | **WIN** |  |
| ROUGE-1 | 0.603 | 0.4433 |
| Vocab overlap | 0.373 | 0.2184 |
| Word count | 634 | 312 |

**Judge reason**: Response B excels in specific, grounded details and maintains a consistent 'friend over wine' tone without self-help jargon. Its authentic, slightly unpolished ending also strongly mirrors Jacq's original style, whereas A includes some generic AI red flags.

### Example 7
**Prompt**: Write a blog post titled "Finding your way"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 4/10 | 8/10 |
| Winner |  | **WIN** |
| ROUGE-1 | 0.4763 | 0.4605 |
| Vocab overlap | 0.254 | 0.2377 |
| Word count | 583 | 483 |

**Judge reason**: Response B masterfully captures Jacq's grounded specificity with vivid real-life details and a conversational, direct tone. Response A, in contrast, relies on generic self-help buzzwords and a structured, less personal approach, hitting many AI red flags.

### Example 8
**Prompt**: Write about why women should stop waiting for permission to write...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 5/10 | 9/10 |
| Winner |  | **WIN** |
| ROUGE-1 | 0.3734 | 0.385 |
| Vocab overlap | 0.209 | 0.2481 |
| Word count | 401 | 379 |

**Judge reason**: Response B masterfully captures Jacq's brash, direct, and conversational tone, using grounded metaphors and specific examples that mirror her authentic voice. Response A, in contrast, frequently falls into generic self-help jargon and lacks the distinct edge and personal specificity of Jacq's writing.

### Example 9
**Prompt**: Write a blog post about crisis comms...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 7/10 | 5/10 |
| Winner | **WIN** |  |
| ROUGE-1 | 0.6468 | 0.4047 |
| Vocab overlap | 0.4592 | 0.1983 |
| Word count | 564 | 478 |

**Judge reason**: Response A successfully captures Jacq's brash, specific, and conversational tone, including her use of direct language and implied profanity, while Response B falls into generic self-help jargon and lacks personal specificity.

### Example 10
**Prompt**: Write a blog post titled "Writing with astrology - days of the week"...

| | Fine-tuned | Baseline |
|---|---|---|
| Judge score | 5/10 | 7/10 |
| Winner |  | **WIN** |
| ROUGE-1 | 0.2621 | 0.3826 |
| Vocab overlap | 0.1742 | 0.2123 |
| Word count | 385 | 728 |

**Judge reason**: Response A captures Jacq's brash, specific, and conversational tone with personal anecdotes and real-life metaphors. Response B is overly generic, instructional, and lacks her distinct voice, relying on self-help buzzwords and a listicle format.
