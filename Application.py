import csv
import time
import socket
import os.path
import argparse
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen


MAX_TIME = 60
PORT_READER = 4000
PORT_SERVER = 5000
FILE = "Application.csv"
HOST_READER = "127.0.0.1"
HOST_SERVER = "127.0.0.1"
LABEL = ["identificator", "surname", "name", "middle_name", "birth_day", "birth_month",
         "birth_year", "work", "sex", "mobile_number", "host", "port"]


Window.fullscreen = 'auto'


def create_message():
    result = ""
    message = ""
    identificator = ""
    check = False
    with open(FILE, 'r') as file:
        results = csv.reader(file)
        for row in results:
            if check:
                result = ",".join(row)
                result = result.split(",")
                identificator = result[0]
                for i in range(len(result)):
                    if i != len(result) - 1:
                        message += (result[i] + ",")
                    else:
                        message += result[i]
            else:
                check = True
    return result, identificator, message


def change_file(data):
    new_rows = [LABEL, data]
    with open(FILE, 'w', newline='') as file:
        create = csv.writer(file)
        for i in new_rows:
            create.writerow(i)
    return


class Application(App):
    def build(self):
        work = Greeting()
        work.run()
        sm.add_widget(MainScreen())
        sm.add_widget(DataScreen())
        sm.add_widget(OutputScreen())
        sm.add_widget(InputIsReady())
        sm.add_widget(BadSocketWork())
        sm.add_widget(GoodSocketWork())
        sm.add_widget(NoSocketWork())
        sm.add_widget(InputIsNotReady())
        sm.add_widget(EditSocket())
        sm.add_widget(DeleteSocket())
        sm.add_widget(Exit())
        return sm


class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Menu'
        self.max_time = MAX_TIME
        main_layout = BoxLayout(orientation="vertical")
        self.add_widget(main_layout)
        buttons = ["Ввести данные",
                   "Вывести данные",
                   "Связаться с сервером",
                   "Принять соединение с сервером (даётся " + str(self.max_time) + " секунд)",
                   "Получить доступ",
                   "Выход"]
        chrono = Myclock()
        Clock.schedule_interval(chrono.update, 0.01)
        main_layout.add_widget(chrono)
        for label in buttons:
            button = Button(
                text=label,
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
            if label == "Ввести данные":
                button.bind(on_press=self.button_data_input)
            if label == "Вывести данные":
                button.bind(on_press=self.button_data_output)
            if label == "Связаться с сервером":
                button.bind(on_press=self.button_socket)
            if label == "Принять соединение с сервером (даётся " + str(self.max_time) + " секунд)":
                button.bind(on_press=self.button_connect)
            if label == "Получить доступ":
                button.bind(on_press=self.button_qrcode)
            if label == "Выход":
                button.bind(on_press=self.button_exit)
            main_layout.add_widget(button)

    def button_data_input(self, *args):
        if not os.path.exists(FILE):
            self.manager.current = 'Data_Input'
        else:
            self.manager.current = 'Message'
        return

    def button_data_output(self, *args):
        if os.path.exists(FILE):
            self.manager.current = 'Data_Output'
        else:
            self.manager.current = 'No_Data'
        return

    def button_socket(self, *args):
        count = 0
        port_number = 0
        column_number = 0
        host_number = ""
        message = "delete,XXX-XXX-XXX-XXX-XXX,"
        new_row = []
        new_result = [LABEL]
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    column_number = len(row)
                count += 1
        if os.path.exists(FILE):
            result, identificator, message = create_message()
            try:
                sock = socket.socket()
                sock.connect((HOST_SERVER, PORT_SERVER))
                my_host, my_port = sock.getsockname()
                sock.send(message.encode())
                data = sock.recv(1024)
                new_identificator = data.decode('UTF-8')
                sock.close()
                if new_identificator != "":
                    result[0] = new_identificator
                    if column_number < len(LABEL):
                        result.append(my_host)
                        result.append(my_port)
                    new_rows = [LABEL, result]
                    with open(FILE, 'w', newline='') as file:
                        create = csv.writer(file)
                        for i in new_rows:
                            create.writerow(i)
                    self.manager.current = 'Socket_Good_Info'
                else:
                    self.manager.current = 'Socket_No_Info'
            except ConnectionRefusedError:
                self.manager.current = 'Socket_Bad_Info'
        else:
            self.manager.current = 'No_Data'
        return

    def button_connect(self, *args):
        count = 0
        new_result = [LABEL]
        data = []
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    new_row = row
                count += 1
        try:
            sock = socket.socket()
            sock.settimeout(self.max_time)
            sock.bind((new_row[len(new_row) - 2], int(new_row[len(new_row) - 1])))
            sock.listen(1)
            conn, address = sock.accept()
            data = conn.recv(1024)
            data = data.decode('UTF-8')
            data = data.split(",")
            conn.close()
        except TimeoutError:
            self.manager.current = 'Socket_Bad_Info'
        if len(data) > 0:
            action = data.pop(0)
            change_file(data)
            if action == "edit":
                self.manager.current = 'Edit_Connection'
            if action == "delete":
                self.manager.current = 'Delete_Connection'
        return

    @staticmethod
    def button_qrcode(*args):
        count = 0
        identificator = ""
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    identificator = row[0]
                count += 1
        try:
            sock = socket.socket()
            sock.connect((HOST_READER, PORT_READER))
            sock.send(identificator.encode())
            sock.close()
            return
        except ConnectionRefusedError:
            return

    def button_exit(self, *args):
        self.manager.current = 'Exit'
        Clock.schedule_once(app.stop, 2.5)
        return


class OutputScreen(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Data_Output'
        self.info = ["Имя: ", "Фамилия: ", "Отчество: ", "День Рождения: ", "Месяц Рождения: ", "Год Рождения: ",
                     "Должность: ", "Пол: ", "Номер телефона: "]
        self.labels = []
        output_layout = GridLayout(cols=3, spacing=10, padding=10)
        self.add_widget(output_layout)
        for i in range(len(self.info)):
            label = Label(text="   ",
                          size_hint=(1, .25),
                          pos_hint={"center_x": .5, "center_y": .5})
            self.labels.append(label)
            output_layout.add_widget(label)
        button = Button(text='Вывести',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button.bind(on_press=self.to_output)
        output_layout.add_widget(button)
        button = Button(text='В меню',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button.bind(on_press=self.to_menu)
        output_layout.add_widget(button)

    def to_output(self, *args):
        count = 0
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    for j in range(len(row)):
                        if (j < len(self.info) + 1) and (j > 0):
                            self.labels[j - 1].text = self.info[j - 1] + str(row[j])
                count += 1
        return

    def to_menu(self, *args):
        for i in range(len(self.labels)):
            self.labels[i].text = self.info[i]
        self.manager.current = 'Menu'
        return


class DataScreen(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Data_Input'
        input_layout = GridLayout(cols=3, row_force_default=True, row_default_height=60, padding=10)
        self.add_widget(input_layout)
        self.user_surname = TextInput(text='Введите свою фамилию')
        self.user_name = TextInput(text='Введите своё имя')
        self.user_middle_name = TextInput(text='Введите своё отчество')
        self.birth_day = TextInput(text='Введите свой день рождения')
        self.birth_month = TextInput(text='Введите свой месяц рождения')
        self.birth_year = TextInput(text='Введите свой год рождения')
        self.work = TextInput(text='Введите свою должность')
        self.sex = TextInput(text='Введите свой пол (М/Ж)')
        self.mobile_number = TextInput(text='Введите свой номер телефона (X-XXX-XXX-XX-XX)')
        input_layout.add_widget(self.user_surname)
        input_layout.add_widget(self.user_name)
        input_layout.add_widget(self.user_middle_name)
        input_layout.add_widget(self.birth_day)
        input_layout.add_widget(self.birth_month)
        input_layout.add_widget(self.birth_year)
        input_layout.add_widget(self.work)
        input_layout.add_widget(self.sex)
        input_layout.add_widget(self.mobile_number)
        button = Button(text='Подтвердить',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button.bind(on_press=self.to_confirm)
        input_layout.add_widget(button)

    def to_confirm(self, *args):
        check_emptiness = False
        check_fillness = False
        check_birth = False
        check_work = True
        check_sex = False
        check_mobile_number = False
        text_1 = "Введите свою фамилию"
        text_2 = "Введите своё имя"
        text_3 = "Введите своё отчество"
        text_7 = "Введите свою должность"
        if self.user_surname.text != text_1 and self.user_name.text != text_2 and self.user_middle_name.text != text_3\
                and self.work.text != text_7:
            check_emptiness = True
        if self.user_surname.text != "" and self.user_name.text != "" and self.user_middle_name.text != "" and \
                self.work.text != "":
            check_fillness = True
        if self.birth_day.text.isdigit() and self.birth_month.text.isdigit() and self.birth_year.text.isdigit():
            check_birth = True
        if self.sex.text == 'М' or self.sex.text == 'Ж':
            check_sex = True
        for i in range(len(self.work.text)):
            if self.work.text[i].isdigit():
                check_work = True
        if len(self.mobile_number.text) == 15:
            check_mobile_number = True
        if check_birth and check_sex and check_work and check_mobile_number and check_emptiness and check_fillness:
            self.write_files()
            self.manager.current = 'Menu'
        return

    def write_files(self):
        file = open(FILE, "w+")
        file.close()
        row_result = ["XXX-XXX-XXX-XXX-XXX", self.user_surname.text, self.user_name.text, self.user_middle_name.text,
                      self.birth_day.text, self.birth_month.text, self.birth_year.text, self.work.text,
                      self.sex.text, self.mobile_number.text]
        new_result = [LABEL, row_result]
        with open(FILE, 'a', newline='') as file:
            create = csv.writer(file)
            for i in new_result:
                create.writerow(i)


class InputIsReady(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Message'
        no_input_layout = BoxLayout()
        self.add_widget(no_input_layout)
        button = Button(text='Вы уже выполнили ввод данных! Чтобы вернуться\n'
                             'в меню, нажмите на данную кнопку, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        no_input_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class BadSocketWork(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Socket_Bad_Info'
        no_input_layout = BoxLayout()
        self.add_widget(no_input_layout)
        button = Button(text='Соединение не было установлено! Нажмите на кнопку,\n'
                             'чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        no_input_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class GoodSocketWork(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Socket_Good_Info'
        no_input_layout = BoxLayout()
        self.add_widget(no_input_layout)
        button = Button(text='Соединение было успешно выполнено! Нажмите на\n'
                             'кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        no_input_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class NoSocketWork(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Socket_No_Info'
        no_input_layout = BoxLayout()
        self.add_widget(no_input_layout)
        button = Button(text='В соединении вам было отказано сервером! Нажмите на\n'
                             'кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        no_input_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class InputIsNotReady(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'No_Data'
        not_ready_layout = BoxLayout()
        self.add_widget(not_ready_layout)
        button = Button(text='Вы не выполнили ввод данных! Вернитесь\n'
                             'в меню и выполните ввод, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        not_ready_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class EditSocket(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Edit_Connection'
        no_input_layout = BoxLayout()
        self.add_widget(no_input_layout)
        button = Button(text='Ваша информация была успешно изменена! Нажмите на\n'
                             'кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        no_input_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class DeleteSocket(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Delete_Connection'
        no_input_layout = BoxLayout()
        self.add_widget(no_input_layout)
        button = Button(text='Ваше удаление было завершено! Нажмите на\n'
                             'кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        no_input_layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class Exit(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Exit'
        exit_layout = BoxLayout()
        self.add_widget(exit_layout)
        label = Label(text='До свидания, пользователь!')
        exit_layout.add_widget(label)


class Greeting(App):
    def build(self):
        label = Label(text='Здравствуйте, пользователь!')
        Clock.schedule_once(self.stop_interval, 2.5)
        return label

    @staticmethod
    def stop_interval(self):
        app.stop()


class Myclock(Label):
    def update(self, *args):
        self.text = time.asctime()


if __name__ == '__main__':
    sm = ScreenManager()
    app = Application()
    try:
        app.run()
    except argparse.ArgumentError:
        app.stop()
