from config.connect import Neo4jConnection
from src.query import query_kg
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
import logging
import argparse

logging.basicConfig(filename="output/logs/rag.log", level=logging.INFO)

def get_llm():
    try:
        llm = ChatOllama(
            model="llama3.2:1b",
            base_url="http://localhost:11435",
            max_tokens=50,
            temperature=0.7
        )
        return llm
    except Exception as e:
        logging.error(f"Failed to load LLM: {str(e)}")
        raise

def graph_rag(question, team_name, skill_name):
    logging.info(f"Querying KG for team={team_name}, skill={skill_name}")
    try:
        context = query_kg(team_name, skill_name)
        context_str = "\n".join([f"{item['name']} ({item['role']}, {item['department']})" for item in context])
        logging.info("Initializing LLM")
        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(
            "Based on the context, answer the question.\nContext: {context}\nQuestion: {question}"
        )
        logging.info(f"Running RAG for question: {question}")
        chain = prompt | llm
        response = chain.invoke({"context": context_str, "question": question})
        logging.info(f"Question: {question}, Answer: {response.content}")
        return response.content
    except Exception as e:
        logging.error(f"Error in graph_rag: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Graph RAG Pipeline")
    parser.add_argument("--question", required=True, help="Question to answer")
    parser.add_argument("--team", required=True, help="Team name (e.g., AIResearchTeam)")
    parser.add_argument("--skill", required=True, help="Skill name (e.g., DeepLearning)")
    args = parser.parse_args()
    answer = graph_rag(args.question, args.team, args.skill)
    print("Answer:", answer)