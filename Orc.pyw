# -*- coding: utf-8 -*-
import os
import json

import tkinter

from PIL import Image, ImageTk, ImageGrab
from cv2 import resize, GaussianBlur, imwrite
from numpy import array

try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    ORC_check = True
except ModuleNotFoundError:
    ORC_check = False


class ORC():
    ####################################################
    def __init__(self) -> None:
        self.__optimization() 
        self.__x, self.__y = 0, 0
        self.__all_cord = []
        self.__text_args = []

    def __optimization(self) -> None:
        # Если нет папке дял фоток
        if not os.path.exists('Photo'):
            os.makedirs('Photo')
        # Если модуль распознования текста не установлен
        if not ORC_check:
            self.__writ_result([False])
            raise ModuleNotFoundError
    ####################################################


    ####################################################
    """Для получения результата когда будет .exe"""
    def __writ_result(self,list_odject:list) -> None:
         with open('res_orc.json', 'w', encoding='utf-8') as json_writ:
            json.dump(list_odject, json_writ,sort_keys=False, ensure_ascii=False)
    ####################################################


    ####################################################
    """Скриншот рабочего стола и поиск по нему"""
    def search_desktop(self) -> list:
        #Скриншот экрана
        image_decktop = ImageGrab.grab() 
        image_decktop.save("Photo\\photo_t.png")
        self.search_photo("Photo\\photo_t.png")
        return self.__text_args

    """Поиск по фото"""
    def search_photo(self, name_photo: str) -> list:
        self.__init__()

        self.__Windows = tkinter.Tk()

        self.__Windows.overrideredirect(1)
        self.__Windows.wm_attributes('-topmost', 1)
        self.__paint = tkinter.Canvas(self.__Windows)

        self.__imgas_ITk = ImageTk.PhotoImage(image = Image.open(r'{}'.format(name_photo)))

        self.__Windows.geometry('{}x{}+0+0'.format(
            self.__imgas_ITk._PhotoImage__size[0],
            self.__imgas_ITk._PhotoImage__size[1]))

        self.__paint['width'] = self.__imgas_ITk._PhotoImage__size[0]
        self.__paint['height'] = self.__imgas_ITk._PhotoImage__size[1]
        self.__paint.create_image(0, 0, anchor=tkinter.NW, image=self.__imgas_ITk)
        self.__paint.pack()

        self.__Windows.update()

        self.__Windows.bind('<B1-Motion>', self.__press_mous)
        self.__Windows.bind('<ButtonRelease-1>', self.__held_mouse)
        self.__Windows.bind('<F2>', self.__exit_func)

        self.__Windows.mainloop()

        return self.__text_args
    ####################################################
    

    ####################################################
    """Получение фоток из выделеных областей"""
    def __cap_box(self) -> list:
        imags_f = []
        for x in self.__all_cord:
            monitor = ImageGrab.grab(bbox=(x[1], x[0], x[4], x[5]))  
            img = resize(array(monitor), (0, 0), fx=10, fy=10)
            img = GaussianBlur(img, (11, 11), 0)
            imags_f.append(img)
        return imags_f

    """Распознование текста в выделеных областях"""
    def __exit_func(self, event) -> None:
        del event
        self.__Windows.unbind('<B1-Motion>')
        self.__Windows.unbind('<ButtonRelease-1>')
        self.__Windows.unbind('<F2>')

        # Получение фоток из выделеных областей
        imags = self.__cap_box()

        self.__paint.pack_forget()
        self.__Windows.destroy()

        self.__text_args = []
        for img_loc in enumerate(imags):
            try:
                a = pytesseract.image_to_string(img_loc[1], lang='eng')
                # Если текст не распознан то сохраняем фото
                if a == '':
                    imwrite('Photo\\except_photo{}.png'.format(
                        img_loc[0]), img_loc[1])
                # Записываем текст в массив
                self.__text_args.append(a)

            except pytesseract.pytesseract.TesseractNotFoundError:
                if 'tesseract-ocr.exe' in os.listdir(os.getcwd()):
                    os.system('tesseract-ocr.exe')
                    return False
                print('Для работы этой функции необходимо устоновить tesseract по ссылки\nhttps://github.com/UB-Mannheim/tesseract/wiki\nУкажите при установки следующий путь\nC:\\Program Files\\Tesseract-OCR')
                return False

            except pytesseract.pytesseract.TesseractError:
                print('Выбраный язык не устоновлен - выберите этот язык при устоновки')
                return False

        # запись результата в файл
        self.__writ_result(self.__text_args)

    """Рисует квадрат и запоминает начальное положение мыши"""
    def __press_mous(self, event) -> None:
        if self.__x == 0 and self.__y == 0:
            self.__x = event.x
            self.__y = event.y
        else:
            self.__paint.delete('circle')
            self.__paint.create_rectangle(event.x,
                                          event.y,
                                          self.__x,
                                          self.__y,
                                          outline='blue',
                                          tag='circle')

    """Высчитывает положение окна"""
    def __held_mouse(self, event) -> None:
        if self.__x != 0 and self.__y != 0:
            #########################################
            x0, x_max = self.__x, event.x
            X = x0 - x_max
            if X < 0:
                X *= -1
            else:
                x0, x_max = x_max, x0
            #########################################
            y0, y_max = self.__y, event.y
            Y = y0 - y_max
            if Y < 0:
                Y *= -1
            else:
                y0, y_max = y_max, y0
            #########################################
            self.__x = self.__y = 0
            # Отображение нескольких квадратов
            self.__paint.create_rectangle(
                x_max, y_max, x0, y0, outline='blue', tag=str(x_max))
            # Положение всех квадратов записываеться
            self.__all_cord.append((y0, x0, X, Y, x_max, y_max))

        # Если просто нажата кнопка то завершаем сканирываение
        else:
            self.__exit_func(0)
    ####################################################


if __name__ == "__main__":
    #pyinstaller -F -w Orc.pyw
    Or = ORC()
    ph = Or.search_desktop()
    print(ph)
    