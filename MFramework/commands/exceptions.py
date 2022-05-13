from mdiscord.exceptions import SoftError


class Error(SoftError):
    pass


class CooldownError(Error):
    pass


class ChanceError(Error):
    pass


class EventInactive(Error):
    pass


class CommandException(Error):
    pass


class MissingPermissions(CommandException):
    pass


class CommandNotFound(CommandException):
    pass


class WrongContext(CommandException):
    pass
