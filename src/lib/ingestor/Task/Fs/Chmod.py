import os
from ..Task import Task

class Chmod(Task):
    """
    Chmod task that can be operated over a single file or over a directory path recursively.

    Require options: directoryMode and fileMode
    """

    def _perform(self):
        """
        Perform the task.
        """
        alreadyDone = set()
        directoryMode = int(str(self.option('directoryMode')), 8)
        fileMode = int(str(self.option('fileMode')), 8)

        for pathCrawler in self.pathCrawlers():
            filePath = self.filePath(pathCrawler)

            if filePath in alreadyDone:
                continue
            else:
                alreadyDone.add(filePath)

            collectedFiles = self.__collectAllFiles(filePath)
            collectedFiles.sort(reverse=True)

            for collectedFile in collectedFiles:

                if os.path.islink(collectedFile):
                    continue

                if os.path.isdir(collectedFile):
                    os.chmod(collectedFile, directoryMode)
                else:
                    os.chmod(collectedFile, fileMode)

        # default result based on the target filePath
        return super(Chmod, self)._perform()

    @classmethod
    def __collectAllFiles(cls, path):
        """
        Return all files recursively from the given path.
        """
        result = [path]

        if os.path.isdir(path):
            for entry in os.listdir(path):
                fullPath = os.path.join(path, entry)
                if os.path.isdir(fullPath):
                    result += cls.__collectAllFiles(fullPath)
                else:
                    result.append(fullPath)
        return result


# registering task
Task.register(
    'chmod',
    Chmod
)