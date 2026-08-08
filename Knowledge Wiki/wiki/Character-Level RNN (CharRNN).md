# Character-Level RNN (CharRNN)

**Source:** Marconi Lab DL Course, Day 4

## What It Is

A language model that predicts the next character given the previous ones. After training on a corpus, it can generate new text that mimics the style.

## Architecture

```
Character IDs → Embedding → LSTM → FC → vocab_size logits → softmax → sample
```

```python
class CharRNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
```

## Generation via Sampling

```python
probs = torch.softmax(out[0, -1], dim=0)
next_idx = torch.multinomial(probs, 1).item()  # sample, not greedy
```

`torch.multinomial` samples from the probability distribution — introduces randomness. Greedy (always pick highest) produces repetitive, boring text.

## Character vs Word Level

- **Character:** tiny vocab (~50-200 chars), can generate unseen words, great for agglutinative languages
- **Trade-off:** sequences are ~6× longer (50-word sentence = ~300 characters)
- **Ideal for:** generating any word, especially valuable for languages with huge possible word counts
