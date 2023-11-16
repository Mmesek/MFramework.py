from typing import TYPE_CHECKING, Optional

from mdiscord import Interaction


from MFramework.utils.localizations import DEFAULT_LOCALE, LOCALIZATIONS
from MFramework.commands.command import Command

if TYPE_CHECKING:
    from MFramework.bot import Bot


class Localizable:
    bot: "Bot"
    language: str = "en"
    _cmd_path: list[str]

    def __init__(self, data: Interaction, cmd: Command = None):
        if type(data) is Interaction:
            self.language = data.locale or data.guild_locale

        if cmd:
            self._cmd_path = [cmd.func.__module__]

            if cmd.master_command:
                self._cmd_path.append(cmd.master_command._cmd.name)
                self._cmd_path.append("sub_commands")

            self._cmd_path.append(cmd.name)

        if self.language not in LOCALIZATIONS:
            self.language = DEFAULT_LOCALE

        super().__init__()

    def t(self, key: str, _namespace: Optional[str] = None, _bot: Optional[str] = None, **kwargs) -> str:
        """Retrieves translation according to key prefixed by user language & context's command

        Injects command namespace into `translate` patterns:
        - {path}.{group}
        - {path}.{group}.{sub_commands}
        - {path}.{group}.{sub_commands}.{command}
        """
        from MFramework.utils.localizations import translate

        return translate(
            key=key,
            locale=self.language,
            _namespace=_namespace or self._cmd_path,
            _bot=_bot or self.bot.username,
            **kwargs,
        )
