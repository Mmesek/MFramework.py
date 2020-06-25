from MFramework.commands import register
from MFramework.utils.utils import Embed
from MFramework.utils.api import Spotify

@register(group='System', help='search spotify', alias='', category='')
async def ssearch(self, *query, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = Spotify()
    await s.connect()
    res = await s.search('+'.join(query), 'artist', '&limit=10')
    l = ''
    for i in res['artists']['items']:
        l += f"\n- [{i['name']}](https://open.spotify.com/artist/{i['id']})"
    embed = Embed().setDescription(l).setColor(1947988).setAuthor(' '.join(query),res['artists']['href'].replace('api','open').replace('/v1/','/').replace('?query=','/').split('&')[0],'https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png').setThumbnail(res['artists']['items'][0]['images'][0]['url'])
    await self.embed(data.channel_id, '', embed.embed)
    await s.disconnect()
