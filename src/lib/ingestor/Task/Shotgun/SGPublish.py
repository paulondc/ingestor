import os
import tempfile
from ..Task import Task
from ...Template import Template
from ...Crawler.Fs.Path import Path
from ...Crawler.Fs.Image import Image

class SGPublish(Task):
    """
    Publish data to shotgun.

    """

    def __init__(self, *args, **kwargs):
        """
        Create a RenderPublish object.
        """
        super(SGPublish, self).__init__(*args, **kwargs)

        self.__publishData = {}

    def _perform(self):
        """
        Perform the task.
        """
        from ushotgun import Session
        sg = Session.get()

        # Source crawler is a json crawler that points to published data
        sourceCrawler = self.pathCrawlers()[0]

        filePath = sourceCrawler.var('filePath')
        # if sourceCrawler.isSequence():
        #     filePath = os.path.join(
        #         os.path.dirname(filePath),
        #         '{0}.%0{1}d.{2}'.format(
        #             sourceCrawler.var('name'),
        #             sourceCrawler.var('padding'),
        #             sourceCrawler.var('ext')
        #             )
        #         )

        self.__publishData["path"] = {"local_path": filePath}

        self.__publishData["description"] = self.option('comment')
        self.__publishData["version_number"] = self.pathCrawlers()[0].var('version')

        if "_sgTask" in sourceCrawler.varNames():
            self.__publishData["task"] = sourceCrawler.var("_sgTask")

        publishName = Template(self.option('publishName')).valueFromCrawler(sourceCrawler)
        self.__publishData["name"] = publishName
        self.__publishData["code"] = publishName

        self.__linkData(sg)
        self.__sgFileType(sg)
        self.__sgUser(sg)

        sgPublishFile = sg.create("PublishedFile", self.__publishData)
        self.__makeThumbnail(sgPublishFile, sg)
        self.__makeDaily(sgPublishFile, sg)

        # this task does not return any crawlers as result
        return []

    def __linkData(self, sg):
        """
        Find the data that needs to be linked to the publish in Shotgun.
        """
        sourceCrawler = self.pathCrawlers()[0]

        project = sg.find_one('Project', [['name', 'is', sourceCrawler.var('job')]])
        self.__publishData['project'] = project

        if "shot" in sourceCrawler.varNames() or "assetName" in sourceCrawler.varNames():
            varName = "shot" if "shot" in sourceCrawler.varNames() else "assetName"
            varType = "Shot" if "shot" in sourceCrawler.varNames() else "Asset"

            filters = [
                ['code', 'is', sourceCrawler.var(varName)],
                ['project', 'is', project]
            ]
            entityData = sg.find(varType, filters)
            if len(entityData) != 1:
                raise Exception(
                    "[SGPublish] Cannot find unique {} {} in project {}. Skip Publish.".format(
                        varName,
                        sourceCrawler.var(varName),
                        sourceCrawler.var('job')
                    )
                )
            self.__publishData['entity'] = entityData[0]
        else:
            self.__publishData['entity'] = project

    def __sgFileType(self, sg):
        publishedFileType = self.option('publishedFileType')
        sgFileType = sg.find_one('PublishedFileType', filters=[["code", "is", publishedFileType]])
        if not sgFileType:
            # create a published file type on the fly
            sgFileType = sg.create("PublishedFileType", {"code": publishedFileType})
        self.__publishData["published_file_type"] = sgFileType

    def __sgUser(self, sg):
        fields = ["id", "type", "email", "login", "name", "image"]
        user = os.environ.get('USERNAME', '')
        self.__publishData["created_by"] = sg.find_one("HumanUser", filters=[["login", "is", user]], fields=fields)

    def __makeThumbnail(self, sgPublishFile, sg):

        createThumbnail = False
        sourceCrawler = self.pathCrawlers()[0]
        if "thumbnailFile" in self.optionNames():
            thumbnailFilePath = Template(self.option('thumbnailFile')).valueFromCrawler(sourceCrawler)
        else:
            createThumbnail = True
            imageCrawlers = sourceCrawler.glob(filterTypes=[Image])
            if not imageCrawlers:
                return
            targetCrawler = imageCrawlers[int(len(self.pathCrawlers()) / 2)]

            tempFile = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".jpg",
                mode='w'
            )
            thumbnailFilePath = tempFile.name
            # Remove file so ffmpeg doesn't ask to overwrite it
            os.unlink(thumbnailFilePath)

            # thumbnailTask = Task.create('imageThumbnail')
            # thumbnailTask.add(targetCrawler, thumbnailFilePath)
            # thumbnailTask.output()
            cmd = 'ffmpeg -v quiet -loglevel error -i {} -vf scale=640:-1 {}'.format(
                    targetCrawler.var("filePath"),
                    thumbnailFilePath
                    )
            os.system(cmd)

        if os.path.exists(thumbnailFilePath):
            sg.upload_thumbnail("PublishedFile", sgPublishFile["id"], thumbnailFilePath)

        if createThumbnail:
            # removing the temporary file
            os.unlink(thumbnailFilePath)

    def __makeDaily(self, sgPublishFile, sg):
        """
        Create a version in Shotgun for this path and linked to this publish.
        """
        sourceCrawler = self.pathCrawlers()[0]
        if 'movieFile' not in self.optionNames():
            # No movie provided, glob for a mov
            movCrawlers = sourceCrawler.glob(fileTypes=["mov"])
            if not movCrawlers:
                return
            movieFilePath = movCrawlers[0].var("filePath")
        else:
            movieFilePath = Template(self.option('movieFile')).valueFromCrawler(sourceCrawler)
            if not movieFilePath or not os.path.exists(movieFilePath):
                raise Exception("Movie provided for daily creation does not exist: {}".format(movieFilePath))

        # create a name for the version based on the file name
        # grab the file name, strip off extension
        name = os.path.splitext(os.path.basename(movieFilePath))[0]
        # do some replacements
        name = name.replace("_", " ")
        # and capitalize
        name = name.capitalize()

        firstFrame = None
        lastFrame = None
        movCrawler = Path.createFromPath(movieFilePath)
        if firstFrame in movCrawler.varNames():
            firstFrame = movCrawler.var('firstFrame')
            lastFrame = movCrawler.var('lastFrame')
        # else:
        #     imageCrawlers = sourceCrawler.glob(filterTypes=["Image"])
        #     if imageCrawlers and imageCrawlers[0].isSequence():
        #         firstFrame = self.pathCrawlers()[0].var('frame')
        #         lastFrame = self.pathCrawlers()[-1].var('frame')

        # Create the version in Shotgun
        data = {
            "code": name,
            "sg_status_list": "rev",
            "entity": self.__publishData['entity'],
            "created_by": self.__publishData['created_by'],
            "user": self.__publishData['created_by'],
            "description": self.__publishData['description'],
            "sg_path_to_frames": self.__publishData["path"]["local_path"],
            "project": self.__publishData['project']
        }

        if firstFrame is not None and lastFrame is not None:
            data["sg_first_frame"] = firstFrame
            data["sg_last_frame"] = lastFrame
            data["frame_count"] = (lastFrame - firstFrame + 1)
            data["frame_range"] = "%s-%s" % (firstFrame, lastFrame)

        data["published_files"] = [sgPublishFile]
        data["sg_path_to_movie"] = movieFilePath

        sgVersion = sg.create("Version", data)
        # upload files
        sg.upload("Version", sgVersion["id"], movieFilePath, "sg_uploaded_movie")

        return sgVersion


# registering task
Task.register(
    'sgPublish',
    SGPublish
)
