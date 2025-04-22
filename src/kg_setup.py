from config.connect import Neo4jConnection
import pandas as pd
import logging

logging.basicConfig(filename="output/logs/setup.log", level=logging.INFO)

def create_knowledge_graph():
    logger = logging.getLogger()
    logger.info("Starting knowledge graph creation")

    try:
        conn = Neo4jConnection()
        driver = conn.get_driver()

        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared existing graph")

            employees = pd.read_csv("data/employees.csv")
            for _, row in employees.iterrows():
                session.run(
                    """
                    MERGE (p:Person {id: $id})
                    SET p.name = $name, p.role = $role, p.department = $department
                    """,
                    id=row["id"], name=row["name"], role=row["role"], department=row["department"]
                )
            logger.info(f"Loaded {len(employees)} employees")

            teams = pd.read_csv("data/teams.csv")
            for _, row in teams.iterrows():
                session.run(
                    """
                    MERGE (t:Team {name: $name})
                    SET t.department = $department
                    """,
                    name=row["name"], department=row["department"]
                )
            logger.info(f"Loaded {len(teams)} teams")

            skills = pd.read_csv("data/skills.csv")
            for _, row in skills.iterrows():
                session.run(
                    """
                    MERGE (s:Skill {name: $name})
                    SET s.category = $category
                    """,
                    name=row["name"], category=row["category"]
                )
            logger.info(f"Loaded {len(skills)} skills")

            person_team = pd.read_csv("data/person_team.csv")
            for _, row in person_team.iterrows():
                session.run(
                    """
                    MATCH (p:Person {id: $employee_id})
                    MATCH (t:Team {name: $team_name})
                    MERGE (p)-[:WORKS_IN]->(t)
                    """,
                    employee_id=row["employee_id"], team_name=row["team_name"]
                )
            logger.info(f"Loaded {len(person_team)} person-team relationships")

            person_skill = pd.read_csv("data/person_skill.csv")
            for _, row in person_skill.iterrows():
                session.run(
                    """
                    MATCH (p:Person {id: $employee_id})
                    MATCH (s:Skill {name: $skill_name})
                    MERGE (p)-[:HAS_SKILL]->(s)
                    """,
                    employee_id=row["employee_id"], skill_name=row["skill_name"]
                )
            logger.info(f"Loaded {len(person_skill)} person-skill relationships")

        logger.info("Knowledge graph created!")
        print("Knowledge graph created!")

    except Exception as e:
        logger.error(f"Failed to create knowledge graph: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_knowledge_graph()