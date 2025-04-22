import unittest
from src.query import query_kg

class TestQuery(unittest.TestCase):
    def test_query(self):
        results = query_kg("Team_1", "NLP")
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main()