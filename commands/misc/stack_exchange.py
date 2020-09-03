from MFramework.commands import register
from MFramework.utils.utils import Embed
import requests

@register(group='System', help='Search Stack Overflow', alias='', category='')
async def stack_search(self, *search, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    #Inspired by https://github.com/Vik0105/Devscord
    r = requests.get("https://api.stackexchange.com/2.2/search?order=desc&site=stackoverflow&intitle=" + ' '.join(search))
    r = r.json()
    size = f'Total Questions: {len(r["items"])}'
    if r["has_more"]:
        size+= "+"
    e = Embed().setTitle(' '.join(search)).setFooter("", size)
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
    await self.embed(data.channel_id, "", e.embed)

