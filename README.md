# 🩺 Bacteremia Clinical Guideline Assistant 

[![Live App](https://img.shields.io/badge/🚀_Live_App-Streamlit-FF4B4B?style=for-the-badge)](https://bacteremia-clinical-guideline-assistant.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge)](https://www.python.org/)


Ask a clinical question about bacteremia and get an answer pulled straight 
from hospital antibiotic stewardship guidelines, with the source document 
and page number attached to every claim.

**[👉 Try it live here](https://bacteremia-clinical-guideline-assistant.streamlit.app/)**

Built to stop the back-and-forth of flipping through 20-page PDF guidelines for a quick answer. This is a research and prototyping tool, not a replacement for clinical judgment or an ID consult.

**[ This is a DOMAIN agnostic pipeline (isn't tied to bacteremia specifically, point it at a different set of clinical guideline PDFs and it works the same way for another condition.) ]**

## How It Works

PDFs → chunked by meaning → embedded into a FAISS index
│
Question comes in → rewritten into 3 clinical phrasings
(catches synonym mismatches like "complicated" vs "source control")
│
Best-matching chunks retrieved → reranked for relevance
│
LLM answers only from those chunks, citing filename + page

---

## 📊 Evaluation

Answer quality was measured with [RAGAS](https://github.com/explodinggym/ragas) across multiple evaluation runs on a held-out test set of clinical questions:

| Metric | Score | What it measures |
|---|---|---|
| Faithfulness | ~0.73 | How well the answer sticks to the retrieved sources, without adding unsupported claims |
| Context Precision | ~0.87 | How relevant the retrieved chunks are to the question |
| Context Recall | ~0.97 | How well the retrieval step captures all the relevant information available |
| Answer Relevancy | ~0.75 | How directly the final answer addresses the question asked |

High context recall combined with lower faithfulness suggests the retriever is doing its job well, and most remaining improvement is in how tightly the generation step sticks to the retrieved text — a known trade-off worth tuning further.

---

## Getting Started

```bash
git clone https://github.com/sunilkumar-nallani/Bacteremia_Clinical_Guideline_Assistant.git
cd Bacteremia_Clinical_Guideline_Assistant
pip install -r requirements.txt
```

Add a `.env` file (see `.env.example`):

OPENAI_API_KEY=your_key_here
OPENAI_API_BASE=your_base_url_here   #optional


## Usage

```bash
python build_index.py     # run once, builds the FAISS index
streamlit run app.py       # launches the chat interface
```

## Tech Stack

LangChain · FAISS · FlashRank · Streamlit · OpenAI-compatible LLM/embeddings API

## Limitations

- Prototyping tool, not for clinical decision-making
- Only answers from the PDFs you load in, nothing outside them
- Page numbers come from PDF metadata and may not match the printed page exactly

## Contributing

PRs and issues welcome, whether it's a code fix or a suggestion on how a 
clinical question should be handled. Domain feedback from clinicians and ID 
pharmacists is just as valuable as code.

## License

MIT

## Contact

**Sunil Kumar Nallani** — sunilkumar.nallani@gmail.com — [LinkedIn](https://www.linkedin.com/in/nallani-sunil-kumar-67227a243/)
