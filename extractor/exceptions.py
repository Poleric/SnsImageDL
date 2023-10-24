# base exception for all custom exception to inherit from
class InvalidLink(ValueError):
    pass


class ExtractorError(Exception):
    pass


class ScrapingException(ExtractorError):
    pass


class MediaNotFound(ScrapingException):
    pass

    def __int__(self):
        return 404
