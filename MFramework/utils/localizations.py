import os
from typing import Optional

from mdiscord.types import Locales
from mlib.utils import remove_None

from MFramework import log
from MFramework.commands.command import Command, commands

LOCALIZATIONS: list[str] = []
"""Locales found in locale directory"""

DEFAULT_LOCALE: str = "en-US"
"""Fallback locale used when user locale couldn't be found"""

try:
    import os

    import i18n

    i18n.load_path.append("././locale")
    i18n.set("filename_format", "{namespace}.{format}")
    i18n.set("skip_locale_root_data", True)
    i18n.set("file_format", "json")

    for path in [p for p in i18n.load_path if os.path.exists(p)]:
        for locale in os.listdir(path):
            if locale == "en":
                log.warn(
                    "Detected locale 'en' which is ambigiuous. Rename it to either en-US or en-GB. Setting up as en-US"
                )
                locale = "en-US"
            if locale not in Locales:
                continue
            log.debug("Found directory for locale %s", locale)
            LOCALIZATIONS.append(locale)

    if len(LOCALIZATIONS) == 1:
        log.debug("Found only one %s locale. Setting up as default", LOCALIZATIONS[0])
        DEFAULT_LOCALE = LOCALIZATIONS[0]

except ImportError:
    log.debug("Package i18n not found. Localizations are unavailable")

try:
    import json

    import yaml

    _load = yaml.safe_load

except ImportError:
    import json

    log.debug("Package yaml not found. Localizations can only use .json format")

    _load = json.load


SKIP: list[str] = ["ctx"]
"""Parameters that should be skipped while generating command localization files"""


def _load_locale(locale_path: str) -> dict[str, dict | str]:
    """
    Loads localization files. Merges all namespaces into nested dictonary
    Parameters
    ---
    locale_path:
        Locale's Path to load
    """
    _ = {}
    if os.path.exists(locale_path):
        # Merge from namespaces
        for path in os.listdir(locale_path):
            if os.path.isdir(locale_path + "/" + path):
                _[path.split(".", 1)[0]] = _load_locale(locale_path + "/" + path)
            else:
                with open(locale_path + "/" + path, "r", encoding="utf-8") as file:
                    _[path.split(".", 1)[0]] = _load(file)

    return _


def _update_locale(locale: str, localization_strings: dict[str, dict | str]):
    """
    Writes localization files to drive

    Parameters
    ---
    locale:
        Locale to write for
    localization_strings:
        Dictonary containing localization keys
    """
    for key, value in localization_strings.items():
        if type(value) is not dict:
            continue
        if value.get("_namespace"):
            _update_locale(locale + "/" + key, localization_strings[key])
        else:
            if not os.path.isdir(locale):
                os.makedirs(locale)
            with open(locale + "/" + key + ".json", "w", encoding="utf-8") as file:
                file.write(json.dumps(localization_strings[key], indent=4, ensure_ascii=False))


def _generate(localization: dict, name: str, obj: Command) -> dict[str, dict | str]:
    """
    Generates basic localization dictonary with registered commands

    Inferred keys
    ---
    `name`, `description`, `choices`, `arguments`, `sub_commands`

    Parameters
    ---
    localization:
        Dictonary containing so far found strings
    name:
        Name of scope to fetch metadata for (like command name)
    obj:
        object supporting `name`, `description` and optionally `choices`, `arguments` and/or `sub_commands`
    """
    if name in SKIP:
        return {}

    if name not in localization:
        localization[name] = {}
    _ = localization[name]

    if type(_) is str:
        return localization

    if not _.get("name", None):
        _["name"] = obj.name

    if not _.get("description", None):
        _["description"] = obj.description

    for key in ["choices", "arguments"]:
        _o = getattr(obj, key, None)
        if not _o:
            continue

        for _name, attr in _o.items():
            if key not in _:
                _[key] = {}

            if key != "choices" and type(attr) is str:
                _[key][_name] = attr
                continue
            elif type(attr) is int or key == "choices":
                _[key][_name] = _name
                continue

            _[key][_name] = _generate(_[key], _name, attr).get(_name, None)

    for sub_cmd in getattr(obj, "sub_commands", []):
        if "sub_commands" not in _:
            _["sub_commands"] = {}

        _["sub_commands"] = _generate(_["sub_commands"], sub_cmd.name, sub_cmd)

    return localization


def update_localization(locale_path: str) -> None:
    """
    Updates localization files with missing keys

    Parameters
    ---
    locale_path:
        Path to locale that should be updated
    """
    localization = _load_locale(locale_path)

    for name, command in commands.items():
        # We are redoing everything for each locale in order to update only relevant data
        # Otherwise we would need to update locale using missing keys
        # in which case we would still need to get commands with almost same flow
        # just with branching in a different place
        # PRs are welcome
        _nested = localization

        _namespaces = command.func.__module__.split(".")
        for x, _namespace in enumerate(_namespaces):
            if _namespace not in _nested:
                _nested[_namespace] = {}

            # If we don't add 1, it'll result in translation file for each code file
            # This behaviour might be desired in certain cases
            # however *personally* I'm not convinced to that style for translations
            if x + 1 != len(_namespaces):
                _nested["_namespace"] = True
            _nested = _nested[_namespace]

        _nested.update(_generate(_nested, name, command))

    localization = remove_None(localization)

    _update_locale(locale_path, localization)


def update_all_localizations(locale_path: str = "locale") -> None:
    """
    Updates all found localization files with missing keys

    Parameters
    ---
    locale_path:
        Path to locale directory that should contain locales
    """
    for locale in LOCALIZATIONS:
        update_localization(locale_path + "/" + locale)


def translate(
    key: str,
    locale: str,
    _namespace: Optional[str | list[str]] = None,
    _bot: Optional[str] = None,
    default: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Fetches localization strings according to possible patterns

    Parameters
    ---
    key:
        Key to find
    locale:
        Which locale to look for
    _namespace:
        Namespace to look for. Leave empty to skip. Supports list for nested lookup
    _bot:
        Bot namespace override. Leave empty to skip
    default:
        Default value, returned if nothing found

    Returns
    ---
    Localized string or `default`

    Resolution order & Patterns
    ---
    - {locale}.{bot}.{namespace}.{key}
    - {locale}.{bot}.{namespace}.global.{key}
    - {locale}.{bot}.{key}
    - {locale}.{bot}.global.{key}
    - {locale}.{namespace}.{key}
    - {locale}.{namespace}.global.{key}
    - {locale}.{key}

    Compiled keys examples
    ---
    key = `my_key`, bot = `name`, namespace = `commands`, locale = `en`
    - en.name.commands.my_command.my_key
    - en.name.commands.global.my_key
    - en.name.my_key
    - en.name.global.my_key
    - en.commands.my_key
    - en.commands.global.my_key
    - en.my_key
    """
    import i18n

    keys = []
    if type(_namespace) is not list:
        _namespace = [_namespace]
    ns = [".".join(_namespace[: x + 1]) for x, _ in enumerate(_namespace)]
    if _bot:
        for _ in ns:
            keys.append(f"{_bot}.{_}")
            keys.append(f"{_bot}.{_}.global")
        keys.append(_bot)
        keys.append(f"{_bot}.global")
    for _ in ns:
        keys.append(_)
        keys.append(f"{_}.global")

    for _key in keys:
        _key = f"{locale}.{_key}.{key}"
        _k = i18n.t(_key, **kwargs)
        if _k and _k != _key:
            return _k

    if default:
        kwargs["default"] = default

    return i18n.t(f"{locale}.{key}", **kwargs)
