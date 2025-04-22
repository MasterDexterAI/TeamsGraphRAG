from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset
import pandas as pd
from langchain_community.chat_models import ChatOllama
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
import numpy as np

# Custom embedding class for SentenceTransformers
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name, device="cpu")  # Use CPU for M1

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], convert_to_numpy=True, show_progress_bar=False)[0]
        return embedding.tolist()

# Load evaluation data
eval_data = pd.read_json("notebooks/eval_data.json")

# Ensure contexts is a list of strings
eval_data["contexts"] = eval_data["contexts"].apply(lambda x: x if isinstance(x, list) else [x])

# Create Dataset for RAGAS
dataset = Dataset.from_dict({
    "question": eval_data["question"].tolist(),
    "contexts": eval_data["contexts"].tolist(),  # Already a list of strings per row
    "answer": eval_data["answer"].tolist(),
    "ground_truth": eval_data["ground_truth"].tolist()
})

# Initialize LLM for evaluation
llm = ChatOllama(
    model="llama3.2:1b",
    base_url="http://localhost:11434",  # Default Ollama port
    max_tokens=50,
    temperature=0.7
)

# Initialize embeddings
embeddings = SentenceTransformerEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Evaluate with RAGAS
result = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ],
    llm=llm,
    embeddings=embeddings
)

# Print and save results
print("Evaluation Results:", result)
result_df = pd.DataFrame([result])
result_df.to_csv("output/ragas_results.csv", index=False)
print("Results saved to output/ragas_results.csv")