"""Errors that are safe to display to an operator."""

class LMSError(Exception):
    """Base class for expected application errors."""

class ValidationError(LMSError):
    pass

class ConflictError(LMSError):
    pass

class RelatedRecordsError(LMSError):
    pass

class NotFoundError(LMSError):
    pass

class StorageError(LMSError):
    pass
