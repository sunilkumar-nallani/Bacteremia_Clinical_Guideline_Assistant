# Module file (a file meant to be imported elsewhere)

# rag_pipeline.py  (runs every time someone asks a question)
#     │
#     │  FAISS.load_local("faiss_index", ...) → reads both files back into memory
#     ▼
# main_chain ready to answer questions instantly, no re-embedding needed

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers import MultiQueryRetriever

# Specialized model to filterout which chunks (in total 10) are highly releveant to question
# Fixed: Moved from langchain.retrievers to langchain_classic.retrievers
from langchain_classic.retrievers import ContextualCompressionRetriever

# Third-party integrations like Flashrank are imported from langchain_community
from langchain_community.document_compressors import FlashrankRerank

from langchain_classic.retrievers import MultiQueryRetriever
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate

from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="e5-mistral-7b-instruct",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ["OPENAI_API_BASE"],
    tiktoken_enabled=False,
    check_embedding_ctx_length=False
)

# retreiveing embeddings from vector store and creating retriever for similarity search

# it opens that same faiss_index/ folder, reads both files back into memory, and rebuilds an identical FAISS vector store object, without needing to re-embed any documents or call the embedding API again.
# Saves Cost and Time
# allow_dangerous_deserialization=True is required because index.pkl uses Python's pickle format, which can technically execute arbitrary code if the file came from an untrusted source. Since you created this file yourself with your own trusted documents, this is safe — but never load a faiss_index/ folder you downloaded from someone else without inspecting it first.

vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Model for generating phraphrasings of question as well as answer generation.

gwdg_llm = ChatOpenAI(
    model="qwen3-30b-a3b-instruct-2507",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ["OPENAI_API_BASE"],
    temperature=0
)

# Constrained Query Generation Prompt Template to generate 3 alternative phrasings of the question using standard medical terminology.

query_gen_prompt = PromptTemplate(
    input_variables=["question"],
    template="""Generate exactly 3 alternative phrasings of this clinical question, using standard medical terminology only. Keep each rewrite concise and literal, avoid creative rephrasing.

Question: {question}

Alternative phrasings:"""
)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever, llm=gwdg_llm, prompt=query_gen_prompt
)

# Reranker --
# A specialized cross-encoder model re-scores all merged candidate chunks
# and keeps only the top 3 most relevant ones (out of up to 30 from multi-query).

compressor = FlashrankRerank(top_n=3)
final_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=multi_query_retriever
)


# Format retrieved docs with citations before they reach the prompt ---
# It prepends "Source: {filename}, p.{page}"
# to every chunk's text, so the LLM prompt's citation rule has real filenames/pages to copy.

def format_docs_with_citations(docs):
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page_label", "?")
        formatted.append(f"Source: {source}, p.{page}\n{doc.page_content}")
    return "\n\n".join(formatted)


# Propmt template for answer generation. It instructs the model to strictly adhere to the provided reference documents and avoid using any outside knowledge. The template also emphasizes the importance of citing sources accurately and clearly distinguishing between different clinical situations.

answer_prompt = prompt = PromptTemplate(
    template="""You are a clinical guideline assistant for infectious disease and bacteremia questions. This tool is for research and prototyping only, not for clinical decision-making.

Rules you must follow:
1. Answer only using the provided reference documents below. Do not use outside knowledge.
2. Do not combine or synthesize information across different retrieved chunks into a single claim, unless that exact combined claim is explicitly stated together in one source. If multiple chunks are relevant but address different aspects or scenarios, present them as separate points with their own citations rather than merging them into one unified statement.
3. If two sources appear related but address different clinical situations, state this distinction clearly rather than merging them.
4. If the answer is not explicitly stated in the references, say so honestly instead of inferring or guessing.
5. If the retrieved context does not contain information directly relevant to the question, explicitly state that the provided guidelines don't address this, rather than attempting to answer from general knowledge.
6. For every claim, cite the source using the exact filename and page number shown in the context metadata, formatted exactly as [filename, p.X]. Replace 'filename' and 'X' with the real values found in the context. Never output the literal placeholder word SOURCE.

Reference documents:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"]
)

llm = ChatOpenAI(model="qwen3-30b-a3b-instruct-2507", temperature=0)

# RunnableParallel runs two branches at once:
#   "context" branch -> final_retriever fetches docs, then format_docs_with_citations joins them into one string
#   "question" branch -> RunnablePassthrough just forwards the raw question string unchanged

# Both branch outputs are combined into a dict {"context": ..., "question": ...},

# which matches the prompt's input_variables exactly.

# That dict is piped into prompt -> llm -> StrOutputParser, which unwraps the AIMessage into plain text.


main_chain = (
    RunnableParallel({
        "context": final_retriever | RunnableLambda(format_docs_with_citations),
        "question": RunnablePassthrough()
    })
    | prompt
    | llm
    | StrOutputParser()
)

# --- Convenience wrapper matching your notebook's invoke_with_retry usage pattern ---
def answer_question(question: str) -> str:
    """Runs the full RAG pipeline end-to-end and returns a plain string answer."""
    return main_chain.invoke(question)



# runs only when this file is executed directly, not when imported as a module

if __name__ == "__main__":  
    question = "Is bacteremia considered complicated when immunosuppression is the sole underlying condition?"
    print(answer_question(question))