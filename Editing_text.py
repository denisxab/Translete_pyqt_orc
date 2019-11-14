# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C0301
# pylint: disable=R0902
# pylint: disable=W0105


import os
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
        self.__hash_lang = {}  # Хешь с преводом
        self.__hash_spel = {}  # Хешь с орфографией
        self.__hash_spel_all_text = set()  # времяный хешь слов без ошибок
        self.__optimization()  # Проверки и оптимизации
        self.__Read_hash()  # Считывания хеша их файла
        self.size_hash_lang = self.__hash_lang.__sizeof__()
        self.size_hash_spel = self.__hash_spel.__sizeof__()
    ############################################################

    ##################################
    """Проверки и оптимизации"""

    def __optimization(self) -> None:
        # Если нет папке дял хеша
        if not os.path.exists('hash'):
            os.makedirs('hash')

    """Сохранение хеша"""

    def Save_hash(self) -> None:
        # Save __hash_lang
        with open(r'hash\\save_hash_lang.json', 'w', encoding='utf-8') as JSon_W:
            json.dump(self.__hash_lang, JSon_W,
                      sort_keys=False, ensure_ascii=False)

        # Save __hash_spel
        with open(r'hash\\save_hash_spel.json', 'w', encoding='utf-8') as JSon_W:
            json.dump(self.__hash_spel, JSon_W,
                      sort_keys=False, ensure_ascii=False)

    """Чтение хеша"""

    def __Read_hash(self) -> None:
        # Save __hash_lang
        try:
            with open(r'hash\\save_hash_lang.json', 'r', encoding='utf-8') as JSon_R:
                self.__hash_lang = json.load(JSon_R)

        except FileNotFoundError:
            self.__hash_lang = {}

        # Save __hash_spel
        try:
            with open(r'hash\\save_hash_spel.json', 'r', encoding='utf-8') as JSon_R:
                self.__hash_spel = json.load(JSon_R)

        except FileNotFoundError:
            self.__hash_spel = {}
    ##################################

    ##################################
    """Переводчик"""

    def __transelte_func(self, text: str) -> str:

        # Если есть в хеши
        if text in self.__hash_lang:
            # Чтобы ключ и значение были разыне
            if self.__hash_lang[text] != text:
                return self.__hash_lang[text]

        # Если нет то ищем в интеренете
        try:
            # Запрос в интеренат для перевода текста
            answer = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate',
                                  params={
                                      "key": self.__token,
                                      'text': text,
                                      'format': 'plain',
                                      'lang': self.__lang_tr}).json()

            # Если все хорошо
            if answer['code'] == requests.codes["ALL_GOOD"]:  # 200
                # Хешируем перевод
                self.__hash_lang[text] = answer['text'][0]
                return answer['text'][0]
            # Если токен неработает
            elif answer['code'] == requests.codes["UNAUTHORIZED"]:  # 401
                return None
        # Если нет интернета
        except requests.exceptions.ConnectionError:
            return False

        return None

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

    def __control_spelling(self, text: str) -> list:

        # Если есть в хеши то не ищем в интернете
        all_wrong_text = []
        for word in text.split(" "):
            if word in self.__hash_spel:
                # Если в предложение есть несколько слов с ошибкой
                # то возвращаем все слова
                res = (word, self.__hash_spel[word])
                all_wrong_text.append(res)
        if all_wrong_text:
            return all_wrong_text

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
                    if not wodr_x['word'] in self.__hash_spel:
                        self.__hash_spel[wodr_x['word']] = wodr_x['s']
                # Отправляем двумерный массив
                return [[respons[0]['word'], respons[0]['s']]]

        # Если нет интеренета
        except requests.exceptions.ConnectionError:
            return False

        return None

    """Связка для орфографии"""

    def spl_search(self, text: str) -> list:
        text = text.split(".")
        # Переменная для всех неправильных слов в тексте
        return_spl = {}
        for proposal in text:
            # Обрезаем лишнии пробелы
            proposal = re.sub(" +", " ", proposal.strip())
            if not proposal in self.__hash_spel_all_text:
                # Временная пременная для результата функции
                tmp_spl_res = self.__control_spelling(proposal)
                # Если в слове есть ошибки
                if tmp_spl_res:
                    # Записываем эти слова в общую кучу
                    for key, value in tmp_spl_res:
                        return_spl[key] = value
                # Если слово предложение без ошибки то пропускаем
                else:
                    # Временный хешь с предложениями без ошибок
                    self.__hash_spel_all_text.add(proposal)

        # конвертируем словарь в список для того чтобы небыло повторений
        return_spl = [(key, value) for key, value in return_spl.items()]
        return return_spl
    ##################################


if __name__ == "__main__":
    Tr = Editing_text(None, "en", "ru")
    text_1 = " Приве умнек. умнек Приве "
    a = Tr.spl_search(text_1)
    print(a)
    Tr.transl_search(text_1)
    Tr.Save_hash()
