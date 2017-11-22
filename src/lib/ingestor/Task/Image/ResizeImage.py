import os
import multiprocessing
import OpenImageIO as oiio
from ...Template import Template
from ..Task import Task


class ResizeImage(Task):
    """
    Resizes the image to the sizes defined by the options "width" and "height".

    TODO: missing to umedia metadata/source image attributes.
    """

    def _perform(self):
        """
        Perform the task.
        """

        for pathCrawler in self.pathCrawlers():
            yield pathCrawler

            width = self.option('width')
            height = self.option('height')

            # resolving template
            if isinstance(width, str):
                width = int(Template(width).valueFromCrawler(
                    pathCrawler
                ))

            if isinstance(height, str):
                height = int(Template(height).valueFromCrawler(
                    pathCrawler
                ))

            targetFilePath = self.filePath(pathCrawler)

            # trying to create the directory automatically in case it does not exist
            try:
                os.makedirs(os.path.dirname(targetFilePath))
            except OSError:
                pass

            # opening the source image to generate a resized image
            inputImageBuf = oiio.ImageBuf(pathCrawler.var('filePath'))
            inputSpec = inputImageBuf.spec()

            # output spec
            outputSpec = oiio.ImageSpec(
                width,
                height,
                inputSpec.nchannels,
                oiio.FLOAT
            )

            # resized image buf
            resizedImageBuf = oiio.ImageBuf(
                outputSpec
            )

            # resizing image
            oiio.ImageBufAlgo.resize(
                resizedImageBuf,
                inputImageBuf,
                nthreads=multiprocessing.cpu_count()
            )

            # saving target resized image
            resizedImageBuf.write(targetFilePath)


# registering task
Task.register(
    'resizeImage',
    ResizeImage
)
