import unittest
import os
from ..BaseTestCase import BaseTestCase
from centipede.ExpressionEvaluator import ExpressionEvaluator

class VersionTest(BaseTestCase):
    """Test Version expressions."""

    def testNewVersion(self):
        """
        Test that the new expression works properly.
        """
        result = ExpressionEvaluator.run("newver", BaseTestCase.dataDirectory())
        self.assertEqual(result, "v003")

    def testLatestVersion(self):
        """
        Test that the latest version is found properly.
        """
        result = ExpressionEvaluator.run("latestver", BaseTestCase.dataDirectory())
        self.assertEqual(result, "v002")
        result = ExpressionEvaluator.run("latestver", os.path.join(BaseTestCase.dataDirectory(), "glob"))
        self.assertEqual(result, "v000")


if __name__ == "__main__":
    unittest.main()
