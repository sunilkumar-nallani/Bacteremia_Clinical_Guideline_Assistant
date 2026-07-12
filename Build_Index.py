import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="e5-mistral-7b-instruct",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ["OPENAI_API_BASE"],
    tiktoken_enabled=False,
    check_embedding_ctx_length=False
)

def is_reference_page(page_text):
    markers = ["REFERENCES", "doi:10.", "Clin Infect Dis.", "et al."]
    hits = sum(1 for m in markers if m in page_text)
    return hits >= 2

# Documents Loading

def build_and_save_index(pdf_folder="Bacteremia_Guidelines/", save_path="faiss_index"):
    all_documents = []
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, filename))
            all_documents.extend(loader.load())

    print(f"Loaded {len(all_documents)} pages from {pdf_folder}")

    filtered_pages = [p for p in all_documents if not is_reference_page(p.page_content)]
    print(f"After reference filtering: {len(filtered_pages)} pages remain")

    # Semantic Splitting (chunking)

    semantic_splitter = SemanticChunker(
        embeddings, breakpoint_threshold_type="percentile", breakpoint_threshold_amount=85
    )
    chunks = semantic_splitter.split_documents(filtered_pages)
    print(f"Created {len(chunks)} semantic chunks")

    # Creating Embeddings and store in Faiss vector store

    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(save_path)
    print(f"Saved FAISS index to {save_path}/")

    # save_path was a Python variable set to the string "faiss_index" inside your function's default argument (save_path="faiss_index"). When this line runs, FAISS doesn't save anything into a database or the cloud — it creates a folder on your computer's hard disk, named exactly faiss_index, sitting right next to your build_index.py fil
    # stores 2 files in disk 
    # index.faiss is a phone book sorted by "sounds like," and 
    # index.pkl is the actual list of names and addresses that phone book entries point to. You need both files together, or the index is useless.

if __name__ == "__main__":
    build_and_save_index()