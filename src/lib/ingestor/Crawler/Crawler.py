import os

class InvalidVarError(Exception):
    """Invalid Var Error."""

class InvalidTagError(Exception):
    """Invalid Tag Error."""

class Crawler(object):
    """
    Abstracted Crawler.
    """

    def __init__(self, name, parentCrawler=None):
        """
        Create a crawler.
        """
        self.__vars = {}
        self.__tags = {}
        self.__hasComputedSelf = False

        # passing variables
        if parentCrawler:
            assert isinstance(parentCrawler, Crawler), \
                "Invalid crawler type!"

            for varName in parentCrawler.varNames():
                self.setVar(varName, parentCrawler.var(varName))

            self.setVar(
                'path',
                os.path.join(
                    parentCrawler.var('path'),
                    name
                )
            )
        else:
            self.setVar('path', '/')

        self.setVar('name', name)

    def isLeaf(self):
        """
        For re-implementation: Return a bollean telling if the crawler is leaf.
        """
        return True

    def children(self):
        """
        Return a list of crawlers.
        """
        assert not self.isLeaf(), "Can't compute children from a leaf crawler!"

        result = self._computeChildren()
        for crawler in result:
            assert isinstance(crawler, Crawler), \
                "Invalid Crawler Type"

        return result

    def varNames(self):
        """
        Return a list of variable names assigned to the crawler.
        """
        return self.__vars.keys()

    def setVar(self, name, value):
        """
        Set a value for a variable.
        """
        self.__vars[name] = value

    def var(self, name):
        """
        Return the value for a variable.
        """
        if name not in self.__vars:
            raise InvalidVarError(
                'Variable not found "{0}"'.format(name)
            )

        return self.__vars[name]

    def tagNames(self):
        """
        Return a list of tag names assigned to the crawler.
        """
        return self.__tags.keys()

    def setTag(self, name, value):
        """
        Set a value for a tag.
        """
        self.__tags[name] = value

    def tag(self, name):
        """
        Return the value for a tagiable.
        """
        if name not in self.__tags:
            raise InvalidTagError(
                'Tag not found "{0}"'.format(name)
            )

        return self.__tags[name]

    def clone(self):
        """
        Return a cloned instance about the current crawler.
        """
        newInstance = self.__class__(self.var('name'))

        # clonning variables
        for varName in self.varNames():
            newInstance.setVar(varName, self.var(varName))

        # clonning tags
        for tagName in self.tagNames():
            newInstance.setTag(tagName, self.tag(tagName))

        return newInstance
