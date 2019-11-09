# -*- coding: utf-8 -*-
import re
import json
import requests

class Editing_text:
    ############################################################
    def __init__(self, token_f: str, lang_f_tr: str, lang_f_sp: str):
        self.__token = token_f  # Токен Яндекс Api
        if not self.__token:
            self.__token = "trnsl.1.1.20190515T103629Z.7e7b77fe38876871.71ae08a964ef85fe1e434223e5b095b3f79ce4ee"
        self.__lang_tr = lang_f_tr  # Язык перевода
        self.__lang_sp = lang_f_sp  # Язык перевода
        self.hash_lang = {}  # Хешь с преводом
        self.hash_spel = {}  # Хешь с орфографией
        self.hash_spel_all_text = set() #
        self.__Read_hash()  # Считывания хеша их файла
        self.size_hash_lang = self.hash_lang.__sizeof__()
        self.size_hash_spel = self.hash_spel.__sizeof__()
    ############################################################


    ##################################
    """Сохранение хеша"""
    def Save_hash(self) -> None:
        # Save hash_lang
        with open('save_hash_lang.json', 'w', encoding='utf-8') as JSon_W:
            json.dump(self.hash_lang, JSon_W,
                      sort_keys=False, ensure_ascii=False)

        # Save hash_spel
        with open('save_hash_spel.json', 'w', encoding='utf-8') as JSon_W:
            json.dump(self.hash_spel, JSon_W,
                      sort_keys=False, ensure_ascii=False)
    
    """Чтение хеша"""
    def __Read_hash(self) -> None:
        # Save hash_lang
        try:
            with open('save_hash_lang.json', 'r', encoding='utf-8') as JSon_R:
                self.hash_lang = json.load(JSon_R)

        except FileNotFoundError:
            self.hash_lang = {}

        # Save hash_spel
        try:
            with open('save_hash_spel.json', 'r', encoding='utf-8') as JSon_R:
                self.hash_spel = json.load(JSon_R)

        except FileNotFoundError:
            self.hash_spel = {}
    ##################################


    ##################################
    """Переводчик"""
    def __transelte_func(self, text: str) -> str:

        # Если есть в хеши
        if text in self.hash_lang:
            return text 

        # Если нет то ищем в интеренете
        try:
            # Запрос в интеренат для перевода текста
            answer = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate',
                                    params={
                                        "key": self.__token,
                                        'text': str(text),
                                        'format': 'plain',
                                        'lang': self.__lang_tr}).json()

            # Если все хорошо
            if answer['code'] == requests.codes["ALL_GOOD"]:  # 200
                #Хешируем перевод
                self.hash_lang[text] = answer['text'][0]
                return answer['text'][0]
            # Если токен неработает
            elif answer['code'] == requests.codes["UNAUTHORIZED"]:  # 401
                return None
        # Если нет интернета
        except requests.exceptions.ConnectionError:
            return False

    """Связка для перевода"""
    def transl_search(self, text: str) -> str:
        text = text.split(".")
        res_two_lg = ""
        for proposal in text:
            # Обрезать повторяющиеся пробелы и пробелы вначале и конце
            # чтобы лишний раз не искать в интернете одинаковые слова
            # с разными пробелами 
            proposal = re.sub(" +", " ", proposal.strip())
            tmp_trans = self.__transelte_func(proposal)
            if tmp_trans:
                res_two_lg += f"{tmp_trans}."
        return res_two_lg

    """Переопредление языка для перевода"""
    def set_lang_tr(self, lang: str) -> None:
        option_lang = {"Ru": "ru", "Eng": "en"}
        self.__lang_tr = option_lang[lang]
    ##################################


    ##################################
    """Варианты замены не правильного слова"""
    def __control_spelling(self, text: str) -> tuple:
        # Если есть в хеши то не ищем в интернете
        for x in text.split(" "):
            if x in self.hash_spel:
                return (x, self.hash_spel[x])

        # Если нет то ищем в интеренте
        try:
            # get запрос на проверку текста
            respons = requests.get('https://speller.yandex.net/services/spellservice.json/checkText?',
                                   params={
                                       'text': text,
                                       'lang': self.__lang_sp}).json()
       
            if respons:
                # Записывать в хешь
                for wodr_x in respons:
                    if not wodr_x['word'] in self.hash_spel:
                        self.hash_spel[wodr_x['word']] = wodr_x['s']

                return (respons[0]['word'], respons[0]['s'])
       
        # Если нет интеренета
        except requests.exceptions.ConnectionError: 
            return False

    """Связка для орфографии"""
    def spl_search(self, text: str) -> tuple:
        text = text.split(".")
        tmp_spl = tuple()
        for proposal in text:
            proposal = re.sub(" +", " ", proposal.strip())
            if not proposal in self.hash_spel_all_text:
                tmp_spl = self.__control_spelling(proposal)
                if tmp_spl:
                    return tmp_spl
                self.hash_spel_all_text.add(proposal)
        return tmp_spl

        """
        for x in text:
            # Если нет в хеши предложений с ошибкой
            if not x in self.hash_spel_all_text:
                # Разделяем преложение по словам и проверяем их
                for list_x in x.split(" "):
                    # Если нет в хеши слов с ошибками то ищем в интеренте
                    if not list_x in self.hash_spel:
                        tmp_spl = self.__control_spelling(list_x)
                        if tmp_spl:
                            # Записываем в хешь новое неправильное слово
                            self.hash_spel[tmp_spl[0]] = tmp_spl[1]
                            return tmp_spl
                    # Если есть в хеши то возвращаем имеющийся список
                    else:
                        return (list_x, self.hash_spel[list_x])
                    self.hash_spel_all_text.add(x)
        """
    ##################################


if __name__ == "__main__":
    Tr = Editing_text(None, "en", "ru")
    text_1 = "Приве"
    Tr.spl_search(text_1)
    Tr.transl_search(text_1)