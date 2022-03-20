from enum import Enum

ALPHABET_UA = 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФЧЦШЩЬЮЯ'
ALPHABET_EN = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class Language(Enum):
    UKRAINIAN = 1
    ENGLISH = 2


class Encrypter:
    def _getAlphabet(self, lang: Language) -> str:
        # todo: python 3.10 match
        if lang == Language.UKRAINIAN:
            return ALPHABET_UA
        elif lang == Language.ENGLISH:
            return ALPHABET_EN
        else:
            raise Exception(f"unknown language {lang}")

    def __init__(self, language: Language):
        self._alphabet = self._getAlphabet(language)
        self._symbol_map: dict[str, int] = {}
        for i, s in enumerate(self._alphabet):
            self._symbol_map[s] = i

    def encrypt(self, text: str, key: int) -> str:
        result = ""
        for s in text:
            symbolIndex = self._symbol_map.get(s.upper())
            if symbolIndex is None:
                result += s
                continue
            encryptedSymbolIndex = (symbolIndex + key) % len(self._alphabet)
            encryptedSumbol = self._alphabet[encryptedSymbolIndex]
            result += (encryptedSumbol if s.isupper() else encryptedSumbol.lower())
        return result

    def decrypt(self, text: str, key: int) -> str:
        result = ""
        for s in text:
            symbolIndex = self._symbol_map.get(s.upper())
            if symbolIndex is None:
                result += s
                continue
            decryptedSymbolIndex = (symbolIndex - key) % len(self._alphabet)
            decryptedSymbol = self._alphabet[decryptedSymbolIndex]
            result += (decryptedSymbol if s.isupper() else decryptedSymbol.lower())
        return result
