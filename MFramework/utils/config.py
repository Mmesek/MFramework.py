import configparser
from os.path import dirname
path = dirname(__file__)+"/../.././data/secrets.ini"


def ConfigToDict():
    dictonary = {}
    config = configparser.ConfigParser()
    config.read(path)
    sections = config.sections()
    if sections == []:
        GenerateConfig()
        exit()
    for section in sections:
        dictonary[section] = {}
        for option in config.options(section):
            try:
                value = config.get(section, option)
                if value.isdigit():
                    value = config.getint(section, option)
                elif value.lower() in ['true', 'false', 'yes', 'no', 'on', 'off']:
                    value = config.getboolean(section, option)
                dictonary[section][option] = value
            except Exception as ex:
                print("Exception while reading from config file: ", ex)
                dictonary[section][option] = None
    return dictonary


def GenerateConfig():
    config = configparser.ConfigParser()
    config.read_dict({
        "Tokens": {'discord': '', 'steam': '', 'spotify': '', 'twitter': '', 'twitch': ''},
        "Discord": {'presence': '', 'subscription': False, 'presence_type': 3, 'status': 'dnd', 'alias': '!'},
        "Spotify": {'client': '', 'secret': '', 'auth': ''},
        "Twitter": {'client': '', 'secret': '', 'auth': ''},
        "Database": {'db': 'sqlite', 'user': '', 'password': '', 'location': 'raspberry', 'port': '', 'name': 'MBot', 'echo': True},
        "Influx": {'db': 'MFramework', 'host': 'raspberry'},
        "Defaults": {"locale":"en_GB", "owner": 273499695186444289}
    })
    with open(path, 'w') as file:
        config.write(file)
    print('Generated config file, edit it and restart')


cfg = ConfigToDict()