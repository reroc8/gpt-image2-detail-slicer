import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RealESRGANInitTests(unittest.TestCase):
    def test_realesrganer_is_not_called_with_device_keyword(self):
        for rel in ("mac/watch.py", "windows/watch.py"):
            with self.subTest(script=rel):
                tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
                calls = [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "RealESRGANer"
                ]

                self.assertTrue(calls, f"{rel} should initialize RealESRGANer")
                for call in calls:
                    keywords = {kw.arg for kw in call.keywords}
                    self.assertNotIn("device", keywords)


if __name__ == "__main__":
    unittest.main()
