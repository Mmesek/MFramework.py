from MFramework.commands import register, helpList, extHelpList, Groups, commandList
from MFramework.utils.utils import Embed, replaceMultiple, tr

#@register(help='Sends list of commands')
async def help(self, command=None, *category, group, data, categories=False, **kwargs):
    '''Shows detailed help message for specified command alongside it's parameters, required permission, category and example usage.\nParameters: :command: - Command to show detailed help info for - Example: command\n:category: - Categories to show commands for - Example: Category another...\n:categories: - Shows list of categories - Example: -categories'''
    l = 'en'
    if command != None and self.alias in command:
        command = command.replace(self.alias, '').lower()
        embed = Embed().setTitle(tr('commands.help.title',l, command=command))#(tr.t(f'{language}.commands.help.title',command=command))#('Help details for: ' + command)
        perm = None
        for _group in helpList:
            if command.casefold() in helpList[_group]:
                perm = _group
                if Groups[perm] > Groups[group]:
                    break
                category = helpList[_group][command].get('category', None)
                alias = helpList[_group][command].get('alias', None)
                sig = helpList[_group][command].get('sig', None)
                msg = helpList[_group][command].get('msg', None)
                ext = extHelpList[_group].get(command, None)
                break
        try:
            if perm is not None and Groups[perm] <= Groups[group]:
                embed.addField(tr('commands.help.reqPerm', l), perm, True)
            if category is not None and category != ():
                embed.addField(tr('commands.help.category_', l), category, True)
            if alias is not None:
                embed.addField(tr('commands.help.alias_',l), alias, True)
            if msg is not None:
                embed.addField(tr('commands.help.short_desc',l), msg)
            if sig is not None and sig != '':
                params = sig.split(' ')
                s = ''
                extparams = []
                parameters = {'Required':[], 'Optional':[], 'Multiple':[], 'Named Flag':[], 'Flag':[]}
                for param in params:
                    if '*' in param:
                        parameters['Multiple']+=[param]
                    elif '--' in param:
                        parameters['Named Flag']+=[param]
                    elif '-' in param:
                        parameters['Flag']+=[param]
                    elif '[' in param:
                        parameters['Required']+=[param]
                    elif '(' in param:
                        parameters['Optional'] += [param]
                if ext is not None:
                    ext = ext.split('Parameters: ')
                    extparams = ext[1].split('\n')
                example = self.alias + command
                orderOfParamTypes = ['Command']
                orderofParams = []
                for t in parameters:
                    if parameters[t] == []:
                        continue
                    s += '\n\n**'+t + '**:'
                    for x, param in enumerate(parameters[t]):
                        param = replaceMultiple(param, ['[', ']', '(', ')', '*', '-', '\\'],' ').strip()                        
                        if t == 'Flag':
                            orderOfParamTypes += ['Flag']
                            e ='`-'+param+'`'
                        elif t == 'Named Flag':
                            e = f'`--{param}=abc`'
                            orderOfParamTypes += ['Named Flag']
                        elif t == 'Multiple':
                            e = f'`a b c...`'
                            orderOfParamTypes += ['Multiple...']
                        else:
                            e = '`abc`'
                            if t == 'Required':
                                orderOfParamTypes += ['Required']
                            else:
                                orderOfParamTypes += ['Optional']
                        orderofParams += [param]
                        example += f' {e}'
                if extparams != []:
                    example = self.alias
                    orderOfParamTypes = []
                    for x, args in enumerate(extparams):
                        arg = args.split(' - ')
                        arg[0] = arg[0].replace(':', '').replace('  ', '')
                        if arg[0] == orderofParams[x]:
                            s+='\n'+param
                            s += ' - ' + arg[1]
                        if len(arg) > 1:
                            example += '`'+arg[2].replace('Example: ', '')+'` '
                            orderOfParamTypes += [t for t in parameters if (p for p in parameters[t] if p == arg[0])]
                example +='\n `'+'`|`'.join(orderOfParamTypes)+'`'
                embed.addField(tr('commands.help.example_usage',l),example)
                embed.addField(tr('commands.help.parameters',l), s[:1023])
            if ext is not None and ext[0] != '':
                embed.setDescription(ext[0][:2023].strip())
        except Exception as ex:
            print(ex)
            if perm != None:
                if Groups[perm] > Groups[group]:
                    embed.setDescription(tr('commands.help.noPerm',l)).addField(tr('commands.help.reqPerm',l), perm, True).addField(tr('commands.help.yourPerm',l), group, True)
            else:
                embed.setDescription("Command not found.")
        embed.setColor(self.cache[data.guild_id].color)
        await self.embed(data.channel_id, '', embed.embed)
        return
    elif command != None and self.alias not in command:
        category = [c for c in category]+[command]
    embed = Embed().setTitle('Commands')
    desc = f"""Trigger can be any of: <@{self.user_id}>, `{self.username}` or `{self.alias}`\n"""
    if self.cache[data.guild_id].alias != self.alias:
        desc += f"""Server's Trigger Alias is set to: `{self.cache[data.guild_id].alias}`\n"""
    desc+="""\n**Parameters:**
`[Required]`
`(optional=default value unless default is empty or 0)`
`*` Argument ends with the message. 
`(-flag)`
`(--flag=value)` provided value for flag's variable.
`[@Mention]` - Mention or Snowflake ID that defaults to relative user IDs that issued a command if not specified

**Arguments:**
If there is a single, double quote or a code block then everything inside is treated as a single argument. Mentions won't be removed from message in that case (Unless argument is just "@mention")
If your argument contains a quote, use different quote around whole: \'`"argument go here, double quote is preserved, single is stripped"`\'
Flags are removed from argument list therefore can be specifed anywhere

**Example: ** """+f"""
`{self.alias}add_cc name "trigger goes here" "and 'here' is @mention response" mod`: Will answer `and 'here' is @ mention response` to anyone that types `trigger goes here` and has right permission, in this example: only moderators """
    embed.setDescription(desc)
    g = group
    category = [c.lower().capitalize() for c in category]
    lower = False
    c = {}
    for group in helpList:
        if group == g:
            lower = True
        elif lower == False:
            continue
        elif group == 'dm' and g != 'dm':
            continue
        string = ''
        for one in helpList[group]:
        # Maybe show only commands for certain group/commands up to certain group?
            cat = helpList[group][one].get('category', None)
            if categories and cat not in c.get(group, {}):
                string += f"{cat}\n"
                if group not in c:
                    c[group] = []
                c[group]+=[cat]
            elif categories is False and (cat != None and cat in category or len(category) == 0):
                string += f"**{self.alias}{one}** {helpList[group][one]['sig']}"
                if 'msg' in helpList[group][one]:
                    if helpList[group][one]['msg'] != "Short description to use with help command":
                        string+= f" - {helpList[group][one]['msg']}"
                if 'alias' in helpList[group][one]:
                    string+= ' - Alias: `'+helpList[group][one]['alias']+'`'
                string+='\n'
        if string != '':
            embed.addFields(group, string)
    if categories:
        embed.setDescription('').setTitle(tr('commands.help.available_categories',l))
    embed.setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

from MFramework.utils.utils import check_translation
@register(help='Sends list of commands')
async def help(self, *command, group, data, language, **kwargs):
    '''Shows detailed help message for specified command alongside it's parameters, required permission, category and example usage.
    Parameters: 
        :command: - Command to show detailed help info for - Example: command'''
    embed = Embed()
    if command != ():
        cmd = ''.join(command)
        translated_cmd = check_translation(f"commands.{cmd}.cmd_trigger", language, cmd)
        embed.setTitle(tr("commands.help.title", language, command=translated_cmd))
        embed.setDescription(check_translation(f'commands.{cmd}.cmd_extended_help', language, ""))
        _h = check_translation(f'commands.{cmd}.cmd_help', language, '')
        if _h != '':
            embed.addField(tr('commands.help.short_desc', language), _h)
        return await self.embed(data.channel_id, '', embed.embed)
    embed.setTitle(tr('commands.help.available_triggers', language))
    desc = tr('commands.help.available_triggers', language, botid=self.user_id, botname=self.username, alias=self.alias) + "\n"
    if self.cache[data.guild_id].alias != self.alias:
        desc += tr('commands.help.server_trigger', language, server_alias=self.cache[data.guild_id].alias) + "\n"
    desc += "\n" + tr('commands.help.example_command', language, alias=self.alias) + "\n"
    embed.setDescription(desc)
    filtered = {i: {} for i in commandList}
    groups = list(commandList)
    groups.reverse()
    for x, _group in enumerate(groups):
        if x != 0:
            l = set(commandList[groups[x - 1]].items())
        else:
            l = set()
        c = set(commandList[_group].items()) - l
        filtered[_group] = {i[0]: i[1] for i in c}
    lower = False
    for _group in filtered:
        filtered[_group] = sorted(filtered[_group])
    for g in filtered:
        if group == g:
            lower = True
        elif lower == False:
            continue
        elif g == 'dm' and group != 'dm':
            continue
        string = ""
        for cmd in filtered[g]:
            _cmd = check_translation(f'commands.{cmd}.cmd_trigger', language, cmd)
            _sig = check_translation(f'commands.{cmd}.cmd_signature', language, '')
            _help = check_translation(f'commands.{cmd}.cmd_help', language, '')
            string += f"**{self.alias}{_cmd}**"
            string += f" {_sig}" if _sig != '' else ""
            string += f" - {_help}" if _help != '' else ""
            alias = check_translation(f'commands.{cmd}.cmd_alias', language, '')
            if alias != '':
                string += tr(f'commands.help.alias_message', language, alias=alias)
            string += '\n'
        if string != '':
            embed.addFields(g, string)
    embed.setColor(self.cache[data.guild_id].color).setFooter("", tr('commands.help.yourPerm', language, group=group))
    await self.embed(data.channel_id, '', embed.embed)
