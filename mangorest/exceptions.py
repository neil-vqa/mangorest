"""Custom exceptions."""


class MangoRestException(Exception):
    pass


class CollectionNotFoundError(MangoRestException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DocumentNotFoundError(MangoRestException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ResourceNameNotFoundError(MangoRestException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
