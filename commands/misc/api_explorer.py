from MFramework.commands import register
from MFramework.utils.utils import Embed
import requests

@register(group='System', help='Search for API', alias='', category='')
async def api(self, *category, data, random=False, desc='', title='', cors='', https='', auth='', language, **kwargs):
    '''Extended description to use with detailed help command'''
    #Inspired by https://github.com/Vik0105/Devscord
    base_url = "https://api.publicapis.org/"
    _category = ' '.join(category)
    params = []
    if category != ():
        params += ["category=" + _category]
    if desc != '':
        params += ["description=" + desc]
    if title != '':
        params += ["title=" + title]
    if cors in ['yes','no','unknown']:
        params += ["cors=" + cors]
    if https in ["true", "false"]:
        params += ["https=" + https]
    if auth != '':
        params += ["auth="+auth]

    if random:
        url = base_url + "random"
        url += '?' + '&'.join(params)
        r = requests.get(url)
        response = r.json()['entries'][0]
        e = Embed().setTitle(response['API']).setDescription(response["Description"])
        e.addField("HTTPS", f'{response["HTTPS"]}', True).addField("Category", response["Category"], True).addField("Cross-Origin Resource Sharing", response["Cors"], True).addField("URL", response["Link"], True)
        if response['Auth'] != "":
            e.addField("Auth", response["Auth"], True)
        return await self.embed(data.channel_id, "", e.embed)
    if params == [] and category == ():
        r = requests.get(base_url + "categories")
        categories = ', '.join(r.json())
        return await self.message(data.channel_id, "Available categories: " + categories)
    url = base_url + "entries"
    url += '?' + '&'.join(params)
    r = requests.get(url)
    apis = ''
    response = r.json()
    embed = Embed().setTitle(_category).setFooter("", f"Total: {response['count']}")
    for api in response['entries']:
        title = api["API"]
        _ = f'- {api["Description"]}\n{api["Link"]}'
        if response['count'] < 25:
            embed.addField(title, _, True)
        else:
            _ = f"**{title}**\n{_}\n"
            if len(apis + _) < 2000:
                apis += _
            else:
                break
    if apis != '':
        embed.setDescription(apis)
    await self.embed(data.channel_id, "", embed.embed)