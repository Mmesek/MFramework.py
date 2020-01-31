Table | | | | | | | | | | |
|-|-|-|-|-|-|-|-|-|-|-|
Servers | GuildID | AdminID | ModID | VipID | NitroID | MutedID | LogFlags? | LogWebhook? | NoExpRoles | NoExpChannels
EmbedTemplates | GuildID | UserID | Name | Message | Title | Description | URL | Footer | Color | Image | Timestamp | Trigger
ServersRegex | GuildID | | Trigger | Response | Group
ReactionRoles | GuildID | ChannelID | MessageID | RoleID | Reaction | RoleGroup
LevelRoles | GuildID | Level | Role | Stacked
UserLevels | GuildID | UserID | EXP | vEXP | LastMessage
Infractions | GuildID | UserID | Timestamp | Reason | ModeratorID | Duration | InfractionType
Webhooks | GuildID | Webhook | Source | Content | Regex | AddedBy
Giveaways | GuildID | ChannelID | MessageID | UserID | Timestamp | Duration | WinnerCount
Games | | UserID | Title | LastPlayed
RSS | | Source | Last | URL | Color | Language
Spotify | | SpotifyID | Artist | AddedBy
ActionLog | GuildID | UserID | Timestamp | Action | Details
RPSessionPlayers | GuildID | HostID | PlayerID | Campaign
PickUps | GuildID | ChannelID | Name | ReqPlayers | Maps | Playcount









Not so important:
```json
GuildID {
   Roles{
       group:[roles]},
   Log{
       settings:{
           action:bool},
       webhooks:{
           action:webhook}},
   Responses{
       group:{
           trigger:response}},
   Users{
       UserID:{
           exp:int,
           vexp:int}},
   Infractions{
       UserID:{
           Timestamp:{
               Reason:'',
               From:uid,
               Duration:int,
               infractiontype:''
}}}}
```

```json
# cache = {
# "server": {
#   "msgs":{
#       "id":{}},
#   "reactions":{
#       "message_id":{
#           "name:id":["role","group"]}},
#   "roles":{
#       "123":2, #mod
#       "234":1, #admin
#       "345":4, #vip
#       "456":3  #nitro
#       },
#   "muted":"567"
#   "groups":["1","2","3"],
#   "responses":{
#       "trigger":"response"},
#   "logging":{
#       "dm":"webhook",
#       "modActions":"webhook",
#       "botActions":"webhook",
#       "logChannel":"webhook"}
#   }
# }```