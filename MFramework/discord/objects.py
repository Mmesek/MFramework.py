# -*- coding: utf-8 -*-
'''
Discord Objects & Endpoints
----------

Discord API types & api endpoint call functions.

:copyright: (c) 2020 Mmesek

'''

#Generated structure from docs at 11:48 2020/12/23
#Generated source code at 11:48 2020/12/23
from __future__ import annotations
from enum import Enum, Flag, IntEnum
from typing import List, Optional
from datetime import datetime
from ctypes import c_byte, c_uint, c_ushort
from dataclasses import dataclass, is_dataclass, asdict, fields
# HACK: add `+ ["**kwargs"]` to a second argument for _create_fn in _init_fn to allow additional arguments in auto generated constructors 

DISCORD_EPOCH = 1420070400000
BASE_URL = "https://discord.com/api"
CDN_URL = "https://cdn.discordapp.com/"

class Snowflake(int):
    _value: int = 0
    def __new__(cls, value=0):
        return super(cls, cls).__new__(cls, value)
    def __init__(self, value=0):
        self._value = int(value)
#    def __class_getitem__(cls, key='value'):
#        return cls._value
    @property
    def as_date(self):
        ms = ((self._value >> 22)+DISCORD_EPOCH)
        return datetime.utcfromtimestamp(ms//1000.0).replace(microsecond=ms % 1000*1000)

class UserID(Snowflake):
    pass

class ChannelID(Snowflake):
    pass

class RoleID(Snowflake):
    pass

class Enum(Enum):
    def __str__(self):
        return str(self.name)
    def by_str(self, value):
        return self.value
    def __lt__(self, other):
        return self.value < other.value

class Events(Enum):
    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

@dataclass
class DiscordObject:
    _Client: Optional[Bot] = None
    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
    def __post_init__(self):
        for field in self.__dict__:
            if field == '_Client':
                continue
            __type = self.__annotations__.get(field) or type(self).__bases__[0].__annotations__.get(field)
            value = getattr(self, field)
            if value is None or type(value) not in [int, str, bool, type, list, dict]:
                continue
            _type = __type.replace('List[', '').replace(']', '')
            is_basic = _type in ['int', 'str', 'Snowflake', 'bool', 'datatime']
            types = {
                "int": int,
                "bool": bool,
                "str": str
            }
            _type = types.get(_type, globals().get(_type))
            if _type is None:
                continue
            elif value is list:
                #continue
                self.__setattr__(field, [])
            elif 'List' in __type:
                try:
                    if issubclass(_type, Enum):
                        self.__setattr__(field, [getattr(_type, i, i) for i in value if i])
                    else:
                        self.__setattr__(field, [_type(**i if not is_basic and not is_dataclass(i) else i or None) for i in value or []])
                except:
                    self.__setattr__(field, [_type(i) if type(i) is not _type else i for i in value or []])            
            elif _type is datetime:
                self.__setattr__(field, _type.fromisoformat(value) if value else _type.now())
            else:
                if type(value) is dict:
                    self.__setattr__(field, _type(**value if value is not None else value or None))
                elif issubclass(_type, Flag):
                    _flags = []
                    for _flag in _type:
                        if value & _flag.value == 0:
                            _flags.append(_flag)
                    self.__setattr__(field, _flags)
                else:
                    self.__setattr__(field, _type(value or (0 if _type is not str else '')))
    @property
    def as_dict(self):
        _dict = asdict(self)
        for field in _dict:
            if field == '_Client':
                continue
            if is_dataclass(_dict.get(field)):
                _dict[field] = asdict(_dict.get(field))
            else:
                _dict[field] = as_dict(_dict.get(field))
        _dict.pop("_Client")
        return _dict

def dataclass_from_dict(klass, dikt):
    try:
        types = {
            "int": int,
            "bool": bool,
            "str": str
        }
        fieldtypes = {}
        for f in fields(klass):
            _type = f.type
            is_list = False
            if 'List' in f.type:
                _type = f.type.replace('List[', '').replace(']', '')
                is_list = True
            _type = types.get(_type, globals().get(_type))
            if is_list:
                fieldtypes[f.name] = (list, _type)
            else:
                fieldtypes[f.name] = _type
        #fieldtypes = {f.name:types.get(f.type, globals().get(f.type)) if 'List' not in f.type else (list, f.type.replace('List[', '').replace(']', '')) for f in fields(klass)}
        #fieldtypes = {f.name:types.get(f.type, globals().get(f.type)) for f in fields(klass)}
        _dict = {}
        for f in dikt:
            if f not in fieldtypes:
                continue
            if type(fieldtypes[f]) is tuple:
                _dict[f] = [dataclass_from_dict(fieldtypes[f][1], i) for i in dikt[f]]
            else:
                _dict[f] = dataclass_from_dict(fieldtypes[f], dikt[f])
        return klass(**_dict)
        #return klass(**{f:dataclass_from_dict(fieldtypes[f],dikt[f]) for f in dikt if f in fieldtypes})
    except Exception as ex:
        #print(ex)
        return dikt

def as_dict(object):
    if type(object) is dict:
        _object = {}
        for key in object:
            if key != '_Client':
                _object[key] = as_dict(object[key])
        return _object
    elif type(object) is list:
        return [as_dict(key) for key in object]
    elif is_dataclass(object):
        return object.as_dict
    elif isinstance(object, datetime):
        return object.isoformat()
    elif isinstance(object, Enum):
        return object.value
    return object

class Insufficient_Permissions(Exception):
    pass

def Permissions(*permissions):
    def inner(f):
        def wrapped(Client, *args, **kwargs):
            for permission in permissions:
                if not Bitwise_Permission_Flags.check(Client.bot.permissions, getattr(Bitwise_Permission_Flags, permission)):
                    raise Insufficient_Permissions(*permissions)
            return f(Client, *args, **kwargs)
        return wrapped #Why was it returning f instead of wrapped before?
    return inner

@dataclass
class Audit_Log(DiscordObject):
    '''
    Params:
        :webhooks: list of webhooks found in the audit log
        :users: list of users found in the audit log
        :audit_log_entries: list of audit log entries
        :integrations: list of  integration s
    '''
    webhooks: List[Webhook] = list
    users: List[User] = list
    audit_log_entries: List[Audit_Log_Entry] = list
    integrations: List[Integration] = list


@dataclass
class Audit_Log_Entry(DiscordObject):
    '''
    Params:
        :target_id: id of the affected entity
        :changes: changes made to the target_id
        :user_id: the user who made the changes
        :id: id of the entry
        :action_type: type of action that occurred
        :options: additional info for certain action types
        :reason: the reason for the change
    '''
    target_id: str = ''
    changes: List[Audit_Log_Change] = list
    user_id: Snowflake = 0
    id: Snowflake = 0
    action_type: Audit_Log_Events = None
    options: Optional_Audit_Entry_Info = None
    reason: str = ''


class Audit_Log_Events(Enum):
    GUILD_UPDATE = 1
    CHANNEL_CREATE = 10
    CHANNEL_UPDATE = 11
    CHANNEL_DELETE = 12
    CHANNEL_OVERWRITE_CREATE = 13
    CHANNEL_OVERWRITE_UPDATE = 14
    CHANNEL_OVERWRITE_DELETE = 15
    MEMBER_KICK = 20
    MEMBER_PRUNE = 21
    MEMBER_BAN_ADD = 22
    MEMBER_BAN_REMOVE = 23
    MEMBER_UPDATE = 24
    MEMBER_ROLE_UPDATE = 25
    MEMBER_MOVE = 26
    MEMBER_DISCONNECT = 27
    BOT_ADD = 28
    ROLE_CREATE = 30
    ROLE_UPDATE = 31
    ROLE_DELETE = 32
    INVITE_CREATE = 40
    INVITE_UPDATE = 41
    INVITE_DELETE = 42
    WEBHOOK_CREATE = 50
    WEBHOOK_UPDATE = 51
    WEBHOOK_DELETE = 52
    EMOJI_CREATE = 60
    EMOJI_UPDATE = 61
    EMOJI_DELETE = 62
    MESSAGE_DELETE = 72
    MESSAGE_BULK_DELETE = 73
    MESSAGE_PIN = 74
    MESSAGE_UNPIN = 75
    INTEGRATION_CREATE = 80
    INTEGRATION_UPDATE = 81
    INTEGRATION_DELETE = 82


@dataclass
class Optional_Audit_Entry_Info(DiscordObject):
    '''
    Params:
        :delete_member_days: number of days after which inactive members were kicked
        :members_removed: number of members removed by the prune
        :channel_id: channel in which the entities were targeted
        :message_id: id of the message that was targeted
        :count: number of entities that were targeted
        :id: id of the overwritten entity
        :type: type of overwritten entity - "0" for "role"
        :role_name: name of the role if type is "0"
    '''
    delete_member_days: str = ''
    members_removed: str = ''
    channel_id: Snowflake = 0
    message_id: Snowflake = 0
    count: str = ''
    id: Snowflake = 0
    type: str = ''
    role_name: str = ''


@dataclass
class Audit_Log_Change(DiscordObject):
    '''
    Params:
        :new_value: new value of the key
        :old_value: old value of the key
        :key: Change_Key
    '''
    new_value: dict = dict
    old_value: dict = dict
    key: str = ''


@dataclass
class Audit_Log_Change_Key(DiscordObject):
    '''
    Params:
        :name: name changed
        :icon_hash: icon changed
        :splash_hash: invite splash page artwork changed
        :owner_id: owner changed
        :region: region changed
        :afk_channel_id: afk channel changed
        :afk_timeout: afk timeout duration changed
        :mfa_level: two-factor auth requirement changed
        :verification_level: required verification level changed
        :explicit_content_filter: Whose_Messages
        :default_message_notifications: Message_Notification_Level
        :vanity_url_code: guild invite vanity url changed
        :$add: new role added
        :$remove: role removed
        :prune_delete_days: change in number of days after which inactive and role-unassigned members are kicked
        :widget_enabled: server widget enabled/disable
        :widget_channel_id: channel id of the server widget changed
        :system_channel_id: id of the system channel changed
        :position: text
        :topic: text channel topic changed
        :bitrate: voice channel bitrate changed
        :permission_overwrites: permissions on a channel changed
        :nsfw: channel nsfw restriction changed
        :application_id: application id of the added
        :rate_limit_per_user: amount of seconds a user has to wait before sending another message changed
        :permissions: Permissions
        :color: role color changed
        :hoist: role is now displayed/no longer displayed separate from online users
        :mentionable: role is now mentionable/unmentionable
        :allow: a permission on a text
        :deny: a permission on a text
        :code: invite code changed
        :channel_id: channel for invite code changed
        :inviter_id: person who created invite code changed
        :max_uses: change to max number of times invite code can be used
        :uses: number of times invite code used changed
        :max_age: how long invite code lasts changed
        :temporary: invite code is temporary/never expires
        :deaf: user server deafened/undeafened
        :mute: user server muted/unmuted
        :nick: user nickname changed
        :avatar_hash: user avatar changed
        :id: the id of the changed entity - sometimes used in conjunction with other keys
        :type: type of entity created
        :enable_emoticons: integration emoticons enabled/disabled
        :expire_behavior: integration expiring subscriber behavior changed
        :expire_grace_period: integration expire grace period changed
    '''
    name: str = ''
    icon_hash: str = ''
    splash_hash: str = ''
    owner_id: Snowflake = 0
    region: str = ''
    afk_channel_id: Snowflake = 0
    afk_timeout: int = 0
    mfa_level: int = 0
    verification_level: int = 0
    explicit_content_filter: int = 0
    default_message_notifications: int = 0
    vanity_url_code: str = ''
    add: List[Role] = list
    remove: List[Role] = list
    prune_delete_days: int = 0
    widget_enabled: bool = False
    widget_channel_id: Snowflake = 0
    system_channel_id: Snowflake = 0
    position: int = 0
    topic: str = ''
    bitrate: int = 0
    permission_overwrites: List[Overwrite] = list
    nsfw: bool = False
    application_id: Snowflake = 0
    rate_limit_per_user: int = 0
    permissions: str = ''
    color: int = 0
    hoist: bool = False
    mentionable: bool = False
    allow: str = ''
    deny: str = ''
    code: str = ''
    channel_id: Snowflake = 0
    inviter_id: Snowflake = 0
    max_uses: int = 0
    uses: int = 0
    max_age: int = 0
    temporary: bool = False
    deaf: bool = False
    mute: bool = False
    nick: str = ''
    avatar_hash: str = ''
    id: Snowflake = 0
    type: Channel_Types = None
    enable_emoticons: bool = False
    expire_behavior: int = 0
    expire_grace_period: int = 0


@dataclass
class Channel(DiscordObject):
    '''
    Params:
        :id: the id of this channel
        :type: Type_Of_Channel
        :guild_id: the id of the guild
        :position: sorting position of the channel
        :permission_overwrites: explicit permission overwrites for members and roles
        :name: the name of the channel
        :topic: the channel topic
        :nsfw: whether the channel is nsfw
        :last_message_id: the id of the last message sent in this channel
        :bitrate: the bitrate
        :user_limit: the user limit of the voice channel
        :rate_limit_per_user: amount of seconds a user has to wait before sending another message
        :recipients: the recipients of the DM
        :icon: icon hash
        :owner_id: id of the DM creator
        :application_id: application id of the group DM creator if it is bot-created
        :parent_id: id of the parent category for a channel
        :last_pin_timestamp: when the last pinned message was pinned. This may be `null` in events such as `GUILD_CREATE` when a message is not pinned.
    '''
    id: Snowflake = 0
    type: int = 0
    guild_id: Snowflake = 0
    position: int = 0
    permission_overwrites: List[Overwrite] = list
    name: str = ''
    topic: str = ''
    nsfw: bool = False
    last_message_id: Snowflake = 0
    bitrate: int = 0
    user_limit: int = 0
    rate_limit_per_user: int = 0
    recipients: List[User] = None
    icon: str = ''
    owner_id: Snowflake = 0
    application_id: Snowflake = 0
    parent_id: Snowflake = 0
    last_pin_timestamp: datetime = datetime.now().isoformat()


class Channel_Types(Enum):
    '''
    Params:
        :GUILD_TEXT: a text channel within a server
        :DM: a direct message between users
        :GUILD_VOICE: a voice channel within a server
        :GROUP_DM: a direct message between multiple users
        :GUILD_CATEGORY: Organizational_Category
        :GUILD_NEWS: Users_Can_Follow_And_Crosspost_Into_Their_Own_Server
        :GUILD_STORE: Sell_Their_Game_On_Discord
    '''
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


@dataclass
class Message(DiscordObject):
    '''
    * The author object follows the structure of the user object, but is only a valid user in the case where the message is generated by a user or bot user. If the message is generated by a webhook, the author object corresponds to the webhook's id, username, and avatar. You can tell if a message is generated by a webhook by checking for the `webhook_id` on the message object.
    ** The member object exists in [MESSAGE_CREATE](#DOCS_TOPICS_GATEWAY/message-create) and [MESSAGE_UPDATE](#DOCS_TOPICS_GATEWAY/message-update) events from text-based guild channels. This allows bots to obtain real-time member data without requiring bots to store member state in memory.
    *** The user objects in the mentions array will only have the partial `member` field present in [MESSAGE_CREATE](#DOCS_TOPICS_GATEWAY/message-create) and [MESSAGE_UPDATE](#DOCS_TOPICS_GATEWAY/message-update) events from text-based guild channels.
    **** Not all channel mentions in a message will appear in `mention_channels`. Only textual channels that are visible to everyone in a lurkable guild will ever be included. Only crossposted messages (via Channel Following) currently include `mention_channels` at all. If no mentions in the message meet these requirements, this field will not be sent.
    ***** This field is only returned for messages with a `type` of `19` (REPLY). If the message is a reply but the `referenced_message` field is not present, the backend did not attempt to fetch the message that was being replied to, so its state is unknown. If the field exists but is null, the referenced message was deleted.
    
    Params:
        :id: id of the message
        :channel_id: id of the channel the message was sent in
        :guild_id: id of the guild the message was sent in
        :author: the author of this message
        :member: member properties for this message's author
        :content: contents of the message
        :timestamp: when this message was sent
        :edited_timestamp: when this message was edited
        :tts: whether this was a TTS message
        :mention_everyone: whether this message mentions everyone
        :mentions: users specifically mentioned in the message
        :mention_roles: roles specifically mentioned in this message
        :mention_channels: channels specifically mentioned in this message
        :attachments: any attached files
        :embeds: any embedded content
        :reactions: reactions to the message
        :nonce: used for validating a message was sent
        :pinned: whether this message is pinned
        :webhook_id: if the message is generated by a webhook, this is the webhook's id
        :type: Type_Of_Message
        :activity: sent with Rich Presence-related chat embeds
        :application: sent with Rich Presence-related chat embeds
        :message_reference: reference data sent with crossposted messages and replies
        :flags: Message_Flags
        :stickers: the stickers sent with the message
        :referenced_message: the message associated with the message_reference
    '''
    id: Snowflake = 0
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0
    author: User = None
    member: Guild_Member = None
    content: str = ""
    timestamp: datetime = datetime.now().isoformat()
    edited_timestamp: datetime = datetime.now().isoformat()
    tts: bool = False
    mention_everyone: bool = False
    mentions: List[User] = list
    mention_roles: List[Role] = list
    mention_channels: List[Channel_Mention] = list
    attachments: List[Attachment] = list
    embeds: List[Embed] = list
    reactions: List[Reaction] = list
    nonce: int = 0
    pinned: bool = False
    webhook_id: Snowflake = 0
    type: int = 0
    activity: Message_Activity = None
    application: Message_Application = None
    message_reference: Message_Reference = None
    flags: int = 0
    stickers: List[Message_Sticker] = list
    referenced_message: Message = None

    async def reply(self, content="", embeds=[]):
        return await self._Client.create_message(self.channel_id,
        content=content if content != "" else self.content,
        embed=embeds[0] if embeds != [] else self.embeds[0] if self.embeds != [] else None,
        message_reference=Message_Reference(self.id, self.channel_id, self.guild_id))
    
    async def delete(self):
        return await self._Client.delete_message(self.channel_id, self.message_id)
    
    async def edit(self):
        return await self._Client.edit_message(self.channel_id, self.message_id, self.content, self.embeds[0], self.flags, self.allowed_mentions)
    
    async def send(self):
        return await self._Client.create_message(self.channel_id, content=self.content, embed=self.embeds[0])
    
    async def webhook(self, webhook_id: Snowflake, webhook_token: int, username: str = None, avatar_url: str = None, file: bytes = None):
        return await self._Client.execute_webhook(webhook_id, webhook_token, content=self.content, username=username, avatar_url=avatar_url, file=file, embeds=self.embeds, allowed_mentions=self.allowed_mentions)
    
    async def webhook_edit(self, webhook_id, webhook_token, content: str = None, embeds: List[Embed] = None, allowed_mentions: Allowed_Mentions = None):
        return await self._Client.edit_webhook_message(webhook_id, webhook_token, self.message_id, content, embeds, allowed_mentions)
    
    async def get(self):
        return await self._Client.get_channel_message(self.channel_id, self.message_id)

    async def react(self, reaction):
        return await self._Client.create_reaction(self.channel_id, self.message_id, reaction)
    
    async def delete_reaction(self, reaction):
        return await self._Client.delete_own_reaction(self.channel_id, self.message_id, reaction)


class Message_Types(Enum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    REPLY = 19
    APPLICATION_COMMAND = 20


@dataclass
class Message_Activity(DiscordObject):
    '''
    Params:
        :type: Type_Of_Message_Activity
        :party_id: Rich_Presence_Event
    '''
    type: int = 0
    party_id: str = ''


@dataclass
class Message_Application(DiscordObject):
    '''
    Params:
        :id: id of the application
        :cover_image: id of the embed's image asset
        :description: application's description
        :icon: id of the application's icon
        :name: name of the application
    '''
    id: Snowflake = 0
    cover_image: str = ''
    description: str = ''
    icon: str = ''
    name: str = ''


@dataclass
class Message_Reference(DiscordObject):
    '''
    * `channel_id` is optional when creating a reply, but will always be present when receiving an event/response that includes this data model.
    
    Params:
        :message_id: id of the originating message
        :channel_id: id of the originating message's channel
        :guild_id: id of the originating message's guild
    '''
    message_id: Snowflake = 0
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0


class Message_Activity_Types(Enum):
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class Message_Flags(Flag):
    '''
    Params:
        :CROSSPOSTED: this message has been published to subscribed channels
        :IS_CROSSPOST: this message originated from a message in another channel
        :SUPPRESS_EMBEDS: do not include any embeds when serializing this message
        :SOURCE_MESSAGE_DELETED: the source message for this crosspost has been deleted
        :URGENT: this message came from the urgent message system
    '''
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4


@dataclass
class Message_Sticker(DiscordObject):
    '''
    * The URL for fetching sticker assets is currently private.
    
    Params:
        :id: id of the sticker
        :pack_id: id of the pack the sticker is from
        :name: name of the sticker
        :description: description of the sticker
        :tags: a comma-separated list of tags for the sticker
        :asset: sticker asset hash
        :preview_asset: sticker preview asset hash
        :format_type: Type_Of_Sticker_Format
    '''
    id: Snowflake = 0
    pack_id: Snowflake = 0
    name: str = ''
    description: str = ''
    tags: List[str] = list
    asset: str = ''
    preview_asset: str = ''
    format_type: int = 0


class Message_Sticker_Format_Types(Enum):
    PNG = 1
    APNG = 2
    LOTTIE = 3


@dataclass
class Followed_Channel(DiscordObject):
    '''
    Params:
        :channel_id: source channel id
        :webhook_id: created target webhook id
    '''
    channel_id: Snowflake = 0
    webhook_id: Snowflake = 0


@dataclass
class Reaction(DiscordObject):
    '''
    Params:
        :count: times this emoji has been used to react
        :me: whether the current user reacted using this emoji
        :emoji: emoji information
    '''
    count: int = 0
    me: bool = False
    emoji: Emoji = None


@dataclass
class Overwrite(DiscordObject):
    '''
    Params:
        :id: role
        :type: either 0 (role) or 1 (member)
        :allow: permission bit set
        :deny: permission bit set
    '''
    id: Snowflake = 0
    type: int = 0
    allow: str = 0x0
    deny: str = 0x0


@dataclass
class Embed(DiscordObject):
    '''
    Params:
        :title: title of embed
        :type: Type_Of_Embed
        :description: description of embed
        :url: url of embed
        :timestamp: timestamp of embed content
        :color: color code of the embed
        :footer: footer information
        :image: image information
        :thumbnail: thumbnail information
        :video: video information
        :provider: provider information
        :author: author information
        :fields: fields information
    '''
    title: str = None
    type: str = None
    description: str = None
    url: str = None
    timestamp: datetime = None
    color: int = None
    footer: Embed_Footer = None
    image: Embed_Image = None
    thumbnail: Embed_Thumbnail = None
    video: Embed_Video = None
    provider: Embed_Provider = None
    author: Embed_Author = None
    fields: List[Embed_Field] = list
    
    def setTitle(self, title):
        title = str(title)[:Limits.TITLE]
        if self.total_characters + len(str(title)) <= 6000:
            self.title = title
        return self

    def setDescription(self, description):
        description = str(description)[:Limits.DESCRIPTION]
        if self.total_characters + len(str(description)) <= 6000:
            self.description = description
        return self

    def setColor(self, color):
        if type(color) == str and '#' in color:
            color = int(color.lstrip('#'), 16)
        elif type(color) == tuple:
            color = (color[0]<<16) + (color[1]<<8) + color[2]
        self.color = color
        return self

    def setUrl(self, url):
        self.url = url
        return self

    def setImage(self, url, proxy_url=None, height=None, width=None):
        self.image = Embed_Image(url, proxy_url, height, width)
        return self

    def setThumbnail(self, url, proxy_url=None, height=None, width=None):
        self.thumbnail = Embed_Thumbnail(url, proxy_url, height, width)
        return self

    def setFooter(self, text='', icon_url=None, proxy_icon_url=None):
        text = str(text)[:Limits.FOOTER_TEXT]
        if self.total_characters + len(str(text)) <= 6000:
            self.footer = Embed_Footer(text, icon_url, proxy_icon_url)
        return self

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp
        return self

    def setAuthor(self, name='', url=None, icon_url=None, proxy_icon_url=None):
        name = str(name)[:Limits.AUTHOR_NAME]
        if self.total_characters + len(str(name)) <= 6000:
            self.author = Embed_Author(name, url, icon_url, proxy_icon_url)
        return self

    def addField(self, name, value, inline=False):
        name = str(name)[:Limits.FIELD_NAME]
        value = str(value)[:Limits.FIELD_VALUE]
        value = str(value)[:6000 - self.total_characters]

        if self.total_characters + len(str(name)) + len(str(value)) <= 6000:
            self.fields.append(Embed_Field(name=name, value=value, inline=inline))
        return self
    
    def addFields(self, title, text, inline=False):
        from textwrap import wrap
        for x, chunk in enumerate(wrap(text, 1024, replace_whitespace=False)):
            if len(self.fields) == 25:
                break
            if x == 0:
                self.addField(title, chunk, inline)
            else:
                self.addField('\u200b', chunk, inline)
        return self

    @property
    def total_characters(self):
        return len(self.title or "") + len(self.description or "") + len(self.author.name or "" if self.author else "") + len(self.footer.text or "" if self.footer else "") + sum([len(field.name) + len(field.value) for field in self.fields])


class Embed_Types(Enum):
    '''
    Params:
        :rich: generic embed rendered from embed attributes
        :image: image embed
        :video: video embed
        :gifv: animated gif image embed rendered as a video embed
        :article: article embed
        :link: link embed
    '''
    rich = "Generic_Embed_Rendered_From_Embed_Attributes"
    image = "Image_Embed"
    video = "Video_Embed"
    gifv = "Animated_Gif_Image_Embed_Rendered_As_A_Video_Embed"
    article = "Article_Embed"
    link = "Link_Embed"


@dataclass
class Embed_Thumbnail(DiscordObject):
    '''
    Params:
        :url: source url of thumbnail
        :proxy_url: a proxied url of the thumbnail
        :height: height of thumbnail
        :width: width of thumbnail
    '''
    url: str = ''
    proxy_url: str = ''
    height: int = 0
    width: int = 0


@dataclass
class Embed_Video(DiscordObject):
    '''
    Params:
        :url: source url of video
        :height: height of video
        :width: width of video
    '''
    url: str = ''
    height: int = 0
    width: int = 0


@dataclass
class Embed_Image(DiscordObject):
    '''
    Params:
        :url: source url of image
        :proxy_url: a proxied url of the image
        :height: height of image
        :width: width of image
    '''
    url: str = ''
    proxy_url: str = ''
    height: int = 0
    width: int = 0


@dataclass
class Embed_Provider(DiscordObject):
    '''
    Params:
        :name: name of provider
        :url: url of provider
    '''
    name: str = ''
    url: str = ''


@dataclass
class Embed_Author(DiscordObject):
    '''
    Params:
        :name: name of author
        :url: url of author
        :icon_url: url of author icon
        :proxy_icon_url: a proxied url of author icon
    '''
    name: str = ''
    url: str = ''
    icon_url: str = ''
    proxy_icon_url: str = ''


@dataclass
class Embed_Footer(DiscordObject):
    '''
    Params:
        :text: footer text
        :icon_url: url of footer icon
        :proxy_icon_url: a proxied url of footer icon
    '''
    text: str = ''
    icon_url: str = ''
    proxy_icon_url: str = ''


@dataclass
class Embed_Field(DiscordObject):
    '''
    Params:
        :name: name of the field
        :value: value of the field
        :inline: whether
    '''
    name: str = ''
    value: str = ''
    inline: bool = False


@dataclass
class Attachment(DiscordObject):
    '''
    Params:
        :id: attachment id
        :filename: name of file attached
        :size: size of file in bytes
        :url: source url of file
        :proxy_url: a proxied url of file
        :height: height of file
        :width: width of file
    '''
    id: Snowflake = 0
    filename: str = ''
    size: int = 0
    url: str = ''
    proxy_url: str = ''
    height: int = 0
    width: int = 0


@dataclass
class Channel_Mention(DiscordObject):
    '''
    Params:
        :id: id of the channel
        :guild_id: id of the guild containing the channel
        :type: Type_Of_Channel
        :name: the name of the channel
    '''
    id: Snowflake = 0
    guild_id: Snowflake = 0
    type: int = 0
    name: str = ''


class Allowed_Mention_Types(Enum):
    '''
    Params:
        :Role Mentions: Controls role mentions
        :User Mentions: Controls user mentions
        :Everyone Mentions: Controls @everyone and @here mentions
    '''
    Role_Mentions = "roles"
    User_Mentions = "users"
    Everyone_Mentions = "everyone"


@dataclass
class Allowed_Mentions(DiscordObject):
    '''
    Params:
        :parse: Allowed_Mention_Types
        :roles: Array of role_ids to mention
        :users: Array of user_ids to mention
        :replied_user: For replies, whether to mention the author of the message being replied to
    '''
    parse: List[Allowed_Mention_Types] = list
    roles: List[int] = list
    users: List[int] = list
    replied_user: bool = False


class Limits(IntEnum):
    '''
    Additionally, the characters in all `title`, `description`, `field.name`, `field.value`, `footer.text`, and `author.name` fields must not exceed 6000 characters in total. Violating any of these constraints will result in a `Bad Request` response.
    '''
    TITLE = 256
    DESCRIPTION = 2048
    FIELDS = 25
    FIELD_NAME = 256
    FIELD_VALUE = 1024
    FOOTER_TEXT = 2048
    AUTHOR_NAME = 256
    TOTAL = 6000


@dataclass
class Emoji(DiscordObject):
    '''
    Params:
        :id: Emoji_Id
        :name: emoji name
        :roles: roles this emoji is whitelisted to
        :user: user that created this emoji
        :require_colons: whether this emoji must be wrapped in colons
        :managed: whether this emoji is managed
        :animated: whether this emoji is animated
        :available: whether this emoji can be used, may be false due to loss of Server Boosts
    '''
    id: Snowflake = 0
    name: str = ""
    roles: List[Role] = list
    user: User = None
    require_colons: bool = False
    managed: bool = False
    animated: bool = False
    available: bool = False


@dataclass
class Guild(DiscordObject):
    '''
    ** * These fields are only sent within the [GUILD_CREATE](#DOCS_TOPICS_GATEWAY/guild-create) event **
    ** ** These fields are only sent when using the [GET Current User Guilds](#DOCS_RESOURCES_USER/get-current-user-guilds) endpoint and are relative to the requested user **
    
    Params:
        :id: guild id
        :name: guild name
        :icon: Icon_Hash
        :icon_hash: Icon_Hash
        :splash: Splash_Hash
        :discovery_splash: Discovery_Splash_Hash
        :owner: The_User
        :owner_id: id of owner
        :permissions: The_User
        :region: Voice_Region
        :afk_channel_id: id of afk channel
        :afk_timeout: afk timeout in seconds
        :widget_enabled: true if the server widget is enabled
        :widget_channel_id: the channel id that the widget will generate an invite to,
        :verification_level: Verification_Level
        :default_message_notifications: Message_Notifications_Level
        :explicit_content_filter: Explicit_Content_Filter_Level
        :roles: roles in the guild
        :emojis: custom guild emojis
        :features: enabled guild features
        :mfa_level: MFA_Level
        :application_id: application id of the guild creator if it is bot-created
        :system_channel_id: the id of the channel where guild notices such as welcome messages and boost events are posted
        :system_channel_flags: System_Channel_Flags
        :rules_channel_id: the id of the channel where Community guilds can display rules and/or guidelines
        :joined_at: when this guild was joined at
        :large: true if this is considered a large guild
        :unavailable: true if this guild is unavailable due to an outage
        :member_count: total number of members in this guild
        :voice_states: states of members currently in voice channels; lacks the `guild_id` key
        :members: users in the guild
        :channels: channels in the guild
        :presences: presences of the members in the guild, will only include non-offline members if the size is greater than `large threshold`
        :max_presences: the maximum number of presences for the guild
        :max_members: the maximum number of members for the guild
        :vanity_url_code: the vanity url code for the guild
        :description: the description for the guild, if the guild is discoverable
        :banner: Banner_Hash
        :premium_tier: Premium_Tier
        :premium_subscription_count: the number of boosts this guild currently has
        :preferred_locale: the preferred locale of a Community guild; used in server discovery and notices from Discord; defaults to "en-US"
        :public_updates_channel_id: the id of the channel where admins and moderators of Community guilds receive notices from Discord
        :max_video_channel_users: the maximum amount of users in a video channel
        :approximate_member_count: approximate number of members in this guild, returned from the `GET /guilds/<id>` endpoint when `with_counts` is `true`
        :approximate_presence_count: approximate number of non-offline members in this guild, returned from the `GET /guilds/<id>` endpoint when `with_counts` is `true`
    '''
    id: Snowflake = 0
    name: str = ""
    icon: str = ""
    icon_hash: str = ""
    splash: str = ""
    discovery_splash: str = ""
    owner: bool = False
    owner_id: Snowflake = 0
    permissions: str = 0x0
    region: str = ""
    afk_channel_id: Snowflake = 0
    afk_timeout: int = 0
    widget_enabled: bool = False
    widget_channel_id: Snowflake = 0
    verification_level: int = 0
    default_message_notifications: int = 0
    explicit_content_filter: int = 0
    roles: List[Role] = list
    emojis: List[Emoji] = list
    features: List[Guild_Features] = list
    mfa_level: int = 0
    application_id: Snowflake = 0
    system_channel_id: Snowflake = 0
    system_channel_flags: int = 0
    rules_channel_id: Snowflake = 0
    joined_at: datetime = datetime.now().isoformat()
    large: bool = False
    unavailable: bool = False
    member_count: int = 0
    voice_states: List[Voice_State] = list
    members: List[Guild_Member] = list
    channels: List[Channel] = list
    presences: List[Presence_Update] = list
    max_presences: int = 0
    max_members: int = 0
    vanity_url_code: str = ''
    description: str = ''
    banner: str = ''
    premium_tier: int = 0
    premium_subscription_count: int = 0
    preferred_locale: str = ''
    public_updates_channel_id: Snowflake = 0
    max_video_channel_users: int = 0
    approximate_member_count: int = 0
    approximate_presence_count: int = 0


@dataclass
class Default_Message_Notification_Level(Enum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


@dataclass
class Explicit_Content_Filter_Level(Enum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


@dataclass
class MFA_Level(Enum):
    NONE = 0
    ELEVATED = 1


@dataclass
class Verification_Level(Enum):
    '''
    Params:
        :NONE: unrestricted
        :LOW: must have verified email on account
        :MEDIUM: must be registered on Discord for longer than 5 minutes
        :HIGH: must be a member of the server for longer than 10 minutes
        :VERY_HIGH: must have a verified phone number
    '''
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


@dataclass
class Premium_Tier(Enum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class System_Channel_Flags(Flag):
    '''
    Params:
        :SUPPRESS_JOIN_NOTIFICATIONS: Suppress member join notifications
        :SUPPRESS_PREMIUM_SUBSCRIPTIONS: Suppress server boost notifications
    '''
    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1


class Guild_Features(Enum):
    '''
    Params:
        :INVITE_SPLASH: guild has access to set an invite splash background
        :VIP_REGIONS: guild has access to set 384kbps bitrate in voice
        :VANITY_URL: guild has access to set a vanity URL
        :VERIFIED: guild is verified
        :PARTNERED: guild is partnered
        :COMMUNITY: guild can enable welcome screen and discovery, and receives community updates
        :COMMERCE: guild has access to use commerce features
        :NEWS: guild has access to create news channels
        :DISCOVERABLE: guild is lurkable and able to be discovered in the directory
        :FEATURABLE: guild is able to be featured in the directory
        :ANIMATED_ICON: guild has access to set an animated guild icon
        :BANNER: guild has access to set a guild banner image
        :WELCOME_SCREEN_ENABLED: guild has enabled the welcome screen
    '''
    INVITE_SPLASH = "Guild has access to Set An Invite Splash Background"
    VIP_REGIONS = "Guild has access to Set 384 Kbps Bitrate In Voice"
    VANITY_URL = "Guild has access to Set A Vanity Url"
    VERIFIED = "Guild Is Verified"
    PARTNERED = "Guild Is Partnered"
    COMMUNITY = "Guild Can Enable Welcome Screen and Discovery, and Receives Community Updates"
    COMMERCE = "Guild has access to Use Commerce Features"
    NEWS = "Guild has access to Create News Channels"
    DISCOVERABLE = "Guild Is Lurkable and Able to Be Discovered In The Directory"
    FEATURABLE = "Guild Is Able to Be Featured In The Directory"
    ANIMATED_ICON = "Guild has access to Set An Animated Guild Icon"
    BANNER = "Guild has access to Set A Guild Banner Image"
    WELCOME_SCREEN_ENABLED = "Guild has Enabled The Welcome Screen"


@dataclass
class Guild_Preview(DiscordObject):
    '''
    Params:
        :id: guild id
        :name: guild name
        :icon: Icon_Hash
        :splash: Splash_Hash
        :discovery_splash: Discovery_Splash_Hash
        :emojis: custom guild emojis
        :features: enabled guild features
        :approximate_member_count: approximate number of members in this guild
        :approximate_presence_count: approximate number of online members in this guild
        :description: the description for the guild
    '''
    id: Snowflake = 0
    name: str = ''
    icon: str = ''
    splash: str = ''
    discovery_splash: str = ''
    emojis: List[Emoji] = list
    features: List[Guild_Features] = list
    approximate_member_count: int = 0
    approximate_presence_count: int = 0
    description: str = ''


@dataclass
class Guild_Widget(DiscordObject):
    '''
    Params:
        :enabled: whether the widget is enabled
        :channel_id: the widget channel id
    '''
    enabled: bool = False
    channel_id: Snowflake = 0


@dataclass
class Guild_Member(DiscordObject):
    '''
    > info
    > The field `user` won't be included in the member object attached to `MESSAGE_CREATE` and `MESSAGE_UPDATE` gateway events.
    
    Params:
        :user: the user this guild member represents
        :nick: this users guild nickname
        :roles: Role
        :joined_at: when the user joined the guild
        :premium_since: Boosting
        :deaf: whether the user is deafened in voice channels
        :mute: whether the user is muted in voice channels
        :pending: whether the user has passed the guild's Membership Screening requirements
    '''
    user: User = None
    nick: str = None
    roles: List[int] = list
    joined_at: datetime = datetime.now().isoformat()
    premium_since: datetime = datetime.now().isoformat()
    deaf: bool = False
    mute: bool = False
    pending: bool = False


@dataclass
class Integration(DiscordObject):
    '''
    ** * These fields are not provided for discord bot integrations. **
    
    Params:
        :id: integration id
        :name: integration name
        :type: integration type
        :enabled: is this integration enabled
        :syncing: is this integration syncing
        :role_id: id that this integration uses for "subscribers"
        :enable_emoticons: whether emoticons should be synced for this integration
        :expire_behavior: the behavior of expiring subscribers
        :expire_grace_period: the grace period
        :user: user for this integration
        :account: integration account information
        :synced_at: when this integration was last synced
        :subscriber_count: how many subscribers this integration has
        :revoked: has this integration been revoked
        :application: The bot/OAuth2 application for discord integrations
    '''
    id: Snowflake = 0
    name: str = ''
    type: str = ''
    enabled: bool = False
    syncing: bool = False
    role_id: Snowflake = 0
    enable_emoticons: bool = False
    expire_behavior: Integration_Expire_Behaviors = None
    expire_grace_period: int = 0
    user: User = None
    account: Integration_Account = None
    synced_at: datetime = datetime.now().isoformat()
    subscriber_count: int = 0
    revoked: bool = False
    application: Integration_Application = None


class Integration_Expire_Behaviors(Enum):
    REMOVE_ROLE: 0
    KICK: 1


@dataclass
class Integration_Account(DiscordObject):
    '''
    Params:
        :id: id of the account
        :name: name of the account
    '''
    id: str = ''
    name: str = ''


@dataclass
class Integration_Application(DiscordObject):
    '''
    Params:
        :id: the id of the app
        :name: the name of the app
        :icon: Icon_Hash
        :description: the description of the app
        :summary: the description of the app
        :bot: the bot associated with this application
    '''
    id: Snowflake = 0
    name: str = ''
    icon: str = ''
    description: str = ''
    summary: str = ''
    bot: User = None


@dataclass
class Ban(DiscordObject):
    '''
    Params:
        :reason: the reason for the ban
        :user: the banned user
    '''
    reason: str = ''
    user: User = None


@dataclass
class Invite(DiscordObject):
    '''
    Params:
        :code: the invite code
        :guild: the guild this invite is for
        :channel: the channel this invite is for
        :inviter: the user who created the invite
        :target_user: the target user for this invite
        :target_user_type: Type_Of_User_Target
        :approximate_presence_count: approximate count of online members
        :approximate_member_count: approximate count of total members
    '''
    code: str = ''
    guild: Guild = None
    channel: Channel = None
    inviter: User = None
    target_user: User = None
    target_user_type: int = 0
    approximate_presence_count: int = 0
    approximate_member_count: int = 0


class Target_User_Types(Enum):
    STREAM = 1


@dataclass
class Invite_Metadata(DiscordObject):
    '''
    Params:
        :uses: number of times this invite has been used
        :max_uses: max number of times this invite can be used
        :max_age: duration
        :temporary: whether this invite only grants temporary membership
        :created_at: when this invite was created
    '''
    uses: int = 0
    max_uses: int = 0
    max_age: int = 0
    temporary: bool = False
    created_at: datetime = datetime.now().isoformat()


@dataclass
class User(DiscordObject):
    '''
    Params:
        :id: the user's id
        :username: the user's username, not unique across the platform
        :discriminator: the user's 4-digit discord-tag
        :avatar: Avatar_Hash
        :bot: whether the user belongs to an OAuth2 application
        :system: whether the user is an Official Discord System user
        :mfa_enabled: whether the user has two factor enabled on their account
        :locale: the user's chosen language option
        :verified: whether the email on this account has been verified
        :email: the user's email
        :flags: Flags
        :premium_type: Type_Of_Nitro_Subscription
        :public_flags: Flags
    '''
    id: Snowflake = 0
    username: str = ""
    discriminator: int = 0000
    avatar: str = ""
    bot: bool = False
    system: bool = False
    mfa_enabled: bool = False
    locale: str = ""
    verified: bool = False
    email: str = ""
    flags: int = 0
    premium_type: int = 0
    public_flags: int = 0


class User_Flags(Flag):
    '''
    Params:
        :None: None
        :Discord Employee: Discord Employee
        :Partnered Server Owner: Partnered Server Owner
        :HypeSquad Events: HypeSquad Events
        :Bug Hunter Level 1: Bug Hunter Level 1
        :House Bravery: House Bravery
        :House Brilliance: House Brilliance
        :House Balance: House Balance
        :Early Supporter: Early Supporter
        :Team User: Team User
        :System: System
        :Bug Hunter Level 2: Bug Hunter Level 2
        :Verified Bot: Verified Bot
        :Early Verified Bot Developer: Early Verified Bot Developer
    '''
    NONE = 0
    DISCORD_EMPLOYEE = 1 << 0
    PARTNERED_SERVER_OWNER = 1 << 1
    HYPESQUAD_EVENTS = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HOUSE_BRAVERY = 1 << 6
    HOUSE_BRILLIANCE = 1 << 7
    HOUSE_BALANCE = 1 << 8
    EARLY_SUPPORTER = 1 << 9
    TEAM_USER = 1 << 10
    SYSTEM = 1 << 12
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    EARLY_VERIFIED_BOT_DEVELOPER = 1 << 17


class Premium_Types(Enum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


@dataclass
class Connection(DiscordObject):
    '''
    Params:
        :id: id of the connection account
        :name: the username of the connection account
        :type: the service of the connection
        :revoked: whether the connection is revoked
        :integrations: Server_Integrations
        :verified: whether the connection is verified
        :friend_sync: whether friend sync is enabled for this connection
        :show_activity: whether activities related to this connection will be shown in presence updates
        :visibility: Visibility
    '''
    id: str = ''
    name: str = ''
    type: str = ''
    revoked: bool = False
    integrations: List[list] = list
    verified: bool = False
    friend_sync: bool = False
    show_activity: bool = False
    visibility: int = 0


class Visibility_Types(Enum):
    '''
    Params:
        :None: invisible to everyone except the user themselves
        :Everyone: visible to everyone
    '''
    NONE = 0
    EVERYONE = 1


@dataclass
class Voice_State(DiscordObject):
    '''
    Params:
        :guild_id: the guild id this voice state is for
        :channel_id: the channel id this user is connected to
        :user_id: the user id this voice state is for
        :member: the guild member this voice state is for
        :session_id: the session id for this voice state
        :deaf: whether this user is deafened by the server
        :mute: whether this user is muted by the server
        :self_deaf: whether this user is locally deafened
        :self_mute: whether this user is locally muted
        :self_stream: whether this user is streaming using "Go Live"
        :self_video: whether this user's camera is enabled
        :suppress: whether this user is muted by the current user
    '''
    guild_id: Snowflake = 0
    channel_id: Snowflake = 0
    user_id: Snowflake = None
    member: Guild_Member = None
    session_id: str = None
    deaf: bool = False
    mute: bool = False
    self_deaf: bool = False
    self_mute: bool = False
    self_stream: bool = False
    self_video: bool = False
    suppress: bool = False


@dataclass
class Voice_Region(DiscordObject):
    '''
    Params:
        :id: unique ID for the region
        :name: name of the region
        :vip: true if this is a vip-only server
        :optimal: true for a single server that is closest to the current user's client
        :deprecated: whether this is a deprecated voice region
        :custom: whether this is a custom voice region
    '''
    id: str = ''
    name: str = ''
    vip: bool = False
    optimal: bool = False
    deprecated: bool = False
    custom: bool = False


@dataclass
class Webhook(DiscordObject):
    '''
    Params:
        :id: the id of the webhook
        :type: Type
        :guild_id: the guild id this webhook is for
        :channel_id: the channel id this webhook is for
        :user: the user this webhook was created by
        :name: the default name of the webhook
        :avatar: the default avatar of the webhook
        :token: the secure token of the webhook
        :application_id: the bot/OAuth2 application that created this webhook
    '''
    id: Snowflake = 0
    type: int = 0
    guild_id: Snowflake = 0
    channel_id: Snowflake = 0
    user: User = None
    name: str = ''
    avatar: str = ''
    token: str = ''
    application_id: Snowflake = 0


class Webhook_Types(Enum):
    '''
    Params:
        :Incoming: Incoming Webhooks can post messages to channels with a generated token
        :Channel Follower: Channel Follower Webhooks are internal webhooks used with Channel Following to post new messages into channels
    '''
    INCOMING = 1
    CHANNEL_FOLLOWER = 2


@dataclass
class Gateway_Payload(DiscordObject):
    '''
    * `s` and `t` are `null` when `op` is not `0` (Gateway Dispatch Opcode).
    
    Params:
        :op: Opcode
        :d: event data
        :s: sequence number, used for resuming sessions and heartbeats
        :t: the event name for this payload
    '''
    op: int = 0
    d: dict = dict
    s: int = 0
    t: str = None


@dataclass
class Identify(DiscordObject):
    '''
    Params:
        :token: authentication token
        :properties: Connection_Properties
        :compress: whether this connection supports compression of packets
        :large_threshold: value between 50 and 250, total number of members where the gateway will stop sending offline members in the guild member list
        :shard: Guild_Sharding
        :presence: presence structure for initial presence information
        :guild_subscriptions: enables dispatching of guild subscription events
        :intents: Gateway_Intents
    '''
    token: str = "-"
    properties: dict = None
    compress: bool = False
    large_threshold: int = 50
    shard: List[int] = list
    presence: Gateway_Status_Update = None
    guild_subscriptions: bool = True
    intents: int = 0


@dataclass
class Identify_Connection_Properties(DiscordObject):
    '''
    Params:
        :$os: your operating system
        :$browser: your library name
        :$device: your library name
    '''
    os: str = ''
    browser: str = ''
    device: str = ''


@dataclass
class Resume(DiscordObject):
    '''
    Params:
        :token: session token
        :session_id: session id
        :seq: last sequence number received
    '''
    token: str = ''
    session_id: str = ''
    seq: int = 0


@dataclass
class Guild_Request_Members(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild to get members for
        :query: string that username starts with,
        :limit: maximum number of members to send matching the `query`; a limit of `0` can be used with an empty string `query` to return all members
        :presences: used to specify if we want the presences of the matched members
        :user_ids: used to specify which users you wish to fetch
        :nonce: Guild_Members_Chunk
    '''
    guild_id: Snowflake = 0
    query: str = ''
    limit: int = 0
    presences: bool = False
    user_ids: List[int] = list
    nonce: str = ''


@dataclass
class Gateway_Voice_State_Update(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
        :channel_id: id of the voice channel client wants to join
        :self_mute: is the client muted
        :self_deaf: is the client deafened
    '''
    guild_id: Snowflake = 0
    channel_id: Snowflake = 0
    self_mute: bool = False
    self_deaf: bool = False


@dataclass
class Gateway_Status_Update(DiscordObject):
    '''
    Params:
        :since: unix time
        :activities: null,
        :status: Status
        :afk: whether
    '''
    since: int = 0
    activities: List[Bot_Activity] = list
    status: str = ''
    afk: bool = False


class Status_Types(Enum):
    '''
    Params:
        :online: Online
        :dnd: Do Not Disturb
        :idle: AFK
        :invisible: Invisible and shown as offline
        :offline: Offline
    '''
    ONLINE = "online"
    DND = "dnd"
    IDLE = "idle"
    INVISIBLE = "invisible"
    OFFLINE = "offline"


@dataclass
class Hello(DiscordObject):
    '''
    Params:
        :heartbeat_interval: the interval
    '''
    heartbeat_interval: int = 0


@dataclass
class Ready(DiscordObject):
    '''
    Params:
        :v: Gateway_Version
        :user: information about the user including email
        :private_channels: empty array
        :guilds: the guilds the user is in
        :session_id: used for resuming connections
        :shard: Shard_Information
        :application: contains `id` and `flags`
    '''
    v: int = 0
    user: User = None
    private_channels: list = list
    guilds: List[Guild] = list
    session_id: str = ''
    shard: List[int] = list
    application: Application = None


@dataclass
class Channel_Pins_Update(DiscordObject):
    '''
    Params:
        :guild_id: the id of the guild
        :channel_id: the id of the channel
        :last_pin_timestamp: the time at which the most recent pinned message was pinned
    '''
    guild_id: Snowflake = 0
    channel_id: Snowflake = 0
    last_pin_timestamp: datetime = datetime.now().isoformat()


@dataclass
class Guild_Ban_Add(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
        :user: the banned user
    '''
    guild_id: Snowflake = 0
    user: User = None


@dataclass
class Guild_Ban_Remove(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
        :user: the unbanned user
    '''
    guild_id: Snowflake = 0
    user: User = None


@dataclass
class Guild_Emojis_Update(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
        :emojis: Emojis
    '''
    guild_id: Snowflake = 0
    emojis: List[Emoji] = list


@dataclass
class Guild_Integrations_Update(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild whose integrations were updated
    '''
    guild_id: Snowflake = 0


@dataclass
class Guild_Member_Add(Guild_Member, DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
    '''
    guild_id: Snowflake = 0


@dataclass
class Guild_Member_Remove(DiscordObject):
    '''
    Params:
        :guild_id: the id of the guild
        :user: the user who was removed
    '''
    guild_id: Snowflake = 0
    user: User = None


@dataclass
class Guild_Member_Update(DiscordObject):
    '''
    Params:
        :guild_id: the id of the guild
        :roles: user role ids
        :user: the user
        :nick: nickname of the user in the guild
        :joined_at: when the user joined the guild
        :premium_since: Boosting
    '''
    guild_id: Snowflake = 0
    roles: List[Snowflake] = list
    user: User = None
    nick: str = ''
    joined_at: datetime = datetime.now().isoformat()
    premium_since: datetime = datetime.now().isoformat()


@dataclass
class Guild_Members_Chunk(DiscordObject):
    '''
    Params:
        :guild_id: the id of the guild
        :members: set of guild members
        :chunk_index: the chunk index in the expected chunks for this response
        :chunk_count: the total number of expected chunks for this response
        :not_found: if passing an invalid id to `REQUEST_GUILD_MEMBERS`, it will be returned here
        :presences: if passing true to `REQUEST_GUILD_MEMBERS`, presences of the returned members will be here
        :nonce: Guild_Members_Request
    '''
    guild_id: Snowflake = 0
    members: List[Guild_Member] = list
    chunk_index: int = 0
    chunk_count: int = 0
    not_found: list = list
    presences: List[Presence_Update] = list
    nonce: str = ''


@dataclass
class Guild_Role_Create(DiscordObject):
    '''
    Params:
        :guild_id: the id of the guild
        :role: the role created
    '''
    guild_id: Snowflake = 0
    role: Role = None


@dataclass
class Guild_Role_Update(DiscordObject):
    '''
    Params:
        :guild_id: the id of the guild
        :role: the role updated
    '''
    guild_id: Snowflake = 0
    role: Role = None


@dataclass
class Guild_Role_Delete(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
        :role_id: id of the role
    '''
    guild_id: Snowflake = 0
    role_id: Snowflake = 0


@dataclass
class Invite_Create(DiscordObject):
    '''
    Params:
        :channel_id: the channel the invite is for
        :code: Code
        :created_at: the time at which the invite was created
        :guild_id: the guild of the invite
        :inviter: the user that created the invite
        :max_age: how long the invite is valid for
        :max_uses: the maximum number of times the invite can be used
        :target_user: the target user for this invite
        :target_user_type: Type_Of_User_Target
        :temporary: whether
        :uses: how many times the invite has been used
    '''
    channel_id: Snowflake = 0
    code: str = ''
    created_at: datetime = datetime.now().isoformat()
    guild_id: Snowflake = 0
    inviter: User = None
    max_age: int = 0
    max_uses: int = 0
    target_user: User = None
    target_user_type: int = 0
    temporary: bool = False
    uses: int = 0


@dataclass
class Invite_Delete(DiscordObject):
    '''
    Params:
        :channel_id: the channel of the invite
        :guild_id: the guild of the invite
        :code: Code
    '''
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0
    code: str = ''


@dataclass
class Message_Delete(DiscordObject):
    '''
    Params:
        :id: the id of the message
        :channel_id: the id of the channel
        :guild_id: the id of the guild
    '''
    id: Snowflake = 0
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0


@dataclass
class Message_Delete_Bulk(DiscordObject):
    '''
    Params:
        :ids: the ids of the messages
        :channel_id: the id of the channel
        :guild_id: the id of the guild
    '''
    ids: List[int] = list
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0


@dataclass
class Message_Reaction_Add(DiscordObject):
    '''
    Params:
        :user_id: the id of the user
        :channel_id: the id of the channel
        :message_id: the id of the message
        :guild_id: the id of the guild
        :member: the member who reacted if this happened in a guild
        :emoji: Example
    '''
    user_id: Snowflake = 0
    channel_id: Snowflake = 0
    message_id: Snowflake = 0
    guild_id: Snowflake = 0
    member: Guild_Member = None
    emoji: Emoji = None


@dataclass
class Message_Reaction_Remove(DiscordObject):
    '''
    Params:
        :user_id: the id of the user
        :channel_id: the id of the channel
        :message_id: the id of the message
        :guild_id: the id of the guild
        :emoji: Example
    '''
    user_id: Snowflake = 0
    channel_id: Snowflake = 0
    message_id: Snowflake = 0
    guild_id: Snowflake = 0
    emoji: Emoji = None


@dataclass
class Message_Reaction_Remove_All(DiscordObject):
    '''
    Params:
        :channel_id: the id of the channel
        :message_id: the id of the message
        :guild_id: the id of the guild
    '''
    channel_id: Snowflake = 0
    message_id: Snowflake = 0
    guild_id: Snowflake = 0


@dataclass
class Message_Reaction_Remove_Emoji(DiscordObject):
    '''
    Params:
        :channel_id: the id of the channel
        :guild_id: the id of the guild
        :message_id: the id of the message
        :emoji: the emoji that was removed
    '''
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0
    message_id: Snowflake = 0
    emoji: Emoji = None


@dataclass
class Presence_Update(DiscordObject):
    '''
    Params:
        :user: the user presence is being updated for
        :guild_id: id of the guild
        :status: either "idle", "dnd", "online",
        :activities: user's current activities
        :client_status: user's platform-dependent status
    '''
    user: User = None
    guild_id: Snowflake = 0
    status: str = ''
    activities: List[Activity] = list
    client_status: Client_Status = None


@dataclass
class Client_Status(DiscordObject):
    '''
    Params:
        :desktop: the user's status set for an active desktop
        :mobile: the user's status set for an active mobile
        :web: the user's status set for an active web
    '''
    desktop: str = ''
    mobile: str = ''
    web: str = ''


@dataclass
class Bot_Activity(DiscordObject):
    name: str = ''
    type: Activity_Types = None
    url: str = ''

@dataclass
class Activity(DiscordObject):
    '''
    > info
    > Bots are only able to send `name`, `type`, and optionally `url`.
    
    Params:
        :name: the activity's name
        :type: Activity_Type
        :url: stream url, is validated when type is 1
        :created_at: unix timestamp of when the activity was added to the user's session
        :timestamps: unix timestamps for start and/or end of the game
        :application_id: application id for the game
        :details: what the player is currently doing
        :state: the user's current party status
        :emoji: the emoji used for a custom status
        :party: information for the current party of the player
        :assets: images for the presence and their hover texts
        :secrets: secrets for Rich Presence joining and spectating
        :instance: whether or not the activity is an instanced game session
        :flags: Activity_Flags ORd together, describes what the payload includes
    '''
    name: str = ''
    type: Activity_Types = None
    url: str = ''
    created_at: int = 0
    timestamps: Activity_Timestamps = None
    application_id: Snowflake = 0
    details: str = ''
    state: str = ''
    emoji: Emoji = None
    party: Activity_Party = None
    assets: Activity_Assets = None
    secrets: Activity_Secrets = None
    instance: bool = False
    flags: Activity_Flags = None


class Activity_Types(Enum):
    '''
    > info
    > The streaming type currently only supports Twitch and YouTube. Only `https://twitch.tv/` and `https://youtube.com/` urls will work.
    '''
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


@dataclass
class Activity_Timestamps(DiscordObject):
    '''
    Params:
        :start: unix time
        :end: unix time
    '''
    start: int = 0
    end: int = 0


@dataclass
class Activity_Emoji(DiscordObject):
    '''
    Params:
        :name: the name of the emoji
        :id: the id of the emoji
        :animated: whether this emoji is animated
    '''
    name: str = ""
    id: Snowflake = 0
    animated: bool = False


@dataclass
class Activity_Party(DiscordObject):
    '''
    Params:
        :id: the id of the party
        :size: used to show the party's current and maximum size
    '''
    id: str = ""
    size: List[int] = list


@dataclass
class Activity_Assets(DiscordObject):
    '''
    Params:
        :large_image: the id for a large asset of the activity, usually a snowflake
        :large_text: text displayed when hovering over the large image of the activity
        :small_image: the id for a small asset of the activity, usually a snowflake
        :small_text: text displayed when hovering over the small image of the activity
    '''
    large_image: str = ''
    large_text: str = ''
    small_image: str = ''
    small_text: str = ''


@dataclass
class Activity_Secrets(DiscordObject):
    '''
    Params:
        :join: the secret for joining a party
        :spectate: the secret for spectating a game
        :match: the secret for a specific instanced match
    '''
    join: str = ''
    spectate: str = ''
    match: str = ''


class Activity_Flags(Flag):
    INSTANCE = 1 << 0
    JOIN = 1 << 1
    SPECTATE = 1 << 2
    JOIN_REQUEST = 1 << 3
    SYNC = 1 << 4
    PLAY = 1 << 5


@dataclass
class Typing_Start(DiscordObject):
    '''
    Params:
        :channel_id: id of the channel
        :guild_id: id of the guild
        :user_id: id of the user
        :timestamp: unix time
        :member: the member who started typing if this happened in a guild
    '''
    channel_id: Snowflake = 0
    guild_id: Snowflake = 0
    user_id: Snowflake = 0
    timestamp: int = 0
    member: Guild_Member = None


@dataclass
class Voice_Server_Update(DiscordObject):
    '''
    Params:
        :token: voice connection token
        :guild_id: the guild this voice server update is for
        :endpoint: the voice server host
    '''
    token: str = ''
    guild_id: Snowflake = 0
    endpoint: str = ''


@dataclass
class Webhook_Update(DiscordObject):
    '''
    Params:
        :guild_id: id of the guild
        :channel_id: id of the channel
    '''
    guild_id: Snowflake = 0
    channel_id: Snowflake = 0


@dataclass
class JSON_Response(DiscordObject):
    '''
    Params:
        :url: The WSS URL that can be used for connecting to the gateway
        :shards: Shards
        :session_start_limit: Information on the current session start limit
    '''
    url: str = ''
    shards: int = 0
    session_start_limit: Session_Start_Limit = None


@dataclass
class Session_Start_Limit(DiscordObject):
    '''
    Params:
        :total: The total number of session starts the current user is allowed
        :remaining: The remaining number of session starts the current user is allowed
        :reset_after: The number of milliseconds after which the limit resets
        :max_concurrency: The number of identify requests allowed per 5 seconds
    '''
    total: int = 0
    remaining: int = 0
    reset_after: int = 0
    max_concurrency: int = 0


class OAuth2_URLs(Enum):
    '''
    > warn
    > In accordance with the relevant RFCs, the token and token revocation URLs will **only** accept a content type of `x-www-form-urlencoded`. JSON content is not permitted and will return an error.
    
    Params:
        :Base authorization URL: Base authorization URL
        :Token URL: Token URL
        :Token_Revocation: Token_Revocation
    '''
    Base_authorization_URL = "https://discord.com/api/oauth2/authorize"
    Token_URL = "https://discord.com/api/oauth2/token"
    Token_Revocation = "https://discord.com/api/oauth2/token/revoke"


@dataclass
class Application(DiscordObject):
    '''
    Params:
        :id: the id of the app
        :name: the name of the app
        :icon: the icon hash of the app
        :description: the description of the app
        :rpc_origins: an  rpc origin urls, if rpc is enabled
        :bot_public: when false only app owner can join the app's bot to guilds
        :bot_require_code_grant: when true the app's bot will only join upon completion of the full oauth2 code grant flow
        :owner: user  containing info on the owner of the application
        :summary: if this application is a game sold on Discord, this field will be the summary field for the store page of its primary sku
        :verify_key: GetTicket
        :team: if the application belongs to a team, this will be a list of the members of that team
        :guild_id: if this application is a game sold on Discord, this field will be the guild to which it has been linked
        :primary_sku_id: if this application is a game sold on Discord, this field will be the id of the "Game SKU" that is created, if exists
        :slug: if this application is a game sold on Discord, this field will be the URL slug that links to the store page
        :cover_image: if this application is a game sold on Discord, this field will be the hash of the image on store embeds
        :flags: the application's public flags
    '''
    id: Snowflake = 0
    name: str = ''
    icon: str = ''
    description: str = ''
    rpc_origins: List[str] = list
    bot_public: bool = False
    bot_require_code_grant: bool = False
    owner: User = None
    summary: str = ''
    verify_key: str = ''
    team: List[Team] = list
    guild_id: Snowflake = 0
    primary_sku_id: Snowflake = 0
    slug: str = ''
    cover_image: str = ''
    flags: int = 0


class Gateway_Opcodes(Enum):
    '''
    Params:
        :Dispatch: An event was dispatched.
        :Heartbeat: Fired periodically by the client to keep the connection alive.
        :Identify: Starts a new session during the initial handshake.
        :Presence Update: Update the client's presence.
        :Voice State Update: Used to join/leave
        :Resume: Resume a previous session that was disconnected.
        :Reconnect: You should attempt to reconnect and resume immediately.
        :Request Guild Members: Request information about offline guild members in a large guild.
        :Invalid Session: The session has been invalidated. You should reconnect and identify/resume accordingly.
        :Hello: Sent immediately after connecting, contains the `heartbeat_interval` to use.
        :Heartbeat ACK: Sent in response to receiving a heartbeat to acknowledge that it has been received.
    '''
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class Gateway_Close_Event_Codes(Enum):
    '''
    Params:
        :4000: Unknown error
        :4001: Unknown opcode
        :4002: Decode error
        :4003: Not authenticated
        :4004: Authentication failed
        :4005: Already authenticated
        :4007: Invalid `seq`
        :4008: Rate limited
        :4009: Session timed out
        :4010: Invalid shard
        :4011: Sharding required
        :4012: Invalid API version
        :4013: Invalid intent
        :4014: Disallowed intent
    '''
    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    INVALID_SEQ = 4007
    RATE_LIMITED = 4008
    SESSION_TIMED_OUT = 4009
    INVALID_SHARD = 4010
    SHARDING_REQUIRED = 4011
    INVALID_API_VERSION = 4012
    INVALID_INTENT = 4013
    DISALLOWED_INTENT = 4014


class Voice_Opcodes(Enum):
    '''
    Params:
        :Identify: Begin a voice websocket connection.
        :Select Protocol: Select the voice protocol.
        :Ready: Complete the websocket handshake.
        :Heartbeat: Keep the websocket connection alive.
        :Session Description: Describe the session.
        :Speaking: Indicate which users are speaking.
        :Heartbeat ACK: Sent to acknowledge a received client heartbeat.
        :Resume: Resume a connection.
        :Hello: Time to wait between sending heartbeats in milliseconds.
        :Resumed: Acknowledge a successful session resume.
        :Client Disconnect: A client has disconnected from the voice channel
    '''
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class Voice_Close_Event_Codes(Enum):
    '''
    Params:
        :4001: Unknown opcode
        :4002: Failed to decode payload
        :4003: Not authenticated
        :4004: Authentication failed
        :4005: Already authenticated
        :4006: Session no longer valid
        :4009: Session timeout
        :4011: Server not found
        :4012: Unknown protocol
        :4014: Disconnected
        :4015: Voice server crashed
        :4016: Unknown encryption mode
    '''
    UNKNOWN_OPCODE = 4001
    FAILED_TO_DECODE_PAYLOAD = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    SESSION_NO_LONGER_VALID = 4006
    SESSION_TIMEOUT = 4009
    SERVER_NOT_FOUND = 4011
    UNKNOWN_PROTOCOL = 4012
    DISCONNECTED = 4014
    VOICE_SERVER_CRASHED = 4015
    UNKNOWN_ENCRYPTION_MODE = 4016


class HTTP_Response_Codes(Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    TOO_MANY_REQUESTS = 429
    GATEWAY_UNAVAILABLE = 502

'''
class JSON_Error_Codes(Enum):
    General_error = 0
    Unknown_account = 10001
    Unknown_application = 10002
    Unknown_channel = 10003
    Unknown_guild = 10004
    Unknown_integration = 10005
    Unknown_invite = 10006
    Unknown_member = 10007
    Unknown_message = 10008
    Unknown_permission_overwrite = 10009
    Unknown_provider = 10010
    Unknown_role = 10011
    Unknown_token = 10012
    Unknown_user = 10013
    Unknown_emoji = 10014
    Unknown_webhook = 10015
    Unknown_ban = 10026
    Unknown_SKU = 10027
    Unknown_Store_Listing = 10028
    Unknown_entitlement = 10029
    Unknown_build = 10030
    Unknown_lobby = 10031
    Unknown_branch = 10032
    Unknown_redistributable = 10036
    Unknown_guild_template = 10057
    Only_Users = 20001
    Only_Bots = 20002
    NONE = 20022
    NONE = 20028
    Maximum_guilds_reached_100 = 30001
    Maximum_friends_reached_1000 = 30002
    Maximum__reached_50 = 30003
    Maximum__reached_250 = 30005
    Maximum_webhooks_reached_10 = 30007
    Maximum_reactions_reached_20 = 30010
    Maximum__reached_500 = 30013
    Maximum_attachments_reached_10 = 30015
    Maximum_invites_reached_100 = 30016
    Guild_already_has_a_template = 30031
    NONE = 40001
    NONE = 40002
    NONE = 40005
    NONE = 40006
    NONE = 40007
    NONE = 40033
    Missing_access = 50001
    Invalid_account_type = 50002
    NONE = 50003
    NONE = 50004
    Cannot_edit_a_message_authored_by_another_user = 50005
    Cannot_send_an_empty_message = 50006
    Cannot_send_messages_to_this_user = 50007
    Cannot_send_messages_in_a_voice_channel = 50008
    NONE = 50009
    NONE = 50010
    NONE = 50011
    Invalid_OAuth2_state = 50012
    NONE = 50013
    NONE = 50014
    NONE = 50015
    NONE = 50016
    NONE = 50019
    NONE = 50020
    NONE = 50021
    NONE = 50024
    NONE = 50025
    NONE = 50033
    NONE = 50034
    NONE = 50035
    NONE = 50036
    Invalid_API_version = 50041
    NONE = 50074
    Invalid_sticker = 50081
    Reaction_blocked = 90001
    Try_Again_Later = 130000'''


class RPC_Error_Codes(Enum):
    '''
    Params:
        :Unknown error: An unknown error occurred.
        :Invalid payload: You sent an invalid payload.
        :Invalid command: Invalid command name specified.
        :Invalid guild: Invalid guild ID specified.
        :Invalid event: Invalid event name specified.
        :Invalid channel: Invalid channel ID specified.
        :Invalid permissions: You lack permissions to access the given resource.
        :Invalid client ID: An invalid OAuth2 application ID was used to authorize
        :Invalid origin: An invalid OAuth2 application origin was used to authorize
        :Invalid token: An invalid OAuth2 token was used to authorize
        :Invalid user: The specified user ID was invalid.
        :OAuth2 error: A standard OAuth2 error occurred; check the data  for the OAuth2 error details.
        :Select channel timed out: An asynchronous `SELECT_TEXT_CHANNEL`/`SELECT_VOICE_CHANNEL` command timed out.
        :`GET_GUILD` timed out: An asynchronous `GET_GUILD` command timed out.
        :Select voice force required: You tried to join a user to a voice channel but the user was already in one.
        :Capture shortcut already listening: You tried to capture more than one shortcut key at once.
    '''
    UNKNOWN_ERROR = 1000
    INVALID_PAYLOAD = 4000
    INVALID_COMMAND = 4002
    INVALID_GUILD = 4003
    INVALID_EVENT = 4004
    INVALID_CHANNEL = 4005
    INVALID_PERMISSIONS = 4006
    INVALID_CLIENT_ID = 4007
    INVALID_ORIGIN = 4008
    INVALID_TOKEN = 4009
    INVALID_USER = 4010
    OAUTH2_ERROR = 5000
    SELECT_CHANNEL_TIMED_OUT = 5001
    GET_GUILD_TIMED_OUT = 5002
    SELECT_VOICE_FORCE_REQUIRED = 5003
    CAPTURE_SHORTCUT_ALREADY_LISTENING = 5004


class RPC_Close_Event_Codes(Enum):
    '''
    Params:
        :Invalid client ID: You connected to the RPC server with an invalid client ID.
        :Invalid origin: You connected to the RPC server with an invalid origin.
        :Rate limited: You are being rate limited.
        :Token revoked: The OAuth2 token associated with a connection was revoked, get a new one!
        :Invalid version: The RPC Server version specified in the connection string was not valid.
        :Invalid encoding: The encoding specified in the connection string was not valid.
    '''
    INVALID_CLIENT_ID = 4000
    INVALID_ORIGIN = 4001
    RATE_LIMITED = 4002
    TOKEN_REVOKED = 4003
    INVALID_VERSION = 4004
    INVALID_ENCODING = 4005

class Intents(Flag):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14

class Bitwise_Permission_Flags(Flag):
    '''
    *** These permissions require the owner account to use [two-factor authentication](#DOCS_TOPICS_OAUTH2/twofactor-authentication-requirement) when used on a guild that has server-wide 2FA enabled.**
    Note that these internal permission names may be referred to differently by the Discord client. For example, "Manage Permissions" refers to MANAGE_ROLES, "Read Messages" refers to VIEW_CHANNEL, and "Use Voice Activity" refers to USE_VAD.
    
    Params:
        :CREATE_INSTANT_INVITE: Allows creation of instant invites
        :KICK_MEMBERS: Allows kicking members
        :BAN_MEMBERS: Allows banning members
        :ADMINISTRATOR: Allows all permissions and bypasses channel permission overwrites
        :MANAGE_CHANNELS: Allows management and editing of channels
        :MANAGE_GUILD: Allows management and editing of the guild
        :ADD_REACTIONS: Allows for the addition of reactions to messages
        :VIEW_AUDIT_LOG: Allows for viewing of audit logs
        :PRIORITY_SPEAKER: Allows for using priority speaker in a voice channel
        :STREAM: Allows the user to go live
        :VIEW_CHANNEL: Allows guild members to view a channel, which includes reading messages in text channels
        :SEND_MESSAGES: Allows for sending messages in a channel
        :SEND_TTS_MESSAGES: Allows for sending of `/tts` messages
        :MANAGE_MESSAGES: Allows for deletion of other users messages
        :EMBED_LINKS: Links sent by users with this permission will be auto-embedded
        :ATTACH_FILES: Allows for uploading images and files
        :READ_MESSAGE_HISTORY: Allows for reading of message history
        :MENTION_EVERYONE: Allows for using the `@everyone` tag to notify all users in a channel, and the `@here` tag to notify all online users in a channel
        :USE_EXTERNAL_EMOJIS: Allows the usage of custom emojis from other servers
        :VIEW_GUILD_INSIGHTS: Allows for viewing guild insights
        :CONNECT: Allows for joining of a voice channel
        :SPEAK: Allows for speaking in a voice channel
        :MUTE_MEMBERS: Allows for muting members in a voice channel
        :DEAFEN_MEMBERS: Allows for deafening of members in a voice channel
        :MOVE_MEMBERS: Allows for moving of members between voice channels
        :USE_VAD: Allows for using voice-activity-detection in a voice channel
        :CHANGE_NICKNAME: Allows for modification of own nickname
        :MANAGE_NICKNAMES: Allows for modification of other users nicknames
        :MANAGE_ROLES: Allows management and editing of roles
        :MANAGE_WEBHOOKS: Allows management and editing of webhooks
        :MANAGE_EMOJIS: Allows management and editing of emojis
    '''
    CREATE_INSTANT_INVITE = 0x00000001
    KICK_MEMBERS = 0x00000002
    BAN_MEMBERS = 0x00000004
    ADMINISTRATOR = 0x00000008
    MANAGE_CHANNELS = 0x00000010
    MANAGE_GUILD = 0x00000020
    ADD_REACTIONS = 0x00000040
    VIEW_AUDIT_LOG = 0x00000080
    PRIORITY_SPEAKER = 0x00000100
    STREAM = 0x00000200
    VIEW_CHANNEL = 0x00000400
    SEND_MESSAGES = 0x00000800
    SEND_TTS_MESSAGES = 0x00001000
    MANAGE_MESSAGES = 0x00002000
    EMBED_LINKS = 0x00004000
    ATTACH_FILES = 0x00008000
    READ_MESSAGE_HISTORY = 0x00010000
    MENTION_EVERYONE = 0x00020000
    USE_EXTERNAL_EMOJIS = 0x00040000
    VIEW_GUILD_INSIGHTS = 0x00080000
    CONNECT = 0x00100000
    SPEAK = 0x00200000
    MUTE_MEMBERS = 0x00400000
    DEAFEN_MEMBERS = 0x00800000
    MOVE_MEMBERS = 0x01000000
    USE_VAD = 0x02000000
    CHANGE_NICKNAME = 0x04000000
    MANAGE_NICKNAMES = 0x08000000
    MANAGE_ROLES = 0x10000000
    MANAGE_WEBHOOKS = 0x20000000
    MANAGE_EMOJIS = 0x40000000

    def check(cls, permissions: hex, *values: List[hex]):
        return all([(permissions & permission) == permission for permission in values])
    def current_permissions(cls, permissions: hex):
        current = []
        for permission in cls:
            if (permissions & permission.value) == permission.value:
                current.append(permission.name)
        return current


@dataclass
class Role(DiscordObject):
    '''
    Roles without colors (`color == 0`) do not count towards the final computed color in the user list.
    
    Params:
        :id: role id
        :name: role name
        :color: integer representation of hexadecimal color code
        :hoist: if this role is pinned in the user listing
        :position: position of this role
        :permissions: permission bit set
        :managed: whether this role is managed by an integration
        :mentionable: whether this role is mentionable
        :tags: the tags this role has
    '''
    id: Snowflake = 0
    name: str = ''
    color: int = 0
    hoist: bool = False
    position: int = 0
    permissions: str = ''
    managed: bool = False
    mentionable: bool = False
    tags: Role_Tags = None


@dataclass
class Role_Tags(DiscordObject):
    '''
    Params:
        :bot_id: the id of the bot this role belongs to
        :integration_id: the id of the integration this role belongs to
        :premium_subscriber: whether this is the guild's premium subscriber role
    '''
    bot_id: Snowflake = 0
    integration_id: Snowflake = 0
    premium_subscriber: bool = False


@dataclass
class Rate_Limit_Response(DiscordObject):
    '''
    Note that the normal rate-limiting headers will be sent in this response. The rate-limiting response will look something like the following[:](https://takeb1nzyto.space/)
    
    Params:
        :message: A message saying you are being rate limited.
        :retry_after: The number of seconds to wait before submitting another request.
        :_global: A value indicating if you are being globally rate limited
    '''
    message: str = ''
    retry_after: float = 0.0
    _global: bool = False


@dataclass
class Team(DiscordObject):
    '''
    Params:
        :icon: a hash of the image of the team's icon
        :id: the unique id of the team
        :members: the members of the team
        :owner_user_id: the user id of the current team owner
    '''
    icon: str = ''
    id: Snowflake = 0
    members: List[Team_Members] = list
    owner_user_id: Snowflake = 0


@dataclass
class Team_Members(DiscordObject):
    '''
    Params:
        :membership_state: Membership_State
        :permissions: will always be `[""]`
        :team_id: the id of the parent team of which they are a member
        :user: the avatar, discriminator, id, and username of the user
    '''
    membership_state: int = 0
    permissions: List[str] = list
    team_id: Snowflake = 0
    user: User = None


class Membership_State_Enum(Enum):
    INVITED = 1
    ACCEPTED = 2


@dataclass
class Encryption_Modes(Enum):
    '''
    >warn
    >The nonce has to be stripped from the payload before encrypting and before decrypting the audio data
    Finally, the voice server will respond with a [Opcode 4 Session Description](#DOCS_TOPICS_OPCODES_AND_STATUS_CODES/voice) that includes the `mode` and `secret_key`, a 32 byte array used for [encrypting and sending](#DOCS_TOPICS_VOICE_CONNECTIONS/encrypting-and-sending-voice) voice data:
    '''
    Normal = "Xsalsa20_Poly1305"
    Suffix = "Xsalsa20_Poly1305_Suffix"
    Lite = "Xsalsa20_Poly1305_Lite"


@dataclass
class Voice_Packet(DiscordObject):
    Version__Flags: c_byte = 0x80
    Payload_Type: c_byte = 0x78
    Sequence: c_ushort = 0x0
    Timestamp: c_uint = 0x0
    SSRC: c_uint = 0x0
    Encrypted_audio: bytearray = 0x0


class Speaking(Enum):
    MICROPHONE = 1 << 0
    SOUNDSHARE = 1 << 1
    PRIORITY = 1 << 2


@dataclass
class IP_Discovery(DiscordObject):
    '''
    Params:
        :Type: Values 0x1 and 0x2 indicate request and response, respectively
        :Length: Message length excluding Type and Length fields
        :SSRC: Unsigned integer
        :Address: Null-terminated string in response
        :Port: Unsigned short
    '''
    Type: str = ''
    Length: str = ''
    SSRC: c_uint = None
    Address: str = ''
    Port: c_ushort = None


@dataclass
class Example_Nullable_and_Optional_Fields(DiscordObject):
    optional_field: str = ''
    nullable_field: str = ''
    optional_and_nullable_field: str = ''


class Formats(Enum):
    '''
    Using the markdown for either users, roles, or channels will usually mention the target(s) accordingly, but this can be suppressed using the `allowed_mentions` parameter when creating a message. Standard emoji are currently rendered using [Twemoji](https://twemoji.twitter.com/) for Desktop/Android and Apple's native emoji on iOS.
    '''
    User = "<@{user_id}>"
    Nickname = "<@!{user_id}>"
    Channel = "<#{channel_id}>"
    Role = "<@&{role_id}>"
    Standard_Emoji = "Unicode Characters"
    Custom_Emoji = "<:{name}:{id}>"
    Custom_Animated_Emoji = "<a:{name}:{id}>"


class Image_Formats(Enum):
    JPEG = "jpg"
    PNG = "png"
    WebP = "webp"
    GIF = "gif"


class CDN_Endpoints(Enum):
    '''
    * In the case of the Default User Avatar endpoint, the value for `user_discriminator` in the path should be the user's discriminator modulo 5—Test#1337 would be `1337 % 5`, which evaluates to 2.
    ** In the case of endpoints that support GIFs, the hash will begin with `a_` if it is available in GIF format. (example: `a_1269e74af4df7417b13759eae50c83dc`)
    *** In the case of the Default User Avatar endpoint, the size of images returned is constant with the "size" querystring parameter being ignored.
    '''
    Custom_Emoji = "emojis/{emoji_id}.png"
    Guild_Icon = "icons/{guild_id}/guild_icon.png"
    Guild_Splash = "splashes/{guild_id}/guild_splash.png"
    Guild_Discovery_Splash = "discovery-splashes/{guild_id}/guild_discovery_splash.png"
    Guild_Banner = "banners/{guild_id}/guild_banner.png"
    Default_User_Avatar = "embed/avatars/{user_discriminator}.png"
    User_Avatar = "avatars/{user_id}/{user_avatar}.png"
    Application_Icon = "app-icons/{application_id}/icon.png"
    Application_Asset = "app-assets/{application_id}/{asset_id}.png"
    Achievement_Icon = "app-assets/{application_id}/achievements/{achievement_id}/icons/{icon_hash}.png"
    Team_Icon = "team-icons/{team_id}/team_icon.png"


@dataclass
class Application_Command(DiscordObject):
    '''
    Params:
        :id: unique id of the command
        :application_id: unique id of the parent application
        :name: 3-32 character name matching `^
        :description: 1-100 character description
        :options: the parameters for the command
    '''
    id: Snowflake = 0
    application_id: Snowflake = 0
    name: str = ''
    description: str = ''
    options: List[Application_Command_Option] = list


@dataclass
class Application_Command_Option(DiscordObject):
    '''
    Params:
        :type: ApplicationCommandOptionType
        :name: 1-32 character name matching `^
        :description: 1-100 character description
        :default: the first `required` option for the user to complete--only one option can be `default`
        :required: if the parameter is required
        :choices: choices for `string` and `int` types for the user to pick from
        :options: if the option is a subcommand
    '''
    type: int = 0
    name: str = ''
    description: str = ''
    default: bool = False
    required: bool = False
    choices: List[Application_Command_Option_Choice] = list
    options: List[Application_Command_Option] = list


class Application_Command_Option_Type(Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


@dataclass
class Application_Command_Option_Choice(DiscordObject):
    '''
    Params:
        :name: 1-100 character choice name
        :value: value of the choice
    '''
    name: str = ''
    value: str = ''


@dataclass
class Interaction(DiscordObject):
    '''
    * This is always present on `ApplicationCommand` interaction types. It is optional for future-proofing against new interaction types
    
    Params:
        :id: id of the interaction
        :type: the type of interaction
        :data: the command data payload
        :guild_id: the guild it was sent from
        :channel_id: the channel it was sent from
        :member: guild member data for the invoking user
        :token: a continuation token for responding to the interaction
        :version: read-only property, always `1`
    '''
    id: Snowflake = 0
    type: Interaction_Type = None
    data: Application_Command_Interaction_Data = None
    guild_id: Snowflake = 0
    channel_id: Snowflake = 0
    member: Guild_Member = None
    token: str = ''
    version: int = 0
    async def pong(self):
        response = Interaction_Response(
            type=Interaction_Response_Type.PONG,
            data=None
        )
        return await self._Client.create_interaction_response(self.id, self.token, response)
    async def ack(self):
        response = Interaction_Response(
            type=Interaction_Response_Type.ACKNOWLEDGE,
            data=None
        )
        return await self._Client.create_interaction_response(self.id, self.token, response)
    async def respond(self, response: Interaction_Response):
        return await self._Client.create_interaction_response(self.id, self.token, response)
    async def edit_response(self, content: str = None, embeds: List[Embed] = None, allowed_mentions: Allowed_Mentions = None):
        return await self._Client.edit_original_interaction_response(self._Client.application.id, self.token, content, embeds, allowed_mentions)
    async def delete_response(self):
        return await self._Client.delete_original_interaction_response(self._Client.application.id, self.token)
    async def reply(self, content: str = None, username: str = None, avatar_url: str = None, tts: bool = None, file: bytes = None, filename=None, embeds: List[Embed] = None, payload_json: str = None, allowed_mentions: Allowed_Mentions = [], wait: bool = False):
        return await self._Client.create_followup_message(self._Client.application.id, self.token, wait=wait, content=content, username=username, avatar_url=avatar_url, tts=tts, file=file, filename=filename, embeds=embeds, payload_json=payload_json, allowed_mentions=allowed_mentions)
    async def edit(self, message_id, content: str = None, embeds: List[Embed] = None, allowed_mentions: Allowed_Mentions = []):
        return await self._Client.edit_followup_message(self._Client.application.id, self.token, message_id, content, embeds, allowed_mentions)
    async def delete(self, message_id):
        return await self._Client.delete_followup_message(self._Client.application.id, self.token, message_id)


class Interaction_Type(Enum):
    PING = 1
    APPLICATIONCOMMAND = 2


@dataclass
class Application_Command_Interaction_Data(DiscordObject):
    '''
    Params:
        :id: the ID of the invoked command
        :name: the name of the invoked command
        :options: the params + values from the user
    '''
    id: Snowflake = 0
    name: str = ""
    options: List[Application_Command_Interaction_Data_Option] = list


@dataclass
class Application_Command_Interaction_Data_Option(DiscordObject):
    '''
    Params:
        :name: the name of the parameter
        :value: the value of the pair
        :options: present if this option is a group
    '''
    name: str = ""
    value: dict = dict
    options: List[Application_Command_Interaction_Data_Option] = list


@dataclass
class Interaction_Response(DiscordObject):
    '''
    Params:
        :type: the type of response
        :data: an optional response message
    '''
    type: Interaction_Response_Type = None
    data: Interaction_Application_Command_Callback_Data = None


class Interaction_Response_Type(Enum):
    '''
    Params:
        :Pong: ACK a `Ping`
        :Acknowledge: ACK a command without sending a message, eating the user's input
        :ChannelMessage: respond with a message, eating the user's input
        :ChannelMessageWithSource: respond with a message, showing the user's input
        :AcknowledgeWithSource: ACK a command without sending a message, showing the user's input
    '''
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNELMESSAGE = 3
    CHANNELMESSAGEWITHSOURCE = 4
    ACKNOWLEDGEWITHSOURCE = 5


@dataclass
class Interaction_Application_Command_Callback_Data(DiscordObject):
    '''
    Params:
        :tts: is the response TTS
        :content: message content
        :embeds: supports up to 10 embeds
        :allowed_mentions: Allowed_Mentions
    '''
    tts: bool = False
    content: str = None
    embeds: List[Embed] = None
    allowed_mentions: Allowed_Mentions = None


class Gateway_Commands(Events):
    '''
    Events are payloads sent over the socket to a client that correspond to events in Discord.
    
    Params:
        :Identify: triggers the initial handshake with the gateway
        :Resume: resumes a dropped gateway connection
        :Heartbeat: maintains an active gateway connection
        :Request_Guild_Members: requests members for a guild
        :Update_Voice_State: joins, moves,
        :Update_Status: updates a client's presence
    '''
    Identify = staticmethod(Identify)
    Resume = staticmethod(Resume)
    Heartbeat = staticmethod(int)
    Request_Guild_Members = staticmethod(Guild_Request_Members)
    Update_Voice_State = staticmethod(Gateway_Voice_State_Update)
    Update_Status = staticmethod(Gateway_Status_Update)


class Gateway_Events(Events):
    '''
    Params:
        :Hello: defines the heartbeat interval
        :Ready: contains the initial state information
        :Resumed: Resume
        :Reconnect: server is going away, client should reconnect to gateway and resume
        :Invalid_Session: Identify
        :Channel_Create: new guild channel created
        :Channel_Update: channel was updated
        :Channel_Delete: channel was deleted
        :Channel_Pins_Update: message was pinned
        :Guild_Create: lazy-load for unavailable guild, guild became available,
        :Guild_Update: guild was updated
        :Guild_Delete: guild became unavailable,
        :Guild_Ban_Add: user was banned from a guild
        :Guild_Ban_Remove: user was unbanned from a guild
        :Guild_Emojis_Update: guild emojis were updated
        :Guild_Integrations_Update: guild integration was updated
        :Guild_Member_Add: new user joined a guild
        :Guild_Member_Remove: user was removed from a guild
        :Guild_Member_Update: guild member was updated
        :Guild_Members_Chunk: Request_Guild_Members
        :Guild_Role_Create: guild role was created
        :Guild_Role_Update: guild role was updated
        :Guild_Role_Delete: guild role was deleted
        :Invite_Create: invite to a channel was created
        :Invite_Delete: invite to a channel was deleted
        :Message_Create: message was created
        :Message_Update: message was edited
        :Message_Delete: message was deleted
        :Message_Delete_Bulk: multiple messages were deleted at once
        :Message_Reaction_Add: user reacted to a message
        :Message_Reaction_Remove: user removed a reaction from a message
        :Message_Reaction_Remove_All: all reactions were explicitly removed from a message
        :Message_Reaction_Remove_Emoji: all reactions for a given emoji were explicitly removed from a message
        :Presence_Update: user was updated
        :Typing_Start: user started typing in a channel
        :User_Update: properties about the user changed
        :Voice_State_Update: someone joined, left,
        :Voice_Server_Update: guild's voice server was updated
        :Webhooks_Update: guild channel webhook was created, update,
        :Interaction_Create: Slash_Command
    '''
    Hello = staticmethod(Hello)
    Ready = staticmethod(Ready)
    Resumed = staticmethod(Resume)
    Reconnect = staticmethod(dict)
    Invalid_Session = staticmethod(bool)
    Channel_Create = staticmethod(Channel)
    Channel_Update = staticmethod(Channel)
    Channel_Delete = staticmethod(Channel)
    Channel_Pins_Update = staticmethod(Channel_Pins_Update)
    Guild_Create = staticmethod(Guild)
    Guild_Update = staticmethod(Guild)
    Guild_Delete = staticmethod(dict)
    Guild_Ban_Add = staticmethod(Guild_Ban_Add)
    Guild_Ban_Remove = staticmethod(Guild_Ban_Remove)
    Guild_Emojis_Update = staticmethod(Guild_Emojis_Update)
    Guild_Integrations_Update = staticmethod(Guild_Integrations_Update)
    Guild_Member_Add = staticmethod(Guild_Member_Add)
    Guild_Member_Remove = staticmethod(Guild_Member_Remove)
    Guild_Member_Update = staticmethod(Guild_Member_Update)
    Guild_Members_Chunk = staticmethod(Guild_Members_Chunk)
    Guild_Role_Create = staticmethod(Guild_Role_Create)
    Guild_Role_Update = staticmethod(Guild_Role_Update)
    Guild_Role_Delete = staticmethod(Guild_Role_Delete)
    Invite_Create = staticmethod(Invite_Create)
    Invite_Delete = staticmethod(Invite_Delete)
    Message_Create = staticmethod(Message)
    Message_Update = staticmethod(Message)
    Message_Delete = staticmethod(Message_Delete)
    Message_Delete_Bulk = staticmethod(Message_Delete_Bulk)
    Message_Reaction_Add = staticmethod(Message_Reaction_Add)
    Message_Reaction_Remove = staticmethod(Message_Reaction_Remove)
    Message_Reaction_Remove_All = staticmethod(Message_Reaction_Remove_All)
    Message_Reaction_Remove_Emoji = staticmethod(Message_Reaction_Remove_Emoji)
    Presence_Update = staticmethod(Presence_Update)
    Typing_Start = staticmethod(Typing_Start)
    User_Update = staticmethod(User)
    Voice_State_Update = staticmethod(Voice_State)
    Voice_Server_Update = staticmethod(Voice_Server_Update)
    Webhooks_Update = staticmethod(Webhook_Update)
    Interaction_Create = staticmethod(Interaction)


class Endpoints:
    async def api_call(self, path: str, method: str = "GET", reason: str = None, **kwargs):
        raise NotImplementedError
    
    @Permissions("VIEW_AUDIT_LOG")
    async def get_guild_audit_log(self, guild_id: Snowflake, user_id: Snowflake, action_type: int, before: int, limit: int) -> Audit_Log:
        '''
        Returns an [audit log](https://discord.com/developers/docs/resources/audit_log#audit-log-object) object for the guild. Requires the 'VIEW_AUDIT_LOG' permission.

        Params:
            :user_id: filter the log for actions made by a user
            :action_type: Audit_Log_Event
            :before: filter the log before a certain entry id
            :limit: how many entries are returned
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/audit-logs", method = "GET", params = {"user_id": user_id, "action_type": action_type, "before": before, "limit": limit})
        return Audit_Log(**r)

    async def get_channel(self, channel_id: Snowflake) -> Channel:
        '''
        Get a channel by ID. Returns a [channel](https://discord.com/developers/docs/resources/channel#channel-object) object.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}", method = "GET")
        return Channel(**r)

    @Permissions("MANAGE_CHANNELS")
    async def modify_channel(self, channel_id: Snowflake, name: str, type: int, position: int=None, topic: str=None, nsfw: bool=None, rate_limit_per_user: int=None, bitrate: int=None, user_limit: int=None, permission_overwrites: List[Overwrite]=None, parent_id: Snowflake=None) -> Channel:
        '''
        Update a channel's settings. Requires the `MANAGE_CHANNELS` permission for the guild. Returns a [channel](https://discord.com/developers/docs/resources/channel#channel-object) on success, and a 400 BAD REQUEST on invalid parameters. Fires a [Channel Update](https://discord.com/developers/docs/topics/gateway#channel-update) Gateway event. If modifying a category, individual [Channel Update](https://discord.com/developers/docs/topics/gateway#channel-update) events will fire for each child channel that also changes. All JSON parameters are optional.

        Params:
            :name: 2-100 character channel name
            :type: Type_Of_Channel
            :position: the position of the channel in the left-hand listing
            :topic: 0-1024 character channel topic
            :nsfw: whether the channel is nsfw
            :rate_limit_per_user: amount of seconds a user has to wait before sending another message
            :bitrate: the bitrate
            :user_limit: the user limit of the voice channel; 0 refers to no limit, 1 to 99 refers to a user limit
            :permission_overwrites: channel
            :parent_id: id of the new parent category for a channel
        '''
        r = await self.api_call(path = f"/channels/{channel_id}", method = "PATCH", json = {"name": name, "type": type, "position": position, "topic": topic, "nsfw": nsfw, "rate_limit_per_user": rate_limit_per_user, "bitrate": bitrate, "user_limit": user_limit, "permission_overwrites": permission_overwrites, "parent_id": parent_id})
        return Channel(**r)

    @Permissions("MANAGE_CHANNELS")
    async def delete_close_channel(self, channel_id: Snowflake) -> Channel:
        '''
        Delete a channel, or close a private message. Requires the `MANAGE_CHANNELS` permission for the guild. Deleting a category does not delete its child channels; they will have their `parent_id` removed and a [Channel Update](https://discord.com/developers/docs/topics/gateway#channel-update) Gateway event will fire for each of them. Returns a [channel](https://discord.com/developers/docs/resources/channel#channel-object) object on success. Fires a [Channel Delete](https://discord.com/developers/docs/topics/gateway#channel-delete) Gateway event.
        > warn
        > Deleting a guild channel cannot be undone. Use this with caution, as it is impossible to undo this action when performed on a guild channel. In contrast, when used with a private message, it is possible to undo the action by opening a private message with the recipient again.
        > info
        > For Community guilds, the Rules or Guidelines channel and the Community Updates channel cannot be deleted.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}", method = "DELETE")
        return Channel(**r)

    @Permissions("VIEW_CHANNEL")
    async def get_channel_messages(self, channel_id: Snowflake, around: int=None, before: int=None, after: int=None, limit: int=50) -> List[Message]:
        '''
        Returns the messages for a channel. If operating on a guild channel, this endpoint requires the `VIEW_CHANNEL` permission to be present on the current user. If the current user is missing the 'READ_MESSAGE_HISTORY' permission in the channel then this will return no messages (since they cannot read the message history). Returns an array of [message](https://discord.com/developers/docs/resources/channel#message-object) objects on success.
        > info
        > The before, after, and around keys are mutually exclusive, only one may be passed at a time.

        Params:
            :around: get messages around this message ID
            :before: get messages before this message ID
            :after: get messages after this message ID
            :limit: max number of messages to return
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/messages", method = "GET", params = {"around": around, "before": before, "after": after, "limit": limit})
        return [Message(**i) for i in r]

    @Permissions("READ_MESSAGE_HISTORY")
    async def get_channel_message(self, channel_id: Snowflake, message_id: Snowflake) -> Message:
        '''
        Returns a specific message in the channel. If operating on a guild channel, this endpoint requires the 'READ_MESSAGE_HISTORY' permission to be present on the current user. Returns a [message](https://discord.com/developers/docs/resources/channel#message-object) object on success.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}", method = "GET")
        return Message(**r)

    @Permissions("SEND_MESSAGES", "READ_MESSAGE_HISTORY")
    async def create_message(self, channel_id: Snowflake=None, content: str=None, nonce: int=None, tts: bool=None, file: bytes=None, embed: Embed=None, payload_json: str=None, allowed_mentions: Allowed_Mentions=None, message_reference: Message_Reference=None) -> Message:
        '''
        > warn
        > Before using this endpoint, you must connect to and identify with a [gateway](https://discord.com/developers/docs/topics/gateway#gateways) at least once.
        > warn
        > Discord may strip certain characters from message content, like invalid unicode characters or characters which cause unexpected message formatting. If you are passing user-generated strings into message content, consider sanitizing the data to prevent unexpected behavior and utilizing `allowed_mentions` to prevent unexpected mentions.
        Post a message to a guild text or DM channel. If operating on a guild channel, this endpoint requires the `SEND_MESSAGES` permission to be present on the current user. If the `tts` field is set to `true`, the `SEND_TTS_MESSAGES` permission is required for the message to be spoken. Returns a [message](https://discord.com/developers/docs/resources/channel#message-object) object. Fires a [Message Create](https://discord.com/developers/docs/topics/gateway#message-create) Gateway event. See [message formatting](https://discord.com/developers/docs/reference#message-formatting) for more information on how to properly format messages.
        The maximum request size when sending a message is 8MB.
        This endpoint supports requests with `Content-Type`s of both `application/json` and `multipart/form-data`. You must however use `multipart/form-data` when uploading files. Note that when sending `multipart/form-data` requests the `embed` field cannot be used, however you can pass a JSON encoded body as form value for `payload_json`, where additional request parameters such as `embed` can be set.
        > info
        > Note that when sending `application/json` you must send at least one of `content` or `embed`, and when sending `multipart/form-data`, you must send at least one of `content`, `embed` or `file`. For a `file` attachment, the `Content-Disposition` subpart header MUST contain a `filename` parameter.
        You may create a message as a reply to another message. To do so, include a [`message_reference`](https://discord.com/developers/docs/resources/channel#message-object-message-reference-structure) with a `message_id`. This requires the `READ_MESSAGE_HISTORY` permission, and the referenced message must exist and cannot be a system message. The `channel_id` and `guild_id` in the `message_reference` are optional, but will be validated if provided.

        Params:
            :content: the message contents
            :nonce: a nonce that can be used for optimistic message sending
            :tts: true if this is a TTS message
            :file: the contents of the file being sent
            :embed: embedded `rich` content
            :payload_json: JSON encoded body of any additional request fields.
            :allowed_mentions: allowed mentions for a message
            :message_reference: include to make your message a reply
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/messages", method = "POST", json = {"content": content, "nonce": nonce, "tts": tts, "file": file, "embed": embed, "payload_json": payload_json, "allowed_mentions": allowed_mentions, "message_reference": message_reference})
        return Message(**r)

    @Permissions("SEND_MESSAGES")
    async def crosspost_message(self, channel_id: Snowflake, message_id: Snowflake) -> Message:
        '''
        Crosspost a message in a News Channel to following channels. This endpoint requires the 'SEND_MESSAGES' permission, if the current user sent the message, or additionally the 'MANAGE_MESSAGES' permission, for all other messages, to be present for the current user.
        Returns a [message](https://discord.com/developers/docs/resources/channel#message-object) object.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/crosspost", method = "POST")
        return Message(**r)
    
    @Permissions("READ_MESSAGE_HISTORY", "ADD_REACTIONS")
    async def create_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: str) -> None:
        '''
        Create a reaction for the message. This endpoint requires the 'READ_MESSAGE_HISTORY' permission to be present on the current user. Additionally, if nobody else has reacted to the message using this emoji, this endpoint requires the 'ADD_REACTIONS' permission to be present on the current user. Returns a 204 empty response on success.
        The `emoji` must be [URL Encoded](https:#/en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`.
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me", method = "PUT")
    
    async def delete_own_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: int) -> None:
        '''
        Delete a reaction the current user has made for the message. Returns a 204 empty response on success.
        The `emoji` must be [URL Encoded](https:#/en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`.
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me", method = "DELETE")
    
    @Permissions("MANAGE_MESSAGES")
    async def delete_user_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: int, user_id: Snowflake) -> None:
        '''
        Deletes another user's reaction. This endpoint requires the 'MANAGE_MESSAGES' permission to be present on the current user. Returns a 204 empty response on success.
        The `emoji` must be [URL Encoded](https:#/en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`.
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}", method = "DELETE")
    
    async def get_reactions(self, channel_id: Snowflake, message_id: Snowflake, emoji: int, before: int=None, after: int=None, limit: int=25) -> List[User]:
        '''
        Get a list of users that reacted with this emoji. Returns an array of [user](https://discord.com/developers/docs/resources/user#user-object) objects on success.
        The `emoji` must be [URL Encoded](https:#/en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`.

        Params:
            :before: get users before this user ID
            :after: get users after this user ID
            :limit: max number of users to return
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", method = "GET", params = {"before": before, "after": after, "limit": limit})
        return [User(**i) for i in r]

    @Permissions("MANAGE_MESSAGES")
    async def delete_all_reactions(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        '''
        Deletes all reactions on a message. This endpoint requires the 'MANAGE_MESSAGES' permission to be present on the current user. Fires a [Message Reaction Remove All](https://discord.com/developers/docs/topics/gateway#message-reaction-remove-all) Gateway event.
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/reactions", method = "DELETE")

    @Permissions("MANAGE_MESSAGES")
    async def delete_all_reactions_for_emoji(self, channel_id: Snowflake, message_id: Snowflake, emoji: int) -> None:
        '''
        Deletes all the reactions for a given emoji on a message. This endpoint requires the `MANAGE_MESSAGES` permission to be present on the current user. Fires a [Message Reaction Remove Emoji](https://discord.com/developers/docs/topics/gateway#message-reaction-remove-emoji) Gateway event.
        The `emoji` must be [URL Encoded](https:#/en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`.
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", method = "DELETE")

    async def edit_message(self, channel_id: Snowflake, message_id: Snowflake, content: str, embed: Embed, flags: int, allowed_mentions: Allowed_Mentions) -> Message:
        '''
        Edit a previously sent message. The fields `content`, `embed`, `allowed_mentions` and `flags` can be edited by the original message author. Other users can only edit `flags` and only if they have the `MANAGE_MESSAGES` permission in the corresponding channel. When specifying flags, ensure to include all previously set flags/bits in addition to ones that you are modifying. Only `flags` documented in the table below may be modified by users (unsupported flag changes are currently ignored without error).
        Returns a [message](https://discord.com/developers/docs/resources/channel#message-object) object. Fires a [Message Update](https://discord.com/developers/docs/topics/gateway#message-update) Gateway event.
        > info
        > All parameters to this endpoint are optional and nullable.

        Params:
            :content: the new message contents
            :embed: embedded `rich` content
            :flags: Flags
            :allowed_mentions: allowed mentions for the message
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}", method = "PATCH", json = {"content": content, "embed": embed, "flags": flags, "allowed_mentions": allowed_mentions})
        return Message(**r)

    @Permissions("MANAGE_MESSAGES")
    async def delete_message(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        '''
        Delete a message. If operating on a guild channel and trying to delete a message that was not sent by the current user, this endpoint requires the `MANAGE_MESSAGES` permission. Returns a 204 empty response on success. Fires a [Message Delete](https://discord.com/developers/docs/topics/gateway#message-delete) Gateway event.
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/{message_id}", method = "DELETE")

    @Permissions("MANAGE_MESSAGES")
    async def bulk_delete_messages(self, channel_id: Snowflake, messages: List[int]) -> None:
        '''
        Delete multiple messages in a single request. This endpoint can only be used on guild channels and requires the `MANAGE_MESSAGES` permission. Returns a 204 empty response on success. Fires a [Message Delete Bulk](https://discord.com/developers/docs/topics/gateway#message-delete-bulk) Gateway event.
        Any message IDs given that do not exist or are invalid will count towards the minimum and maximum message count (currently 2 and 100 respectively).
        > warn
        > This endpoint will not delete messages older than 2 weeks, and will fail with a 400 BAD REQUEST if any message provided is older than that or if any duplicate message IDs are provided.

        Params:
            :messages: an  message ids to delete
        '''
        await self.api_call(path = f"/channels/{channel_id}/messages/bulk-delete", method = "POST", json = {"messages": messages})

    @Permissions("MANAGE_ROLES")
    async def edit_channel_permissions(self, channel_id: Snowflake, overwrite_id: Snowflake, allow: str, deny: str, type: int) -> None:
        '''
        Edit the channel permission overwrites for a user or role in a channel. Only usable for guild channels. Requires the `MANAGE_ROLES` permission. Returns a 204 empty response on success. For more information about permissions, see [permissions](https://discord.com/developers/docs/topics/permissions#permissions).
        
        Params:
            :allow: the bitwise value of all allowed permissions
            :deny: the bitwise value of all disallowed permissions
            :type: 0 for a role
        '''
        await self.api_call(path = f"/channels/{channel_id}/permissions/{overwrite_id}", method = "PUT", json = {"allow": allow, "deny": deny, "type": type})
    
    @Permissions("MANAGE_CHANNELS")
    async def get_channel_invites(self, channel_id: Snowflake) -> List[Invite]:
        '''
        Returns a list of [invite](https://discord.com/developers/docs/resources/invite#invite-object) objects (with [invite metadata](https://discord.com/developers/docs/resources/invite#invite-metadata-object)) for the channel. Only usable for guild channels. Requires the `MANAGE_CHANNELS` permission.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/invites", method = "GET")
        return [Invite(**i) for i in r]
    
    @Permissions("CREATE_INSTANT_INVITE")
    async def create_channel_invite(self, channel_id: Snowflake, max_age: int=86400, max_uses: int=0, temporary: bool=False, unique: bool=False, target_user: str=None, target_user_type: int=None) -> Invite:
        '''
        Create a new [invite](https://discord.com/developers/docs/resources/invite#invite-object) object for the channel. Only usable for guild channels. Requires the `CREATE_INSTANT_INVITE` permission. All JSON parameters for this route are optional, however the request body is not. If you are not sending any fields, you still have to send an empty JSON object (`{}`). Returns an [invite](https://discord.com/developers/docs/resources/invite#invite-object) object. Fires an [Invite Create](https://discord.com/developers/docs/topics/gateway#invite-create) Gateway event.
        
        Params:
            :max_age: duration of invite in seconds before expiry,
            :max_uses: max number of uses
            :temporary: whether this invite only grants temporary membership
            :unique: if true, don't try to reuse a similar invite
            :target_user: the target user id for this invite
            :target_user_type: the type of target user for this invite
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/invites", method = "POST", json = {"max_age": max_age, "max_uses": max_uses, "temporary": temporary, "unique": unique, "target_user": target_user, "target_user_type": target_user_type})
        return Invite(**r)
    
    @Permissions("MANAGE_ROLES")
    async def delete_channel_permission(self, channel_id: Snowflake, overwrite_id: Snowflake) -> None:
        '''
        Delete a channel permission overwrite for a user or role in a channel. Only usable for guild channels. Requires the `MANAGE_ROLES` permission. Returns a 204 empty response on success. For more information about permissions, see [permissions](https://discord.com/developers/docs/topics/permissions#permissions)
        '''
        await self.api_call(path = f"/channels/{channel_id}/permissions/{overwrite_id}", method = "DELETE")
    
    @Permissions("MANAGE_WEBHOOKS")
    async def follow_news_channel(self, channel_id: Snowflake, webhook_channel_id: Snowflake) -> Followed_Channel:
        '''
        Follow a News Channel to send messages to a target channel. Requires the `MANAGE_WEBHOOKS` permission in the target channel. Returns a [followed channel](https://discord.com/developers/docs/resources/channel#followed-channel-object) object.
        
        Params:
            :webhook_channel_id: id of target channel
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/followers", method = "POST", json = {"webhook_channel_id": webhook_channel_id})
        return Followed_Channel(**r)
    
    async def trigger_typing_indicator(self, channel_id: Snowflake) -> None:
        '''
        Post a typing indicator for the specified channel. Generally bots should **not** implement this route. However, if a bot is responding to a command and expects the computation to take a few seconds, this endpoint may be called to let the user know that the bot is processing their message. Returns a 204 empty response on success. Fires a [Typing Start](https://discord.com/developers/docs/topics/gateway#typing-start) Gateway event.
        '''
        await self.api_call(path = f"/channels/{channel_id}/typing", method = "POST")
    
    async def get_pinned_messages(self, channel_id: Snowflake) -> Message:
        '''
        Returns all pinned messages in the channel as an array of [message](https://discord.com/developers/docs/resources/channel#message-object) objects.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/pins", method = "GET")
        return Message(**r)
    
    @Permissions("MANAGE_MESSAGES")
    async def add_pinned_channel_message(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        '''
        Pin a message in a channel. Requires the `MANAGE_MESSAGES` permission. Returns a 204 empty response on success.
        > warn
        > The max pinned messages is 50.
        '''
        await self.api_call(path = f"/channels/{channel_id}/pins/{message_id}", method = "PUT")
    
    @Permissions("MANAGE_MESSAGES")
    async def delete_pinned_channel_message(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        '''
        Delete a pinned message in a channel. Requires the `MANAGE_MESSAGES` permission. Returns a 204 empty response on success.
        '''
        await self.api_call(path = f"/channels/{channel_id}/pins/{message_id}", method = "DELETE")
    
    async def group_dm_add_recipient(self, channel_id: Snowflake, user_id: Snowflake, access_token: str, nick: str) -> None:
        '''
        Adds a recipient to a Group DM using their access token
        
        Params:
            :access_token: access token of a user that has granted your app the `gdm.join` scope
            :nick: nickname of the user being added
        '''
        await self.api_call(path = f"/channels/{channel_id}/recipients/{user_id}", method = "PUT", json = {"access_token": access_token, "nick": nick})
    
    async def group_dm_remove_recipient(self, channel_id: Snowflake, user_id: Snowflake) -> None:
        '''
        Removes a recipient from a Group DM
        '''
        await self.api_call(path = f"/channels/{channel_id}/recipients/{user_id}", method = "DELETE")
    
    async def list_guild_emojis(self, guild_id: Snowflake) -> List[Emoji]:
        '''
        Returns a list of [emoji](https://discord.com/developers/docs/resources/emoji#emoji-object) objects for the given guild.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/emojis", method = "GET")
        return [Emoji(**i) for i in r]
    
    async def get_guild_emoji(self, guild_id: Snowflake, emoji_id: Snowflake) -> Emoji:
        '''
        Returns an [emoji](https://discord.com/developers/docs/resources/emoji#emoji-object) object for the given guild and emoji IDs.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/emojis/{emoji_id}", method = "GET")
        return Emoji(**r)
    
    @Permissions("MANAGE_EMOJIS")
    async def create_guild_emoji(self, guild_id: Snowflake, name: str, image: str, roles: List[int]) -> Emoji:
        '''
        Create a new emoji for the guild. Requires the `MANAGE_EMOJIS` permission. Returns the new [emoji](https://discord.com/developers/docs/resources/emoji#emoji-object) object on success. Fires a [Guild Emojis Update](https://discord.com/developers/docs/topics/gateway#guild-emojis-update) Gateway event.
        > warn
        > Emojis and animated emojis have a maximum file size of 256kb. Attempting to upload an emoji larger than this limit will fail and return 400 Bad Request and an error message, but not a [JSON status code](https://discord.com/developers/docs/topics/opcodes_and_status_codes#json).
        
        Params:
            :name: name of the emoji
            :image: the 128x128 emoji image
            :roles: roles for which this emoji will be whitelisted
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/emojis", method = "POST", json = {"name": name, "image": image, "roles": roles})
        return Emoji(**r)
    
    @Permissions("MANAGE_EMOJIS")
    async def modify_guild_emoji(self, guild_id: Snowflake, emoji_id: Snowflake, name: str, roles: List[int]=None) -> Emoji:
        '''
        Modify the given emoji. Requires the `MANAGE_EMOJIS` permission. Returns the updated [emoji](https://discord.com/developers/docs/resources/emoji#emoji-object) object on success. Fires a [Guild Emojis Update](https://discord.com/developers/docs/topics/gateway#guild-emojis-update) Gateway event.
        > info
        > All parameters to this endpoint are optional.
        
        Params:
            :name: name of the emoji
            :roles: roles to which this emoji will be whitelisted
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/emojis/{emoji_id}", method = "PATCH", json = {"name": name, "roles": roles})
        return Emoji(**r)
    
    @Permissions("MANAGE_EMOJIS")
    async def delete_guild_emoji(self, guild_id: Snowflake, emoji_id: Snowflake) -> None:
        '''
        Delete the given emoji. Requires the `MANAGE_EMOJIS` permission. Returns `204 No Content` on success. Fires a [Guild Emojis Update](https://discord.com/developers/docs/topics/gateway#guild-emojis-update) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/emojis/{emoji_id}", method = "DELETE")
    
    async def create_guild(self, name: str, region: str=None, icon: str=None, verification_level: int=None, default_message_notifications: int=None, explicit_content_filter: int=None, roles: List[Role]=None, channels: List[Channel]=None, afk_channel_id: Snowflake=None, afk_timeout: int=None, system_channel_id: Snowflake=None) -> Guild:
        '''
        Create a new guild. Returns a [guild](https://discord.com/developers/docs/resources/guild#guild-object) object on success. Fires a [Guild Create](https://discord.com/developers/docs/topics/gateway#guild-create) Gateway event.
        > warn
        > This endpoint can be used only by bots in less than 10 guilds.
        
        Params:
            :name: name of the guild
            :region: Voice_Region
            :icon: base64 128x128 image for the guild icon
            :verification_level: Verification_Level
            :default_message_notifications: Message_Notification_Level
            :explicit_content_filter: Explicit_Content_Filter_Level
            :roles: new guild roles
            :channels: new guild's channels
            :afk_channel_id: id for afk channel
            :afk_timeout: afk timeout in seconds
            :system_channel_id: the id of the channel where guild notices such as welcome messages and boost events are posted
        '''
        r = await self.api_call(path = f"/guilds", method = "POST", json = {"name": name, "region": region, "icon": icon, "verification_level": verification_level, "default_message_notifications": default_message_notifications, "explicit_content_filter": explicit_content_filter, "roles": roles, "channels": channels, "afk_channel_id": afk_channel_id, "afk_timeout": afk_timeout, "system_channel_id": system_channel_id})
        return Guild(**r)
    
    async def get_guild(self, guild_id: Snowflake, with_counts: bool=False) -> Guild:
        '''
        Returns the [guild](https://discord.com/developers/docs/resources/guild#guild-object) object for the given id. If `with_counts` is set to `true`, this endpoint will also return `approximate_member_count` and `approximate_presence_count` for the guild.
        
        Params:
            :with_counts: when `true`, will return approximate member and presence counts for the guild
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}", method = "GET", params = {"with_counts": with_counts})
        return Guild(**r)
    
    async def get_guild_preview(self, guild_id: Snowflake) -> Guild_Preview:
        '''
        Returns the [guild preview](https://discord.com/developers/docs/resources/guild#guild-preview-object) object for the given id. If the user is not in the guild, then the guild must be Discoverable.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/preview", method = "GET")
        return Guild_Preview(**r)
    
    @Permissions("MANAGE_GUILD")
    async def modify_guild(self, guild_id: Snowflake, name: str, afk_timeout: int, icon: str, owner_id: Snowflake, splash: str, banner: str, region: str=None, verification_level: int=None, default_message_notifications: int=None, explicit_content_filter: int=None, afk_channel_id: Snowflake=None, system_channel_id: Snowflake=None, rules_channel_id: Snowflake=None, public_updates_channel_id: Snowflake=None, preferred_locale: str=None) -> Guild:
        '''
        Modify a guild's settings. Requires the `MANAGE_GUILD` permission. Returns the updated [guild](https://discord.com/developers/docs/resources/guild#guild-object) object on success. Fires a [Guild Update](https://discord.com/developers/docs/topics/gateway#guild-update) Gateway event.
        > info
        > All parameters to this endpoint are optional
        
        Params:
            :name: guild name
            :region: Voice_Region
            :verification_level: Verification_Level
            :default_message_notifications: Message_Notification_Level
            :explicit_content_filter: Explicit_Content_Filter_Level
            :afk_channel_id: id for afk channel
            :afk_timeout: afk timeout in seconds
            :icon: base64 1024x1024 png/jpeg/gif image for the guild icon
            :owner_id: user id to transfer guild ownership to
            :splash: base64 16:9 png/jpeg image for the guild splash
            :banner: base64 16:9 png/jpeg image for the guild banner
            :system_channel_id: the id of the channel where guild notices such as welcome messages and boost events are posted
            :rules_channel_id: the id of the channel where Community guilds display rules and/or guidelines
            :public_updates_channel_id: the id of the channel where admins and moderators of Community guilds receive notices from Discord
            :preferred_locale: the preferred locale of a Community guild used in server discovery and notices from Discord; defaults to "en-US"
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}", method = "PATCH", json = {"name": name, "region": region, "verification_level": verification_level, "default_message_notifications": default_message_notifications, "explicit_content_filter": explicit_content_filter, "afk_channel_id": afk_channel_id, "afk_timeout": afk_timeout, "icon": icon, "owner_id": owner_id, "splash": splash, "banner": banner, "system_channel_id": system_channel_id, "rules_channel_id": rules_channel_id, "public_updates_channel_id": public_updates_channel_id, "preferred_locale": preferred_locale})
        return Guild(**r)
    
    async def delete_guild(self, guild_id: Snowflake) -> None:
        '''
        Delete a guild permanently. User must be owner. Returns `204 No Content` on success. Fires a [Guild Delete](https://discord.com/developers/docs/topics/gateway#guild-delete) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}", method = "DELETE")
    
    async def get_guild_channels(self, guild_id: Snowflake) -> List[Channel]:
        '''
        Returns a list of guild [channel](https://discord.com/developers/docs/resources/channel#channel-object) objects.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/channels", method = "GET")
        return [Channel(**i) for i in r]
    
    @Permissions("MANAGE_CHANNELS")
    async def create_guild_channel(self, guild_id: Snowflake, name: str, type: int, topic: str, bitrate: int, user_limit: int, rate_limit_per_user: int, position: int, permission_overwrites: List[Overwrite], parent_id: Snowflake, nsfw: bool) -> Channel:
        '''
        Create a new [channel](https://discord.com/developers/docs/resources/channel#channel-object) object for the guild. Requires the `MANAGE_CHANNELS` permission. Returns the new [channel](https://discord.com/developers/docs/resources/channel#channel-object) object on success. Fires a [Channel Create](https://discord.com/developers/docs/topics/gateway#channel-create) Gateway event.
        > info
        > All parameters to this endpoint are optional excluding 'name'
        
        Params:
            :name: channel name
            :type: Type_Of_Channel
            :topic: channel topic
            :bitrate: the bitrate
            :user_limit: the user limit of the voice channel
            :rate_limit_per_user: amount of seconds a user has to wait before sending another message
            :position: sorting position of the channel
            :permission_overwrites: the channel's permission overwrites
            :parent_id: id of the parent category for a channel
            :nsfw: whether the channel is nsfw
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/channels", method = "POST", json = {"name": name, "type": type, "topic": topic, "bitrate": bitrate, "user_limit": user_limit, "rate_limit_per_user": rate_limit_per_user, "position": position, "permission_overwrites": permission_overwrites, "parent_id": parent_id, "nsfw": nsfw})
        return Channel(**r)

    async def modify_guild_channel_positions(self, guild_id: Snowflake, id: Snowflake, position: int=None) -> None:
        '''
        Modify the positions of a set of [channel](https://discord.com/developers/docs/resources/channel#channel-object) objects for the guild. Requires `MANAGE_CHANNELS` permission. Returns a 204 empty response on success. Fires multiple [Channel Update](https://discord.com/developers/docs/topics/gateway#channel-update) Gateway events.
        > info
        > Only channels to be modified are required, with the minimum being a swap between at least two channels.
        This endpoint takes a JSON array of parameters in the following format:

        Params:
            :id: channel id
            :position: sorting position of the channel
        '''
        await self.api_call(path = f"/guilds/{guild_id}/channels", method = "PATCH", json = {"id": id, "position": position})

    async def get_guild_member(self, guild_id: Snowflake, user_id: Snowflake) -> Guild_Member:
        '''
        Returns a [guild member](https://discord.com/developers/docs/resources/guild#guild-member-object) object for the specified user.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/members/{user_id}", method = "GET")
        return Guild_Member(**r)

    async def list_guild_members(self, guild_id: Snowflake, limit: int=1, after: int=0) -> List[Guild_Member]:
        '''
        Returns a list of [guild member](https://discord.com/developers/docs/resources/guild#guild-member-object) objects that are members of the guild.
        > warn
        > In the future, this endpoint will be restricted in line with our [Privileged Intents](https://discord.com/developers/docs/topics/gateway#privileged-intents)
        > info
        > All parameters to this endpoint are optional

        Params:
            :limit: max number of members to return
            :after: the highest user id in the previous page
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/members", method = "GET", params = {"limit": limit, "after": after})
        return [Guild_Member(**i) for i in r]

    async def add_guild_member(self, guild_id: Snowflake, user_id: Snowflake, access_token: str, nick: str, roles: List[int], mute: bool, deaf: bool) -> Guild_Member:
        '''
        Adds a user to the guild, provided you have a valid oauth2 access token for the user with the `guilds.join` scope. Returns a 201 Created with the [guild member](https://discord.com/developers/docs/resources/guild#guild-member-object) as the body, or 204 No Content if the user is already a member of the guild. Fires a [Guild Member Add](https://discord.com/developers/docs/topics/gateway#guild-member-add) Gateway event.
        > info
        > All parameters to this endpoint except for `access_token` are optional.
        > info
        > The Authorization header must be a Bot token (belonging to the same application used for authorization), and the bot must be a member of the guild with `CREATE_INSTANT_INVITE` permission.

        Params:
            :access_token: an oauth2 access token granted with the `guilds.join` to the bot's application for the user you want to add to the guild
            :nick: value to set users nickname to
            :roles: role ids the member is assigned
            :mute: whether the user is muted in voice channels
            :deaf: whether the user is deafened in voice channels
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/members/{user_id}", method = "PUT", json = {"access_token": access_token, "nick": nick, "roles": roles, "mute": mute, "deaf": deaf})
        return Guild_Member(**r)

    async def modify_guild_member(self, guild_id: Snowflake, user_id: Snowflake, nick: str, roles: List[int], mute: bool, deaf: bool, channel_id: Snowflake) -> None:
        '''
        Modify attributes of a [guild member](https://discord.com/developers/docs/resources/guild#guild-member-object). Returns a 204 empty response on success. Fires a [Guild Member Update](https://discord.com/developers/docs/topics/gateway#guild-member-update) Gateway event. If the `channel_id` is set to null, this will force the target user to be disconnected from voice.
        > info
        > All parameters to this endpoint are optional and nullable. When moving members to channels, the API user _must_ have permissions to both connect to the channel and have the `MOVE_MEMBERS` permission.

        Params:
            :nick: value to set users nickname to
            :roles: role ids the member is assigned
            :mute: whether the user is muted in voice channels. Will throw a 400 if the user is not in a voice channel
            :deaf: whether the user is deafened in voice channels. Will throw a 400 if the user is not in a voice channel
            :channel_id: id of channel to move user to
        '''
        await self.api_call(path = f"/guilds/{guild_id}/members/{user_id}", method = "PATCH", json = {"nick": nick, "roles": roles, "mute": mute, "deaf": deaf, "channel_id": channel_id})

    async def modify_current_user_nick(self, guild_id: Snowflake, nick: str=None) -> str:
        '''
        Modifies the nickname of the current user in a guild. Returns a 200 with the nickname on success. Fires a [Guild Member Update](https://discord.com/developers/docs/topics/gateway#guild-member-update) Gateway event.

        Params:
            :nick: value to set users nickname to
        '''
        return await self.api_call(path = f"/guilds/{guild_id}/members/@me/nick", method = "PATCH", json = {"nick": nick})

    @Permissions("MANAGE_ROLES")
    async def add_guild_member_role(self, guild_id: Snowflake, user_id: Snowflake, role_id: Snowflake) -> None:
        '''
        Adds a role to a [guild member](https://discord.com/developers/docs/resources/guild#guild-member-object). Requires the `MANAGE_ROLES` permission. Returns a 204 empty response on success. Fires a [Guild Member Update](https://discord.com/developers/docs/topics/gateway#guild-member-update) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", method = "PUT")

    @Permissions("MANAGE_ROLES")
    async def remove_guild_member_role(self, guild_id: Snowflake, user_id: Snowflake, role_id: Snowflake) -> None:
        '''
        Removes a role from a [guild member](https://discord.com/developers/docs/resources/guild#guild-member-object). Requires the `MANAGE_ROLES` permission. Returns a 204 empty response on success. Fires a [Guild Member Update](https://discord.com/developers/docs/topics/gateway#guild-member-update) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", method = "DELETE")

    async def remove_guild_member(self, guild_id: Snowflake, user_id: Snowflake) -> None:
        '''
        Remove a member from a guild. Requires `KICK_MEMBERS` permission. Returns a 204 empty response on success. Fires a [Guild Member Remove](https://discord.com/developers/docs/topics/gateway#guild-member-remove) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/members/{user_id}", method = "DELETE")

    @Permissions("BAN_MEMBERS")
    async def get_guild_bans(self, guild_id: Snowflake) -> List[Ban]:
        '''
        Returns a list of [ban](https://discord.com/developers/docs/resources/guild#ban-object) objects for the users banned from this guild. Requires the `BAN_MEMBERS` permission.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/bans", method = "GET")
        return [Ban(**i) for i in r]

    @Permissions("BAN_MEMBERS")
    async def get_guild_ban(self, guild_id: Snowflake, user_id: Snowflake) -> Ban:
        '''
        Returns a [ban](https://discord.com/developers/docs/resources/guild#ban-object) object for the given user or a 404 not found if the ban cannot be found. Requires the `BAN_MEMBERS` permission.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/bans/{user_id}", method = "GET")
        return Ban(**r)

    @Permissions("BAN_MEMBERS")
    async def create_guild_ban(self, guild_id: Snowflake, user_id: Snowflake, delete_message_days: int=None, reason: str=None) -> None:
        '''
        Create a guild ban, and optionally delete previous messages sent by the banned user. Requires the `BAN_MEMBERS` permission. Returns a 204 empty response on success. Fires a [Guild Ban Add](https://discord.com/developers/docs/topics/gateway#guild-ban-add) Gateway event.

        Params:
            :delete_message_days: number of days to delete messages for
            :reason: reason for the ban
        '''
        await self.api_call(path = f"/guilds/{guild_id}/bans/{user_id}", method = "PUT", json = {"delete_message_days": delete_message_days, "reason": reason})

    @Permissions("BAN_MEMBERS")
    async def remove_guild_ban(self, guild_id: Snowflake, user_id: Snowflake) -> None:
        '''
        Remove the ban for a user. Requires the `BAN_MEMBERS` permissions. Returns a 204 empty response on success. Fires a [Guild Ban Remove](https://discord.com/developers/docs/topics/gateway#guild-ban-remove) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/bans/{user_id}", method = "DELETE")

    async def get_guild_roles(self, guild_id: Snowflake) -> List[Role]:
        '''
        Returns a list of [role](https://discord.com/developers/docs/topics/permissions#role-object) objects for the guild.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/roles", method = "GET")
        return [Role(**i) for i in r]

    @Permissions("MANAGE_ROLES")
    async def create_guild_role(self, guild_id: Snowflake, name: str="new_role", permissions: str="@everyone_permissions_in_guild", color: int=0, hoist: bool=False, mentionable: bool=False) -> Role:
        '''
        Create a new [role](https://discord.com/developers/docs/topics/permissions#role-object) for the guild. Requires the `MANAGE_ROLES` permission. Returns the new [role](https://discord.com/developers/docs/topics/permissions#role-object) object on success. Fires a [Guild Role Create](https://discord.com/developers/docs/topics/gateway#guild-role-create) Gateway event. All JSON params are optional.

        Params:
            :name: name of the role
            :permissions: bitwise value of the enabled/disabled permissions
            :color: RGB color value
            :hoist: whether the role should be displayed separately in the sidebar
            :mentionable: whether the role should be mentionable
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/roles", method = "POST", json = {"name": name, "permissions": permissions, "color": color, "hoist": hoist, "mentionable": mentionable})
        return Role(**r)

    @Permissions("MANAGE_ROLES")
    async def modify_guild_role_positions(self, guild_id: Snowflake, id: Snowflake, position: int=None) -> List[Role]:
        '''
        Modify the positions of a set of [role](https://discord.com/developers/docs/topics/permissions#role-object) objects for the guild. Requires the `MANAGE_ROLES` permission. Returns a list of all of the guild's [role](https://discord.com/developers/docs/topics/permissions#role-object) objects on success. Fires multiple [Guild Role Update](https://discord.com/developers/docs/topics/gateway#guild-role-update) Gateway events.
        This endpoint takes a JSON array of parameters in the following format:

        Params:
            :id: role
            :position: sorting position of the role
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/roles", method = "PATCH", json = {"id": id, "position": position})
        return [Role(**i) for i in r]

    @Permissions("MANAGE_ROLES")
    async def modify_guild_role(self, guild_id: Snowflake, role_id: Snowflake, name: str, permissions: str, color: int, hoist: bool, mentionable: bool) -> Role:
        '''
        Modify a guild role. Requires the `MANAGE_ROLES` permission. Returns the updated [role](https://discord.com/developers/docs/topics/permissions#role-object) on success. Fires a [Guild Role Update](https://discord.com/developers/docs/topics/gateway#guild-role-update) Gateway event.
        > info
        > All parameters to this endpoint are optional and nullable.

        Params:
            :name: name of the role
            :permissions: bitwise value of the enabled/disabled permissions
            :color: RGB color value
            :hoist: whether the role should be displayed separately in the sidebar
            :mentionable: whether the role should be mentionable
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/roles/{role_id}", method = "PATCH", json = {"name": name, "permissions": permissions, "color": color, "hoist": hoist, "mentionable": mentionable})
        return Role(**r)

    @Permissions("MANAGE_ROLES")
    async def delete_guild_role(self, guild_id: Snowflake, role_id: Snowflake) -> None:
        '''
        Delete a guild role. Requires the `MANAGE_ROLES` permission. Returns a 204 empty response on success. Fires a [Guild Role Delete](https://discord.com/developers/docs/topics/gateway#guild-role-delete) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/roles/{role_id}", method = "DELETE")

    @Permissions("KICK_MEMBERS")
    async def get_guild_prune_count(self, guild_id: Snowflake, days: int=7, include_roles: List[int]=None) -> dict:
        '''
        Returns an object with one 'pruned' key indicating the number of members that would be removed in a prune operation. Requires the `KICK_MEMBERS` permission.
        By default, prune will not remove users with roles. You can optionally include specific roles in your prune by providing the `include_roles` parameter. Any inactive user that has a subset of the provided role(s) will be counted in the prune and users with additional roles will not.

        Params:
            :days: number of days to count prune for
            :include_roles: role
        '''
        return await self.api_call(path = f"/guilds/{guild_id}/prune", method = "GET", params = {"days": days, "include_roles": include_roles})

    @Permissions("KICK_MEMBERS")
    async def begin_guild_prune(self, guild_id: Snowflake, days: int=7, compute_prune_count: bool=True, include_roles: List[int]=None) -> None:
        '''
        Begin a prune operation. Requires the `KICK_MEMBERS` permission. Returns an object with one 'pruned' key indicating the number of members that were removed in the prune operation. For large guilds it's recommended to set the `compute_prune_count` option to `false`, forcing 'pruned' to `null`. Fires multiple [Guild Member Remove](https://discord.com/developers/docs/topics/gateway#guild-member-remove) Gateway events.
        By default, prune will not remove users with roles. You can optionally include specific roles in your prune by providing the `include_roles` parameter. Any inactive user that has a subset of the provided role(s) will be included in the prune and users with additional roles will not.

        Params:
            :days: number of days to prune
            :compute_prune_count: whether 'pruned' is returned, discouraged for large guilds
            :include_roles: role
        '''
        await self.api_call(path = f"/guilds/{guild_id}/prune", method = "POST", json = {"days": days, "compute_prune_count": compute_prune_count, "include_roles": include_roles})

    async def get_guild_voice_regions(self, guild_id: Snowflake) -> List[Voice_Region]:
        '''
        Returns a list of [voice region](https://discord.com/developers/docs/resources/voice#voice-region-object) objects for the guild. Unlike the similar `/voice` route, this returns VIP servers when the guild is VIP-enabled.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/regions", method = "GET")
        return [Voice_Region(**i) for i in r]

    @Permissions("MANAGE_GUILD")
    async def get_guild_invites(self, guild_id: Snowflake) -> List[Invite]:
        '''
        Returns a list of [invite](https://discord.com/developers/docs/resources/invite#invite-object) objects (with [invite metadata](https://discord.com/developers/docs/resources/invite#invite-metadata-object)) for the guild. Requires the `MANAGE_GUILD` permission.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/invites", method = "GET")
        return [Invite(**i) for i in r]

    @Permissions("MANAGE_GUILD")
    async def get_guild_integrations(self, guild_id: Snowflake) -> List[Integration]:
        '''
        Returns a list of [integration](https://discord.com/developers/docs/resources/guild#integration-object) objects for the guild. Requires the `MANAGE_GUILD` permission.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/integrations", method = "GET")
        return [Integration(**i) for i in r]

    @Permissions("MANAGE_GUILD")
    async def create_guild_integration(self, guild_id: Snowflake, type: str, id: Snowflake) -> None:
        '''
        Attach an [integration](https://discord.com/developers/docs/resources/guild#integration-object) object from the current user to the guild. Requires the `MANAGE_GUILD` permission. Returns a 204 empty response on success. Fires a [Guild Integrations Update](https://discord.com/developers/docs/topics/gateway#guild-integrations-update) Gateway event.

        Params:
            :type: the integration type
            :id: the integration id
        '''
        await self.api_call(path = f"/guilds/{guild_id}/integrations", method = "POST", json = {"type": type, "id": id})

    @Permissions("MANAGE_GUILD")
    async def modify_guild_integration(self, guild_id: Snowflake, integration_id: Snowflake, expire_behavior: int, expire_grace_period: int, enable_emoticons: bool) -> None:
        '''
        Modify the behavior and settings of an [integration](https://discord.com/developers/docs/resources/guild#integration-object) object for the guild. Requires the `MANAGE_GUILD` permission. Returns a 204 empty response on success. Fires a [Guild Integrations Update](https://discord.com/developers/docs/topics/gateway#guild-integrations-update) Gateway event.
        > info
        > All parameters to this endpoint are optional and nullable.

        Params:
            :expire_behavior: Integration_Expire_Behaviors
            :expire_grace_period: period
            :enable_emoticons: whether emoticons should be synced for this integration
        '''
        await self.api_call(path = f"/guilds/{guild_id}/integrations/{integration_id}", method = "PATCH", json = {"expire_behavior": expire_behavior, "expire_grace_period": expire_grace_period, "enable_emoticons": enable_emoticons})

    @Permissions("MANAGE_GUILD")
    async def delete_guild_integration(self, guild_id: Snowflake, integration_id: Snowflake) -> None:
        '''
        Delete the attached [integration](https://discord.com/developers/docs/resources/guild#integration-object) object for the guild. Deletes any associated webhooks and kicks the associated bot if there is one. Requires the `MANAGE_GUILD` permission. Returns a 204 empty response on success. Fires a [Guild Integrations Update](https://discord.com/developers/docs/topics/gateway#guild-integrations-update) Gateway event.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/integrations/{integration_id}", method = "DELETE")

    @Permissions("MANAGE_GUILD")
    async def sync_guild_integration(self, guild_id: Snowflake, integration_id: Snowflake) -> None:
        '''
        Sync an integration. Requires the `MANAGE_GUILD` permission. Returns a 204 empty response on success.
        '''
        await self.api_call(path = f"/guilds/{guild_id}/integrations/{integration_id}/sync", method = "POST")

    @Permissions("MANAGE_GUILD")
    async def get_guild_widget_settings(self, guild_id: Snowflake) -> Guild_Widget:
        '''
        Returns a [guild widget](https://discord.com/developers/docs/resources/guild#guild-widget-object) object. Requires the `MANAGE_GUILD` permission.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/widget", method = "GET")
        return Guild_Widget(**r)

    @Permissions("MANAGE_GUILD")
    async def modify_guild_widget(self, guild_id: Snowflake) -> Guild_Widget:
        '''
        Modify a [guild widget](https://discord.com/developers/docs/resources/guild#guild-widget-object) object for the guild. All attributes may be passed in with JSON and modified. Requires the `MANAGE_GUILD` permission. Returns the updated [guild widget](https://discord.com/developers/docs/resources/guild#guild-widget-object) object.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/widget", method = "PATCH")
        return Guild_Widget(**r)

    async def get_guild_widget(self, guild_id: Snowflake) -> Guild_Widget:
        '''
        Returns the widget for the guild.
        '''
        r = await self.api_call(path=f"/guilds/{guild_id}/widget_json", method="GET")
        return Guild_Widget(**r)

    @Permissions("MANAGE_GUILD")
    async def get_guild_vanity_url(self, guild_id: Snowflake) -> Invite:
        '''
        Returns a partial [invite](https://discord.com/developers/docs/resources/invite#invite-object) object for guilds with that feature enabled. Requires the `MANAGE_GUILD` permission. `code` will be null if a vanity url for the guild is not set.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/vanity-url", method = "GET")
        return Invite(**r)

    async def get_guild_widget_image(self, guild_id: Snowflake, style: str="shield") -> str:
        '''
        Returns a PNG image widget for the guild. Requires no permissions or authentication.
        > info
        > All parameters to this endpoint are optional.

        Params:
            :style: style of the widget image returned
        '''
        return await self.api_call(path = f"/guilds/{guild_id}/widget_png", method = "GET", params = {"style": style})

    async def get_invite(self, invite_code: int, with_counts: bool=None) -> Invite:
        '''
        Returns an [invite](https://discord.com/developers/docs/resources/invite#invite-object) object for the given code.

        Params:
            :with_counts: whether the invite should contain approximate member counts
        '''
        r = await self.api_call(path = f"/invites/{invite_code}", method = "GET", json = {"with_counts": with_counts})
        return Invite(**r)

    @Permissions("MANAGE_CHANNELS")
    async def delete_invite(self, invite_code: int) -> Invite:
        '''
        Delete an invite. Requires the `MANAGE_CHANNELS` permission on the channel this invite belongs to, or `MANAGE_GUILD` to remove any invite across the guild. Returns an [invite](https://discord.com/developers/docs/resources/invite#invite-object) object on success. Fires a [Invite Delete](https://discord.com/developers/docs/topics/gateway#invite-delete) Gateway event.
        '''
        r = await self.api_call(path = f"/invites/{invite_code}", method = "DELETE")
        return Invite(**r)

    async def get_current_user(self) -> User:
        '''
        Returns the [user](https://discord.com/developers/docs/resources/user#user-object) object of the requester's account. For OAuth2, this requires the `identify` scope, which will return the object _without_ an email, and optionally the `email` scope, which returns the object _with_ an email.
        '''
        r = await self.api_call(path = f"/users/@me", method = "GET")
        return User(**r)

    async def get_user(self, user_id: Snowflake) -> User:
        '''
        Returns a [user](https://discord.com/developers/docs/resources/user#user-object) object for a given user ID.
        '''
        r = await self.api_call(path = f"/users/{user_id}", method = "GET")
        return User(**r)

    async def modify_current_user(self, username: str, avatar: str) -> User:
        '''
        Modify the requester's user account settings. Returns a [user](https://discord.com/developers/docs/resources/user#user-object) object on success.
        > info
        > All parameters to this endpoint are optional.

        Params:
            :username: user's username, if changed may cause the user's discriminator to be randomized.
            :avatar: if passed, modifies the user's avatar
        '''
        r = await self.api_call(path = f"/users/@me", method = "PATCH", json = {"username": username, "avatar": avatar})
        return User(**r)

    async def get_current_user_guilds(self) -> List[Guild]:
        '''
        Returns a list of partial [guild](https://discord.com/developers/docs/resources/guild#guild-object) objects the current user is a member of. Requires the `guilds` OAuth2 scope.
        '''
        r = await self.api_call(path = f"/users/@me/guilds", method = "GET")
        return [Guild(**i) for i in r]

    async def leave_guild(self, guild_id: Snowflake) -> None:
        '''
        Leave a guild. Returns a 204 empty response on success.
        '''
        await self.api_call(path = f"/users/@me/guilds/{guild_id}", method = "DELETE")

    async def get_user_dms(self) -> List[Channel]:
        '''
        Returns a list of [DM channel](https://discord.com/developers/docs/resources/channel#channel-object) objects. For bots, this is no longer a supported method of getting recent DMs, and will return an empty array.
        '''
        r = await self.api_call(path = f"/users/@me/channels", method = "GET")
        return [Channel(**i) for i in r]

    async def create_dm(self, recipient_id: Snowflake) -> Channel:
        '''
        Create a new DM channel with a user. Returns a [DM channel](https://discord.com/developers/docs/resources/channel#channel-object) object.
        > warn
        > You should not use this endpoint to DM everyone in a server about something. DMs should generally be initiated by a user action. If you open a significant amount of DMs too quickly, your bot may be rate limited or blocked from opening new ones.

        Params:
            :recipient_id: the recipient to open a DM channel with
        '''
        r = await self.api_call(path = f"/users/@me/channels", method = "POST", json = {"recipient_id": recipient_id})
        return Channel(**r)

    async def create_group_dm(self, access_tokens: List[str], nicks: dict) -> Channel:
        '''
        Create a new group DM channel with multiple users. Returns a [DM channel](https://discord.com/developers/docs/resources/channel#channel-object) object. This endpoint was intended to be used with the now-deprecated GameBridge SDK. DMs created with this endpoint will not be shown in the Discord client
        > warn
        > This endpoint is limited to 10 active group DMs.

        Params:
            :access_tokens: access tokens of users that have granted your app the `gdm.join` scope
            :nicks: a dictionary of user ids to their respective nicknames
        '''
        r = await self.api_call(path = f"/users/@me/channels", method = "POST", json = {"access_tokens": access_tokens, "nicks": nicks})
        return Channel(**r)

    async def get_user_connections(self) -> List[Connection]:
        '''
        Returns a list of [connection](https://discord.com/developers/docs/resources/user#connection-object) objects. Requires the `connections` OAuth2 scope.
        '''
        r = await self.api_call(path = f"/users/@me/connections", method = "GET")
        return [Connection(**i) for i in r]

    async def list_voice_regions(self) -> List[Voice_Region]:
        '''
        Returns an array of [voice region](https://discord.com/developers/docs/resources/voice#voice-region-object) objects that can be used when creating servers.
        '''
        r = await self.api_call(path = f"/voice/regions", method = "GET")
        return [Voice_Region(**i) for i in r]

    @Permissions("MANAGE_WEBHOOKS")
    async def create_webhook(self, channel_id: Snowflake, name: str, avatar: str) -> Webhook:
        '''
        Create a new webhook. Requires the `MANAGE_WEBHOOKS` permission. Returns a [webhook](https://discord.com/developers/docs/resources/webhook#webhook-object) object on success. Webhook names follow our naming restrictions that can be found in our [Usernames and Nicknames](https://discord.com/developers/docs/resources/user#usernames-and-nicknames) documentation, with the following additional stipulations:
        - Webhook names cannot be: 'clyde'

        Params:
            :name: name of the webhook
            :avatar: image for the default webhook avatar
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/webhooks", method = "POST", json = {"name": name, "avatar": avatar})
        return Webhook(**r)

    @Permissions("MANAGE_WEBHOOKS")
    async def get_channel_webhooks(self, channel_id: Snowflake) -> List[Webhook]:
        '''
        Returns a list of channel [webhook](https://discord.com/developers/docs/resources/webhook#webhook-object) objects. Requires the `MANAGE_WEBHOOKS` permission.
        '''
        r = await self.api_call(path = f"/channels/{channel_id}/webhooks", method = "GET")
        return [Webhook(**i) for i in r]

    @Permissions("MANAGE_WEBHOOKS")
    async def get_guild_webhooks(self, guild_id: Snowflake) -> List[Webhook]:
        '''
        Returns a list of guild [webhook](https://discord.com/developers/docs/resources/webhook#webhook-object) objects. Requires the `MANAGE_WEBHOOKS` permission.
        '''
        r = await self.api_call(path = f"/guilds/{guild_id}/webhooks", method = "GET")
        return [Webhook(**i) for i in r]

    async def get_webhook(self, webhook_id: Snowflake) -> Webhook:
        '''
        Returns the new [webhook](https://discord.com/developers/docs/resources/webhook#webhook-object) object for the given id.
        '''
        r = await self.api_call(path = f"/webhooks/{webhook_id}", method = "GET")
        return Webhook(**r)

    async def get_webhook_with_token(self, webhook_id: Snowflake, webhook_token: int) -> None:
        '''
        Same as above, except this call does not require authentication and returns no user in the webhook object.
        '''
        r = await self.api_call(path=f"/webhooks/{webhook_id}/{webhook_token}", method="GET")
        return Webhook(**r)

    @Permissions("MANAGE_WEBHOOKS")
    async def modify_webhook(self, webhook_id: Snowflake, name: str, avatar: str, channel_id: Snowflake) -> Webhook:
        '''
        Modify a webhook. Requires the `MANAGE_WEBHOOKS` permission. Returns the updated [webhook](https://discord.com/developers/docs/resources/webhook#webhook-object) object on success.
        > info
        > All parameters to this endpoint are optional

        Params:
            :name: the default name of the webhook
            :avatar: image for the default webhook avatar
            :channel_id: the new channel id this webhook should be moved to
        '''
        r = await self.api_call(path = f"/webhooks/{webhook_id}", method = "PATCH", json = {"name": name, "avatar": avatar, "channel_id": channel_id})
        return Webhook(**r)

    async def modify_webhook_with_token(self, webhook_id: Snowflake, webhook_token: int) -> None:
        '''
        Same as above, except this call does not require authentication, does not accept a `channel_id` parameter in the body, and does not return a user in the webhook object.
        '''
        r = await self.api_call(path=f"/webhooks/{webhook_id}/{webhook_token}", method="PATCH")
        return Webhook(**r)

    @Permissions("MANAGE_WEBHOOKS")
    async def delete_webhook(self, webhook_id: Snowflake) -> None:
        '''
        Delete a webhook permanently. Requires the `MANAGE_WEBHOOKS` permission. Returns a 204 NO CONTENT response on success.
        '''
        await self.api_call(path = f"/webhooks/{webhook_id}", method = "DELETE")

    async def delete_webhook_with_token(self, webhook_id: Snowflake, webhook_token: int) -> None:
        '''
        Same as above, except this call does not require authentication.
        '''
        await self.api_call(path = f"/webhooks/{webhook_id}/{webhook_token}", method = "DELETE")

    async def execute_webhook(self, webhook_id: Snowflake, webhook_token: int, wait: bool = False, content: str = None, username: str = None, avatar_url: str = None, tts: bool = None, file: bytes = None, embeds: List[Embed] = None, payload_json: str = None, allowed_mentions: Allowed_Mentions = None) -> Message:
        '''
        > warn
        > This endpoint supports both JSON and form data bodies. It does require multipart/form-data requests instead of the normal JSON request type when uploading files. Make sure you set your `Content-Type` to `multipart/form-data` if you're doing that. Note that in that case, the `embeds` field cannot be used, but you can pass an url-encoded JSON body as a form value for `payload_json`.

        Params:
            :wait: waits for server confirmation of message send before response, and returns the created message body
            :content: the message contents
            :username: override the default username of the webhook
            :avatar_url: override the default avatar of the webhook
            :tts: true if this is a TTS message
            :file: the contents of the file being sent
            :embeds: embedded `rich` content
            :payload_json: Message_Create
            :allowed_mentions: allowed mentions for the message
        '''
        r = await self.api_call(path = f"/webhooks/{webhook_id}/{webhook_token}", method = "POST", params = {"wait": wait}, json = {"content": content, "username": username, "avatar_url": avatar_url, "tts": tts, "file": file, "embeds": embeds, "payload_json": payload_json, "allowed_mentions": allowed_mentions})
        return Message(**r) if wait else None

    async def execute_slack_compatible_webhook(self, webhook_id: Snowflake, webhook_token: int, wait: bool) -> None:
        '''
        Params:
            :wait: waits for server confirmation of message send before response
        '''
        await self.api_call(path = f"/webhooks/{webhook_id}/{webhook_token}/slack", method = "POST", params = {"wait": wait})

    async def execute_github_compatible_webhook(self, webhook_id: Snowflake, webhook_token: int, wait: bool) -> None:
        '''
        Params:
            :wait: waits for server confirmation of message send before response
        '''
        await self.api_call(path = f"/webhooks/{webhook_id}/{webhook_token}/github", method = "POST", params = {"wait": wait})

    async def edit_webhook_message(self, webhook_id: Snowflake, webhook_token: int, message_id: Snowflake, content: str, embeds: List[Embed], allowed_mentions: Allowed_Mentions) -> None:
        '''
        Edits a previously-sent webhook message from the same token.
        > info
        > All parameters to this endpoint are optional and nullable.

        Params:
            :content: the message contents
            :embeds: embedded `rich` content
            :allowed_mentions: allowed mentions for the message
        '''
        await self.api_call(path = f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", method = "PATCH", json = {"content": content, "embeds": embeds, "allowed_mentions": allowed_mentions})

    async def get_gateway(self) -> dict:
        '''
        > info
        > This endpoint does not require authentication.
        Returns an object with a single valid WSS URL, which the client can use for [Connecting](https://discord.com/developers/docs/topics/gateway#connecting). selfs **should** cache this value and only call this endpoint to retrieve a new URL if they are unable to properly establish a connection using the cached version of the URL.
        '''
        return await self.api_call(path = f"/gateway", method = "GET")

    async def get_gateway_bot(self) -> dict:
        '''
        > warn
        > This endpoint requires authentication using a valid bot token.
        Returns an object based on the information in [Get Gateway](https://discord.com/developers/docs/topics/gateway#get-gateway), plus additional metadata that can help during the operation of large or [sharded](https://discord.com/developers/docs/topics/gateway#sharding) bots. Unlike the [Get Gateway](https://discord.com/developers/docs/topics/gateway#get-gateway), this route should not be cached for extended periods of time as the value is not guaranteed to be the same per-call, and changes as the bot joins/leaves guilds.
        '''
        return await self.api_call(path = f"/gateway/bot", method = "GET")

    async def get_current_application_information(self) -> None:
        '''
        Returns the bot's OAuth2 [application object](https://discord.com/developers/docs/topics/oauth2#application-object) without `flags`.
        '''
        r = await self.api_call(path=f"/oauth2/applications/@me", method="GET")
        return Application(**r)

    async def get_global_application_commands(self, application_id: Snowflake) -> List[Application_Command]:
        '''
        Fetch all of the global commands for your application. Returns an array of [ApplicationCommand](https://discord.com/developers/docs/interactions/slash_commands#applicationcommand) objects.
        '''
        r = await self.api_call(path = f"/applications/{application_id}/commands", method = "GET")
        return [Application_Command(**i) for i in r]

    async def create_global_application_command(self, application_id: Snowflake, name: str, description: str, options: List[Application_Command_Option]=None) -> Application_Command:
        '''
        > danger
        > Creating a command with the same name as an existing command for your application will overwrite the old command.
        Create a new global command. New global commands will be available in all guilds after 1 hour. Returns `201` and an [ApplicationCommand](https://discord.com/developers/docs/interactions/slash_commands#applicationcommand) object.

        Params:
            :name: 3-32 character command name
            :description: 1-100 character description
            :options: the parameters for the command
        '''
        r = await self.api_call(path = f"/applications/{application_id}/commands", method = "POST", json = {"name": name, "description": description, "options": options})
        return Application_Command(**r)

    async def edit_global_application_command(self, application_id: Snowflake, command_id: Snowflake, name: str, description: str, options: List[Application_Command_Option]=None) -> Application_Command:
        '''
        Edit a global command. Updates will be available in all guilds after 1 hour. Returns `200` and an [ApplicationCommand](https://discord.com/developers/docs/interactions/slash_commands#applicationcommand) object.

        Params:
            :name: 3-32 character command name
            :description: 1-100 character description
            :options: the parameters for the command
        '''
        r = await self.api_call(path = f"/applications/{application_id}/commands/{command_id}", method = "PATCH", json = {"name": name, "description": description, "options": options})
        return Application_Command(**r)

    async def delete_global_application_command(self, application_id: Snowflake, command_id: Snowflake) -> None:
        '''
        Deletes a global command. Returns `204`.
        '''
        await self.api_call(path = f"/applications/{application_id}/commands/{command_id}", method = "DELETE")

    async def get_guild_application_commands(self, application_id: Snowflake, guild_id: Snowflake) -> List[Application_Command]:
        '''
        Fetch all of the guild commands for your application for a specific guild. Returns an array of [ApplicationCommand](https://discord.com/developers/docs/interactions/slash_commands#applicationcommand) objects.
        '''
        r = await self.api_call(path = f"/applications/{application_id}/guilds/{guild_id}/commands", method = "GET")
        return [Application_Command(**i) for i in r]

    async def create_guild_application_command(self, application_id: Snowflake, guild_id: Snowflake, name: str, description: str, options: List[Application_Command_Option]=[]) -> Application_Command:
        '''
        > danger
        > Creating a command with the same name as an existing command for your application will overwrite the old command.
        Create a new guild command. New guild commands will be available in the guild immediately. Returns `201` and an [ApplicationCommand](https://discord.com/developers/docs/interactions/slash_commands#applicationcommand) object.

        Params:
            :name: 3-32 character command name
            :description: 1-100 character description
            :options: the parameters for the command
        '''
        r = await self.api_call(path = f"/applications/{application_id}/guilds/{guild_id}/commands", method = "POST", json = {"name": name, "description": description, "options": options})
        return Application_Command(**r)

    async def edit_guild_application_command(self, application_id: Snowflake, guild_id: Snowflake, command_id: Snowflake, name: str, description: str, options: List[Application_Command_Option]=[]) -> Application_Command:
        '''
        Edit a guild command. Updates for guild commands will be available immediately. Returns `200` and an [ApplicationCommand](https://discord.com/developers/docs/interactions/slash_commands#applicationcommand) object.

        Params:
            :name: 3-32 character command name
            :description: 1-100 character description
            :options: the parameters for the command
        '''
        r = await self.api_call(path = f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}", method = "PATCH", json = {"name": name, "description": description, "options": options})
        return Application_Command(**r)

    async def delete_guild_application_command(self, application_id: Snowflake, guild_id: Snowflake, command_id: Snowflake) -> None:
        '''
        Delete a guild command. Returns `204` on success.
        '''
        await self.api_call(path = f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}", method = "DELETE")

    async def create_interaction_response(self, interaction_id: Snowflake, interaction_token: int, response: Interaction_Response) -> None:
        '''
        Create a response to an Interaction from the gateway. Takes an [Interaction response](https://discord.com/developers/docs/interactions/slash_commands#interaction-response).
        '''
        await self.api_call(path = f"/interactions/{interaction_id}/{interaction_token}/callback", method = "POST", json = as_dict(response))

    async def edit_original_interaction_response(self, application_id: Snowflake, interaction_token: int, content: str = None, embeds: List[Embed] = None, allowed_mentions: Allowed_Mentions = None) -> None:
        '''
        Edits the initial Interaction response. Functions the same as [Edit Webhook Message](https://discord.com/developers/docs/resources/webhook#edit-webhook-message).
        '''
        await self.api_call(path = f"/webhooks/{application_id}/{interaction_token}/messages/@original", method = "PATCH", json={"content":content, "embeds": embeds, "allowed_mentions": allowed_mentions})

    async def delete_original_interaction_response(self, application_id: Snowflake, interaction_token: int) -> None:
        '''
        Deletes the initial Interaction response. Returns `204` on success.
        '''
        await self.api_call(path = f"/webhooks/{application_id}/{interaction_token}/messages/@original", method = "DELETE")

    async def create_followup_message(self, application_id: Snowflake, interaction_token: int, wait: bool = False, content: str = None, username: str = None, avatar_url: str = None, tts: bool = None, file: bytes = None, filename: str="file.txt", embeds: List[Embed] = None, payload_json: str = None, allowed_mentions: Allowed_Mentions = []) -> Message:
        '''
        Create a followup message for an Interaction. Functions the same as [Execute Webhook](https://discord.com/developers/docs/resources/webhook#execute-webhook)
        '''
        r = await self.api_call(path=f"/webhooks/{application_id}/{interaction_token}", method="POST", params={"wait": wait}, json={"content": content, "username": username, "avatar_url": avatar_url, "tts": tts, "embeds": embeds, "payload_json": payload_json, "allowed_mentions": allowed_mentions}, file=file, filename=filename)
        return Message(**r)

    async def edit_followup_message(self, application_id: Snowflake, interaction_token: int, message_id: Snowflake, content: str = None, embeds: List[Embed] = None, allowed_mentions: Allowed_Mentions = []) -> None:
        '''
        Edits a followup message for an Interaction. Functions the same as [Edit Webhook Message](https://discord.com/developers/docs/resources/webhook#edit-webhook-message).
        '''
        await self.api_call(path = f"/webhooks/{application_id}/{interaction_token}/messages/{message_id}", method = "PATCH", json={"content":content, "embeds": embeds, "allowed_mentions": allowed_mentions})

    async def delete_followup_message(self, application_id: Snowflake, interaction_token: int, message_id: Snowflake) -> None:
        '''
        Deletes a followup message for an Interaction. Returns `204` on success.
        '''
        await self.api_call(path=f"/webhooks/{application_id}/{interaction_token}/messages/{message_id}", method="DELETE")

from . import Deserializer
from ..database.database import Database
from ..database.cache import Cache
class Bot(Endpoints):
    token: str
    username: str
    
    counters: dict
    
    db: Database
    cache: Cache
    
    context: dict

    latency: Optional[int]
    cfg: dict

    alias: str
    sub: bool
    intents: int

    presence: Gateway_Status_Update
    activity: Bot_Activity


    shards: List[int]
    lock: dict

    decompress: Deserializer