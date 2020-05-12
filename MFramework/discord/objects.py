# Generated file from docs at 17:28 2020/03/20.
from __future__ import annotations
import datetime
class BaseClass:
    def __getitem__(cls, x):
        return getattr(cls, x)


class Audit_Log:
    '''
    :webhooks: array of [webhook](https://discordapp.com/developers/docs/resources/webhook#webhook-object) objects - list of webhooks found in the audit log\n
    :users: array of [user](https://discordapp.com/developers/docs/resources/user#user-object) objects - list of users found in the audit log\n
    :audit_log_entries: array of [audit log entry](https://discordapp.com/developers/docs/resources/audit_log#audit-log-entry-object) objects - list of audit log entries\n
    :integrations: array of partial [integration](https://discordapp.com/developers/docs/resources/guild#integration-object) objects - list of partial integration objects\n'''
    __slots__ = ("webhooks", "users", "audit_log_entries", "integrations")
    webhooks: list
    users: list
    audit_log_entries: list
    integrations: list

    def __init__(self, data):
        self.webhooks = [Webhook(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('webhooks', [])]
        self.users = [User(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('users', [])]
        self.audit_log_entries = [Audit_Log_Entry(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('audit_log_entries', [])]
        self.integrations = [Integration(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('integrations', [])]


class Audit_Log_Entry:
    '''
    :target_id: string - id of the affected entity (webhook, user, role, etc.)\n
    :user_id: snowflake - the user who made the changes\n
    :id: snowflake - id of the entry\n
    :action_type: [audit log event](https://discordapp.com/developers/docs/resources/audit_log#audit-log-entry-object-audit-log-events) - type of action that occurred\n
    Optionals:

    :changes: array of [audit log change](https://discordapp.com/developers/docs/resources/audit_log#audit-log-change-object) objects - changes made to the target_id\n
    :options: [optional audit entry info](https://discordapp.com/developers/docs/resources/audit_log#audit-log-entry-object-optional-audit-entry-info) - additional info for certain action types\n
    :reason: string - the reason for the change (0-512 characters)\n'''
    __slots__ = ("target_id", "user_id", "id", "action_type", "changes", "options", "reason")
    target_id: str
    user_id: int
    id: int
    action_type: int
    changes: list
    options: str
    reason: str

    def __init__(self, data):
        self.target_id = data.get('target_id', None)
        self.user_id = int(data.get('user_id', 0) or 0)
        self.id = int(data.get('id', 0) or 0)
        self.action_type = int(data.get('action_type', 0) or 0)
        self.changes = [Audit_Log_Change(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('changes', [])]
        self.options = data.get('options', None)
        self.reason = data.get('reason', None)


class Audit_Log_Change:
    '''
    :key: string - name of audit log [change key](https://discordapp.com/developers/docs/resources/audit_log#audit-log-change-object-audit-log-change-key)\n
    Optionals:

    :new_value: [mixed](https://discordapp.com/developers/docs/resources/audit_log#audit-log-change-object-audit-log-change-key) - new value of the key\n
    :old_value: [mixed](https://discordapp.com/developers/docs/resources/audit_log#audit-log-change-object-audit-log-change-key) - old value of the key\n'''
    __slots__ = ("key", "new_value", "old_value")
    key: str
    new_value: dict
    old_value: dict

    def __init__(self, data):
        self.key = data.get('key', None)
        self.new_value = data.get('new_value', None)
        self.old_value = data.get('old_value', None)


class Channel:
    '''Represents a guild or DM channel within Discord.

    :id: snowflake - the id of this channel\n
    :type: integer - the [type of channel](https://discordapp.com/developers/docs/resources/channel#channel-object-channel-types)\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n
    :position: integer - sorting position of the channel\n
    :permission_overwrites: array of [overwrite](https://discordapp.com/developers/docs/resources/channel#overwrite-object) objects - explicit permission overwrites for members and roles\n
    :name: string - the name of the channel (2-100 characters)\n
    :topic: string - the channel topic (0-1024 characters)\n
    :nsfw: boolean - whether the channel is nsfw\n
    :last_message_id: snowflake - the id of the last message sent in this channel (may not point to an existing or valid message)\n
    :bitrate: integer - the bitrate (in bits) of the voice channel\n
    :user_limit: integer - the user limit of the voice channel\n
    :rate_limit_per_user: integer - amount of seconds a user has to wait before sending another message (0-21600); bots, as well as users with the permission `manage_messages` or `manage_channel`, are unaffected\n
    :recipients: array of [user](https://discordapp.com/developers/docs/resources/user#user-object) objects - the recipients of the DM\n
    :icon: string - icon hash\n
    :owner_id: snowflake - id of the DM creator\n
    :application_id: snowflake - application id of the group DM creator if it is bot-created\n
    :parent_id: snowflake - id of the parent category for a channel (each parent category can contain up to 50 channels)\n
    :last_pin_timestamp: ISO8601 timestamp - when the last pinned message was pinned\n'''
    __slots__ = ("id", "type", "guild_id", "position", "permission_overwrites", "name", "topic", "nsfw", "last_message_id", "bitrate", "user_limit", "rate_limit_per_user", "recipients", "icon", "owner_id", "application_id", "parent_id", "last_pin_timestamp")
    id: int
    type: int
    guild_id: int
    position: int
    permission_overwrites: list
    name: str
    topic: str
    nsfw: bool
    last_message_id: int
    bitrate: int
    user_limit: int
    rate_limit_per_user: int
    recipients: list
    icon: str
    owner_id: int
    application_id: int
    parent_id: int
    last_pin_timestamp: datetime.datetime

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.type = int(data.get('type', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.position = int(data.get('position', 0) or 0)
        self.permission_overwrites = [Overwrite(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('permission_overwrites', [])]
        self.name = data.get('name', None)
        self.topic = data.get('topic', None)
        self.nsfw = data.get('nsfw', False)
        self.last_message_id = int(data.get('last_message_id', 0) or 0)
        self.bitrate = int(data.get('bitrate', 0) or 0)
        self.user_limit = int(data.get('user_limit', 0) or 0)
        self.rate_limit_per_user = int(data.get('rate_limit_per_user', 0) or 0)
        self.recipients = [User(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('recipients', [])]
        self.icon = data.get('icon', None)
        self.owner_id = int(data.get('owner_id', 0) or 0)
        self.application_id = int(data.get('application_id', 0) or 0)
        self.parent_id = int(data.get('parent_id', 0) or 0)
        self.last_pin_timestamp = data.get('last_pin_timestamp', None)


class Message:
    '''Represents a message sent in a channel within Discord.

    :id: snowflake - id of the message\n
    :channel_id: snowflake - id of the channel the message was sent in\n
    :author: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the author of this message (not guaranteed to be a valid user, see below)\n
    :content: string - contents of the message\n
    :timestamp: ISO8601 timestamp - when this message was sent\n
    :edited_timestamp: ISO8601 timestamp - when this message was edited (or null if never)\n
    :tts: boolean - whether this was a TTS message\n
    :mention_everyone: boolean - whether this message mentions everyone\n
    :mentions: array of [user](https://discordapp.com/developers/docs/resources/user#user-object) objects, with an additional partial [member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) field - users specifically mentioned in the message\n
    :mention_roles: array of [role](https://discordapp.com/developers/docs/topics/permissions#role-object) object ids - roles specifically mentioned in this message\n
    :attachments: array of [attachment](https://discordapp.com/developers/docs/resources/channel#attachment-object) objects - any attached files\n
    :embeds: array of [embed](https://discordapp.com/developers/docs/resources/channel#embed-object) objects - any embedded content\n
    :pinned: boolean - whether this message is pinned\n
    :type: integer - [type of message](https://discordapp.com/developers/docs/resources/channel#message-object-message-types)\n
    Optionals:

    :guild_id: snowflake - id of the guild the message was sent in\n
    :member: partial [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) object - member properties for this message's author\n
    :mention_channels: array of [channel mention](https://discordapp.com/developers/docs/resources/channel#channel-mention-object) objects - channels specifically mentioned in this message\n
    :reactions: array of [reaction](https://discordapp.com/developers/docs/resources/channel#reaction-object) objects - reactions to the message\n
    :nonce: integer or string - used for validating a message was sent\n
    :webhook_id: snowflake - if the message is generated by a webhook, this is the webhook's id\n
    :activity: [message activity](https://discordapp.com/developers/docs/resources/channel#message-object-message-activity-structure) object - sent with Rich Presence-related chat embeds\n
    :application: [message application](https://discordapp.com/developers/docs/resources/channel#message-object-message-application-structure) object - sent with Rich Presence-related chat embeds\n
    :message_reference: [message_reference](https://discordapp.com/developers/docs/resources/channel#message-object-message-reference-structure) object - reference data sent with crossposted messages\n
    :flags: integer - [message flags](https://discordapp.com/developers/docs/resources/channel#message-object-message-flags) `OR`d together, describes extra features of the message\n'''
    __slots__ = ("id", "channel_id", "author", "content", "timestamp", "edited_timestamp", "tts", "mention_everyone", "mentions", "mention_roles", "attachments", "embeds", "pinned", "type", "guild_id", "member", "mention_channels", "reactions", "nonce", "webhook_id", "activity", "application", "message_reference", "flags")
    id: int
    channel_id: int
    author: User
    content: str
    timestamp: datetime.datetime
    edited_timestamp: datetime.datetime
    tts: bool
    mention_everyone: bool
    mentions: list
    mention_roles: list
    attachments: list
    embeds: list
    pinned: bool
    type: int
    guild_id: int
    member: Guild_Member
    mention_channels: list
    reactions: list
    nonce: int
    webhook_id: int
    activity: Message_Activity
    application: Message_Application
    message_reference: Message_Reference
    flags: int

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.author = User(data.get('author', {}))
        self.content = data.get('content', None)
        self.timestamp = data.get('timestamp', None)
        self.edited_timestamp = data.get('edited_timestamp', None)
        self.tts = data.get('tts', False)
        self.mention_everyone = data.get('mention_everyone', False)
        self.mentions = [User(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('mentions', [])]
        self.mention_roles = [Role(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('mention_roles', [])]
        self.attachments = [Attachment(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('attachments', [])]
        self.embeds = [Embed(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('embeds', [])]
        self.pinned = data.get('pinned', False)
        self.type = int(data.get('type', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.member = Guild_Member(data.get('member', {}))
        self.mention_channels = [Channel_Mention(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('mention_channels', [])]
        self.reactions = [Reaction(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('reactions', [])]
        self.nonce = int(data.get('nonce', 0) or 0)
        self.webhook_id = int(data.get('webhook_id', 0) or 0)
        self.activity = Message_Activity(data.get('activity', {}))
        self.application = Message_Application(data.get('application', {}))
        self.message_reference = Message_Reference(data.get('message_reference', {}))
        self.flags = int(data.get('flags', 0) or 0)


class Message_Activity:
    '''
    :type: integer - [type of message activity](https://discordapp.com/developers/docs/resources/channel#message-object-message-activity-types)\n
    Optionals:

    :party_id: string - party_id from a [Rich Presence event](https://discordapp.com/developers/docs/rich/presence_how_to#updating-presence-update-presence-payload-fields)\n'''
    __slots__ = ("type", "party_id")
    type: int
    party_id: str

    def __init__(self, data):
        self.type = int(data.get('type', 0) or 0)
        self.party_id = data.get('party_id', None)


class Message_Application:
    '''
    :id: snowflake - id of the application\n
    :description: string - application's description\n
    :icon: string - id of the application's icon\n
    :name: string - name of the application\n
    Optionals:

    :cover_image: string - id of the embed's image asset\n'''
    __slots__ = ("id", "description", "icon", "name", "cover_image")
    id: int
    description: str
    icon: str
    name: str
    cover_image: str

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.description = data.get('description', None)
        self.icon = data.get('icon', None)
        self.name = data.get('name', None)
        self.cover_image = data.get('cover_image', None)


class Message_Reference:
    '''
    :channel_id: snowflake - id of the originating message's channel\n
    Optionals:

    :message_id: snowflake - id of the originating message\n
    :guild_id: snowflake - id of the originating message's guild\n'''
    __slots__ = ("channel_id", "message_id", "guild_id")
    channel_id: int
    message_id: int
    guild_id: int

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.message_id = int(data.get('message_id', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Reaction:
    '''
    :count: integer - times this emoji has been used to react\n
    :me: boolean - whether the current user reacted using this emoji\n
    :emoji: partial [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) object - emoji information\n'''
    __slots__ = ("count", "me", "emoji")
    count: int
    me: bool
    emoji: Emoji

    def __init__(self, data):
        self.count = int(data.get('count', 0) or 0)
        self.me = data.get('me', False)
        self.emoji = Emoji(data.get('emoji', {}))


class Overwrite:
    '''
    :id: snowflake - role or user id\n
    :type: string - either "role" or "member"\n
    :allow: integer - permission bit set\n
    :deny: integer - permission bit set\n'''
    __slots__ = ("id", "type", "allow", "deny")
    id: int
    type: str
    allow: int
    deny: int

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.type = data.get('type', None)
        self.allow = int(data.get('allow', 0) or 0)
        self.deny = int(data.get('deny', 0) or 0)


class Embed:
    '''
    Optionals:

    :title: string - title of embed\n
    :type: string - [type of embed](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-types) (always "rich" for webhook embeds)\n
    :description: string - description of embed\n
    :url: string - url of embed\n
    :timestamp: ISO8601 timestamp - timestamp of embed content\n
    :color: integer - color code of the embed\n
    :footer: [embed footer](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-footer-structure) object - footer information\n
    :image: [embed image](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-image-structure) object - image information\n
    :thumbnail: [embed thumbnail](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-thumbnail-structure) object - thumbnail information\n
    :video: [embed video](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-video-structure) object - video information\n
    :provider: [embed provider](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-provider-structure) object - provider information\n
    :author: [embed author](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-author-structure) object - author information\n
    :fields: array of [embed field](https://discordapp.com/developers/docs/resources/channel#embed-object-embed-field-structure) objects - fields information\n'''
    __slots__ = ("title", "type", "description", "url", "timestamp", "color", "footer", "image", "thumbnail", "video", "provider", "author", "fields")
    title: str
    type: str
    description: str
    url: str
    timestamp: datetime.datetime
    color: int
    footer: Embed_Footer
    image: Embed_Image
    thumbnail: Embed_Thumbnail
    video: Embed_Video
    provider: Embed_Provider
    author: Embed_Author
    fields: list

    def __init__(self, data):
        self.title = data.get('title', None)
        self.type = data.get('type', None)
        self.description = data.get('description', None)
        self.url = data.get('url', None)
        self.timestamp = data.get('timestamp', None)
        self.color = int(data.get('color', 0) or 0)
        self.footer = Embed_Footer(data.get('footer', {}))
        self.image = Embed_Image(data.get('image', {}))
        self.thumbnail = Embed_Thumbnail(data.get('thumbnail', {}))
        self.video = Embed_Video(data.get('video', {}))
        self.provider = Embed_Provider(data.get('provider', {}))
        self.author = Embed_Author(data.get('author', {}))
        self.fields = [Embed_Field(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('fields', [])]


class Embed_Thumbnail:
    '''
    Optionals:

    :url: string - source url of thumbnail (only supports http(s) and attachments)\n
    :proxy_url: string - a proxied url of the thumbnail\n
    :height: integer - height of thumbnail\n
    :width: integer - width of thumbnail\n'''
    __slots__ = ("url", "proxy_url", "height", "width")
    url: str
    proxy_url: str
    height: int
    width: int

    def __init__(self, data):
        self.url = data.get('url', None)
        self.proxy_url = data.get('proxy_url', None)
        self.height = int(data.get('height', 0) or 0)
        self.width = int(data.get('width', 0) or 0)


class Embed_Video:
    '''
    Optionals:

    :url: string - source url of video\n
    :height: integer - height of video\n
    :width: integer - width of video\n'''
    __slots__ = ("url", "height", "width")
    url: str
    height: int
    width: int

    def __init__(self, data):
        self.url = data.get('url', None)
        self.height = int(data.get('height', 0) or 0)
        self.width = int(data.get('width', 0) or 0)


class Embed_Image:
    '''
    Optionals:

    :url: string - source url of image (only supports http(s) and attachments)\n
    :proxy_url: string - a proxied url of the image\n
    :height: integer - height of image\n
    :width: integer - width of image\n'''
    __slots__ = ("url", "proxy_url", "height", "width")
    url: str
    proxy_url: str
    height: int
    width: int

    def __init__(self, data):
        self.url = data.get('url', None)
        self.proxy_url = data.get('proxy_url', None)
        self.height = int(data.get('height', 0) or 0)
        self.width = int(data.get('width', 0) or 0)


class Embed_Provider:
    '''
    Optionals:

    :name: string - name of provider\n
    :url: string - url of provider\n'''
    __slots__ = ("name", "url")
    name: str
    url: str

    def __init__(self, data):
        self.name = data.get('name', None)
        self.url = data.get('url', None)


class Embed_Author:
    '''
    Optionals:

    :name: string - name of author\n
    :url: string - url of author\n
    :icon_url: string - url of author icon (only supports http(s) and attachments)\n
    :proxy_icon_url: string - a proxied url of author icon\n'''
    __slots__ = ("name", "url", "icon_url", "proxy_icon_url")
    name: str
    url: str
    icon_url: str
    proxy_icon_url: str

    def __init__(self, data):
        self.name = data.get('name', None)
        self.url = data.get('url', None)
        self.icon_url = data.get('icon_url', None)
        self.proxy_icon_url = data.get('proxy_icon_url', None)


class Embed_Footer:
    '''
    :text: string - footer text\n
    Optionals:

    :icon_url: string - url of footer icon (only supports http(s) and attachments)\n
    :proxy_icon_url: string - a proxied url of footer icon\n'''
    __slots__ = ("text", "icon_url", "proxy_icon_url")
    text: str
    icon_url: str
    proxy_icon_url: str

    def __init__(self, data):
        self.text = data.get('text', None)
        self.icon_url = data.get('icon_url', None)
        self.proxy_icon_url = data.get('proxy_icon_url', None)


class Embed_Field:
    '''
    :name: string - name of the field\n
    :value: string - value of the field\n
    Optionals:

    :inline: boolean - whether or not this field should display inline\n'''
    __slots__ = ("name", "value", "inline")
    name: str
    value: str
    inline: bool

    def __init__(self, data):
        self.name = data.get('name', None)
        self.value = data.get('value', None)
        self.inline = data.get('inline', False)


class Attachment:
    '''
    :id: snowflake - attachment id\n
    :filename: string - name of file attached\n
    :size: integer - size of file in bytes\n
    :url: string - source url of file\n
    :proxy_url: string - a proxied url of file\n
    :height: integer - height of file (if image)\n
    :width: integer - width of file (if image)\n'''
    __slots__ = ("id", "filename", "size", "url", "proxy_url", "height", "width")
    id: int
    filename: str
    size: int
    url: str
    proxy_url: str
    height: int
    width: int

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.filename = data.get('filename', None)
        self.size = int(data.get('size', 0) or 0)
        self.url = data.get('url', None)
        self.proxy_url = data.get('proxy_url', None)
        self.height = int(data.get('height', 0) or 0)
        self.width = int(data.get('width', 0) or 0)


class Channel_Mention:
    '''
    :id: snowflake - id of the channel\n
    :guild_id: snowflake - id of the guild containing the channel\n
    :type: integer - the [type of channel](https://discordapp.com/developers/docs/resources/channel#channel-object-channel-types)\n
    :name: string - the name of the channel\n'''
    __slots__ = ("id", "guild_id", "type", "name")
    id: int
    guild_id: int
    type: int
    name: str

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.type = int(data.get('type', 0) or 0)
        self.name = data.get('name', None)


class Allowed_Mentions:
    '''The allowed mention field allows for more granular control over mentions without various hacks to the message content.
    This will always validate against message content to avoid phantom pings (e.g.
    to ping everyone, you must still have `@everyone` in the message content), and check against user/bot permissions.

    :parse: array of allowed mention types - An array of [allowed mention types](https://discordapp.com/developers/docs/resources/channel#allowed-mentions-object-allowed-mention-types) to parse from the content.\n
    :roles: list of snowflakes - Array of role_ids to mention (Max size of 100)\n
    :users: list of snowflakes - Array of user_ids to mention (Max size of 100)\n'''
    __slots__ = ("parse", "roles", "users")
    parse: list
    roles: list
    users: list

    def __init__(self, data):
        self.parse = [i for i in data.get('parse', [])]
        self.roles = [int(i or 0) for i in data.get('roles', [])]
        self.users = [int(i or 0) for i in data.get('users', [])]


class Emoji:
    '''
    :id: snowflake - [emoji id](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :name: string (can be null only in reaction emoji objects) - emoji name\n
    Optionals:

    :roles: array of [role](https://discordapp.com/developers/docs/topics/permissions#role-object) object ids - roles this emoji is whitelisted to\n
    :user: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - user that created this emoji\n
    :require_colons: boolean - whether this emoji must be wrapped in colons\n
    :managed: boolean - whether this emoji is managed\n
    :animated: boolean - whether this emoji is animated\n
    :available: boolean - whether this emoji can be used, may be false due to loss of Server Boosts\n'''
    __slots__ = ("id", "name", "roles", "user", "require_colons", "managed", "animated", "available")
    id: int
    name: str
    roles: list
    user: User
    require_colons: bool
    managed: bool
    animated: bool
    available: bool

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.name = data.get('name', None)
        self.roles = [int(i or 0) for i in data.get('roles', [])]
        self.user = User(data.get('user', {}))
        self.require_colons = data.get('require_colons', False)
        self.managed = data.get('managed', False)
        self.animated = data.get('animated', False)
        self.available = data.get('available', False)


class Guild:
    '''
    :id: snowflake - guild id\n
    :name: string - guild name (2-100 characters)\n
    :icon: string - [icon hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :splash: string - [splash hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :discovery_splash: string - [discovery splash hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :owner_id: snowflake - id of owner\n
    :region: string - [voice region](https://discordapp.com/developers/docs/resources/voice#voice-region-object) id for the guild\n
    :afk_channel_id: snowflake - id of afk channel\n
    :afk_timeout: integer - afk timeout in seconds\n
    :verification_level: integer - [verification level](https://discordapp.com/developers/docs/resources/guild#guild-object-verification-level) required for the guild\n
    :default_message_notifications: integer - default [message notifications level](https://discordapp.com/developers/docs/resources/guild#guild-object-default-message-notification-level)\n
    :explicit_content_filter: integer - [explicit content filter level](https://discordapp.com/developers/docs/resources/guild#guild-object-explicit-content-filter-level)\n
    :roles: array of [role](https://discordapp.com/developers/docs/topics/permissions#role-object) objects - roles in the guild\n
    :emojis: array of [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) objects - custom guild emojis\n
    :features: array of [guild feature](https://discordapp.com/developers/docs/resources/guild#guild-object-guild-features) strings - enabled guild features\n
    :mfa_level: integer - required [MFA level](https://discordapp.com/developers/docs/resources/guild#guild-object-mfa-level) for the guild\n
    :application_id: snowflake - application id of the guild creator if it is bot-created\n
    :system_channel_id: snowflake - the id of the channel where guild notices such as welcome messages and boost events are posted\n
    :system_channel_flags: number - [system channel flags](https://discordapp.com/developers/docs/resources/guild#guild-object-system-channel-flags)\n
    :rules_channel_id: snowflake - the id of the channel where "PUBLIC" guilds display rules and/or guidelines\n
    :vanity_url_code: string - the vanity url code for the guild\n
    :description: string - the description for the guild\n
    :banner: string - [banner hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :premium_tier: integer - [premium tier](https://discordapp.com/developers/docs/resources/guild#guild-object-premium-tier) (Server Boost level)\n
    :preferred_locale: string - the preferred locale of a "PUBLIC" guild used in server discovery and notices from Discord; defaults to "en-US"\n
    :public_updates_channel_id: snowflake - the id of the channel where admins and moderators of "PUBLIC" guilds receive notices from Discord\n
    Optionals:

    :owner: boolean - whether or not [the user](https://discordapp.com/developers/docs/resources/user#get-current-user-guilds) is the owner of the guild\n
    :permissions: integer - total permissions for [the user](https://discordapp.com/developers/docs/resources/user#get-current-user-guilds) in the guild (does not include channel overrides)\n
    :embed_enabled: boolean - whether this guild is embeddable (e.g. widget)\n
    :embed_channel_id: snowflake - if not null, the channel id that the widget will generate an invite to\n
    :widget_enabled: boolean - whether or not the server widget is enabled\n
    :widget_channel_id: snowflake - the channel id for the server widget\n
    :joined_at: ISO8601 timestamp - when this guild was joined at\n
    :large: boolean - whether this is considered a large guild\n
    :unavailable: boolean - whether this guild is unavailable\n
    :member_count: integer - total number of members in this guild\n
    :voice_states: array of partial [voice state](https://discordapp.com/developers/docs/resources/voice#voice-state-object) objects - (without the `guild_id` key)\n
    :members: array of [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) objects - users in the guild\n
    :channels: array of [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) objects - channels in the guild\n
    :presences: array of partial [presence update](https://discordapp.com/developers/docs/topics/gateway#presence-update) objects - presences of the users in the guild\n
    :max_presences: integer - the maximum amount of presences for the guild (the default value, currently 25000, is in effect when null is returned)\n
    :max_members: integer - the maximum amount of members for the guild\n
    :premium_subscription_count: integer - the number of boosts this server currently has\n'''
    __slots__ = ("id", "name", "icon", "splash", "discovery_splash", "owner_id", "region", "afk_channel_id", "afk_timeout", "verification_level", "default_message_notifications", "explicit_content_filter", "roles", "emojis", "features", "mfa_level", "application_id", "system_channel_id", "system_channel_flags", "rules_channel_id", "vanity_url_code", "description", "banner", "premium_tier", "preferred_locale", "public_updates_channel_id", "owner", "permissions", "embed_enabled", "embed_channel_id", "widget_enabled", "widget_channel_id", "joined_at", "large", "unavailable", "member_count", "voice_states", "members", "channels", "presences", "max_presences", "max_members", "premium_subscription_count")
    id: int
    name: str
    icon: str
    splash: str
    discovery_splash: str
    owner_id: int
    region: str
    afk_channel_id: int
    afk_timeout: int
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: list
    emojis: list
    features: list
    mfa_level: int
    application_id: int
    system_channel_id: int
    system_channel_flags: int
    rules_channel_id: int
    vanity_url_code: str
    description: str
    banner: str
    premium_tier: int
    preferred_locale: str
    public_updates_channel_id: int
    owner: bool
    permissions: int
    embed_enabled: bool
    embed_channel_id: int
    widget_enabled: bool
    widget_channel_id: int
    joined_at: datetime.datetime
    large: bool
    unavailable: bool
    member_count: int
    voice_states: list
    members: list
    channels: list
    presences: list
    max_presences: int
    max_members: int
    premium_subscription_count: int

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.name = data.get('name', None)
        self.icon = data.get('icon', None)
        self.splash = data.get('splash', None)
        self.discovery_splash = data.get('discovery_splash', None)
        self.owner_id = int(data.get('owner_id', 0) or 0)
        self.region = data.get('region', None)
        self.afk_channel_id = int(data.get('afk_channel_id', 0) or 0)
        self.afk_timeout = int(data.get('afk_timeout', 0) or 0)
        self.verification_level = int(data.get('verification_level', 0) or 0)
        self.default_message_notifications = int(data.get('default_message_notifications', 0) or 0)
        self.explicit_content_filter = int(data.get('explicit_content_filter', 0) or 0)
        self.roles = [Role(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('roles', [])]
        self.emojis = [Emoji(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('emojis', [])]
        self.features = [i for i in data.get('features', [])]
        self.mfa_level = int(data.get('mfa_level', 0) or 0)
        self.application_id = int(data.get('application_id', 0) or 0)
        self.system_channel_id = int(data.get('system_channel_id', 0) or 0)
        self.system_channel_flags = int(data.get('system_channel_flags', 0) or 0)
        self.rules_channel_id = int(data.get('rules_channel_id', 0) or 0)
        self.vanity_url_code = data.get('vanity_url_code', None)
        self.description = data.get('description', None)
        self.banner = data.get('banner', None)
        self.premium_tier = int(data.get('premium_tier', 0) or 0)
        self.preferred_locale = data.get('preferred_locale', None)
        self.public_updates_channel_id = int(data.get('public_updates_channel_id', 0) or 0)
        self.owner = data.get('owner', False)
        self.permissions = int(data.get('permissions', 0) or 0)
        self.embed_enabled = data.get('embed_enabled', False)
        self.embed_channel_id = int(data.get('embed_channel_id', 0) or 0)
        self.widget_enabled = data.get('widget_enabled', False)
        self.widget_channel_id = int(data.get('widget_channel_id', 0) or 0)
        self.joined_at = data.get('joined_at', None)
        self.large = data.get('large', False)
        self.unavailable = data.get('unavailable', False)
        self.member_count = int(data.get('member_count', 0) or 0)
        self.voice_states = [Voice_State(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('voice_states', [])]
        self.members = [Guild_Member(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('members', [])]
        self.channels = [Channel(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('channels', [])]
        self.presences = [i for i in data.get('presences', [])]
        self.max_presences = int(data.get('max_presences', 0) or 0)
        self.max_members = int(data.get('max_members', 0) or 0)
        self.premium_subscription_count = int(data.get('premium_subscription_count', 0) or 0)


class Guild_Preview:
    '''
    :id: snowflake - guild id\n
    :name: string - guild name (2-100 characters)\n
    :icon: string - [icon hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :splash: string - [splash hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :discovery_splash: string - [discovery splash hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    :emojis: array of [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) objects - custom guild emojis\n
    :features: array of [guild feature](https://discordapp.com/developers/docs/resources/guild#guild-object-guild-features) strings - enabled guild features\n
    :approximate_member_count: integer - approximate number of members in this guild\n
    :approximate_presence_count: integer - approximate number of online members in this guild\n
    :description: string - the description for the guild\n'''
    __slots__ = ("id", "name", "icon", "splash", "discovery_splash", "emojis", "features", "approximate_member_count", "approximate_presence_count", "description")
    id: int
    name: str
    icon: str
    splash: str
    discovery_splash: str
    emojis: list
    features: list
    approximate_member_count: int
    approximate_presence_count: int
    description: str

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.name = data.get('name', None)
        self.icon = data.get('icon', None)
        self.splash = data.get('splash', None)
        self.discovery_splash = data.get('discovery_splash', None)
        self.emojis = [Emoji(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('emojis', [])]
        self.features = [i for i in data.get('features', [])]
        self.approximate_member_count = int(data.get('approximate_member_count', 0) or 0)
        self.approximate_presence_count = int(data.get('approximate_presence_count', 0) or 0)
        self.description = data.get('description', None)


class Guild_Embed:
    '''
    :enabled: boolean - whether the embed is enabled\n
    :channel_id: snowflake - the embed channel id\n'''
    __slots__ = ("enabled", "channel_id")
    enabled: bool
    channel_id: int

    def __init__(self, data):
        self.enabled = data.get('enabled', False)
        self.channel_id = int(data.get('channel_id', 0) or 0)


class Guild_Member:
    '''
    :user: [user](https:#/discordapp.com/developers/docs/resources/user#user-object) object - the user this guild member represents\n
    :roles: array of snowflakes - array of [role](https:#/discordapp.com/developers/docs/topics/permissions#role-object) object ids\n
    :joined_at: ISO8601 timestamp - when the user joined the guild\n
    :deaf: boolean - whether the user is deafened in voice channels\n
    :mute: boolean - whether the user is muted in voice channels\n
    Optionals:

    :nick: string - this users guild nickname (if one is set)\n
    :premium_since: ISO8601 timestamp - when the user started [boosting](https:#/support.discordapp.com/hc/en-us/articles/360028038352-Server-Boosting-) the guild\n'''
    __slots__ = ("user", "roles", "joined_at", "deaf", "mute", "nick", "premium_since", "guild_id")
    user: User
    roles: list
    joined_at: datetime.datetime
    deaf: bool
    mute: bool
    nick: str
    premium_since: datetime.datetime

    def __init__(self, data):
        self.user = User(data.get('user', {}))
        self.roles = [int(i or 0) for i in data.get('roles', [])]
        self.joined_at = data.get('joined_at', None)
        self.guild_id = int(data.get('guild_id',0))
        self.deaf = data.get('deaf', False)
        self.mute = data.get('mute', False)
        self.nick = data.get('nick', None)
        self.premium_since = data.get('premium_since', None)


class Integration:
    '''
    :id: snowflake - integration id\n
    :name: string - integration name\n
    :type: string - integration type (twitch, youtube, etc)\n
    :enabled: boolean - is this integration enabled\n
    :syncing: boolean - is this integration syncing\n
    :role_id: snowflake - id that this integration uses for "subscribers"\n
    :expire_behavior: [integration expire behavior](https://discordapp.com/developers/docs/resources/guild#integration-object-integration-expire-behaviors) - the behavior of expiring subscribers\n
    :expire_grace_period: integer - the grace period (in days) before expiring subscribers\n
    :user: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - user for this integration\n
    :account: [account](https://discordapp.com/developers/docs/resources/guild#integration-account-object) object - integration account information\n
    :synced_at: ISO8601 timestamp - when this integration was last synced\n
    Optionals:

    :enable_emoticons: boolean - whether emoticons should be synced for this integration (twitch only currently)\n'''
    __slots__ = ("id", "name", "type", "enabled", "syncing", "role_id", "expire_behavior", "expire_grace_period", "user", "account", "synced_at", "enable_emoticons")
    id: int
    name: str
    type: str
    enabled: bool
    syncing: bool
    role_id: int
    expire_behavior: int
    expire_grace_period: int
    user: User
    account: Integration_Account
    synced_at: datetime.datetime
    enable_emoticons: bool

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.name = data.get('name', None)
        self.type = data.get('type', None)
        self.enabled = data.get('enabled', False)
        self.syncing = data.get('syncing', False)
        self.role_id = int(data.get('role_id', 0) or 0)
        self.expire_behavior = int(data.get('expire_behavior', 0) or 0)
        self.expire_grace_period = int(data.get('expire_grace_period', 0) or 0)
        self.user = User(data.get('user', {}))
        self.account = Integration_Account(data.get('account', {}))
        self.synced_at = data.get('synced_at', None)
        self.enable_emoticons = data.get('enable_emoticons', False)


class Integration_Account:
    '''
    :id: string - id of the account\n
    :name: string - name of the account\n'''
    __slots__ = ("id", "name")
    id: str
    name: str

    def __init__(self, data):
        self.id = data.get('id', None)
        self.name = data.get('name', None)


class Ban:
    '''
    :reason: string - the reason for the ban\n
    :user: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the banned user\n'''
    __slots__ = ("reason", "user")
    reason: str
    user: User

    def __init__(self, data):
        self.reason = data.get('reason', None)
        self.user = User(data.get('user', {}))


class Invite:
    '''Represents a code that when used, adds a user to a guild or group DM channel.

    :code: string - the invite code (unique ID)\n
    :channel: partial [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object - the channel this invite is for\n
    Optionals:

    :guild: partial [guild](https://discordapp.com/developers/docs/resources/guild#guild-object) object - the guild this invite is for\n
    :inviter: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the user who created the invite\n
    :target_user: partial [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the target user for this invite\n
    :target_user_type: integer - the type of target user for this invite\n
    :approximate_presence_count: integer - approximate count of online members (only present when target_user is set)\n
    :approximate_member_count: integer - approximate count of total members\n'''
    __slots__ = ("code", "channel", "guild", "inviter", "target_user", "target_user_type", "approximate_presence_count", "approximate_member_count")
    code: str
    channel: Channel
    guild: Guild
    inviter: User
    target_user: User
    target_user_type: int
    approximate_presence_count: int
    approximate_member_count: int

    def __init__(self, data):
        self.code = data.get('code', None)
        self.channel = Channel(data.get('channel', {}))
        self.guild = Guild(data.get('guild', {}))
        self.inviter = User(data.get('inviter', {}))
        self.target_user = User(data.get('target_user', {}))
        self.target_user_type = int(data.get('target_user_type', 0) or 0)
        self.approximate_presence_count = int(data.get('approximate_presence_count', 0) or 0)
        self.approximate_member_count = int(data.get('approximate_member_count', 0) or 0)


class Invite_Metadata:
    '''Extra information about an invite, will extend the [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) object.

    :uses: integer - number of times this invite has been used\n
    :max_uses: integer - max number of times this invite can be used\n
    :max_age: integer - duration (in seconds) after which the invite expires\n
    :temporary: boolean - whether this invite only grants temporary membership\n
    :created_at: ISO8601 timestamp - when this invite was created\n'''
    __slots__ = ("uses", "max_uses", "max_age", "temporary", "created_at")
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: datetime.datetime

    def __init__(self, data):
        self.uses = int(data.get('uses', 0) or 0)
        self.max_uses = int(data.get('max_uses', 0) or 0)
        self.max_age = int(data.get('max_age', 0) or 0)
        self.temporary = data.get('temporary', False)
        self.created_at = data.get('created_at', None)


class User:
    '''
    :id: snowflake - the user's id\n
    :username: string - the user's username, not unique across the platform\n
    :discriminator: string - the user's 4-digit discord-tag\n
    :avatar: string - the user's [avatar hash](https://discordapp.com/developers/docs/reference#image-formatting)\n
    Optionals:

    :bot: boolean - whether the user belongs to an OAuth2 application\n
    :system: boolean - whether the user is an Official Discord System user (part of the urgent message system)\n
    :mfa_enabled: boolean - whether the user has two factor enabled on their account\n
    :locale: string - the user's chosen language option\n
    :verified: boolean - whether the email on this account has been verified\n
    :email: string - the user's email\n
    :flags: integer - the [flags](https://discordapp.com/developers/docs/resources/user#user-object-user-flags) on a user's account\n
    :premium_type: integer - the [type of Nitro subscription](https://discordapp.com/developers/docs/resources/user#user-object-premium-types) on a user's account\n'''
    __slots__ = ("id", "username", "discriminator", "avatar", "bot", "system", "mfa_enabled", "locale", "verified", "email", "flags", "premium_type")
    id: int
    username: str
    discriminator: str
    avatar: str
    bot: bool
    system: bool
    mfa_enabled: bool
    locale: str
    verified: bool
    email: str
    flags: int
    premium_type: int

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.username = data.get('username', None)
        self.discriminator = data.get('discriminator', None)
        self.avatar = data.get('avatar', None)
        self.bot = data.get('bot', False)
        self.system = data.get('system', False)
        self.mfa_enabled = data.get('mfa_enabled', False)
        self.locale = data.get('locale', None)
        self.verified = data.get('verified', False)
        self.email = data.get('email', None)
        self.flags = int(data.get('flags', 0) or 0)
        self.premium_type = int(data.get('premium_type', 0) or 0)


class Connection:
    '''The connection object that the user has attached.

    :id: string - id of the connection account\n
    :name: string - the username of the connection account\n
    :type: string - the service of the connection (twitch, youtube)\n
    :revoked: boolean - whether the connection is revoked\n
    :integrations: array - an array of partial [server integrations](https://discordapp.com/developers/docs/resources/guild#integration-object)\n
    :verified: boolean - whether the connection is verified\n
    :friend_sync: boolean - whether friend sync is enabled for this connection\n
    :show_activity: boolean - whether activities related to this connection will be shown in presence updates\n
    :visibility: integer - [visibility](https://discordapp.com/developers/docs/resources/user#user-object-visibility-types) of this connection\n'''
    __slots__ = ("id", "name", "type", "revoked", "integrations", "verified", "friend_sync", "show_activity", "visibility")
    id: str
    name: str
    type: str
    revoked: bool
    integrations: list
    verified: bool
    friend_sync: bool
    show_activity: bool
    visibility: int

    def __init__(self, data):
        self.id = data.get('id', None)
        self.name = data.get('name', None)
        self.type = data.get('type', None)
        self.revoked = data.get('revoked', False)
        self.integrations = [Integration(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('integrations', [])]
        self.verified = data.get('verified', False)
        self.friend_sync = data.get('friend_sync', False)
        self.show_activity = data.get('show_activity', False)
        self.visibility = int(data.get('visibility', 0) or 0)


class Voice_State:
    '''Used to represent a user's voice connection status.

    :channel_id: snowflake - the channel id this user is connected to\n
    :user_id: snowflake - the user id this voice state is for\n
    :session_id: string - the session id for this voice state\n
    :deaf: boolean - whether this user is deafened by the server\n
    :mute: boolean - whether this user is muted by the server\n
    :self_deaf: boolean - whether this user is locally deafened\n
    :self_mute: boolean - whether this user is locally muted\n
    :suppress: boolean - whether this user is muted by the current user\n
    Optionals:

    :guild_id: snowflake - the guild id this voice state is for\n
    :member: [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) object - the guild member this voice state is for\n
    :self_stream: boolean - whether this user is streaming using "Go Live"\n'''
    __slots__ = ("channel_id", "user_id", "session_id", "deaf", "mute", "self_deaf", "self_mute", "suppress", "guild_id", "member", "self_stream")
    channel_id: int
    user_id: int
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    suppress: bool
    guild_id: int
    member: Guild_Member
    self_stream: bool

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.user_id = int(data.get('user_id', 0) or 0)
        self.session_id = data.get('session_id', None)
        self.deaf = data.get('deaf', False)
        self.mute = data.get('mute', False)
        self.self_deaf = data.get('self_deaf', False)
        self.self_mute = data.get('self_mute', False)
        self.suppress = data.get('suppress', False)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.member = Guild_Member(data.get('member', {}))
        self.self_stream = data.get('self_stream', False)


class Voice_Region:
    '''
    :id: string - unique ID for the region\n
    :name: string - name of the region\n
    :vip: boolean - true if this is a vip-only server\n
    :optimal: boolean - true for a single server that is closest to the current user's client\n
    :deprecated: boolean - whether this is a deprecated voice region (avoid switching to these)\n
    :custom: boolean - whether this is a custom voice region (used for events/etc)\n'''
    __slots__ = ("id", "name", "vip", "optimal", "deprecated", "custom")
    id: str
    name: str
    vip: bool
    optimal: bool
    deprecated: bool
    custom: bool

    def __init__(self, data):
        self.id = data.get('id', None)
        self.name = data.get('name', None)
        self.vip = data.get('vip', False)
        self.optimal = data.get('optimal', False)
        self.deprecated = data.get('deprecated', False)
        self.custom = data.get('custom', False)


class Webhook:
    '''Used to represent a webhook.

    :id: snowflake - the id of the webhook\n
    :type: integer - the [type](https://discordapp.com/developers/docs/resources/webhook#webhook-object-webhook-types) of the webhook\n
    :channel_id: snowflake - the channel id this webhook is for\n
    :name: string - the default name of the webhook\n
    :avatar: string - the default avatar of the webhook\n
    Optionals:

    :guild_id: snowflake - the guild id this webhook is for\n
    :user: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the user this webhook was created by (not returned when getting a webhook with its token)\n
    :token: string - the secure token of the webhook (returned for Incoming Webhooks)\n'''
    __slots__ = ("id", "type", "channel_id", "name", "avatar", "guild_id", "user", "token")
    id: int
    type: int
    channel_id: int
    name: str
    avatar: str
    guild_id: int
    user: User
    token: str

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.type = int(data.get('type', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.name = data.get('name', None)
        self.avatar = data.get('avatar', None)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.user = User(data.get('user', {}))
        self.token = data.get('token', None)


class Gateway_Payload:
    '''
    :op: integer - [opcode](https://discordapp.com/developers/docs/topics/opcodes_and_status_codes#gateway-opcodes) for the payload\n
    :d: mixed (any JSON value) - event data\n
    :s: integer - sequence number, used for resuming sessions and heartbeats\n
    :t: string - the event name for this payload\n'''
    __slots__ = ("op", "d", "s", "t")
    op: int
    d: dict
    s: int
    t: str

    def __init__(self, data):
        self.op = int(data.get('op', 0) or 0)
        self.d = data.get('d', None)
        self.s = int(data.get('s', 0) or 0)
        self.t = data.get('t', None)


class Identify:
    '''
    :token: string - authentication token\n
    :properties: object - [connection properties](https://discordapp.com/developers/docs/topics/gateway#identify-identify-connection-properties)\n
    Optionals:

    :compress: boolean - whether this connection supports compression of packets\n
    :large_threshold: integer - value between 50 and 250, total number of members where the gateway will stop sending offline members in the guild member list\n
    :shard: array of two integers (shard_id, num_shards) - used for [Guild Sharding](https://discordapp.com/developers/docs/topics/gateway#sharding)\n
    :presence: [update status](https://discordapp.com/developers/docs/topics/gateway#update-status) object - presence structure for initial presence information\n
    :guild_subscriptions: boolean - enables dispatching of guild subscription events (presence and typing events)\n
    :intents: integer - the [Gateway Intents](https://discordapp.com/developers/docs/topics/gateway#gateway-intents) you wish to receive\n'''
    __slots__ = ("token", "properties", "compress", "large_threshold", "shard", "presence", "guild_subscriptions", "intents")
    token: str
    properties: object
    compress: bool
    large_threshold: int
    shard: list
    presence: Gateway_Status_Update
    guild_subscriptions: bool
    intents: int

    def __init__(self, data):
        self.token = data.get('token', None)
        self.properties = object(data.get('properties', None))
        self.compress = data.get('compress', False)
        self.large_threshold = int(data.get('large_threshold', 0) or 0)
        self.shard = [i for i in data.get('shard', [])]
        self.presence = Gateway_Status_Update(data.get('presence', {}))
        self.guild_subscriptions = data.get('guild_subscriptions', False)
        self.intents = int(data.get('intents', 0) or 0)


class Resume:
    '''
    :token: string - session token\n
    :session_id: string - session id\n
    :seq: integer - last sequence number received\n'''
    __slots__ = ("token", "session_id", "seq")
    token: str
    session_id: str
    seq: int

    def __init__(self, data):
        self.token = data.get('token', None)
        self.session_id = data.get('session_id', None)
        self.seq = int(data.get('seq', 0) or 0)


class Guild_Request_Members:
    '''
    :guild_id: snowflake or array of snowflakes - id of the guild(s) to get members for\n
    :limit: integer - maximum number of members to send matching the `query`; a limit of `0` can be used with an empty string `query` to return all members\n
    Optionals:

    :query: string - string that username starts with, or an empty string to return all members\n
    :presences: boolean - used to specify if we want the presences of the matched members\n
    :user_ids: snowflake or array of snowflakes - used to specify which users you wish to fetch\n'''
    __slots__ = ("guild_id", "limit", "query", "presences", "user_ids")
    guild_id: int
    limit: int
    query: str
    presences: bool
    user_ids: int

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.limit = int(data.get('limit', 0) or 0)
        self.query = data.get('query', None)
        self.presences = data.get('presences', False)
        self.user_ids = int(data.get('user_ids', 0) or 0)


class Gateway_Voice_State_Update:
    '''
    :guild_id: snowflake - id of the guild\n
    :channel_id: snowflake - id of the voice channel client wants to join (null if disconnecting)\n
    :self_mute: boolean - is the client muted\n
    :self_deaf: boolean - is the client deafened\n'''
    __slots__ = ("guild_id", "channel_id", "self_mute", "self_deaf")
    guild_id: int
    channel_id: int
    self_mute: bool
    self_deaf: bool

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.self_mute = data.get('self_mute', False)
        self.self_deaf = data.get('self_deaf', False)


class Gateway_Status_Update:
    '''
    :since: integer - unix time (in milliseconds) of when the client went idle, or null if the client is not idle\n
    :game: [activity](https://discordapp.com/developers/docs/topics/gateway#activity-object) object - null, or the user's new activity\n
    :status: string - the user's new [status](https://discordapp.com/developers/docs/topics/gateway#update-status-status-types)\n
    :afk: boolean - whether or not the client is afk\n'''
    __slots__ = ("since", "game", "status", "afk")
    since: int
    game: Activity
    status: str
    afk: bool

    def __init__(self, data):
        self.since = int(data.get('since', 0) or 0)
        self.game = Activity(data.get('game', {}))
        self.status = data.get('status', None)
        self.afk = data.get('afk', False)


class Hello:
    '''
    :heartbeat_interval: integer - the interval (in milliseconds) the client should heartbeat with\n'''
    __slots__ = ("heartbeat_interval")
    heartbeat_interval: int

    def __init__(self, data):
        self.heartbeat_interval = int(data.get('heartbeat_interval', 0) or 0)


class Ready:
    '''
    :v: integer - [gateway version](https://discordapp.com/developers/docs/topics/gateway#gateways-gateway-versions)\n
    :user: [user](https://discordapp.com/developers/docs/resources/user#user-object) object - information about the user including email\n
    :private_channels: array - empty array\n
    :guilds: array of [Unavailable Guild](https://discordapp.com/developers/docs/resources/guild#unavailable-guild-object) objects - the guilds the user is in\n
    :session_id: string - used for resuming connections\n
    Optionals:

    :shard: array of two integers (shard_id, num_shards) - the [shard information](https://discordapp.com/developers/docs/topics/gateway#sharding) associated with this session, if sent when identifying\n'''
    __slots__ = ("v", "user", "private_channels", "guilds", "session_id", "shard")
    v: int
    user: User
    private_channels: list
    guilds: list
    session_id: str
    shard: list

    def __init__(self, data):
        self.v = int(data.get('v', 0) or 0)
        self.user = User(data.get('user', {}))
        self.private_channels = [i for i in data.get('private_channels', [])]
        self.guilds = [i for i in data.get('guilds', [])]
        self.session_id = data.get('session_id', None)
        self.shard = [i for i in data.get('shard', [])]


class Channel_Pins_Update:
    '''
    :channel_id: snowflake - the id of the channel\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n
    :last_pin_timestamp: ISO8601 timestamp - the time at which the most recent pinned message was pinned\n'''
    __slots__ = ("channel_id", "guild_id", "last_pin_timestamp")
    channel_id: int
    guild_id: int
    last_pin_timestamp: datetime.datetime

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.last_pin_timestamp = data.get('last_pin_timestamp', None)


class Guild_Ban_Add:
    '''
    :guild_id: snowflake - id of the guild\n
    :user: a [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the banned user\n'''
    __slots__ = ("guild_id", "user")
    guild_id: int
    user: User

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.user = User(data.get('user', {}))


class Guild_Ban_Remove:
    '''
    :guild_id: snowflake - id of the guild\n
    :user: a [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the unbanned user\n'''
    __slots__ = ("guild_id", "user")
    guild_id: int
    user: User

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.user = User(data.get('user', {}))


class Guild_Emojis_Update:
    '''
    :guild_id: snowflake - id of the guild\n
    :emojis: array - array of [emojis](https://discordapp.com/developers/docs/resources/emoji#emoji-object)\n'''
    __slots__ = ("guild_id", "emojis")
    guild_id: int
    emojis: list

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.emojis = [i for i in data.get('emojis', [])]


class Guild_Integrations_Update:
    '''
    :guild_id: snowflake - id of the guild whose integrations were updated\n'''
    __slots__ = ("guild_id")
    guild_id: int

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Guild_Member_Remove:
    '''
    :guild_id: snowflake - the id of the guild\n
    :user: a [user](https://discordapp.com/developers/docs/resources/user#user-object) object - the user who was removed\n'''
    __slots__ = ("guild_id", "user")
    guild_id: int
    user: User

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.user = User(data.get('user', {}))


class Guild_Member_Update:
    '''
    :guild_id: snowflake - the id of the guild\n
    :roles: array of snowflakes - user role ids\n
    :user: a [user](https:#/discordapp.com/developers/docs/resources/user#user-object) object - the user\n
    :nick: string - nickname of the user in the guild\n
    :premium_since: ISO8601 timestamp - when the user starting [boosting](https:#/support.discordapp.com/hc/en-us/articles/360028038352-Server-Boosting-) the guild\n'''
    __slots__ = ("guild_id", "roles", "user", "nick", "premium_since")
    guild_id: int
    roles: list
    user: User
    nick: str
    premium_since: datetime.datetime

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.roles = [int(i or 0) for i in data.get('roles', [])]
        self.user = User(data.get('user', {}))
        self.nick = data.get('nick', None)
        self.premium_since = data.get('premium_since', None)


class Guild_Members_Chunk:
    '''
    :guild_id: snowflake - the id of the guild\n
    :members: array of [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) objects - set of guild members\n
    Optionals:

    :not_found: array - if passing an invalid id to `REQUEST_GUILD_MEMBERS`, it will be returned here\n
    :presences: array of [presence](https://discordapp.com/developers/docs/topics/gateway#presence) objects - if passing true to `REQUEST_GUILD_MEMBERS`, presences of the returned members will be here\n'''
    __slots__ = ("guild_id", "members", "not_found", "presences")
    guild_id: int
    members: list
    not_found: list
    presences: list

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.members = [Guild_Member(i) for i in data.get('members', [])]
        self.not_found = [i for i in data.get('not_found', [])]
        self.presences = [i for i in data.get('presences', [])]


class Guild_Role_Create:
    '''
    :guild_id: snowflake - the id of the guild\n
    :role: a [role](https://discordapp.com/developers/docs/topics/permissions#role-object) object - the role created\n'''
    __slots__ = ("guild_id", "role")
    guild_id: int
    role: Role

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.role = Role(data.get('role', {}))


class Guild_Role_Update:
    '''
    :guild_id: snowflake - the id of the guild\n
    :role: a [role](https://discordapp.com/developers/docs/topics/permissions#role-object) object - the role updated\n'''
    __slots__ = ("guild_id", "role")
    guild_id: int
    role: Role

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.role = Role(data.get('role', {}))


class Guild_Role_Delete:
    '''
    :guild_id: snowflake - id of the guild\n
    :role_id: snowflake - id of the role\n'''
    __slots__ = ("guild_id", "role_id")
    guild_id: int
    role_id: int

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.role_id = int(data.get('role_id', 0) or 0)


class Invite_Create:
    '''
    :channel_id: snowflake - the channel the invite is for\n
    :code: string - the unique invite [code](https://discordapp.com/developers/docs/resources/invite#invite-object)\n
    :created_at: timestamp - the time at which the invite was created\n
    :max_age: int - how long the invite is valid for (in seconds)\n
    :max_uses: int - the maximum number of times the invite can be used\n
    :temporary: boolean - whether or not the invite is temporary (invited users will be kicked on disconnect unless they're assigned a role)\n
    :uses: int - how many times the invite has been used (always will be 0)\n
    Optionals:

    :guild_id: snowflake - the guild of the invite\n
    :inviter: [user object](https://discordapp.com/developers/docs/resources/user#user-object) - the user that created the invite\n'''
    __slots__ = ("channel_id", "code", "created_at", "max_age", "max_uses", "temporary", "uses", "guild_id", "inviter")
    channel_id: int
    code: str
    created_at: datetime.datetime
    max_age: int
    max_uses: int
    temporary: bool
    uses: int
    guild_id: int
    inviter: User

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.code = data.get('code', None)
        self.created_at = data.get('created_at', None)
        self.max_age = int(data.get('max_age', 0) or 0)
        self.max_uses = int(data.get('max_uses', 0) or 0)
        self.temporary = data.get('temporary', False)
        self.uses = int(data.get('uses', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.inviter = User(data.get('inviter', {}))


class Invite_Delete:
    '''
    :channel_id: snowflake - the channel of the invite\n
    :code: string - the unique invite [code](https://discordapp.com/developers/docs/resources/invite#invite-object)\n
    Optionals:

    :guild_id: snowflake - the guild of the invite\n'''
    __slots__ = ("channel_id", "code", "guild_id")
    channel_id: int
    code: str
    guild_id: int

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.code = data.get('code', None)
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Message_Delete:
    '''
    :id: snowflake - the id of the message\n
    :channel_id: snowflake - the id of the channel\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n'''
    __slots__ = ("id", "channel_id", "guild_id")
    id: int
    channel_id: int
    guild_id: int

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Message_Delete_Bulk:
    '''
    :ids: array of snowflakes - the ids of the messages\n
    :channel_id: snowflake - the id of the channel\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n'''
    __slots__ = ("ids", "channel_id", "guild_id")
    ids: list
    channel_id: int
    guild_id: int

    def __init__(self, data):
        self.ids = [int(i or 0) for i in data.get('ids', [])]
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Message_Reaction_Add:
    '''
    :user_id: snowflake - the id of the user\n
    :channel_id: snowflake - the id of the channel\n
    :message_id: snowflake - the id of the message\n
    :emoji: a partial [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) object - the emoji used to react - [example](https://discordapp.com/developers/docs/resources/emoji#emoji-object-gateway-reaction-standard-emoji-example)\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n
    :member: [member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) object - the member who reacted if this happened in a guild\n'''
    __slots__ = ("user_id", "channel_id", "message_id", "emoji", "guild_id", "member")
    user_id: int
    channel_id: int
    message_id: int
    emoji: Emoji
    guild_id: int
    member: Guild_Member

    def __init__(self, data):
        self.user_id = int(data.get('user_id', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.message_id = int(data.get('message_id', 0) or 0)
        self.emoji = Emoji(data.get('emoji', {}))
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.member = Guild_Member(data.get('member', {}))


class Message_Reaction_Remove:
    '''
    :user_id: snowflake - the id of the user\n
    :channel_id: snowflake - the id of the channel\n
    :message_id: snowflake - the id of the message\n
    :emoji: a partial [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) object - the emoji used to react - [example](https://discordapp.com/developers/docs/resources/emoji#emoji-object-gateway-reaction-standard-emoji-example)\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n'''
    __slots__ = ("user_id", "channel_id", "message_id", "emoji", "guild_id")
    user_id: int
    channel_id: int
    message_id: int
    emoji: Emoji
    guild_id: int

    def __init__(self, data):
        self.user_id = int(data.get('user_id', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.message_id = int(data.get('message_id', 0) or 0)
        self.emoji = Emoji(data.get('emoji', {}))
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Message_Reaction_Remove_All:
    '''
    :channel_id: snowflake - the id of the channel\n
    :message_id: snowflake - the id of the message\n
    Optionals:

    :guild_id: snowflake - the id of the guild\n'''
    __slots__ = ("channel_id", "message_id", "guild_id")
    channel_id: int
    message_id: int
    guild_id: int

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.message_id = int(data.get('message_id', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)


class Presence_Update:
    '''
    :user: [user](https:#/discordapp.com/developers/docs/resources/user#user-object) object - the user presence is being updated for\n
    :roles: array of snowflakes - roles this user is in\n
    :game: [activity](https:#/discordapp.com/developers/docs/topics/gateway#activity-object) object - null, or the user's current activity\n
    :guild_id: snowflake - id of the guild\n
    :status: string - either "idle", "dnd", "online", or "offline"\n
    :activities: array of [activity](https:#/discordapp.com/developers/docs/topics/gateway#activity-object) objects - user's current activities\n
    :client_status: [client_status](https:#/discordapp.com/developers/docs/topics/gateway#client-status-object) object - user's platform-dependent status\n
    Optionals:

    :premium_since: ISO8601 timestamp - when the user started [boosting](https:#/support.discordapp.com/hc/en-us/articles/360028038352-Server-Boosting-) the guild\n
    :nick: string - this users guild nickname (if one is set)\n'''
    __slots__ = ("user", "roles", "game", "guild_id", "status", "activities", "client_status", "premium_since", "nick")
    user: User
    roles: list
    game: Activity
    guild_id: int
    status: str
    activities: list
    client_status: Gateway_Status_Update
    premium_since: datetime.datetime
    nick: str

    def __init__(self, data):
        self.user = User(data.get('user', {}))
        self.roles = [int(i or 0) for i in data.get('roles', [])]
        self.game = Activity(data.get('game') or {})
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.status = data.get('status', None)
        self.activities = [Activity(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in data.get('activities', [])]
        self.client_status = data.get('client_status',{})#Gateway_Status_Update(data.get('client_status', {}))
        self.premium_since = data.get('premium_since', None)
        self.nick = data.get('nick', None)


class Activity:
    '''
    :name: string - the activity's name\n
    :type: integer - [activity type](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-types)\n
    :created_at: int - unix timestamp of when the activity was added to the user's session\n
    Optionals:

    :url: string - stream url, is validated when type is 1\n
    :timestamps: [timestamps](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-timestamps) object - unix timestamps for start and/or end of the game\n
    :application_id: snowflake - application id for the game\n
    :details: string - what the player is currently doing\n
    :state: string - the user's current party status\n
    :emoji: [emoji](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-emoji) object - the emoji used for a custom status\n
    :party: [party](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-party) object - information for the current party of the player\n
    :assets: [assets](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-assets) object - images for the presence and their hover texts\n
    :secrets: [secrets](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-secrets) object - secrets for Rich Presence joining and spectating\n
    :instance: boolean - whether or not the activity is an instanced game session\n
    :flags: int - [activity flags](https://discordapp.com/developers/docs/topics/gateway#activity-object-activity-flags) `OR`d together, describes what the payload includes\n'''
    __slots__ = ("name", "type", "created_at", "url", "timestamps", "application_id", "details", "state", "emoji", "party", "assets", "secrets", "instance", "flags")
    name: str
    type: int
    created_at: int
    url: str
    timestamps: datetime.datetime
    application_id: int
    details: str
    state: str
    emoji: Activity_Emoji
    party: Activity_Party
    assets: Activity_Assets
    secrets: Activity_Secrets
    instance: bool
    flags: int

    def __init__(self, data):
        self.name = data.get('name', None)
        self.type = int(data.get('type', 0) or 0)
        self.created_at = int(data.get('created_at', 0) or 0)
        self.url = data.get('url', None)
        self.timestamps = data.get('timestamps', None)
        self.application_id = int(data.get('application_id', 0) or 0)
        self.details = data.get('details', None)
        self.state = data.get('state', None)
        self.emoji = Activity_Emoji(data.get('emoji', {}))
        self.party = Activity_Party(data.get('party', {}))
        self.assets = Activity_Assets(data.get('assets', {}))
        self.secrets = Activity_Secrets(data.get('secrets', {}))
        self.instance = data.get('instance', False)
        self.flags = int(data.get('flags', 0) or 0)


class Activity_Timestamps:
    '''
    Optionals:

    :start: int - unix time (in milliseconds) of when the activity started\n
    :end: int - unix time (in milliseconds) of when the activity ends\n'''
    __slots__ = ("start", "end")
    start: int
    end: int

    def __init__(self, data):
        self.start = int(data.get('start', 0) or 0)
        self.end = int(data.get('end', 0) or 0)


class Activity_Emoji:
    '''
    :name: string - the name of the emoji\n
    Optionals:

    :id: snowflake - the id of the emoji\n
    :animated: boolean - whether this emoji is animated\n'''
    __slots__ = ("name", "id", "animated")
    name: str
    id: int
    animated: bool

    def __init__(self, data):
        self.name = data.get('name', None)
        self.id = int(data.get('id', 0) or 0)
        self.animated = data.get('animated', False)


class Activity_Party:
    '''
    Optionals:

    :id: string - the id of the party\n
    :size: array of two integers (current_size, max_size) - used to show the party's current and maximum size\n'''
    __slots__ = ("id", "size")
    id: str
    size: list

    def __init__(self, data):
        self.id = data.get('id', None)
        self.size = [i for i in data.get('size', [])]


class Activity_Assets:
    '''
    Optionals:

    :large_image: string - the id for a large asset of the activity, usually a snowflake\n
    :large_text: string - text displayed when hovering over the large image of the activity\n
    :small_image: string - the id for a small asset of the activity, usually a snowflake\n
    :small_text: string - text displayed when hovering over the small image of the activity\n'''
    __slots__ = ("large_image", "large_text", "small_image", "small_text")
    large_image: str
    large_text: str
    small_image: str
    small_text: str

    def __init__(self, data):
        self.large_image = data.get('large_image', None)
        self.large_text = data.get('large_text', None)
        self.small_image = data.get('small_image', None)
        self.small_text = data.get('small_text', None)


class Activity_Secrets:
    '''
    Optionals:

    :join: string - the secret for joining a party\n
    :spectate: string - the secret for spectating a game\n
    :match: string - the secret for a specific instanced match\n'''
    __slots__ = ("join", "spectate", "match")
    join: str
    spectate: str
    match: str

    def __init__(self, data):
        self.join = data.get('join', None)
        self.spectate = data.get('spectate', None)
        self.match = data.get('match', None)


class Typing_Start:
    '''
    :channel_id: snowflake - id of the channel\n
    :user_id: snowflake - id of the user\n
    :timestamp: integer - unix time (in seconds) of when the user started typing\n
    Optionals:

    :guild_id: snowflake - id of the guild\n
    :member: [member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) object - the member who started typing if this happened in a guild\n'''
    __slots__ = ("channel_id", "user_id", "timestamp", "guild_id", "member")
    channel_id: int
    user_id: int
    timestamp: int
    guild_id: int
    member: Guild_Member

    def __init__(self, data):
        self.channel_id = int(data.get('channel_id', 0) or 0)
        self.user_id = int(data.get('user_id', 0) or 0)
        self.timestamp = int(data.get('timestamp', 0) or 0)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.member = Guild_Member(data.get('member', {}))


class Voice_Server_Update:
    '''
    :token: string - voice connection token\n
    :guild_id: snowflake - the guild this voice server update is for\n
    :endpoint: string - the voice server host\n'''
    __slots__ = ("token", "guild_id", "endpoint")
    token: str
    guild_id: int
    endpoint: str

    def __init__(self, data):
        self.token = data.get('token', None)
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.endpoint = data.get('endpoint', None)


class Webhook_Update:
    '''
    :guild_id: snowflake - id of the guild\n
    :channel_id: snowflake - id of the channel\n'''
    __slots__ = ("guild_id", "channel_id")
    guild_id: int
    channel_id: int

    def __init__(self, data):
        self.guild_id = int(data.get('guild_id', 0) or 0)
        self.channel_id = int(data.get('channel_id', 0) or 0)


class Role:
    '''Roles represent a set of permissions attached to a group of users.
    Roles have unique names, colors, and can be "pinned" to the side bar, causing their members to be listed separately.
    Roles are unique per guild, and can have separate permission profiles for the global context (guild) and channel context.
    The `@everyone` role has the same ID as the guild it belongs to.

    :id: snowflake - role id\n
    :name: string - role name\n
    :color: integer - integer representation of hexadecimal color code\n
    :hoist: boolean - if this role is pinned in the user listing\n
    :position: integer - position of this role\n
    :permissions: integer - permission bit set\n
    :managed: boolean - whether this role is managed by an integration\n
    :mentionable: boolean - whether this role is mentionable\n'''
    __slots__ = ("id", "name", "color", "hoist", "position", "permissions", "managed", "mentionable")
    id: int
    name: str
    color: int
    hoist: bool
    position: int
    permissions: int
    managed: bool
    mentionable: bool

    def __init__(self, data):
        self.id = int(data.get('id', 0) or 0)
        self.name = data.get('name', None)
        self.color = int(data.get('color', 0) or 0)
        self.hoist = data.get('hoist', False)
        self.position = int(data.get('position', 0) or 0)
        self.permissions = int(data.get('permissions', 0) or 0)
        self.managed = data.get('managed', False)
        self.mentionable = data.get('mentionable', False)


class Rate_Limit_Response:
    '''
    :message: string - A message saying you are being rate limited.\n
    :retry_after: integer - The number of milliseconds to wait before submitting another request.\n
    :global: boolean - A value indicating if you are being globally rate limited or not\n'''
    __slots__ = ("message", "retry_after", "global")
    message: str
    retry_after: int
    global_: bool

    def __init__(self, data):
        self.message = data.get('message', None)
        self.retry_after = int(data.get('retry_after', 0) or 0)
        self.global_ = data.get('global', False)


class Voice_Packet:
    '''
    :Version_Flags: Single byte value of `0x80` - 1 byte\n
    :PayloadType: Single byte value of `0x78` - 1 byte\n
    :Sequence: Unsigned short (big endian) - 2 bytes\n
    :Timestamp: Unsigned integer (big endian) - 4 bytes\n
    :SSRC: Unsigned integer (big endian) - 4 bytes\n
    :Encryptedaudio: Binary data - n bytes\n'''
    __slots__ = ("Version_Flags", "PayloadType", "Sequence", "Timestamp", "SSRC", "Encryptedaudio")
    Version_Flags: bytes
    PayloadType: bytes
    Sequence: int
    Timestamp: int
    SSRC: int
    Encryptedaudio: bytes

    def __init__(self, data):
        self.Version_Flags = bytes(data.get('Version_Flags', None))
        self.PayloadType = bytes(data.get('PayloadType', None))
        self.Sequence = int(data.get('Sequence', 0) or 0)
        self.Timestamp = int(data.get('Timestamp', 0) or 0)
        self.SSRC = int(data.get('SSRC', 0) or 0)
        self.Encryptedaudio = bytes(data.get('Encryptedaudio', None))
