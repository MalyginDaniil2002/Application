import csv
import socket
import os.path
import argparse
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen


PORT_READER = 4000
PORT_SERVER = 5000
IDENTIFICATOR_INDEX = 1
LOCAL_TIME_MAX = 5
FILE = "Reader.csv"
HOST_READER = "127.0.0.1"
HOST_SERVER = "127.0.0.1"
LABEL = ["list_number", "identificator", "surname", "name", "middle_name", "birth_day", "birth_month", "birth_year",
         "work", "sex", "mobile_number", "host", "port"]


def update_file():
    data = ""
    new_result = []
    try:
        sock = socket.socket()
        sock.connect((HOST_SERVER, PORT_SERVER))
        while True:
            data = sock.recv(1024)
            if not data:
                break
            else:
                row = data.decode('UTF-8')
                row = row.split(",")
                new_result.append(row)
        sock.close()
        if new_result:
            with open(FILE, 'w', newline='') as my_file:
                new_create = csv.writer(my_file)
                for i in new_result:
                    new_create.writerow(i)
        return
    except ConnectionRefusedError:
        return


def access(data):
    count = 0
    identificators = []
    message = "   "
    with open(FILE, 'r') as my_file:
        results = csv.reader(my_file)
        for row in results:
            if count > 0:
                identificators.append(row[IDENTIFICATOR_INDEX])
            count += 1
    if data in identificators:
        message = "o"
    else:
        message = "x"
    return message


class Reader(App):
    def build(self):
        sm.add_widget(Menu())
        sm.add_widget(GoodAccess())
        sm.add_widget(BadAccess())
        return sm


class Menu(Screen):
    def __init__(self):
        super().__init__()
        self.name = "Menu"
        reader_layout = BoxLayout(orientation="vertical")
        self.add_widget(reader_layout)
        button_1 = Button(text="Зайти")
        button_1.bind(on_press=self.get_access)
        reader_layout.add_widget(button_1)
        button_2 = Button(text="Обновить данные")
        button_2.bind(on_press=self.get_update)
        reader_layout.add_widget(button_2)
        button_3 = Button(text="Выйти")
        button_3.bind(on_press=self.to_exit)
        reader_layout.add_widget(button_3)

    def get_access(self, *args):
        try:
            sock = socket.socket()
            sock.settimeout(LOCAL_TIME_MAX)
            sock.bind((HOST_READER, PORT_READER))
            sock.listen(1)
            application, address = sock.accept()
            data = application.recv(1024)
            message = access(data.decode('UTF-8'))
            sock.close()
            if message == "o":
                self.manager.current = 'Good_Access'
            else:
                self.manager.current = 'Bad_Access'
        except (ConnectionRefusedError, TimeoutError):
            return
        return

    @staticmethod
    def get_update(*args):
        update_file()
        return

    @staticmethod
    def to_exit(*args):
        app.stop()


class GoodAccess(Screen):
    def __init__(self):
        super().__init__()
        self.name = "Good_Access"
        reader_layout = BoxLayout(orientation="vertical")
        self.add_widget(reader_layout)
        button_1 = Button(text="o",
                          font_size="800sp",
                          color=(0, 1, 0, 1))
        button_1.bind(on_press=self.to_finish)
        reader_layout.add_widget(button_1)

    def to_finish(self, *args):
        self.manager.current = 'Menu'
        return


class BadAccess(Screen):
    def __init__(self):
        super().__init__()
        self.name = "Bad_Access"
        reader_layout = BoxLayout(orientation="vertical")
        self.add_widget(reader_layout)
        button_1 = Button(text="x",
                          font_size="800sp",
                          color=(1, 0, 0, 1))
        button_1.bind(on_press=self.to_finish)
        reader_layout.add_widget(button_1)

    def to_finish(self, *args):
        self.manager.current = 'Menu'
        return


if __name__ == "__main__":
    if not os.path.exists(FILE):
        with open(FILE, 'w') as file:
            create = csv.writer(file)
            create.writerow(LABEL)
    sm = ScreenManager()
    app = Reader()
    try:
        app.run()
    except argparse.ArgumentError:
        app.stop()
