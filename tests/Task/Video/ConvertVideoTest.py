import unittest
import os
from ...BaseTestCase import BaseTestCase
from centipede.Task import Task
from centipede.Crawler.Fs import FsPath

class ConvertVideoTest(BaseTestCase):
    """Test ConvertVideo task."""

    __sourcePath = os.path.join(BaseTestCase.dataDirectory(), "test.mov")
    __testPath = os.path.join(BaseTestCase.dataDirectory(), "copyVideo.mov")
    __targetPath = os.path.join(BaseTestCase.dataDirectory(), "testToDelete.mov")

    def testConvertVideo(self):
        """
        Test that the Convert Video task works properly.
        """
        pathCrawler = FsPath.createFromPath(self.__sourcePath)
        convertTask = Task.create('convertVideo')
        convertTask.add(pathCrawler, self.__targetPath)
        result = convertTask.output()
        self.assertEqual(len(result), 1)
        checkTask = Task.create('checksum')
        checkTask.add(result[0], self.__testPath)
        checkTask.output()

    @classmethod
    def tearDownClass(cls):
        """
        Remove the file that was copied.
        """
        os.remove(cls.__targetPath)


if __name__ == "__main__":
    unittest.main()
