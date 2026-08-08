# African Language NLP

**Source:** Marconi Lab DL Course, Day 4

## The Core Challenge

African languages are **agglutinative** — they form words by combining many morphemes. "omulwadde" = "omu" (person prefix) + "lwadde" (sick). Word-level tokenization produces enormous vocabularies because every morpheme combination creates a new word.

## Solutions

- **Subword tokenization** (BPE, SentencePiece) splits into meaningful chunks — the best balance for agglutinative languages
- **Character-level models** avoid the vocabulary explosion entirely (tiny vocab, but longer sequences)
- **Multilingual models** (mBERT, XLM-R, AfroLM) trained on related languages during pre-training

## Lab NLP Projects

| Project | Architecture | Key Consideration |
|---|---|---|
| Luganda text classification | BiLSTM + embeddings | Character or subword tokens |
| Swahili sentiment analysis | BiLSTM + FastText embeddings | Pre-trained available |
| English→Luganda translation | Seq2Seq with attention | Transformers better |
| Clinical notes extraction | BiLSTM-CRF | NER for medical terms |

## Practical Advice

If pre-trained embeddings don't exist for your target language: train from scratch on available data, or use a multilingual model that has seen related languages. Don't abandon the project — the challenge is data, not architecture.
