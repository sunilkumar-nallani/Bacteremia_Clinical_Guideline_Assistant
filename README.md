# Bacteremia Clinical Guideline Assistant

Ask a clinical question about bacteremia and get an answer pulled straight 
from hospital antibiotic stewardship guidelines, with the source document 
and page number attached to every claim.

The retrieval pipeline itself isn't tied to bacteremia specifically — point 
it at a different set of clinical guideline PDFs and it works the same way 
for another condition.

Built to stop the back-and-forth of flipping through 20-page PDF guidelines 
for a quick answer. This is a research and prototyping tool, not a 
replacement for clinical judgment or an ID consult.

## How It Works

PDFs → chunked by meaning → embedded into a FAISS index
│
Question comes in → rewritten into 3 clinical phrasings
(catches synonym mismatches like "complicated" vs "source control")
│
Best-matching chunks retrieved → reranked for relevance
│
LLM answers only from those chunks, citing filename + page


## Getting Started

```bash
git clone https://github.com/<your-username>/bacteremia-rag-assistant.git
cd bacteremia-rag-assistant
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