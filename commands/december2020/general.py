from .utils import _t
from .utils import *
from MFramework.database import alchemy as db
from datetime import datetime, timezone, timedelta

@DecemberEvent()
async def gift(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()

    _user = get_inventory(s, data.author.id)
    user = get_user_id(user)
    if user == data.author.id:
        return await self.message(data.channel_id, _t("cant_send_present_to_yourself", language))

    gift_type = db.Types.by_name(s, "Gift")
    own_present = False

    user_history = db.Log.filter(s, GuildID=data.guild_id, ToUser=user, ByUser=data.author.id, Type=gift_type).first()
    #user_history = s.query(db.Log).filter(db.Log.GuildID == data.guild_id, db.Log.ToUser == user, db.Log.ByUser == data.author.id, db.Log.Type == gift_type).first()

    if user_history is not None:
        return await self.message(data.channel_id, _t('present_already_sent', language, timestamp=user_history.Timestamp.strftime("%Y/%m/%d %H:%M")))

    for item in _user.Items:
        if 'Present' in item.Item.Name and item.Item.Name != 'Golden Present':
            if item.Quantity > 0:
                own_present = True
            break

    if not own_present:
        return await self.message(data.channel_id, _t('not_enough_presents', language))

    golden_present = db.Items.by_name(s, "Golden Present")

    last_gift = s.query(db.Log).filter(db.Log.GuildID == data.guild_id, db.Log.ByUser == data.author.id, db.Log.Type == gift_type).order_by(db.Log.Timestamp.desc()).first()
    now = datetime.now(tz=timezone.utc)

    if last_gift is None or (now - last_gift.Timestamp) >= timedelta(hours=2):
        target_inv = get_inventory(s, user)
        gift = db.Inventory(golden_present, 1)
        send_item = db.Inventory(item.Item)
        transfer_item(s, data.guild_id, _user, target_inv, gift_type, gift, send_item, turn_item=True)
        s.commit()
        await self.message(data.channel_id, _t('present_sent_successfully', language))        
    else:
        await self.message(data.channel_id, _t('remaining_cooldown', language, cooldown=timedelta(hours=2) - (now - last_gift.Timestamp)))

@DecemberEvent()
async def cookie(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()

    _user = get_inventory(s, data.author.id)
    user = get_user_id(user)
    if user == data.author.id:
        return await self.message(data.channel_id, _t("cant_send_cookie_to_yourself", language))
    user = get_inventory(s, user)

    cookie_type = s.query(db.Types).filter(db.Types.Name == 'Cookie').first()
    cookie_item = s.query(db.Items).filter(db.Items.Name == 'Cookie').first()
    cookie_inv = db.Inventory(cookie_item)

    transfer_item(s, data.guild_id, _user, user, cookie_type, cookie_inv, None, remove_item=False)
    s.commit()
    await self.message(data.channel_id, _t('cookie_sent', language))


@DecemberEvent()
async def advent(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    user = get_inventory(s, data.author.id)

    today = datetime.now(tz=timezone.utc)
    if today.month != 12 or today.day > 24:
        return await self.message(data.channel_id, _t('advent_finished', language))

    advent_type = s.query(db.Types).filter(db.Types.Name == 'Advent').first()
    _today = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    _year = datetime(today.year, 1, 1)
    claimed_total = s.query(db.Log).filter(db.Log.ByUser == data.author.id, db.Log.Type == advent_type, db.Log.Timestamp >= _year).all()
    claimed_today = False
    for claimed in claimed_total:
        if claimed.Timestamp >= _today:
            claimed_today = True
    #claimed_today = s.query(db.Log).filter(db.Log.ByUser == data.author.id, db.Log.Type == advent_type, db.Log.Timestamp >= _today).first()
    if not claimed_today:
        advent_item = s.query(db.Items).filter(db.Items.Name == 'Advent').first()
        advent_inventory = db.Inventory(advent_item, 1)
        transfer_item(s, data.guild_id, user, user, advent_type, None, advent_inventory, remove_item=False)
        s.commit()
        await self.message(data.channel_id, _t('advent_claimed_successfully', language, total=len(claimed_total)+1))
    else:
        await self.message(data.channel_id, _t('advent_already_claimed', language))

def transfer_item(s, guild_id: int, ByUser: db.User, ToUser: db.User, TransactionType: db.Types = None, Sent: db.Inventory = None, Recv: db.Inventory = None, remove_item = True, turn_item=False):
    if Sent is not None:
        ToUser.add_item(Sent)
        if remove_item and not turn_item:
            ByUser.remove_item(Sent)
    if Recv is not None:
        if not turn_item:
            ByUser.add_item(Recv)
        else:
            ByUser.remove_item(Recv)
        if remove_item and not turn_item:
            ToUser.remove_item(Recv)
    s.add(db.Log(guild_id, ByUser, ToUser, TransactionType, Sent, Recv))


@register(group='System', help='Short description to use with help command', alias='', category='')
async def _add(self, name, *args, data, language, type='item', **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    things = {
        'type': db.Types,
        'event': db.Events,
        'loc': db.Locations,
        'drop': db.Drop,
        'item': db.Items,
    }
    thing = things.get(type, db.Items)(name, *args)
    s.add(thing)
    s.commit()

@register(group='System', help='Short description to use with help command', alias='', category='')
async def multiple_add(self, *names, data, language, type='type', **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    things = {
        'type': db.Types,
        'loc': db.Locations,
    }
    for i in names:
        thing = things.get(type.lower(), db.Types)(i)
        s.add(thing)
    s.commit()

@DecemberEvent()
async def hat(self, *user, data, language, **kwargs):
    from PIL import Image#, ImageDraw, ImageFilter
    from io import BytesIO
    import requests
    if user != ():
        url = f"https://cdn.discordapp.com/avatars/{data.mentions[0].id}/{data.mentions[0].avatar}.png?size=2048"
        fd = requests.get(url).content
    else:
        fd = requests.get(f"https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png?size=2048").content
    img = Image.open(BytesIO(fd))
    hat_image = Image.open("data/santa_hat.png")
    img.paste(hat_image,(img.width-400,0), hat_image)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = buffered.getvalue()
    await self.withFile(data.channel_id, img_str, "avatar.png")
