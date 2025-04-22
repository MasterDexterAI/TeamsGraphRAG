import unittest
from config.connect import Neo4jConnection

class TestNeo4jConnection(unittest.TestCase):
    def test_connect(self):
        conn = Neo4jConnection()
        driver = conn.get_driver()
        with driver.session() as session:
            result = session.run("RETURN 1")
            self.assertEqual(result.single()[0], 1)
        conn.close()

if __name__ == "__main__":
    unittest.main()