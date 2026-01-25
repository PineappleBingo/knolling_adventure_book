import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import config

class TestTargetPages(unittest.TestCase):
    def test_parsing_single(self):
        os.environ["TARGET_PAGES"] = "1"
        # Reload config module to pick up env change
        import importlib
        importlib.reload(config)
        self.assertEqual(config.TARGET_PAGES_LIST, [1])

    def test_parsing_list(self):
        os.environ["TARGET_PAGES"] = "1,3,5"
        import importlib
        importlib.reload(config)
        self.assertEqual(config.TARGET_PAGES_LIST, [1, 3, 5])

    def test_parsing_range(self):
        os.environ["TARGET_PAGES"] = "1-3"
        import importlib
        importlib.reload(config)
        self.assertEqual(config.TARGET_PAGES_LIST, [1, 2, 3])

    def test_parsing_complex(self):
        os.environ["TARGET_PAGES"] = "1,3-5,7"
        import importlib
        importlib.reload(config)
        self.assertEqual(config.TARGET_PAGES_LIST, [1, 3, 4, 5, 7])

if __name__ == '__main__':
    unittest.main()
