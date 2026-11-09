import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import tempfile
import unittest
from pathlib import Path
from services import vector_store

class VectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = vector_store.INDEX_PATH
        vector_store.INDEX_PATH = Path(self.tmp.name) / "vectors.json"

    def tearDown(self):
        vector_store.INDEX_PATH = self.old
        self.tmp.cleanup()

    def test_upsert_and_semantic_rank(self):
        vector_store.upsert(1, "sunset over ocean", [1.0, 0.0])
        vector_store.upsert(2, "snowy mountain", [0.0, 1.0])
        records = [{"id": 1, "filename": "sea.jpg"}, {"id": 2, "filename": "mountain.jpg"}]
        result = vector_store.search([0.9, 0.1], records, min_score=0.0)
        self.assertEqual(result[0][0]["id"], 1)
        self.assertEqual(vector_store.index_stats()["count"], 2)

    def test_remove(self):
        vector_store.upsert(3, "city at night", [1.0, 2.0])
        vector_store.remove(3)
        self.assertEqual(vector_store.index_stats()["count"], 0)

if __name__ == "__main__":
    unittest.main()
