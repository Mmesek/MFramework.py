from MFramework import register, Groups, Embed, Context
import requests

@register(group=Groups.GLOBAL, interaction=False)
async def api(ctx: Context, category: str, random: bool=False, desc: str='', title: str='', cors: str='', https: bool=True, auth: str='', *args, language='en', **kwargs):
    '''Search for API
    category:
        Category of an API
    random:
        Whether Should fetch random API
    desc:
        Description of API
    title:
        Title of API
    cors:
        Cross Origin Reasource Sharing
    https:
        Whether API should support HTTPS
    auth:
        Authorization method'''
    #Inspired by https://github.com/Vik0105/Devscord
    base_url = "https://api.publicapis.org/"
    params = []
    if category != ():
        params += ["category=" + category]
    if desc:
        params += ["description=" + desc]
    if title:
        params += ["title=" + title]
    if cors in ['yes','no','unknown']:
        params += ["cors=" + cors]
    if https in ["true", "false"]:
        params += ["https=" + https]
    if auth:
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
        return await ctx.reply(embeds=[e])
    if params == [] and category == ():
        r = requests.get(base_url + "categories")
        categories = ', '.join(r.json())
        return await ctx.reply("Available categories: " + categories)
    url = base_url + "entries"
    url += '?' + '&'.join(params)
    r = requests.get(url)
    apis = ''
    response = r.json()
    embed = Embed().setTitle(category).setFooter("", f"Total: {response['count']}")
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
    await ctx.reply(embeds=[embed])

@register(group=Groups.GLOBAL, interaction=False)
async def stack_search(ctx: Context, search: str, *args, language, **kwargs):
    '''Search Stack Overflow
    search:
        Query to search for'''
    #Inspired by https://github.com/Vik0105/Devscord
    r = requests.get("https://api.stackexchange.com/2.2/search?order=desc&site=stackoverflow&intitle=" + search)
    r = r.json()
    size = f'Total Questions: {len(r["items"])}'
    if r["has_more"]:
        size+= "+"
    e = Embed().setTitle(search).setFooter(size)
    desc = ''
    for q in r['items']:
        question = f'- [{q["title"]}]({q["link"]})\nTags: {", ".join(q["tags"])}'
        answered = q["is_answered"]
        if answered:
            question = "☑️" + question
        else:
            question = "❌" + question
        question += f'\nAnswers/Views: {q["answer_count"]}/{q["view_count"]}\n'
        if len(r['items']) < 25:
            e.addField(q["title"], question, True)
        else:
            if len(desc + question) < 2000:
                desc += question
            else:
                break
        if desc != '':
            e.setDescription(desc)
    await ctx.reply(embeds=[e])

