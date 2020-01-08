import configparser
path="bot/data/secrets.ini"

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
                elif value.lower() in ['true','false','yes','no','on','off'] :
                    value = config.getboolean(section, option)
                dictonary[section][option]=value
            except Exception as ex:
                print("Exception while reading from config file: ",ex)
                dictonary[section][option] = None
    return dictonary

    
def GenerateConfig():
    config = configparser.ConfigParser()
    config.read_dict({
        "Tokens":{'discord':'','steam':'','spotify':'','twitter':'','twitch':''},
        "Discord":{'presence':'','subscription':False,'presence_type':3},
        "Spotify":{'client':'','secret':'','auth':''},
        "Twitter":{'client':'','secret':'','auth':''},
        "Database":{'location':'raspberry','name':'MBot'}
    })
    with open(path,'w') as file:
        config.write(file)
    print('Generated config file, edit it and restart')

cfg = ConfigToDict()
