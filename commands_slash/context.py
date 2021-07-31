from MFramework import Groups, Context, register, Message, Embed, log, Snowflake
from typing import List, Dict, Union, Any
# Chapters can point to any other chapter, in any order _however_ if they do not point to any, next chapter in list should be used
# Subscribe to message changes, perhaps involve redis and pub/sub? 
# Otherwise "watch" message for updates
# Not all Story types will make use of updates but it still might be worth adding...
# Otherwise a type-related code is needed
# type being a variable object with duck typed methods?
# next should be some sort of iterator that switches currently active chapter
# Also better initializer could be pretty useful

try:
    import yaml
    def load_story(name, language='en') -> 'Story':
        with open(f'data/stories/{language}/{name}.yaml','r',newline='',encoding='utf-8') as file:
            story = yaml.safe_load(file)
        return Story(**story)
except ImportError:
    import json
    log.warn("Couldn't import yaml. Falling back to JSON as a stories format")
    def load_story(name, language="en") -> 'Story':
        with open(f'data/stories/{language}/{name}.json','r',newline='',encoding='utf-8') as file:
            story = json.load(file)
        return Story(**story)

class Base:
    name: str = "Error"
    description: Union[str, List[str]] = "Chapter not found"
    input_constraints: Dict[str, Any]
    type: str
    reward: Dict[str, int]
    def __init__(self, **kwargs) -> None:
        for keyword, arg in kwargs.items():
            t = self.__annotations__.get(keyword)
            if type(arg) is list:
                updated = []
                for x, item in enumerate(arg):
                    if type(item) is dict and 'embed' in item:
                        item = Embed(**item['embed'])
                    updated.append(item)
                arg = updated
            if hasattr(t, '_name'):
                if t._name == 'Dict':
                    k, v  = t.__args__
                    if v not in {dict, list, str, int} and not hasattr(v, '_name') and type(arg) is dict and v is not type(arg):
                        print(type(v), v)
                        print(type(arg), arg)
                        print(k)
                        arg = {_k: v(**_a) for _k, _a in arg.items()}
            setattr(self, keyword, arg)

    async def send_delayed_message(self, ctx: Context, message: str):
        import asyncio
        if type(message) is not Embed:
            await ctx.send(message)
            sleep = len(message)/60
        else:
            await ctx.send(embeds=[message])
            sleep = 10
        await ctx.deferred()
        await asyncio.sleep(sleep)

    async def send(self, ctx: Context, messages: List[str] = None) -> None:
        parts = messages or (self.description if type(self.description) is list else [self.description])
        for part in parts:
            await self.send_delayed_message(ctx, part)
    

class Chapter(Base):
    choices: List[str]
    next: Dict[str, str]

    def get_next(self, answer: str) -> str:
        if len(self.next) > 1:
            return self.next.get(answer)
        return list(self.next.values())[0]

class Story(Base):
    chapters: Dict[str, Chapter] = {"start": Chapter()}
    choices: Dict[str, List[str]] = {} # Random.choice lists
    blacklisted_answers: List[str] = []
    intro: List[str] = []
    epilogue: List[str] = []
    errors: Dict[str, str] = {}

    async def check_constraints(self, input_constraints: Dict[str, Any], answer: Message) -> bool:
        constraints = {
            "only_digit": answer.content.isdigit(),
            "min_length": len(answer.content),
            "min_words": len(set(answer.content.split(' ')))
        }
        for constraint, value in input_constraints.items():
            c = constraints.get(constraint, False)
            if type(c) is int:
                if c < value:
                    await answer.reply(self.errors.get(f"{constraint}_constraint", "Error"))
                    return True
            elif c:
                await answer.reply(self.errors.get(f"{constraint}_constraint", "Wrong answer"))
                return True
            elif answer.content in self.blacklisted_answers:
                await answer.reply(self.errors.get("blacklisted_answer_constraint", "Wrong answer"))
                return True
        return False

    def next_chapter(self, chapter: Chapter, answer: str) -> Chapter:
        try:
            next = chapter.get_next(answer)
        except:
            next = list(self.chapters.keys()).index(chapter.name)
        return self.chapters.get(next, chapter)

class ContextStory:
    ctx: Context
    story: Story
    current_chapter: Chapter
    messages: Dict[Snowflake, Message]
    user_responses: Dict[str, Snowflake]
    def __init__(self, ctx: Context, story_name: str, language: str) -> None:
        self.ctx = ctx
        self.story = load_story(story_name, language)
        self.current_chapter = self.story.chapters.get("start")
        self.messages = {}
        self.user_responses = {}

    async def get(self, event: str="create", timeout: float=3600) -> Message:
        return await self.ctx.bot.wait_for(
                    "message_"+event if not self.ctx.is_dm else "direct_message_"+event, 
                    check=lambda x: x.author.id == self.ctx.user_id and 
                                    x.channel_id == self.ctx.channel_id and
                                    (x.content in self.current_chapter.choices 
                                    if getattr(self.current_chapter, 'choices', False) else True),
                    timeout=timeout)
    
    def watch(self, msg: Message):
        import asyncio
        async def update(msg):
            r = await self.ctx.bot.wait_for(
                "message_edit" if not self.ctx.is_dm else "direct_message_edit", 
                check=lambda x:
                    x.id == msg.id and
                    x.channel_id == msg.channel_id
            )
            self.messages[msg.id] = r

        asyncio.create_task(update(msg))

    async def chapter(self, *, skip_description: bool = False, event: str="create") -> None:
        if not skip_description:
            await self.current_chapter.send(self.ctx)

        m = await self.get(event)

        if await self.story.check_constraints(self.current_chapter.input_constraints, m):
            return await self.chapter(skip_description=True, event="edit")

        self.save_response(m)
        self.next(m)

        return await self.chapter()

    def next(self, msg: Message):
        self.current_chapter = self.story.next_chapter(self.current_chapter, msg.content)
    
    def save_response(self, message: Message) -> None:
        self.user_responses[self.current_chapter.name] = message.id
        self.messages[message.id] = message
    async def start(self):
        await self.story.send(self.ctx, self.story.intro)
        await self.chapter()
        await self.story.send(self.ctx, self.story.epilogue)
        types.get(self.story.type)(self.user_responses)


@register(group=Groups.GLOBAL)
async def story(ctx: Context, name: str="createcharacter", *, language):
    '''Story Executor'''
    language='pl'
    story = ContextStory(ctx, name, language)
    await story.start()

def createcharacter(ctx: Context, answers: Dict[str, str]):
    from MFramework.database import alchemy as db
    s = ctx.db.sql.session()
    character = db.Character(user_id=ctx.user_id)
    for answer in answers:
        setattr(character, answer, answers[answer])

types = {
    "createcharacter":createcharacter
}


#@register(group=Groups.MODERATOR)
async def conversation(bot: 'HTTP_Client', filename: str, *, channel_id: Snowflake, default_username: str, webhook_id: Snowflake, webhook_token: str):
    '''Runs linear conversation flow'''
    with open(f'data/{filename}.md','r',newline='',encoding='utf-8') as file:
        lines = file
    for line in lines:
        slept = False
        if line.startswith('#') or line.strip() == '' or line.startswith('//'):
            continue
        if ":" in line:
            username, content = line.split(':', 1)
        else:
            username = default_username
            content = line
            if 'później' in line:
                from mlib.converters import total_seconds
                sleep = total_seconds(line).seconds
                slept = True
            await bot.trigger_typing_indicator(channel_id)
            await asyncio.sleep(sleep)
        if '#' in content and '%' in content:
            l = content.split('#',1)
            content = l[0]
            sleep /= int(l[1].strip().split('%',1)[0].strip()) / 100
        if '//' in content:
            content = content.split('//',1)[0]
        sleep = len(content.split(' ')) * 0.73
        await bot.execute_webhook(webhook_id, webhook_token, username=username, content=content)
        if not slept:
            await bot.trigger_typing_indicator(channel_id)
            await asyncio.sleep(sleep)
    


if __name__ == "__main__":
    from mlib import arguments
    from mdiscord.http_client import HTTP_Client
    arguments.add("--token", help="Specifies bot token to use")
    arguments.add("--user", help="Specifies user id to use")
    arguments.add("--webhook", help="Specifies webhook id to use")
    arguments.add("--webhook_token", help="Specifies webhook token to use")
    arguments.add("--username", help="Specifies default username to use")
    arguments.add("--avatar", help="Specifies default avatar to use")
    arguments.add("--channel", help="Specifies channel that should receive messages")
    arguments.add("--filename", help="Specifies conversation file to play")
    import asyncio
    async def main():
        args = arguments.parse()
        e = HTTP_Client(args.token, args.user_id)
        await conversation(e, args.filename, default_username=args.username, webhook_id=args.webhook_id, webhook_token=args.webhook_token)
    asyncio.run(main())
