from flask import Flask, render_template, request
from src.query import query_kg
from src.rag_pipeline import graph_rag
from src.utils import visualize_kg
import logging
import os

logging.basicConfig(filename="output/logs/app.log", level=logging.INFO)
logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    kg_viz_path = None
    
    if request.method == "POST":
        try:
            question = request.form.get("question")
            team_name = request.form.get("team_name")
            skill_name = request.form.get("skill_name")
            logger.info(f"Received query: question={question}, team={team_name}, skill={skill_name}")
            
            answer = graph_rag(question, team_name, skill_name)

            kg_viz_path = visualize_kg(team_name, skill_name)
            result = {
                "question": question,
                "team_name": team_name,
                "skill_name": skill_name,
                "answer": answer
            }
            logger.info(f"Generated answer: {answer}, viz: {kg_viz_path}")
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            result = {"error": str(e)}
    
    static_file = os.path.join("src","static", kg_viz_path) if kg_viz_path else None
    kg_viz_exists = os.path.exists(static_file) if static_file else False
    print(kg_viz_path)
    
    return render_template(
        "index.html",
        result=result,
        kg_viz_path="kg_viz.html"
    )


if __name__ == "__main__":
    logger.info("Starting Flask app")
    app.run(debug=True, host="0.0.0.0", port=5001)