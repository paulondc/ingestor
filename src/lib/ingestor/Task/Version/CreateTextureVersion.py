import os
import tempfile
import subprocess
from ..Task import Task
from .CreateIncrementalVersion import CreateIncrementalVersion

class CreateTextureVersion(CreateIncrementalVersion):
    """
    Create texture version task.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a texture version.
        """
        super(CreateTextureVersion, self).__init__(*args, **kwargs)
        self.setOption('maketxArgs', "-v -u --unpremult --oiio")

    def _perform(self):
        """
        Perform the task.
        """
        for pathCrawler in self.pathCrawlers():

            textureOriginalTargetLocation = self.__computeTextureTargetLocation(
                pathCrawler,
                pathCrawler.var('ext')
            )

            # copying the texture file
            self.copyFile(
                pathCrawler.var('filePath'),
                textureOriginalTargetLocation
            )

            # computing a mipmap version for the texture
            tempTxFilePath = tempfile.mktemp(suffix=".tx")
            subprocess.call(
                '/data/studio/upipe/plugins/maya/2018/mtoa/2.0.2.3/bin/linux/bin/maketx {} -o "{}" "{}"'.format(
                    self.option("maketxArgs"),
                    tempTxFilePath,
                    textureOriginalTargetLocation
                ),
                shell=True
            )

            # copying the texture file
            textureTxTargetLocation = self.__computeTextureTargetLocation(pathCrawler, "tx")

            # copying tx to the target location
            self.copyFile(
                tempTxFilePath,
                textureTxTargetLocation
            )

            # removing temporary tx file
            os.remove(tempTxFilePath)

            # adding texture files to the published version
            self.addFile(textureOriginalTargetLocation)
            self.addFile(textureTxTargetLocation)

        return super(CreateTextureVersion, self)._perform()

    def __computeTextureTargetLocation(self, crawler, ext):
        """
        Compute the target file path for an texture.
        """
        return os.path.join(
            self.dataPath(),
            ext,
            "{0}_{1}.{2}".format(
                crawler.var('mapType'),
                crawler.var('udim'),
                ext
            )
        )


# registering task
Task.register(
    'createTextureVersion',
    CreateTextureVersion
)
