from config.connect import Neo4jConnection
from pyvis.network import Network
import logging
import os

logging.basicConfig(
    filename="output/logs/viz.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)
logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def visualize_kg(team_name=None, skill_name=None):
    logger.info(f"Starting KG visualization for team={team_name}, skill={skill_name}")
    
    try:
        conn = Neo4jConnection()
        driver = conn.get_driver()
        logger.info("Connected to Neo4j")

        with driver.session() as session:
            query = """
            MATCH (p:Person)-[r:WORKS_IN]->(t:Team {name: $team_name})
            MATCH (p)-[:HAS_SKILL]->(s:Skill {name: $skill_name})
            RETURN p, r, t, s
            """
            result = session.run(query, team_name=team_name, skill_name=skill_name)
            logger.info("Fetched KG data")

            net = Network(height="750px", width="100%", bgcolor="white", font_color="black")
            net.barnes_hut()

            nodes_added = set()
            for record in result:
                person = record["p"]
                person_id = person["id"]
                person_name = person["name"]
                if person_id not in nodes_added:
                    title = f"{person['role']}, {person['department']}"
                    net.add_node(person_id, label=person_name, title=title, color="blue")
                    nodes_added.add(person_id)

                team = record["t"]
                team_id = team["name"]
                team_name = team["name"]
                if team_id not in nodes_added:
                    title = f"Team, {team['department']}"
                    net.add_node(team_id, label=team_name, title=title, color="green")
                    nodes_added.add(team_id)

                net.add_edge(person_id, team_id, title="WORKS_IN")

                skill = record["s"]
                if skill:
                    skill_name = skill["name"]
                    skill_id = f"skill_{skill_name}"
                    if skill_id not in nodes_added:
                        title = f"Skill, {skill['category']}"
                        net.add_node(skill_id, label=skill_name, title=title, color="red")
                        nodes_added.add(skill_id)
                    net.add_edge(person_id, skill_id, title="HAS_SKILL")

            logger.info(f"Added {len(nodes_added)} nodes to visualization")

            output_file = f"src/static/kg_viz.html"
            net.save_graph(output_file)
            logger.info(f"Visualization saved to {output_file}")
            print(f"Visualization saved to {output_file}")
            return output_file

    except Exception as e:
        logger.error(f"Failed to visualize KG: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        visualize_kg(team_name="AIResearchTeam", skill_name="DeepLearning")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        print(f"Error: {str(e)}")
        exit(1)