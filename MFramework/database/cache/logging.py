from typing import DefaultDict, Dict, Tuple

from MFramework import Guild, Snowflake
from MFramework.database import alchemy as db
from MFramework.utils.log import Log

from .database import Database


class Logging(Database):
    webhooks: Dict[str, Tuple[Snowflake, str]] = {}
    logging: DefaultDict[str, Log]

    def __init__(self, *, bot, guild: Guild, **kwargs) -> None:
        super().__init__(bot=bot, guild=guild, **kwargs)
        with bot.db.sql.Session.begin() as s:
            self.get_Webhooks(s)
        self.set_loggers(bot)

    def get_Webhooks(self, session):
        webhooks = (
            session.query(db.Webhook)
            .filter(
                db.Webhook.server_id == self.guild_id,
                db.Webhook.subscriptions.any(db.Subscription.source.contains("logging-")),
            )
            .all()
        )
        self.webhooks = {
            sub.source.replace("logging-", "").replace("_log", ""): (
                webhook.id,
                webhook.token,
            )
            for webhook in webhooks
            for sub in webhook.subscriptions
            if "logging-" in sub.source
        }

    def set_loggers(self, ctx):
        from collections import defaultdict

        from mlib.types import aInvalid

        self.logging = defaultdict(lambda: aInvalid)
        from mlib.utils import all_subclasses

        _classes = {i.__name__.lower(): i for i in all_subclasses(Log)}
        for webhook in self.webhooks:
            if webhook in _classes:
                self.logging[webhook] = _classes[webhook](ctx, self.guild_id, webhook, *self.webhooks[webhook])
