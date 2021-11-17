"""Custom exceptions."""


class MangoestCrudException(Exception):
    pass


class CollectionNotFoundError(MangoestCrudException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DocumentNotFoundError(MangoestCrudException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
