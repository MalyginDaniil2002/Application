import csv
import time
import random
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen


MAX_TIME = 60
PORT_SERVER = 5000
LOCAL_TIME_MAX = 10
LIST_NUMBER_INDEX = 0
IDENTIFICATOR_INDEX = 1
SURNAME_INDEX = 2
NAME_INDEX = 3
MIDDLE_NAME_INDEX = 4
BIRTH_DAY_INDEX = 5
BIRTH_MONTH_INDEX = 6
BIRTH_YEAR_INDEX = 7
WORK_INDEX = 8
SEX_INDEX = 9
MOBILE_NUMBER_INDEX = 10
HOST_INDEX = 11
PORT_INDEX = 12
FILE = "Server.csv"
HOST_SERVER = "127.0.0.1"
LABEL = ["list_number", "identificator", "surname", "name", "middle_name", "birth_day", "birth_month", "birth_year",
         "work", "sex", "mobile_number", "host", "port"]


class Server(App):
    def build(self):
        sm.add_widget(Menu())
        sm.add_widget(GetAllScreen())
        sm.add_widget(GetOneScreen())
        sm.add_widget(AddFail())
        sm.add_widget(AddNo())
        sm.add_widget(AddSuccess())
        sm.add_widget(EditFail())
        sm.add_widget(EditSuccess())
        sm.add_widget(EditScreen())
        sm.add_widget(BadDeleteAll())
        sm.add_widget(BadDeleteOne())
        sm.add_widget(GoodDelete())
        sm.add_widget(GoodUpdate())
        sm.add_widget(BadUpdate())
        return sm


class Menu(Screen):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.name = 'Menu'
        self.get_id = TextInput(text='Введите имеющийся номер сотрудника в списке')
        self.delete_id = TextInput(text='Введите имеющийся номер сотрудника в списке')
        self.max_time = MAX_TIME
        main_layout = BoxLayout(orientation="vertical")
        self.add_widget(main_layout)
        buttons = ["Просмотреть всех сотрудников",
                   "Просмотреть конкретного сотрудника",
                   "Добавить сотрудника",
                   "Отредактировать информацию",
                   "Удалить всех сотрудников",
                   "Удалить сотрудника",
                   "Обновить файл для считывателя",
                   "Окончить работу"]
        chrono = Myclock()
        Clock.schedule_interval(chrono.update, 0.01)
        main_layout.add_widget(chrono)
        for label in buttons:
            button = Button(
                text=label,
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
            if label == "Просмотреть всех сотрудников":
                button.bind(on_press=self.button_get_all)
                main_layout.add_widget(button)
            if label == "Просмотреть конкретного сотрудника":
                button.bind(on_press=self.button_get_one)
                main_layout.add_widget(button)
            if label == "Добавить сотрудника":
                button.bind(on_press=self.button_add)
                main_layout.add_widget(button)
            if label == "Отредактировать информацию":
                button.bind(on_press=self.button_edit)
                main_layout.add_widget(button)
            if label == "Удалить всех сотрудников":
                button.bind(on_press=self.button_delete_all)
                main_layout.add_widget(button)
            if label == "Удалить сотрудника":
                h_layout = BoxLayout()
                button.bind(on_press=self.button_delete_one)
                h_layout.add_widget(button)
                h_layout.add_widget(self.delete_id)
                main_layout.add_widget(h_layout)
            if label == "Обновить файл для считывателя":
                button.bind(on_press=self.button_to_update)
                main_layout.add_widget(button)
            if label == "Окончить работу":
                button.bind(on_press=self.button_exit)
                main_layout.add_widget(button)

    def button_get_all(self, *args):
        self.manager.current = 'Get_All'
        return

    def button_get_one(self, *args):
        self.manager.current = 'Get_One'
        return

    def button_add(self, *args):
        count = 0
        new_list_number = 0
        numbers = []
        identificators = []
        new_result = [LABEL]
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    new_result.append(row)
                    numbers.append(int(row[LIST_NUMBER_INDEX]))
                    identificators.append(row[IDENTIFICATOR_INDEX])
                count += 1
        if len(numbers) > 0:
            if numbers[len(numbers) - 1] == len(numbers):
                insert_check = True
                new_list_number = len(numbers) + 1
            else:
                insert_check = False
                new_numbers = [x for x in range(numbers[0], numbers[-1] + 1)]
                the_set = list(set(numbers) ^ set(new_numbers))
                new_list_number = the_set[0]
        else:
            insert_check = True
            new_list_number = len(numbers) + 1
        while True:
            new_identificator = "000-000-000-000-000"
            change = list(new_identificator)
            identificator = random.randint(0, pow(10, 16) - 1)
            for i in range(len(new_identificator)):
                if new_identificator[len(new_identificator) - 1 - i] != '-':
                    change[len(change) - 1 - i] = str(int(identificator % 10))
                    identificator /= 10
            new_identificator = "".join(change)
            if new_identificator in identificators:
                continue
            else:
                break
        try:
            sock = socket.socket()
            sock.settimeout(MAX_TIME)
            sock.bind((HOST_SERVER, PORT_SERVER))
            sock.listen(1)
            conn, address = sock.accept()
            data = conn.recv(1024)
            data = data.decode('UTF-8')
            data = data.split(",")
            data.pop(0)
            for i in range(len(new_result)):
                if (data[0] in new_result[i]) and (data[1] in new_result[i]) and (data[2] in new_result[i]) and\
                        (data[3] in new_result[i]) and (data[4] in new_result[i]):
                    conn.send("".encode())
                    conn.close()
                    self.manager.current = 'Add_No'
                    return
            new_row = [new_list_number, new_identificator]
            for i in range(len(data)):
                new_row.append(data[i])
            if len(new_row) == len(LABEL) - 2:
                for j in range(len(address)):
                    new_row.append(address[j])
            conn.send(new_identificator.encode())
            if insert_check:
                new_result.insert(new_list_number + 1, new_row)
            else:
                new_result.insert(new_list_number, new_row)
            with open(FILE, 'w', newline='') as file:
                create = csv.writer(file)
                create.writerows(new_result)
            conn.close()
            self.manager.current = 'Add_Success'
        except (ConnectionRefusedError, TimeoutError):
            self.manager.current = 'Add_Fail'

    def button_edit(self, *args):
        self.manager.current = 'New_Data_Input'
        return

    def button_delete_all(self, *args):
        count = 0
        self.count = 0
        port_number = 0
        host_number = ""
        new_row = []
        new_result = [LABEL]
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    new_row.append(row)
                count += 1
        for i in range(len(new_row)):
            message = "delete,XXX-XXX-XXX-XXX-XXX,"
            for j in range(len(new_row[i])):
                if j > 1:
                    if j != len(new_row[i]) - 1:
                        message += (new_row[i][j] + ",")
                    else:
                        message += new_row[i][j]
            host_number = new_row[i][HOST_INDEX]
            port_number = int(new_row[i][PORT_INDEX])
            try:
                sock = socket.socket()
                sock.connect((host_number, port_number))
                sock.send(message.encode())
                sock.close()
                self.manager.current = 'Delete_Success'
            except ConnectionRefusedError:
                new_result.append(new_row[i])
                self.count += 1
        if self.count > 0:
            self.manager.current = 'Delete_All_Fail'
        with open(FILE, 'w', newline='') as file:
            create = csv.writer(file)
            create.writerows(new_result)
        return

    def button_delete_one(self, *args):
        count = 0
        port_number = 0
        check_input = True
        complete_check = False
        host_number = ""
        message = "delete,XXX-XXX-XXX-XXX-XXX,"
        new_row = []
        new_result = []
        numbers = []
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    new_row.append(row)
                    numbers.append(row[LIST_NUMBER_INDEX])
                count += 1
        if self.delete_id.text not in numbers:
            check_input = False
        if check_input:
            new_result.append(LABEL)
            for i in range(len(new_row)):
                delete_check = True
                if self.delete_id.text in new_row[i]:
                    for j in range(len(new_row[i])):
                        if j > 1:
                            if j != len(new_row[i]) - 1:
                                message += (new_row[i][j] + ",")
                            else:
                                message += new_row[i][j]
                    host_number = new_row[i][HOST_INDEX]
                    port_number = int(new_row[i][PORT_INDEX])
                    try:
                        sock = socket.socket()
                        sock.connect((host_number, port_number))
                        sock.send(message.encode())
                        sock.close()
                        delete_check = False
                        change_check = True
                    except ConnectionRefusedError:
                        change_check = False
                if delete_check:
                    new_result.append(new_row[i])
            with open(FILE, 'w', newline='') as file:
                create = csv.writer(file)
                create.writerows(new_result)
        if len(new_result) > 0:
            if count != len(new_result):
                self.manager.current = 'Delete_Success'
            else:
                self.manager.current = 'Delete_One_Fail'
        return

    def button_to_update(self, *args):
        data = ""
        result = []
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                result.append(row)
        try:
            sock = socket.socket()
            sock.settimeout(LOCAL_TIME_MAX)
            sock.bind((HOST_SERVER, PORT_SERVER))
            sock.listen(1)
            conn, address = sock.accept()
            for i in range(len(result)):
                message = ""
                for j in range(len(result[i])):
                    if i == len(result[i]) - 1:
                        message += result[i][j]
                    else:
                        message += (result[i][j] + ",")
                conn.send(message.encode())
            conn.close()
            self.manager.current = 'Good_Update'
        except (ConnectionRefusedError, TimeoutError):
            self.manager.current = 'Bad_Update'
        return

    @staticmethod
    def button_exit(*args):
        app.stop()


class GetAllScreen(Screen):
    def __init__(self):
        self.name = 'Get_All'
        super().__init__()
        layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                text = "   ".join(row)
                label = Label(text=text,
                              size_hint=(1, None),
                              pos_hint={"center_x": .5, "center_y": .5},
                              height=40)
                layout.add_widget(label)
        button = Button(text='Обратно в меню',
                             size_hint=(1, None),
                             pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(layout)
        self.add_widget(root)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class GetOneScreen(Screen):
    def __init__(self):
        self.name = 'Get_One'
        super().__init__()
        self.list_numbers = []
        count = 0
        with open(FILE, 'r') as file:
            results = csv.reader(file)
            for row in results:
                if count > 0:
                    self.list_numbers.append(row[LIST_NUMBER_INDEX])
                count += 1
        self.layout = BoxLayout(orientation='vertical', spacing=10)
        self.add_widget(self.layout)
        self.list_number = TextInput(text='Введите номер сотрудника в списке в виде целого числа', size_hint=(1, .2))
        self.layout.add_widget(self.list_number)
        button_1 = Button(text='Вывести',
                          size_hint=(1, .2),
                          pos_hint={"center_x": .5, "center_y": .5})
        button_1.bind(on_press=self.user_output)
        self.layout.add_widget(button_1)
        self.label_1 = Label(text="   ",
                             size_hint=(1, .2),
                             pos_hint={"center_x": .5, "center_y": .5})
        self.layout.add_widget(self.label_1)
        self.label_2 = Label(text="   ",
                             size_hint=(1, .2),
                             pos_hint={"center_x": .5, "center_y": .5})
        self.layout.add_widget(self.label_2)
        button_2 = Button(text='Обратно в меню',
                          size_hint=(1, .2),
                          pos_hint={"center_x": .5, "center_y": .5})
        button_2.bind(on_press=self.to_menu)
        self.layout.add_widget(button_2)

    def user_output(self, *args):
        count = 0
        if self.list_number.text not in self.list_numbers:
            self.label_1.text = "Введите существующий номер в виде числа!"
            self.label_2.text = "   "
        else:
            with open(FILE, 'r') as file:
                results = csv.reader(file)
                for row in results:
                    if count != 0:
                        if self.list_number.text in row:
                            self.label_1.text = "   ".join(LABEL)
                            self.label_2.text = "   ".join(row)
                    count += 1
        return

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class AddFail(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Add_Fail'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text="Не получилось добавить сотрудника!Нажмите на\n"
                             "кнопку, чтобы вернуться в меню, пожалуйста.",
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class AddNo(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Add_No'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text="Данный пользователь и так был добавлен! Нажмите\n"
                             "на кнопку, чтобы вернуться в меню, пожалуйста.",
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class AddSuccess(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Add_Success'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text="Добавление сотрудника было успешно выполнено!\n"
                             "Нажмите на кнопку, чтобы вернуться в меню, пожалуйста.",
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class EditScreen(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'New_Data_Input'
        input_layout = GridLayout(cols=3, row_force_default=True, row_default_height=60, padding=10)
        self.add_widget(input_layout)
        self.list_number = TextInput(text='Введите номер сотрудника в списке')
        self.identificator = ""
        self.user_surname = TextInput(text='Введите новую фамилию')
        self.user_name = TextInput(text='Введите новое имя')
        self.user_middle_name = TextInput(text='Введите новое отчество')
        self.birth_day = TextInput(text='Введите новый день рождения')
        self.birth_month = TextInput(text='Введите новый месяц рождения')
        self.birth_year = TextInput(text='Введите новый год рождения')
        self.work = TextInput(text='Введите новую должность')
        self.sex = TextInput(text='Введите новый пол (М/Ж)')
        self.mobile_number = TextInput(text='Введите новый номер телефона (X-XXX-XXX-XX-XX)')
        self.host = ""
        self.port = 0
        input_layout.add_widget(self.list_number)
        input_layout.add_widget(self.user_surname)
        input_layout.add_widget(self.user_name)
        input_layout.add_widget(self.user_middle_name)
        input_layout.add_widget(self.birth_day)
        input_layout.add_widget(self.birth_month)
        input_layout.add_widget(self.birth_year)
        input_layout.add_widget(self.work)
        input_layout.add_widget(self.sex)
        input_layout.add_widget(self.mobile_number)
        button_1 = Button(text='Подтвердить',
                          size_hint=(.5, .5),
                          pos_hint={'center_x': .5, 'center_y': .5})
        button_1.bind(on_press=self.to_confirm)
        input_layout.add_widget(button_1)
        button_2 = Button(text='Отмена',
                          size_hint=(.5, .5),
                          pos_hint={'center_x': .5, 'center_y': .5})
        button_2.bind(on_press=self.cancel)
        input_layout.add_widget(button_2)

    def to_confirm(self, *args):
        number_check = False
        emptiness_check = False
        fillness_check = False
        birth_check = False
        work_check = True
        sex_check = False
        mobile_number_check = False
        text_0 = "Введите номер сотрудника в списке"
        text_1 = "Введите свою фамилию"
        text_2 = "Введите своё имя"
        text_3 = "Введите своё отчество"
        text_4 = "Введите свой день рождения"
        text_5 = "Введите свой месяц рождения"
        text_6 = "Введите свой год рождения"
        text_7 = "Введите свою должность"
        text_8 = "Введите свой пол (М/Ж)"
        text_9 = "Введите свой номер телефона (X-XXX-XXX-XX-XX)"
        with open(FILE, 'r', newline='') as file:
            results = csv.reader(file)
            for row in results:
                if self.list_number.text == row[LIST_NUMBER_INDEX]:
                    number_check = True
                    self.identificator = row[IDENTIFICATOR_INDEX]
                    self.host = row[HOST_INDEX]
                    self.port = int(row[PORT_INDEX])
        if self.user_surname.text != text_1 and self.user_name.text != text_2 and self.user_middle_name.text != text_3\
                and self.work.text != text_7:
            emptiness_check = True
        if self.user_surname.text != "" and self.user_name.text != "" and self.user_middle_name.text != "" and \
                self.work.text != "":
            fillness_check = True
        if self.birth_day.text.isdigit() and self.birth_month.text.isdigit() and self.birth_year.text.isdigit():
            birth_check = True
        if self.sex.text == 'М' or self.sex.text == 'Ж':
            sex_check = True
        for i in range(len(self.work.text)):
            if self.work.text[i].isdigit():
                work_check = True
        if len(self.mobile_number.text) == 15:
            mobile_number_check = True
        if number_check and birth_check and sex_check and work_check and mobile_number_check and emptiness_check\
                and fillness_check:
            self.write_files()
            self.manager.current = 'Menu'
        return

    def write_files(self):
        message = "edit,"
        all_rows = []
        new_row = [self.identificator, self.user_surname.text, self.user_name.text,
                   self.user_middle_name.text, self.birth_day.text, self.birth_month.text, self.birth_year.text,
                   self.work.text, self.sex.text, self.mobile_number.text, self.host, self.port]
        for i in range(len(new_row)):
            if i == len(new_row) - 1:
                message += new_row[i]
            else:
                message += (new_row[i] + ",")
        new_row.insert(self.list_number.text, 0)
        with open(FILE, 'r', newline='') as file:
            rows = csv.reader(file)
            for row in rows:
                all_rows.append(row)
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            sock.send(message.encode())
            sock.close()
            with open(FILE, 'w', newline='') as file:
                create = csv.writer(file)
                for row in all_rows:
                    if new_row[0] in row:
                        create.writerow(new_row)
                    else:
                        create.writerow(row)
            self.manager.current = 'Edit_Success'
        except ConnectionRefusedError:
            self.manager.current = 'Edit_Fail'
        return

    def cancel(self, *args):
        self.manager.current = 'Menu'
        return


class EditFail(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Edit_Fail'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text="Не получилось настроить соединение с сотрудником!\n"
                             "Нажмите на кнопку, чтобы вернуться в меню, пожалуйста.",
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class EditSuccess(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Edit_Success'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text='Соединение было успешно выполнено! Нажмите на\n'
                             'кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class BadDeleteAll(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Delete_All_Fail'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text="Не получилось удалить целиком всех сотрудников! Нажмите\n"
                             "на кнопку, чтобы вернуться в меню, пожалуйста.",
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class BadDeleteOne(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Delete_One_Fail'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text="Не получилось установить соединение и удалить сотрудника!\n"
                             "Нажмите на кнопку, чтобы вернуться в меню, пожалуйста.",
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class GoodDelete(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Delete_Success'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text='Соединение было успешно выполнено! Нажмите на\n'
                             'кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class GoodUpdate(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Good_Update'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text='Обновление успешно выполнено! Нажмите\n'
                             'на кнопку, чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class BadUpdate(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Bad_Update'
        layout = BoxLayout()
        self.add_widget(layout)
        button = Button(text='Обновление провалено! Нажмите на кнопку,\n'
                             '  чтобы вернуться в меню, пожалуйста.',
                        size_hint=(1, .1),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_press=self.to_menu)
        layout.add_widget(button)

    def to_menu(self, *args):
        self.manager.current = 'Menu'
        return


class Myclock(Label):
    def update(self, *args):
        self.text = time.asctime()


if __name__ == "__main__":
    if not os.path.exists(FILE):
        with open(FILE, 'w') as file:
            create = csv.writer(file)
            create.writerow(LABEL)
    sm = ScreenManager()
    app = Server()
    try:
        app.run()
    except argparse.ArgumentError:
        app.stop()
