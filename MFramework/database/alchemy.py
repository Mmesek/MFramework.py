from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Boolean, BigInteger, ARRAY, TIMESTAMP, Date #, BLOB, PickleType, Date, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import relationship, backref

Base = declarative_base()


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
    LastMessage = Column(TIMESTAMP(True))#Integer)

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

    def __init__(self, UserID, Language=None, Birthday=None, Color=None, Timezone=None):
        self.UserID = UserID
        self.Language = Language
        self.Birthday = Birthday
        self.Color = Color
        self.Timezone = Timezone
