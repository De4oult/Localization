import yaml
import json
import os

def copy_dict(dictionary: dict[str, any]) -> dict[str, str]:
    result: dict[str, str] = {}

    for key, value in dictionary.items():
        result[key] = copy_dict(value) if(isinstance(value, dict)) else ''

    return result

class Localization:
    def __init__(self, path: str, language: str = 'json') -> None:
        """
            class Localization

            arguments
                - path     (str) <- relative or full path to locales folder
                - language (str) <- json || yaml
        """
        if language not in ('json', 'yaml', 'yml'): raise ValueError('Unsupported language. Set JSON or YAML')

        self.path: str = os.path.abspath(path)
        self.language: str = language
        self.messages: dict[str, str] = {}
        
        self.locales: list[str] = ['en']
        self.current_locale: str  = 'en'
        self.fallback_locale: str = 'en'

        self.__load()

    def __load(self) -> None:
        os.makedirs(self.path, exist_ok = True)

        for locale in self.locales:
            self.__load_locale(locale)

    def __load_locale(self, locale: str) -> None:
        locale_path: str = os.path.join(self.path, f'{locale}.{self.language}')
            
        if not os.path.exists(locale_path):
            with open(locale_path, 'w', encoding = 'utf-8') as locale_file: 
                json.dump({}, locale_file)
            
        with open(locale_path, 'r', encoding = 'utf-8') as file:
            self.messages[locale] = json.load(file) if (self.language == 'json') else yaml.safe_load(file)

    def fallback(self, locale: str) -> None: 
        """
        """
        self.fallback_locale: str = locale
        
    def add_locale(self, locale: str) -> None: 
        """
        """
        self.locales.append(locale)
        self.__load_locale(locale)

    def get(self, message_path: str, **kwargs) -> str | None:
        """
        """
        if not isinstance(message_path, str) or not message_path: 
            raise ValueError('The path to the message must be a non-empty string')

        def __nested(parts: list[str], messages: dict[str, str]) -> str | None:
            if parts and messages: 
                try:    messages = messages.get(parts[0], None)
                except: return

                return __nested(parts[1:], messages)

            return messages
        
        parts: list[str] = message_path.split('.')
        message: str | None = __nested([self.current_locale] + parts, self.messages)

        fallback: str | None = __nested([self.fallback_locale] + parts, self.messages) if ((not message) and (self.current_locale != self.fallback_locale)) else None

        message: str = message or fallback

        if not message:
            raise KeyError(f'There is no message in the localization file with the path \'{message_path}\'')

        return message.format(**kwargs)