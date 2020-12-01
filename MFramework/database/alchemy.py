from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Boolean, BigInteger, ARRAY, TIMESTAMP, Date, Float, func #, BLOB, PickleType, Date, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, Query#, backref


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__  #.lower()
    @classmethod
    def filter(cls, session, **kwargs) -> Query:
        ''':param kwargs: Column = Value''' 
        return session.query(cls).filter_by(**kwargs)
    @classmethod
    def by_id(cls, s, id: int) -> object:
        return cls.filter(s, id = id).first()
    @classmethod
    def by_name(cls, s, name: str) -> object:
        return cls.filter(s, Name = name).first()

Base = declarative_base(cls=Base)

class Servers(Base):
    __tablename__ = 'Servers'
    GuildID = Column(BigInteger, primary_key=True)
    AdminIDs = Column(ARRAY(BigInteger))
    ModIDs = Column(ARRAY(BigInteger))
    VipIDs = Column(ARRAY(BigInteger))
    NitroIDs = Column(ARRAY(BigInteger))
    MutedIDs = Column(ARRAY(BigInteger))
    NoExpRoles = Column(ARRAY(BigInteger))
    NoExpChannels = Column(ARRAY(BigInteger))
    Alias = Column(String)
    Color = Column(Integer)
    TrackPresence = Column(Boolean)
    Language = Column(String)
    VoiceLink = Column(BigInteger)
    TrackVoice = Column(Boolean)
    TrackActivity = Column(Boolean)
    DMCount = Column(Integer)
    DMCountForwarded = Column(Integer)

    def __init__(self, GuildID=None, AdminIDs=None, ModIDs=None, VipIDs=None, NitroIDs=None, MutedIDs=None, NoExpRoles=None, NoExpChannels=None, Alias=None, Color=None, TrackPresence=None, Language=None, VoiceLink=None, TrackVoice=None):
        self.GuildID = GuildID
        self.AdminIDs = AdminIDs
        self.ModIDs = ModIDs
        self.VipIDs = VipIDs
        self.NitroIDs = NitroIDs
        self.MutedIDs = MutedIDs
        self.NoExpRoles = NoExpRoles
        self.NoExpChannels = NoExpChannels
        self.Alias = Alias
        self.Color = Color
        self.TrackPresence = TrackPresence
        self.Language = Language
        self.VoiceLink = VoiceLink
        self.TrackVoice = TrackVoice
        self.TrackActivity = None
        self.DMCount = 0
        self.DMCountForwarded = 0


class Regex(Base):
    __tablename__ = 'Regex'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger)
    Name = Column(String, primary_key=True)
    Trigger = Column(String, primary_key=True)
    Response = Column(String)
    ReqRole = Column(String)

    def __init__(self, GuildID=None, UserID=None, Name=None, Trigger=None, Response=None, ReqRole=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Name = Name
        self.Trigger = Trigger
        self.Response = Response
        self.ReqRole = ReqRole


class ReactionRoles(Base):
    __tablename__ = 'ReactionRoles'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    ChannelID = Column(BigInteger)
    MessageID = Column(BigInteger, primary_key=True)
    RoleID = Column(BigInteger)
    Reaction = Column(String, primary_key=True)
    RoleGroup = Column(String)

    def __init__(self, GuildID=None, ChannelID=None, MessageID=None, RoleID=None, Reaction=None, RoleGroup=None):
        self.GuildID = GuildID
        self.ChannelID = ChannelID
        self.MessageID = MessageID
        self.RoleID = RoleID
        self.Reaction = Reaction
        self.RoleGroup = RoleGroup

class PresenceRoles(Base):
    __tablename__ = 'PresenceRoles'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    RoleID = Column(BigInteger)
    Presence = Column(String, primary_key=True)
    RoleGroup = Column(String)

    def __init__(self, GuildID=None, RoleID=None, Presence=None, RoleGroup=None):
        self.GuildID = GuildID
        self.RoleID = RoleID
        self.Presence = Presence
        self.RoleGroup = RoleGroup

class ActivityRoles(Base):
    __tablename__ = 'ActivityRoles'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    RoleID = Column(BigInteger, primary_key=True)
    ReqChatActivity = Column(Integer, primary_key=True)
    ReqVoiceActivity = Column(Integer, primary_key=True)
    ActivityPeriod = Column(Integer, primary_key=True) #Hours
    GracePeriod = Column(String)
    def __init__(self, GuildID, RoleID, ReqAvgActivity, ActivityPeriod, GracePeriod=None):
        self.GuildID = GuildID
        self.RoleID = RoleID
        self.ReqChatActivity = ReqAvgActivity
        self.ActivityPeriod = ActivityPeriod
        self.GracePeriod = GracePeriod

class LevelRoles(Base):
    __tablename__ = 'LevelRoles'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    #Level = Column(Integer, primary_key=True)
    Level = Column(Integer)
    Priority = Column(Integer)
    ReqEXP = Column(Integer)
    ReqVEXP = Column(Integer)
    Role = Column(BigInteger, primary_key=True)
    #Role = Column(ARRAY(BigInteger), primary_key=True)
    Stacked = Column(Boolean)
    Type = Column(String, primary_key=True)  #AND || OR || COMBINED
    ReqRoles = Column(ARRAY(BigInteger))

    def __init__(self, GuildID=None, Level=None, Role=None, Stacked=None):
        self.GuildID = GuildID
        self.Level = Level
        self.Role = Role
        self.Stacked = Stacked


class UserLevels(Base):
    __tablename__ = 'UserLevels'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    EXP = Column(Integer)
    vEXP = Column(Integer)
    LastMessage = Column(TIMESTAMP(True))  #Integer)
    LastActivityCheck = Column(TIMESTAMP(True))
    TopActivityPeriod = Column(Integer)

    def __init__(self, GuildID=None, UserID=None, EXP=None, vEXP=None, LastMessage=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.EXP = EXP
        self.vEXP = vEXP
        self.LastMessage = LastMessage


class Infractions(Base):
    __tablename__ = 'Infractions'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    Timestamp = Column(TIMESTAMP(True), primary_key=True)
    Reason = Column(String)
    ModeratorID = Column(BigInteger)
    Duration = Column(Integer)
    InfractionType = Column(String)

    def __init__(self, GuildID=None, UserID=None, Timestamp=None, Reason=None, ModeratorID=None, Duration=None, InfractionType=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Timestamp = Timestamp
        self.Reason = Reason
        self.ModeratorID = ModeratorID
        self.Duration = Duration
        self.InfractionType = InfractionType


class Webhooks(Base):
    __tablename__ = 'Webhooks'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    Webhook = Column(String)
    Source = Column(String, primary_key=True)
    Content = Column(String)
    Regex = Column(String, primary_key=True)
    AddedBy = Column(BigInteger)

    def __init__(self, GuildID=None, Webhook=None, Source=None, Content=None, Regex=None, AddedBy=None):
        self.GuildID = GuildID
        self.Webhook = Webhook
        self.Source = Source
        self.Content = Content
        self.Regex = Regex
        self.AddedBy = AddedBy


class RSS(Base):
    __tablename__ = 'RSS'
    Source = Column(String, primary_key=True)
    Last = Column(Integer)
    URL = Column(String)
    Color = Column(Integer)
    Language = Column(String)
    AvatarURL = Column(String)

    def __init__(self, Source=None, Last=None, URL=None, Color=None, Language=None, AvatarURL=None):
        self.Source = Source
        self.Last = Last
        self.URL = URL
        self.Color = Color
        self.Language = Language
        self.AvatarURL = AvatarURL


class Spotify(Base):
    __tablename__ = 'Spotify'
    SpotifyID = Column(String, primary_key=True)
    Artist = Column(String)
    AddedBy = Column(BigInteger)

    def __init__(self, SpotifyID=None, Artist=None, AddedBy=None):
        self.SpotifyID = SpotifyID
        self.Artist = Artist
        self.AddedBy = AddedBy


class Tasks(Base):
    __tablename__ = 'Tasks'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    Type = Column(String, primary_key=True)
    ChannelID = Column(BigInteger)
    MessageID = Column(BigInteger)
    UserID = Column(BigInteger)
    TimestampStart = Column(TIMESTAMP(True), primary_key=True)#Integer, primary_key=True)
    TimestampEnd = Column(TIMESTAMP(True))  #Integer)
    Prize = Column(String)
    WinnerCount = Column(Integer)
    Finished = Column(Boolean, primary_key=True)
#    MessageContent = Column(String)
#    SendDM = Column(Boolean)

    def __init__(self, GuildID=None, Type=None, ChannelID=None, MessageID=None, UserID=None, TimestampStart=None, TimestampEnd=None, Prize=None, WinnerCount=None, Finished=None, MessageContent=None, SendDM=None):
        self.GuildID = GuildID
        self.Type = Type
        self.ChannelID = ChannelID
        self.MessageID = MessageID
        self.UserID = UserID
        self.TimestampStart = TimestampStart
        self.TimestampEnd = TimestampEnd
        self.Prize = Prize
        self.WinnerCount = WinnerCount
        self.Finished = Finished
#        self.MessageContent = MessageContent
#        self.SendDM = SendDM


class EmbedTemplates(Base):
    __tablename__ = 'EmbedTemplates'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger)
    Name = Column(String, primary_key=True)
    Message = Column(String)
    Embed = Column(JSON)
    Trigger = Column(String)

    def __init__(self, GuildID=None, UserID=None, Name=None, Message=None, Embed=None, Trigger=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Name = Name
        self.Message = Message
        self.Embed = Embed
        self.Trigger = Trigger


class Presences(Base):
    __tablename__ = 'Presences'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    Title = Column(String, primary_key=True)
    LastPlayed = Column(Integer)
    TotalPlayed = Column(Integer)
    AppID = Column(BigInteger, primary_key=True)
    Type = Column(String, primary_key=True)

    def __init__(self, GuildID=None, UserID=None, Title=None, LastPlayed=None, TotalPlayed=None, AppID=None, Type=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Title = Title
        self.LastPlayed = LastPlayed
        self.TotalPlayed = TotalPlayed
        self.AppID = AppID
        self.Type = Type

class ActionLog(Base):
    __tablename__ = 'ActionLog'
    GuildID = Column(BigInteger, primary_key=True)
    UserID = Column(BigInteger)
    Timestamp = Column(Integer, primary_key=True)
    Action = Column(String, primary_key=True)
    Details = Column(String)

    def __init__(self, GuildID=None, UserID=None, Timestamp=None, Action=None, Details=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Timestamp = Timestamp
        self.Action = Action
        self.Details = Details


class RPSessionPlayers(Base):
    __tablename__ = 'RPSessionPlayers'
    GuildID = Column(BigInteger, primary_key=True)
    HostID = Column(BigInteger)
    PlayerID = Column(BigInteger, primary_key=True)
    Campaign = Column(String, primary_key=True)

    def __init__(self, GuildID=None, HostID=None, PlayerID=None, Campaign=None):
        self.GuildID = GuildID
        self.HostID = HostID
        self.PlayerID = PlayerID
        self.Campaign = Campaign

class Snippets(Base):
    __tablename__ = 'Snippets'
    GuildID = Column(BigInteger, primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    Name = Column(String, primary_key=True)
    Response = Column(String)
    Image = Column(String)
    Filename = Column(String)
    Type = Column(String)
    Trigger = Column(String)
    
    def __init__(self, GuildID=None, UserID=None, Name=None, Response=None, Image=None, Filename=None, Type=None, Trigger=None):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Name = Name
        self.Response = Response
        self.Image = Image
        self.Filename = Filename
        self.Type = Type
        self.Trigger = Trigger

class RolePlayCharacters(Base):
    __tablename__ = "RolePlayCharacters"
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    Name = Column(String, primary_key=True)
    Age = Column(Integer)
    Color = Column(Integer)
    Profession = Column(String)
    Level = Column(Integer)
    Skills = Column(JSON)
    Items = Column(JSON)
    Origin = Column(String)
    Story = Column(String)
    Goals = Column(JSON)
    Favorites = Column(JSON)
    Race = Column(String)
    Gender = Column(String)

    def __init__(self, GuildID, UserID, Name, Age, Color, Profession, Gender, Race):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Name = Name
        self.Age = Age
        self.Color = Color
        self.Profession = Profession
        self.Gender = Gender
        self.Race = Race

class CustomRoles(Base):
    __tablename__ = "CustomRoles"
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    Name = Column(String)
    Color = Column(Integer)
    RoleID = Column(BigInteger, primary_key=True)

    def __init__(self, GuildID, UserID, Name, Color, RoleID):
        self.GuildID = GuildID
        self.UserID = UserID
        self.Name = Name
        self.Color = Color
        self.RoleID = RoleID

class Channels(Base):
    __tablename__ = "Channels"
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    ChannelID = Column(BigInteger, primary_key=True)
    Type = Column(String)
    Template = Column(JSON)
    Language = Column(String)

    def __init__(self, GuildID, ChannelID, Type, Template=None, Language=None):
        self.GuildID = GuildID
        self.ChannelID = ChannelID
        self.Type = Type
        self.Template = Template
        self.Language = Language

class Users(Base):
    __tablename__ = 'Users'
    UserID = Column(BigInteger, primary_key=True)
    Language = Column(String)
    Birthday = Column(Date)
    Color = Column(Integer)
    Timezone = Column(String)
    Region = Column(String)
    Currency = Column(String)
    Gender = Column(Boolean)

    def __init__(self, UserID, Language=None, Birthday=None, Color=None, Timezone=None):
        self.UserID = UserID
        self.Language = Language
        self.Birthday = Birthday
        self.Color = Color
        self.Timezone = Timezone

class HalloweenClasses(Base):
    __tablename__ = 'HalloweenStats'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    CurrentClass = Column(String)
    VampireStats = Column(Integer)
    WerewolfStats = Column(Integer)
    ZombieStats = Column(Integer)
    VampireHunterStats = Column(Integer)
    HuntsmanStats = Column(Integer)
    ZombieSlayerStats = Column(Integer)
    LastAction = Column(TIMESTAMP(True))
    LastUser = Column(BigInteger)
    LastVictim = Column(BigInteger)
    TurnCount = Column(Integer)
    ActionCooldownEnd = Column(TIMESTAMP(True))
    ProtectedBy = Column(BigInteger)
    ProtectionEnds = Column(TIMESTAMP(True))

    def __init__(self, GuildID, UserID, CurrentClass='Human'):
        self.GuildID = GuildID
        self.UserID = UserID
        self.CurrentClass = CurrentClass
        self.VampireStats = 0
        self.WerewolfStats = 0
        self.ZombieStats = 0
        self.VampireHunterStats = 0
        self.HuntsmanStats = 0
        self.ZombieSlayerStats = 0
        self.TurnCount = 0

class HalloweenRoles(Base):
    __tablename__ = 'HalloweenRoles'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    RoleName = Column(String, primary_key=True)
    RoleID = Column(BigInteger)

    def __init__(self, GuildID, RoleName, RoleID):
        self.GuildID = GuildID
        self.RoleName = RoleName
        self.RoleID = RoleID

class HalloweenLog(Base):
    __tablename__ = 'HalloweenLog'
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    UserID = Column(BigInteger, primary_key=True)
    FromClass = Column(String)
    ToClass = Column(String)
    ByUser = Column(BigInteger, primary_key=True)
    Timestamp = Column(TIMESTAMP(True), primary_key=True)

    def __init__(self, GuildID, UserID, FromClass, ToClass, ByUser, Timestamp):
        self.GuildID = GuildID
        self.UserID = UserID
        self.FromClass = FromClass
        self.ToClass = ToClass
        self.ByUser = ByUser
        self.Timestamp = Timestamp

class Default():
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True, nullable=False)
    def __init__(self, Name):
        self.Name = Name

class Types(Default, Base):
    pass

class Items(Default, Base):
    _Type_id = Column(ForeignKey(Types.id), nullable=False) # One to One
    _SubType_id = Column(ForeignKey(Types.id), nullable=False) # One to One
    
    GlobalLimit = Column(Integer)
    Rarity = Column(Integer)
    Worth = Column(Integer)
    Durability = Column(Integer)
    Repairs = Column(Integer)
    Damage = Column(Integer)
    Exclusive = Column(Boolean)
    Stackable = Column(Boolean)
    Tradeable = Column(Boolean)
    Purchasable = Column(Boolean)
    Special = Column(Boolean)
    #ReqSkill = Column(ForeignKey('Skills._id'))

    Type = relationship(Types, foreign_keys='Items._Type_id', uselist=False)
    SubType = relationship(Types, foreign_keys='Items._SubType_id', uselist=False)

    def __init__(self, Name):
        self.Name = Name
        self._Type_id = 0
        self._SubType_id = 0

    def __init__(self, Name, Type, SubType):
        self.Name = Name
        if type(Type) is Types:
            self._Type_id = Type.id
        elif type(Type) is int:
            self._Type_id = Type
        else:
            self._Type_id = int(Type)

        if type(SubType) is Types:
            self._SubType_id = SubType.id
        elif type(SubType) is int:
            self._SubType_id = SubType
        else:
            self._SubType_id = int(SubType)

class User(Base):
    id = Column(BigInteger, primary_key=True)
    Items = relationship('Inventory')

    def __init__(self, id):
        self.id = id

    def add_item(self, Inventory):
        for item in self.Items:
            if Inventory.Item.Name == item.Item.Name:
                item.Quantity += Inventory.Quantity
                return
        self.Items.append(Inventory)
    
    def add_items(self, *Items):
        for i in Items:
            self.add_item(i)
    
    def remove_item(self, Inventory):
        for item in self.Items:
            if Inventory.Item.Name == item.Item.Name:
                item.Quantity -= Inventory.Quantity
                if item.Quantity == 0:
                    pass # Not Implemented. Remove from mapping/association or something
                return
    
    def remove_items(self, *Items):
        for i in Items:
            self.remove_item(i)

class Inventory(Base):
    _User_id = Column(ForeignKey(User.id), primary_key=True)
    _Item_id = Column(ForeignKey(Items.id), primary_key=True)
    Quantity = Column(Integer)
    Item = relationship(Items)
    def __init__(self, Item=None, Quantity=1):
        self.Item = Item
        self.Quantity = Quantity

class Log(Base):
    GuildID = Column(BigInteger, ForeignKey('Servers.GuildID'), primary_key=True)
    Timestamp = Column(TIMESTAMP(True), primary_key=True, default=func.now())
    ByUser = Column(BigInteger, primary_key=True)
    ToUser = Column(BigInteger, primary_key=True)
    Sent_Quantity = Column(Integer)
    Received_Quantity = Column(Integer)

    _Type_id = Column(ForeignKey(Types.id))  # One to One
    Type = relationship(Types, uselist=False)
    _Sent_id = Column(ForeignKey(Items.id))  # One to Many
    Sent = relationship(Items, foreign_keys='Log._Sent_id')
    _Received_id = Column(ForeignKey(Items.id))  # One to Many
    Received = relationship(Items, foreign_keys='Log._Received_id')
    def __init__(self, GuildID: int, ByUser: User, ToUser: User, Type: Types, Sent: Inventory, Received: Inventory):
        self.GuildID = GuildID
        self.ByUser = ByUser.id
        self.ToUser = ToUser.id
        self._Type_id = Type.id
        if Sent is not None:
            self.Sent_Quantity = Sent.Quantity
            self._Sent_id = Sent.Item.id
        if Received is not None:
            self.Received_Quantity = Received.Quantity
            self._Received_id = Received.Item.id
