# -*- coding: utf-8 -*-
import re
import sys
import json
import time

from functools import partial
import threading

from Front_end import Ui_MainWindow  # импорт нашего сгенерированного файла
from PyQt5 import QtWidgets, QtCore

import requests

from Editing_text import Editing_text
from Orc import ORC



class mywindow(QtWidgets.QMainWindow):
    ############################################################
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # setPlainText - удаляет и вставляет текст
        self.ui.plainTextEdit.setPlainText(" Првие")
        self.status = True # Перенная для выхода из потока


        ####################################################################
        # Получение и перевод тектса                                       #
        self.Tr = Editing_text(None, "en", "ru")
        # Переводчик
        # переменна для вставки текста из потока
        self.result_cycle_threading_Translete = ""
        self.thr_1 = threading.Thread(target=self.__cycle_threading_Translete)
        self.thr_1.start()
        # Функция которая записывает полученные данные из потока в окно
        self.timer_tr = QtCore.QTimer()
        self.timer_tr.timeout.connect(self.__cycle_write_Translete)
        self.timer_tr.start(1000)
        ####################################################################

        ####################################################################
        #       Изменение языка                                            #
        # Изменяет язык перевода при выборе его в comboBox
        self.ui.comboBox.currentIndexChanged.connect(self.__change_language)
        ####################################################################

        ####################################################################
        #        Орфография                                                #
        # Все кнопки для вставки текста
        self.all_button = (self.ui.pushButton, self.ui.pushButton_2,
               self.ui.pushButton_3, self.ui.pushButton_4)
        # Отдельынй поток который проверяет орфографию
        self.thr_2 = threading.Thread(target=self.__cycle_threading_Split)
        self.thr_2.start()
        ####################################################################

        ####################################################################
        #       Распознвоание текста                                       #
        try:
            self.Orc = ORC()
            self.ui.pushButton_5.clicked.connect(self.__ORC_Translete)
        # Если ошибка с модулем распознования текста
        except ModuleNotFoundError:
            self.ui.pushButton_5.clicked.connect(lambda:self.ui.pushButton_5.setText("No ORC"))    
    ############################################################


    ############################################################
    """Выключение программы"""
    def delit(self):
        self.status = False
        self.Tr.Save_hash()
    ############################################################


    ############################################################
    """Изменение языка перевода"""
    def __change_language(self) -> None:
        self.Tr.set_lang_tr(self.ui.comboBox.currentText())
        text_1 = self.ui.plainTextEdit.toPlainText()
        self.ui.plainTextEdit.setPlainText(f"{text_1}_")
    ############################################################


    ############################################################
    """Распознвоание текста"""
    def __ORC_Translete(self):
        # Свернуть окно
        self.showMinimized()
        res = ""
        for x in self.Orc.search_desktop():
            res += f"{x}.\n"
        self.ui.plainTextEdit.setPlainText(res)
        # Развернуть окно
        self.showNormal()
    ############################################################


    ############################################################
    """Потоковая функция работа с переводом"""
    def __cycle_threading_Translete(self) -> None:
        # Цикл по получения текста из plainTextEdit
        # и его перевод
        Cheak = ""
        while self.status:
            # Получаем текст для перевода
            text_1 = self.ui.plainTextEdit.toPlainText()
            if text_1 != Cheak:
                Cheak = text_1
                text_2 = self.Tr.transl_search(text_1)
                # Записываем в переменную для функции "__cycle_write_Translete"
                self.result_cycle_threading_Translete = text_2

            time.sleep(1)

    """Отображение перевода"""
    def __cycle_write_Translete(self) -> None:
        # Вставка текста из потока, так как в потоке
        # нельзя вставить текст
        text_2 = self.ui.plainTextEdit_2.toPlainText()
        if text_2 != self.result_cycle_threading_Translete:
            self.ui.plainTextEdit_2.setPlainText(
                self.result_cycle_threading_Translete)
    ############################################################


    ############################################################
    """Отчистка кнопок от функция"""
    def __anbind_button(self) -> None:
        for button in self.all_button:
            button.setText("")
            try:
                button.clicked.disconnect()
            except TypeError:
                pass

    """Потоковая функция работа с орфографией"""
    def __cycle_threading_Split(self) -> None:
        # Переменная для проверки повторения
        Cheak = ""
        while self.status:
            # Получение текста для орфографической проверки
            text_1 = self.ui.plainTextEdit.toPlainText()
            if text_1 != Cheak:
                # Изменяем Cheak
                Cheak = text_1
                # Поиск в тексте ошибки
                text_3 = self.Tr.spl_search(text_1)
                # Если есть ошибка
                if text_3:
                    # Отчиска кнопок от прошлых значений
                    self.__anbind_button()
                    # Если слов замены больше 4 то обрезаем до 4 слов замены
                    lenger = 4 if  len(text_3[1]) > 4 else len(text_3[1])
                    for word_args in range(lenger):
                        # Вставляем в кнопку текст с заменой
                        self.all_button[word_args].setText(text_3[1][word_args])
                        # Назначаем функцию для кнопки
                        self.all_button[word_args].clicked.connect(
                            partial(self.__cycle_write_Split, text_3[0], text_3[1][word_args]))

                # Если в тексте нет ошибок
                # Тогда отчищаем кнопки
                else:
                    self.__anbind_button()
   
            time.sleep(1.5)

    """Замена слова в тексте на слово которое указанно в кнопке"""
    def __cycle_write_Split(self, text_wrong: str, text_right: str) -> None:
        #print(f"tw - {text_wrong}\t tr - {text_wrong}")
        
        # Делим текст по пробелам
        text_1 = self.ui.plainTextEdit.toPlainText().split(" ")

        for word in enumerate(text_1):
            # Если неправтльный слова есть в тексте то заменяем
            # По индексу  
            if text_wrong == word[1]:
                text_1[word[0]] = text_right
        # Вставляем новый текст в текстовое поле plainTextEdit
        self.ui.plainTextEdit.setPlainText(" ".join(text_1))

        # Отчищаем всех кнопки
        self.__anbind_button()
    ############################################################



if __name__ == "__main__":
    #pyinstaller -F -w Translator.py
    ################################
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()
    app.exec()
    ################################
    # Остонавливаем потоки и вызываем save_hash у Editing_text
    application.delit()
    sys.exit(0)
