import os
import unittest
from ....BaseTestCase import BaseTestCase
from ingestor.Crawler.Fs import Path
from ingestor.PathHolder import PathHolder
from ingestor.Crawler.Fs.Ascii import Json

class JsonTest(BaseTestCase):
    """Test Json crawler."""

    __jsonFile = os.path.join(BaseTestCase.dataDirectory(), "test.json")

    def testJsonCrawler(self):
        """
        Test that the Json crawler test works properly.
        """
        crawler = Path.create(PathHolder(self.__jsonFile))
        self.assertIsInstance(crawler, Json)
        self.assertEqual(crawler.var("type"), "json")
        self.assertEqual(crawler.var("category"), "ascii")

    def testContents(self):
        """
        Test that json files are parsed properly.
        """
        crawler = Path.create(PathHolder(self.__jsonFile))
        testData = {
                    "testList": [1, 1.2, "value"],
                    "testDict": {"key": "value", "number": 1},
                    "testString": "blah"
                    }
        self.assertEqual(crawler.contents(), testData)


if __name__ == "__main__":
    unittest.main()
