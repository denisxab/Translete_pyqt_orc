# -*- coding: utf-8 -*-
import re
import sys
import json
import time

from functools import partial
from threading import Thread



from Front_end import Ui_MainWindow  # импорт нашего сгенерированного файла
from PyQt5 import QtWidgets, QtCore

import requests

from Editing_text import Editing_text
from Orc import ORC



class mywindow(QtWidgets.QMainWindow):
    ############################################################
    def __init__(self):
        super(mywindow, self).__init__()


        ####################################################################
        self.ui = Ui_MainWindow()                                          #
        self.ui.setupUi(self)                                              #
        # Перенная для выхода из потока                                    #
        self.status = True                                                 #
        #("приве умнек как дила првие. приве как дила")                    #
        self.ui.textEdit.setPlainText("")                                  #
        ####################################################################


        ####################################################################
        #                   Получение и перевод тектса                     #
        # Переводчик                                                       #
        self.Tr = Editing_text(None, "en", "ru")                           #
        # Переменна для вставки текста из потока                           #
        self.result_cycle_threading_Translete = ""                         #
        # Отдельынй поток для перевода текста                              #
        self.thr_1 = Thread(target=self.__cycle_threading_Translete)       #
        # Запуск потока                                                    #
        self.thr_1.start()                                                 #
        ####################################################################


        ####################################################################
        #                         Орфография                               #
        # Записывает из потока список с ошибок->'__cycle_write_button_spl' #
        self.result_cycle_button_spl = []                                  #
        # Все кнопки для вставки текста                                    #
        self.all_button = (                                                #
            self.ui.pushButton,                                            #
            self.ui.pushButton_2,                                          #
            self.ui.pushButton_3,                                          #
            self.ui.pushButton_4)                                          #
        # Скрываем кнопки при запуске программы для красоты                #
        self.__anbind_button()                                             #
        # Переменная для выделения слова с ошибкой                         #
        self.result_cycle_threading_Split = ""                             #
        # Отдельный поток который проверяет орфографию                     #
        self.thr_2 = Thread(target=self.__cycle_threading_Split)           #
        self.thr_2.start()                                                 #
        # Отображение ошибок выделение их красным цветом                   #
        self.ui.pushButton_6.clicked.connect(self.__cycle_write_sp)        #
        ####################################################################


        ####################################################################
        #                Считывания данных их потоков                      #
        # Функция которая записывает перевод из потока в окно              #
        self.timer_tr = QtCore.QTimer()                                    #
        self.timer_tr.timeout.connect(self.__cycle_write_tr)               #
        self.timer_tr.start(1000)                                          #
        # Функция которая отображает кнопки для орфографии                 #
        self.timer_spl = QtCore.QTimer()                                   #
        self.timer_spl.timeout.connect(self.__cycle_write_button_spl)      #
        self.timer_spl.start(1000)                                         #
        ####################################################################
        

        ####################################################################
        #                       Изменение comboBox                         #
        # Изменяет стиля отображения                                       #
        self.ui.comboBox.currentIndexChanged.connect(self.__edit_styleText)#
        # Изменяет язык перевода при выборе его в comboBox                 #
        self.ui.comboBox_2.currentIndexChanged.connect(self.__edit_lang)   #
        ####################################################################


        ####################################################################
        #                   Распознвоание текста                           #
        self.ui.pushButton_5.clicked.connect(self.__ORC_Translete)         #
        ####################################################################



    """Выключение программы"""
    def delit(self) -> None:
        # Выключаем цикл у потоков и таким образом они выключаються
        self.status = False
        # Сохраняем хешь
        self.Tr.Save_hash()
    ############################################################


    ############################################################
    """Изменение языка перевода"""
    def __edit_lang(self) -> None:
        # Измения у класса язык пеервода
        self.Tr.set_lang_tr(self.ui.comboBox_2.currentText())
        # Берем текст без стилей
        text_one_edit = self.ui.textEdit.toPlainText()
        # Переводим его
        text_new_tr = self.Tr.transl_search(text_one_edit)
        # Вставляем в текстовое поле два
        self.ui.plainTextEdit_2.setPlainText(text_new_tr)
        # Изменяем времянную переменную
        self.result_cycle_threading_Translete = text_new_tr


    """Изменение стиля отображения текста"""
    def __edit_styleText(self) -> None:
        if self.ui.comboBox.currentText() == "Text":
            # Берем текст без стилей
            stock_text = self.ui.textEdit.toPlainText()
            # Записываем без стилей
            self.ui.textEdit.setHtml(stock_text)
            # Обрезаем все лишнее и остовляем только выделенный текст с ошибкой
            a = self.result_cycle_threading_Split.split('<span style=" font-family:\'Nirmala UI\'; color:#FF4D00;">')
            # Если это не перевое слово и если там вообще есть неправильные слова
            if len(a) >= 2:
                # Выделяем текст и обрезаем закрывание стиля
                a = a[1].split("</span>")[0]
                # Оставляем только стиль только у текста с ошибкой
                self.result_cycle_threading_Split = stock_text.replace(a,'<span style=" font-family:\'Nirmala UI\'; color:#FF4D00;">{0}</span>'.format(a))
        elif self.ui.comboBox.currentText() == "Html":
            pass
    ############################################################


    ############################################################
    """Распознвоание текста"""
    def __ORC_Translete(self) -> None:
        try:
            # Создать экземпляр класса
            self.Orc = ORC()
            # Свернуть окно
            self.showMinimized()
            res = ""
            for x in self.Orc.search_desktop():
                res += f"{x}.\n"
            self.ui.textEdit.setPlainText(res)
            # Развернуть окно
            self.showNormal()
        # Если ошибка с модулем распознования текста то выходим
        except ModuleNotFoundError:
            self.ui.pushButton_5.clicked.connect(lambda:self.ui.pushButton_5.setText("No ORC"))    
    ############################################################


    ############################################################
    """Потоковая функция работа с переводом"""
    def __cycle_threading_Translete(self) -> None:
        # Переменная с помощью которой проверяеться изменение текста
        Cheak = ""
        while self.status:
            # Получаем текст для перевода
            text_1 = self.ui.textEdit.toPlainText()
            # Если текст изменилсья
            if text_1 != Cheak:
                # Пока не будет изменен текст не будет переводиться
                Cheak = text_1
                # Получаем перевод
                text_2 = self.Tr.transl_search(text_1)
                # Записываем в переменную для функции "__cycle_write_Translete"
                self.result_cycle_threading_Translete = text_2
            # Задержка между проверками
            time.sleep(1)
    ############################################################


    ############################################################
    """Отображение перевода"""
    def __cycle_write_tr(self) -> None:
        # Берем текст без стилей
        text_2 = self.ui.plainTextEdit_2.toPlainText()
        # Если текст отличаеться то вставляем новый
        if text_2 != self.result_cycle_threading_Translete:
            self.ui.plainTextEdit_2.setPlainText(
                self.result_cycle_threading_Translete)
           
            
    """Отображение ошибок"""
    def __cycle_write_sp(self)-> None:
        # Проверяем какой уставновлен стиль отображения
        self.__edit_styleText()
        # Вставляем с стилями текст
        self.ui.textEdit.setHtml(self.result_cycle_threading_Split)
        # Иземняем потоковую переменную чтобы стереть прошлый стиль
        self.result_cycle_threading_Split = self.ui.textEdit.toHtml()


    """Установка значений кнопкам в реальном времяни"""
    def __cycle_write_button_spl(self)-> None:
        # Заполнение кнопок словами заменны
        if self.result_cycle_button_spl:
            # Отчиска кнопок от прошлых значений
            self.__anbind_button()
            # Устоновка новых
            self.__setbin_button(self.result_cycle_button_spl)
    ############################################################


    ############################################################
    """Потоковая функция работа с орфографией"""
    def __cycle_threading_Split(self) -> None:
        # Переменная для проверки повторения
        Cheak = ""
        while self.status:
            # Получение текста для орфографической проверки
            text_1 = self.ui.textEdit.toPlainText()
            if text_1 != Cheak:
                # Изменяем Cheak
                Cheak = text_1
                # Поиск в тексте ошибки
                text_3 = self.Tr.spl_search(text_1)
                # Если есть ошибка в тексте
                if text_3:

                   # Выделяем красным цветом неправильные слова
                    text_html = self.ui.textEdit.toHtml()
                    for word in text_3:
                        # Выделение неправильных слов путем замены html стиля
                        # Изменять 'font-family:\'Nirmala UI\'' при смене шрифта !!!
                        text_html = text_html.replace(word[0],'<span style=" font-family:\'Nirmala UI\'; color:#FF4D00;">{0}</span>'.format(word[0]))
                    self.result_cycle_threading_Split = text_html

                    # Берем первое слово из списка для устоновки его кнопкам
                    self.result_cycle_button_spl = text_3[0]


                # Если в тексте нет ошибок тогда отчищаем кнопки
                else:
                    self.result_cycle_button_spl = [] # потестить !!!
                    self.__anbind_button()
   
            time.sleep(1.5)


    """Замена слова в тексте на слово которое указанно в кнопке"""
    def __cycle_write_Split(self, text_wrong: str, text_right: str) -> None:
        # Делим текст по пробелам
        text_1 = self.ui.textEdit.toPlainText().split(" ")
        for index, word in enumerate(text_1):
            # При поиске убираем точки и запятые из слова
            word = ' '.join(re.findall(r'\w+' ,word))
            # Если неправильное слова есть в тексте то заменяем его
            if text_wrong == word:
                # По индексу  
                text_1[index] = text_right
        # Вставляем новый текст в текстовое поле textEdit
        self.ui.textEdit.setPlainText(" ".join(text_1))
        # Делаем обычный цвет у текст
        self.result_cycle_threading_Split = self.ui.textEdit.toHtml()
        # Отчищаем всех кнопки
        self.__anbind_button()
        # Чтобы текст изменялься цвет текста на обычный
        self.__cycle_write_sp()


    """Отчистка кнопок от функция"""
    def __anbind_button(self) -> None:
        # Отчищаем текст у кнопки и скрываем их
        self.ui.pushButton_6.setText("")
        self.ui.pushButton_6.hide()
        for button in self.all_button:
            button.setText("")
            button.hide()
            try:
                button.clicked.disconnect()
            except TypeError:
                pass


    """Установка кнопокам значений и функция"""
    def __setbin_button(self, text_3:tuple) -> None:
        # Отображаем первое неправильное слово
        self.ui.pushButton_6.setText(text_3[0])
        self.ui.pushButton_6.show()
        # Если слов замены больше 4 то обрезаем до 4 слов замены
        lenger = 4 if  len(text_3[1]) > 4 else len(text_3[1])
        for word_args in range(lenger):
            # Вставляем в кнопку текст с заменой
            self.all_button[word_args].setText(text_3[1][word_args])
            # Назначаем функцию для кнопки
            self.all_button[word_args].clicked.connect(
                partial(self.__cycle_write_Split, text_3[0], text_3[1][word_args]))
            self.all_button[word_args].show()
        # Отчищаем список так как все уже сделанно
        self.result_cycle_button_spl = []
    ############################################################



def main():
    #pyinstaller -F -w Translator.pyw
    ################################
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()
    app.exec()
    ################################
    # Остонавливаем потоки и вызываем save_hash у Editing_text
    application.delit()
    sys.exit(0)


if __name__ == "__main__":
    main()
