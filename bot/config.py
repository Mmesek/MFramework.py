import configparser
path="data/secrets.ini"

def ConfigSectionMap(section):
    print('Executing ConfigSectionMap!')
    dict1={}
    config = configparser.ConfigParser()
    config.read(path)
    config.sections()
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

tokens=ConfigSectionMap('Tokens')
spotify=ConfigSectionMap('Spotify')
twitter=ConfigSectionMap('Twitter')
twitch=ConfigSectionMap('Twitch')