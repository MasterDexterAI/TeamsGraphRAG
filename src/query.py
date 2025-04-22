from config.connect import Neo4jConnection
import logging
import argparse

logging.basicConfig(filename="output/logs/query.log", level=logging.INFO)

def query_kg(team_name, skill_name):
    logger = logging.getLogger()
    logger.info(f"Querying knowledge graph for team={team_name}, skill={skill_name}")

    try:
        conn = Neo4jConnection()
        driver = conn.get_driver()

        with driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person)-[:WORKS_IN]->(t:Team {name: $team_name})
                MATCH (p)-[:HAS_SKILL]->(s:Skill {name: $skill_name})
                RETURN p.name AS name, p.role AS role, p.department AS department
                """,
                team_name=team_name, skill_name=skill_name
            )
            experts = [
                {"name": record["name"], "role": record["role"], "department": record["department"]}
                for record in result
            ]
            logger.info(f"Found {len(experts)} experts")
            print(f"Experts in {team_name} with {skill_name} skill: {experts}")
            return experts

    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Knowledge Graph")
    parser.add_argument("--team", required=True, help="Team name (e.g., AIResearchTeam)")
    parser.add_argument("--skill", required=True, help="Skill name (e.g., DeepLearning)")
    args = parser.parse_args()
    query_kg(args.team, args.skill)