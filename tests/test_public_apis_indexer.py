"""
tests/test_public_apis_indexer.py
tools/public_apis_indexer.py 的單元測試。
"""

import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from public_apis_indexer import (
    ApiEntry,
    filter_apis,
    generate_markdown,
    group_by_category,
    locate_source_file,
    parse_markdown_table_rows,
)


SAMPLE_README = """
### APIs Covered Under APILayer Suite!
- [IPstack](https://ipstack.com)

### Animals
API | Description | Auth | HTTPS | CORS 
|:---|:---|:---|:---|:---|
| [Cat Facts](https://catfact.ninja/) | Random cat facts | No | Yes | Yes |
| [Dogs](https://dog.ceo/dog-api/) | Based on Stanford Dogs | No | Yes | Yes |
| [The Dog](https://thedogapi.com/) | Dog service | `apiKey` | Yes | No |
| [Foxes](https://randomfox.ca/) | Fox pictures | No | Yes | No |

### Books
API | Description | Auth | HTTPS | CORS |
|:---|:---|:---|:---|:---|
| [Open Library](https://openlibrary.org/developers/api) | Books database | No | Yes | No |
| [Gutendex](https://gutendex.com/) | Project Gutenberg ebook data | No | Yes | Yes |

### Weather
API | Description | Auth | HTTPS | CORS |
|:---|:---|:---|:---|:---|
| [Open-Meteo](https://open-meteo.com/) | Free weather API | No | Yes | Yes |
"""


class PublicApisIndexerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_parse_markdown_table_rows(self):
        entries = parse_markdown_table_rows(SAMPLE_README)
        self.assertEqual(len(entries), 7)

        cats = {e.category for e in entries}
        self.assertIn("Animals", cats)
        self.assertIn("Books", cats)
        self.assertIn("Weather", cats)
        self.assertNotIn("APIs Covered Under APILayer Suite!", cats)

        # Check first entry
        cat_facts = next(e for e in entries if e.name == "Cat Facts")
        self.assertEqual(cat_facts.url, "https://catfact.ninja/")
        self.assertEqual(cat_facts.auth, "No")
        self.assertTrue(cat_facts.https)
        self.assertEqual(cat_facts.cors, "Yes")

        # Check apiKey strip backticks
        dog = next(e for e in entries if e.name == "The Dog")
        self.assertEqual(dog.auth, "apiKey")

    def test_filter_apis_no_auth_and_cors_yes(self):
        entries = parse_markdown_table_rows(SAMPLE_README)
        filtered = filter_apis(entries, auth="no", cors="yes")
        # Cat Facts, Dogs, Gutendex, Open-Meteo
        self.assertEqual(len(filtered), 4)
        names = [e.name for e in filtered]
        self.assertIn("Cat Facts", names)
        self.assertIn("Dogs", names)
        self.assertIn("Gutendex", names)
        self.assertIn("Open-Meteo", names)
        self.assertNotIn("The Dog", names)  # apiKey
        self.assertNotIn("Foxes", names)    # cors: No
        self.assertNotIn("Open Library", names)  # cors: No

    def test_filter_apis_by_category_and_search(self):
        entries = parse_markdown_table_rows(SAMPLE_README)
        weather = filter_apis(entries, category="weather", auth="all", cors="all")
        self.assertEqual(len(weather), 1)
        self.assertEqual(weather[0].name, "Open-Meteo")

        search_res = filter_apis(entries, search="gutenberg", auth="all", cors="all")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0].name, "Gutendex")

    def test_group_by_category(self):
        entries = parse_markdown_table_rows(SAMPLE_README)
        filtered = filter_apis(entries, auth="no", cors="yes")
        grouped = group_by_category(filtered)
        self.assertEqual(len(grouped["Animals"]), 2)
        self.assertEqual(len(grouped["Books"]), 1)
        self.assertEqual(len(grouped["Weather"]), 1)

    def test_generate_markdown(self):
        entries = parse_markdown_table_rows(SAMPLE_README)
        filtered = filter_apis(entries, auth="no", cors="yes")
        md = generate_markdown(filtered)
        self.assertIn("# Public APIs 免金鑰與 CORS 支援精選手冊", md)
        self.assertIn("Open-Meteo", md)
        self.assertIn("Cat Facts", md)
        self.assertIn("https://api.open-meteo.com/v1/forecast", md)
        self.assertIn("### Animals", md)

    def test_locate_source_file_custom(self):
        sample_file = self.tmp / "sample.md"
        sample_file.write_text(SAMPLE_README, encoding="utf-8")
        found = locate_source_file(str(sample_file))
        self.assertEqual(found, sample_file)

    def test_locate_source_file_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            locate_source_file(str(self.tmp / "nonexistent.md"))

    def test_description_with_unescaped_pipe_does_not_shift_columns(self):
        readme = (
            "### Misc\n"
            "API | Description | Auth | HTTPS | CORS |\n"
            "|:---|:---|:---|:---|:---|\n"
            "| [Pipey](https://p.example/) | a | b description | No | Yes | Yes |\n"
        )
        (entry,) = parse_markdown_table_rows(readme)
        self.assertEqual(entry.description, "a | b description")
        self.assertEqual((entry.auth, entry.https, entry.cors), ("No", True, "Yes"))

    def test_toc_anchor_matches_github_for_ampersand_category(self):
        entries = [ApiEntry("Cloud Storage & Backup", "X", "https://x/", "d", "No", True, "Yes")]
        md = generate_markdown(entries)
        self.assertIn("(#cloud-storage--backup)", md)

    def test_markdown_reports_actual_filters(self):
        entries = [ApiEntry("Misc", "X", "https://x/", "d", "apiKey", True, "No")]
        md = generate_markdown(entries, auth="apiKey", cors="all")
        self.assertIn("`Auth: apiKey` 且 `CORS: all`", md)
        self.assertNotIn("免申請金鑰", md)

    def test_name_with_pipe_does_not_break_table_row(self):
        entries = [ApiEntry("Misc", "A|B", "https://x/", "d", "No", True, "Yes")]
        row = [ln for ln in generate_markdown(entries).splitlines() if ln.startswith("| [A")][0]
        self.assertEqual(row.count("|"), 6)


if __name__ == "__main__":
    unittest.main()
