import sys
import os
import json
import requests
import subprocess
import psutil
import time
from pathlib import Path
from dataclasses import dataclass
from multiprocessing.managers import Array
from typing import Optional, List, Dict, Any
from datetime import date
import faulthandler
from xmlrpc.client import Boolean

faulthandler.enable()

from PySide6.QtCore import QDate, Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QGroupBox, QFormLayout, QMessageBox, \
    QLineEdit, QGridLayout, QTabWidget, QComboBox, QDialog, QCheckBox, QDateEdit, QSpinBox, \
    QTableView, QAbstractSpinBox, QHBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem
# ===== SQLAlchemy =====

from datetime import datetime

def makeLog(str):
    f = open('log.txt','a')
    now = datetime.now()
    f.write(f"{now}: {str}\n")
    f.close()

def get_pid_by_port(port):
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return conn.pid
    return None

# -------------------------------
# Конфигурация подключения
# -------------------------------
@dataclass
class PgConfig:
    host: str = "localhost"
    port: int = 5432
    dbname: str = "outsource"
    user: str = "postgres"
    password: str = "root"
    sslmode: str = "prefer"
    connect_timeout: int = 5





# -------------------------------
# Окно Добавления данных в БД
# -------------------------------
class AlterTableWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Alter Table')
        self.setGeometry(300, 300, 600, 220)

        self.tab = QTabWidget()

        self.empl_form = QFormLayout()  # макет для блока ввода данных для таблицы Сотрудники



        # добавление полей ввода в макет
        self.empl_form.addRow("Полное имя:", self.empl_lineedit_fullname)
        self.empl_form.addRow("Возраст:", self.empl_spinbox_age)
        self.empl_form.addRow("Зарплата:", self.empl_spinbox_salary)
        self.empl_form.addRow("Должность:", self.empl_combobox_duty)
        self.empl_form.addRow("Умения:", self.empl_lineedit_skills)

        self.empl_add_button = QPushButton('Добавить данные')  # кнопка добавления данных
        # Создание макета всего внутреннего содержимого блока ввода данных (сами поля данных и кнопка)
        self.empl_layout = QVBoxLayout()
        self.empl_layout.addLayout(self.empl_form)
        self.empl_layout.addWidget(self.empl_add_button)
        self.empl_layout.addStretch()

        # создание и именование блока ввода данных
        self.empl_box = QGroupBox("Изменить таблицу сотрудник")
        self.empl_box.setLayout(self.empl_layout)  # установка макета в блок

        self.tab.insertTab(0, self.empl_box, 'Сотрудники')

        # Данная процедура повторяется ещё два раза для создания ещё двух вкладок

        self.task_form = QFormLayout()

        self.task_lineedit_name = QLineEdit();
        self.task_lineedit_name.setPlaceholderText("Разгром")
        self.task_lineedit_description = QLineEdit()
        self.task_spinbox_id_employ = QSpinBox()
        self.task_spinbox_id_employ.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.task_spinbox_id_employ.setRange(1, 2147483647)
        self.task_spinbox_id_project = QSpinBox()
        self.task_spinbox_id_project.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.task_spinbox_id_project.setRange(1, 2147483647)
        self.task_dateedit_deadline = QDateEdit()
        self.task_dateedit_deadline.setCalendarPopup(True)
        self.task_dateedit_deadline.setDisplayFormat('yyyy-MM-dd')
        self.task_dateedit_deadline.setDate(QDate(2000, 1, 1))
        self.task_combobox_status = QComboBox()
        self.task_combobox_status.addItem('Новая');
        self.task_combobox_status.addItem('В работе')
        self.task_combobox_status.addItem('Можно проверять');
        self.task_combobox_status.addItem('Завершена')

        self.task_form.addRow("Название задачи:", self.task_lineedit_name)
        self.task_form.addRow("Описание задачи:", self.task_lineedit_description)
        self.task_form.addRow("ID работника:", self.task_spinbox_id_employ)
        self.task_form.addRow("ID проекта:", self.task_spinbox_id_project)
        self.task_form.addRow("Дата дедлайна:", self.task_dateedit_deadline)
        self.task_form.addRow("Статус задачи:", self.task_combobox_status)

        self.task_add_button = QPushButton('Добавить данные')

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.task_add_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox("Данные новой задачи")
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')
        # -------------------------------
        self.projects_form = QFormLayout()

        self.projects_add_button = QPushButton('Добавить данные')

        self.projects_layout = QVBoxLayout()
        self.projects_layout.addLayout(self.projects_form)
        self.projects_layout.addWidget(self.projects_add_button)
        self.projects_layout.addStretch()

        self.projects_box = QGroupBox("Данные нового проекта")
        self.projects_box.setLayout(self.projects_layout)

        self.tab.insertTab(2, self.projects_box, 'Проекты')

        # Конец создания вкладок

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()

        self.setLayout(self.layout)


# -------------------------------
# Окно Добавления данных в БД
# -------------------------------
class AddDataWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Input')
        self.setGeometry(300, 300, 600, 220)

        self.employee_col = requests.get('http://localhost:3000/employee/columns').json()[1:]
        self.employee_input = []
        self.project_col = requests.get('http://localhost:3000/project/columns').json()[1:]
        self.project_input = []
        self.task_col = requests.get('http://localhost:3000/task/columns').json()[1:]
        self.task_input = []
        self.tab = QTabWidget()

        self.empl_form = QFormLayout()  # макет для блока ввода данных для таблицы Сотрудники
        # текстовые и числовые поля для блока ввода данных
        for ob in self.employee_col:
            if ob[2] == "character varying":
                self.employee_input.append(QLineEdit())
                self.employee_input[-1].setMaxLength(300)
                self.employee_input[-1].setPlaceholderText("Text")
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "text":
                self.employee_input.append(QLineEdit())
                self.employee_input[-1].setPlaceholderText("Text")
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "integer":
                self.employee_input.append(QSpinBox())
                self.employee_input[-1].setButtonSymbols(QAbstractSpinBox.NoButtons)
                self.employee_input[-1].setRange(1, 2147483647)
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "duty":
                self.employee_input.append(QComboBox())
                self.employee_input[-1].addItem('Frontend'); self.employee_input[-1].addItem('Backend'); self.employee_input[-1].addItem('DevOps')
                self.employee_input[-1].addItem('Teamlead'); self.employee_input[-1].addItem('HR'); self.employee_input[-1].addItem('PM')
                self.employee_input[-1].addItem('CEO')
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "status":
                self.employee_input.append(QComboBox())
                self.employee_input[-1].addItem('Новая');
                self.employee_input[-1].addItem('В работе');
                self.employee_input[-1].addItem('Можно проверять')
                self.employee_input[-1].addItem('Завершена');
                self.empl_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "ARRAY":
                self.employee_input.append(QLineEdit())
                self.employee_input[-1].setMaxLength(300)
                self.employee_input[-1].setPlaceholderText("Obj, Obj, Obj...")
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "boolean":
                self.employee_input.append(QCheckBox())
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "date":
                self.employee_input.append(QDateEdit())
                self.employee_input[-1].setCalendarPopup(True)
                self.employee_input[-1].setDisplayFormat('yyyy-MM-dd')
                self.employee_input[-1].setDate(QDate(2000, 1, 1))
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])

        self.empl_add_button = QPushButton('Добавить данные') # кнопка добавления данных
        self.empl_add_button.clicked.connect(self.add_employee)
        # Создание макета всего внутреннего содержимого блока ввода данных (сами поля данных и кнопка)
        self.empl_layout = QVBoxLayout()
        self.empl_layout.addLayout(self.empl_form)
        self.empl_layout.addWidget(self.empl_add_button)
        self.empl_layout.addStretch()

        self.empl_box = QGroupBox("Данные нового сотрудника")
        self.empl_box.setLayout(self.empl_layout)

        self.tab.insertTab(0, self.empl_box, 'Сотрудники')


        # Данная процедура повторяется ещё два раза для создания ещё двух вкладок


        self.task_form = QFormLayout()

        for ob in self.task_col:
            if ob[2] == "character varying":
                self.task_input.append(QLineEdit())
                self.task_input[-1].setMaxLength(300)
                self.task_input[-1].setPlaceholderText("Text")
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "text":
                self.task_input.append(QLineEdit())
                self.task_input[-1].setPlaceholderText("Text")
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "integer":
                self.task_input.append(QSpinBox())
                self.task_input[-1].setButtonSymbols(QAbstractSpinBox.NoButtons)
                self.task_input[-1].setRange(1, 2147483647)
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "duty":
                self.task_input.append(QComboBox())
                self.task_input[-1].addItem('Frontend'); self.task_input[-1].addItem('Backend'); self.task_input[-1].addItem('DevOps')
                self.task_input[-1].addItem('Teamlead'); self.task_input[-1].addItem('HR'); self.task_input[-1].addItem('PM')
                self.task_input[-1].addItem('CEO')
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "status":
                self.task_input.append(QComboBox())
                self.task_input[-1].addItem('Новая');
                self.task_input[-1].addItem('В работе');
                self.task_input[-1].addItem('Можно проверять')
                self.task_input[-1].addItem('Завершена');
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "ARRAY":
                self.task_input.append(QLineEdit())
                self.task_input[-1].setMaxLength(300)
                self.task_input[-1].setPlaceholderText("Obj, Obj, Obj...")
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "boolean":
                self.task_input.append(QCheckBox())
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])
            if ob[2] == "date":
                self.task_input.append(QDateEdit())
                self.task_input[-1].setCalendarPopup(True)
                self.task_input[-1].setDisplayFormat('yyyy-MM-dd')
                self.task_input[-1].setDate(QDate(2000, 1, 1))
                self.task_form.addRow(ob[0] + ": ", self.task_input[-1])

        self.task_add_button = QPushButton('Добавить данные')
        self.task_add_button.clicked.connect(self.add_task)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.task_add_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox("Данные новой задачи")
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        # -------------------------------
        self.project_form = QFormLayout()

        for ob in self.project_col:
            if ob[2] == "character varying":
                self.project_input.append(QLineEdit())
                self.project_input[-1].setMaxLength(300)
                self.project_input[-1].setPlaceholderText("Text")
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "text":
                self.project_input.append(QLineEdit())
                self.project_input[-1].setPlaceholderText("Text")
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "integer":
                self.project_input.append(QSpinBox())
                self.project_input[-1].setButtonSymbols(QAbstractSpinBox.NoButtons)
                self.project_input[-1].setRange(1, 2147483647)
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "duty":
                self.project_input.append(QComboBox())
                self.project_input[-1].addItem('Frontend');
                self.project_input[-1].addItem('Backend');
                self.project_input[-1].addItem('DevOps')
                self.project_input[-1].addItem('Teamlead');
                self.project_input[-1].addItem('HR');
                self.project_input[-1].addItem('PM')
                self.project_input[-1].addItem('CEO')
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "status":
                self.project_input.append(QComboBox())
                self.project_input[-1].addItem('Новая');
                self.project_input[-1].addItem('В работе');
                self.project_input[-1].addItem('Можно проверять')
                self.project_input[-1].addItem('Завершена');
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "ARRAY":
                self.project_input.append(QLineEdit())
                self.project_input[-1].setMaxLength(300)
                self.project_input[-1].setPlaceholderText("Obj, Obj, Obj...")
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "boolean":
                self.project_input.append(QCheckBox())
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])
            if ob[2] == "date":
                self.project_input.append(QDateEdit())
                self.project_input[-1].setCalendarPopup(True)
                self.project_input[-1].setDisplayFormat('yyyy-MM-dd')
                self.project_input[-1].setDate(QDate(2000, 1, 1))
                self.project_form.addRow(ob[0] + ": ", self.project_input[-1])

        self.projects_add_button = QPushButton('Добавить данные')
        self.projects_add_button.clicked.connect(self.add_project)

        self.projects_layout = QVBoxLayout()
        self.projects_layout.addLayout(self.project_form)
        self.projects_layout.addWidget(self.projects_add_button)
        self.projects_layout.addStretch()

        self.projects_box = QGroupBox("Данные нового проекта")
        self.projects_box.setLayout(self.projects_layout)

        self.tab.insertTab(2, self.projects_box, 'Проекты')

        # Конец создания вкладок

        self.close_button = QPushButton('Закрыть окно')
        self.close_button.clicked.connect(self.close) # при нажатии кнопки окно будет закрываться

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addWidget(self.close_button)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def add_employee(self):
        json_string = '{'
        for i in range(len(self.employee_col)):
            if self.employee_col[i][2] == "character varying":
                text = self.employee_input[i].text().strip()
                if self.employee_col[i][1] == "NO" and not text:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.employee_col[i][0] + '": "' + text + '", '
            if self.employee_col[i][2] == "integer":
                num = self.employee_input[i].value()
                if self.employee_col[i][1] == "NO" and not num:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.employee_col[i][0] + '": ' + str(num) + ', '
            if self.employee_col[i][2] == "duty" or self.employee_col[i][2] == "status":
                text = self.employee_input[i].currentText()
                if self.employee_col[i][1] == "NO" and not text:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.employee_col[i][0] + '": "' + text + '", '
            if self.employee_col[i][2] == "ARRAY":
                arrStr = self.employee_input[i].text().split(", ")
                if self.employee_col[i][1] == "NO" and not arrStr:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.employee_col[i][0] + '": ['
                for el in arrStr:
                    json_string += '"' + el + '", '
                json_string = json_string[:-2]
                json_string += '], '
            if self.employee_col[i][2] == "boolean":
                data = self.employee_input[i].isChecked()
                if self.employee_col[i][1] == "NO" and not data:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                if data:
                    json_string += '"' + self.employee_col[i][0] + '": true, '
                else:
                    json_string += '"' + self.employee_col[i][0] + '": false, '
            if self.employee_col[i][2] == "date":
                date = self._qdate_to_pydate(self.employee_input[i].date())
                if self.employee_col[i][1] == "NO" and not date:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.employee_col[i][0] + '": "' + date + '", '
        json_string = json_string[:-2]
        json_string += '}'
        print(json_string)
        json_data = json.loads(json_string)

        r = requests.post('http://localhost:3000/employee', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Пользователь успешно добавлен!")

    def _qdate_to_pydate(self, qd: QDate) -> date:
        return f"{qd.year()}-{qd.month()}-{qd.day()}"

    def add_task(self):
        json_string = '{'
        for i in range(len(self.task_col)):
            if self.task_col[i][2] == "character varying":
                text = self.task_input[i].text().strip()
                if self.task_col[i][1] == "NO" and not text:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.task_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.task_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.task_col[i][0] + '": "' + text + '", '
            if self.task_col[i][2] == "integer":
                num = self.task_input[i].value()
                if self.task_col[i][1] == "NO" and not num:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.task_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.task_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.task_col[i][0] + '": ' + str(num) + ', '
            if self.task_col[i][2] == "duty" or self.task_col[i][2] == "status":
                text = self.task_input[i].currentText()
                if self.task_col[i][1] == "NO" and not text:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.task_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.task_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.task_col[i][0] + '": "' + text + '", '
            if self.task_col[i][2] == "ARRAY":
                arrStr = self.task_input[i].text().split(", ")
                if self.task_col[i][1] == "NO" and not arrStr:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.task_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.task_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.task_col[i][0] + '": ['
                for el in arrStr:
                    json_string += '"' + el + '", '
                json_string = json_string[:-2]
                json_string += '], '
            if self.task_col[i][2] == "boolean":
                data = self.task_input[i].isChecked()
                if self.task_col[i][1] == "NO" and not data:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.task_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.task_col[i][0]} не заполнено")
                    return
                if data:
                    json_string += '"' + self.task_col[i][0] + '": true, '
                else:
                    json_string += '"' + self.task_col[i][0] + '": false, '
            if self.task_col[i][2] == "date":
                date = self._qdate_to_pydate(self.task_input[i].date())
                if self.task_col[i][1] == "NO" and not date:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.task_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.task_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.task_col[i][0] + '": "' + date + '", '
        json_string = json_string[:-2]
        json_string += '}'
        print(json_string)
        json_data = json.loads(json_string)

        r = requests.post('http://localhost:3000/task', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Пользователь успешно добавлен!")

    def add_project(self):
        json_string = '{'
        for i in range(len(self.project_col)):
            if self.project_col[i][2] == "character varying":
                text = self.project_input[i].text().strip()
                if self.project_col[i][1] == "NO" and not text:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.project_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.project_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.project_col[i][0] + '": "' + text + '", '
            if self.project_col[i][2] == "integer":
                num = self.project_input[i].value()
                if self.project_col[i][1] == "NO" and not num:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.project_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.project_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.project_col[i][0] + '": ' + str(num) + ', '
            if self.project_col[i][2] == "duty" or self.project_col[i][2] == "status":
                text = self.project_input[i].currentText()
                if self.project_col[i][1] == "NO" and not text:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.project_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.project_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.project_col[i][0] + '": "' + text + '", '
            if self.project_col[i][2] == "ARRAY":
                arrStr = self.project_input[i].text().split(", ")
                if self.project_col[i][1] == "NO" and not arrStr:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.project_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.project_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.project_col[i][0] + '": ['
                for el in arrStr:
                    json_string += '"' + el + '", '
                json_string = json_string[:-2]
                json_string += '], '
            if self.project_col[i][2] == "boolean":
                data = self.project_input[i].isChecked()
                if self.project_col[i][1] == "NO" and not data:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.project_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.project_col[i][0]} не заполнено")
                    return
                if data:
                    json_string += '"' + self.project_col[i][0] + '": true, '
                else:
                    json_string += '"' + self.project_col[i][0] + '": false, '
            if self.project_col[i][2] == "date":
                date = self._qdate_to_pydate(self.project_input[i].date())
                if self.project_col[i][1] == "NO" and not date:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.project_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.project_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.project_col[i][0] + '": "' + date + '", '
        json_string = json_string[:-2]
        json_string += '}'
        print(json_string)
        json_data = json.loads(json_string)

        r = requests.post('http://localhost:3000/project', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Проект успешно добавлен!")


# -------------------------------
# Окно отображения данных из БД
# -------------------------------
class ShowDataBaseWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Base show')
        self.resize(1300, 800)

        tab = QTabWidget()
        tab.setObjectName("show")

        t = requests.get('http://localhost:3000/employee/columns').json()

        self.employee_col = [i[0] for i in t]
        self.employee_data = requests.get('http://localhost:3000/employee').json()
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(self.employee_col)

        if self.employee_data is not None:
            for row in self.employee_data:
                items = []
                for k in self.employee_col:
                    #Сделать проверку на время
                    items.append(QStandardItem(str(row[k])))
                model.appendRow(items)

        self.empl_table = QTableView()
        self.empl_table.setModel(model)
        self.empl_table.setSortingEnabled(True)



        tab.insertTab(0, self.empl_table, 'Сотрудники') # добавляем вкладочку


        # Данная процедура повторяется ещё три раза для создания ещё трёх вкладок

        t = requests.get('http://localhost:3000/task/columns').json()

        self.task_col = [i[0] for i in t]
        self.task_data = requests.get('http://localhost:3000/task').json()
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(self.task_col)

        if self.task_data is not None:
            for row in self.task_data:
                items = []
                for k in self.task_col:
                    # Сделать проверку на время
                    items.append(QStandardItem(str(row[k])))
                model.appendRow(items)

        self.task_table = QTableView()
        self.task_table.setModel(model)
        self.task_table.setSortingEnabled(True)

        tab.insertTab(1, self.task_table, 'Задачи')  # добавляем вкладочку

        # -------------------------------
        t = requests.get('http://localhost:3000/project/columns').json()
        self.project_col = [i[0] for i in t]
        self.project_data = requests.get('http://localhost:3000/project').json()
        model_project = QStandardItemModel()
        model_project.setHorizontalHeaderLabels(self.project_col)

        if self.project_data is not None:
            for row in self.project_data:
                items = []
                for k in self.project_col:
                    items.append(QStandardItem(str(row[k])))
                model_project.appendRow(items)

        self.project_table = QTableView()
        self.project_table.setModel(model_project)
        self.project_table.setSortingEnabled(True)

        tab.insertTab(2, self.project_table, 'Проекты')
        # -------------------------------
        # Конец создания вкладок
        # -------------------------------






        layout = QHBoxLayout()
        layout.addWidget(tab)
        self.setLayout(layout)


# -------------------------------
# Окно Добавления данных в БД
# -------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IT Outsource DB')
        self.setGeometry(200, 200, 1000, 500)
        self.process = None

        self.conn_form = QFormLayout() # макет для блока подключения
        # текстовые поля для блока подключения
        self.lineedit_host = QLineEdit("localhost")
        self.lineedit_port = QLineEdit("5436")
        self.lineedit_dbname = QLineEdit("db")
        self.lineedit_user = QLineEdit("user")
        self.lineedit_password = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        self.lineedit_sslmode = QLineEdit("prefer")

        # добавление полей ввода в макет
        self.conn_form.addRow("Host:", self.lineedit_host)
        self.conn_form.addRow("Port:", self.lineedit_port)
        self.conn_form.addRow("DB name:", self.lineedit_dbname)
        self.conn_form.addRow("User:", self.lineedit_user)
        self.conn_form.addRow("Password:", self.lineedit_password)
        self.conn_form.addRow("sslmode:", self.lineedit_sslmode)

        # создание и именование блока подключение
        self.conn_box = QGroupBox("Параметры подключения (SQLAlchemy)")
        self.conn_box.setLayout(self.conn_form) # установка макета в блок

        self.w_layout = QVBoxLayout() # общий макет всего окна
        self.w_layout.addWidget(self.conn_box) # добавление блока подключения в общий макет

        self.newdb_grid_buttons = QGridLayout() # сетка-макет кнопок для работы с подключением и созданием бд
        self.button_conn = QPushButton('Подключиться')
        self.button_conn.clicked.connect(self.do_connect)
        self.button_disconn = QPushButton('Отключиться')
        self.button_disconn.clicked.connect(self.do_disconnect)
        self.button_disconn.setDisabled(True)
        self.button_create = QPushButton('Сбросить и создать БД (CREATE)')
        self.button_create.clicked.connect(self.reset_db)
        self.button_create.setDisabled(True)

        # добавление кнопок в сетку
        self.newdb_grid_buttons.addWidget(self.button_conn, 0, 0)
        self.newdb_grid_buttons.addWidget(self.button_disconn, 0, 1)
        self.newdb_grid_buttons.addWidget(self.button_create, 1, 0, 1, 2)
        self.w_layout.addLayout(self.newdb_grid_buttons) # добавление сетки кнопок в общий макет

        self.w_layout.addSpacing(30) # пробел между кнопками создания таблицы и работы с таблицей

        self.button_adddata = QPushButton('Добавить данные')
        self.button_showdb = QPushButton('Вывести данные')
        self.button_alterdb = QPushButton('Изменить таблицу')
        self.button_jointable = QPushButton('Мастер соединений')
        self.button_adddata.clicked.connect(self.addData)
        self.button_showdb.clicked.connect(self.showDataBase)
        self.button_alterdb.clicked.connect(self.alterTables)
        self.button_adddata.setDisabled(True)
        self.button_showdb.setDisabled(True)
        self.button_alterdb.setDisabled(True)
        self.button_jointable.setDisabled(True)

        self.curdb_grid_buttons = QGridLayout() # сетка-макет кнопок для работы с нынешней бд
        self.curdb_grid_buttons.addWidget(self.button_adddata, 0, 0)
        self.curdb_grid_buttons.addWidget(self.button_showdb, 0, 1)
        self.curdb_grid_buttons.addWidget(self.button_alterdb, 2, 0, 1, 2)
        self.curdb_grid_buttons.addWidget(self.button_jointable, 3, 0, 1, 2)
        self.w_layout.addLayout(self.curdb_grid_buttons) # добавление сетки кнопок в общий макет



        self.w_layout.addStretch()  # объекты прилипают друг к другу, поэтому блок подключения не растягивается при расширении окна
        self.setLayout(self.w_layout) # установка общего макета

    def current_cfg(self) -> PgConfig:
        try:
            port = int(self.lineedit_port.text().strip())
        except ValueError:
            port = 5436
        return PgConfig(
            host=self.lineedit_host.text().strip() or "localhost",
            port=port,
            dbname=self.lineedit_dbname.text().strip() or "db",
            user=self.lineedit_user.text().strip() or "user",
            password=self.lineedit_password.text(),
            sslmode=self.lineedit_sslmode.text().strip() or "prefer",
        )

    def do_connect(self):
        main = self.window()
        if getattr(main, "engine", None) is not None:
            makeLog("Уже подключено. Нажмите «Отключиться» для переподключения.")
            return
        cfg = self.current_cfg()
        f = open("sqlmicroservise/.env", "w")
        f.write(f'#Application \nPRODUCTION_TYPE=prod\nCRYPTOGRAPHY_SECRET_KEY="1234567890123456" \nPOSTGRES_HOST={cfg.host} \nPOSTGRES_PORT={cfg.port} \nPOSTGRES_USER={cfg.user} \nPOSTGRES_PASSWORD={cfg.password} \nPOSTGRES_DB={cfg.dbname}\nPGDATA_PATH="/var/lib/postgresql/data/pgdata"')
        f.close()
        self.process = subprocess.Popen(
        ['go', 'run', 'cmd/app/main.go'],
            cwd='sqlmicroservise',  # меняем рабочую директорию
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        time.sleep(2)
        if get_pid_by_port(3000) != None:
            makeLog(f"Успешное подключение: psycopg2 => {cfg.host}:{cfg.port}/{cfg.dbname} (user={cfg.user})")

            self.button_conn.setDisabled(True)
            self.button_create.setDisabled(False)
            self.button_adddata.setDisabled(False)
            self.button_showdb.setDisabled(False)
            self.button_disconn.setDisabled(False)
            self.button_alterdb.setDisabled(False)
            self.button_jointable.setDisabled(False)
        else:
            makeLog("Ошибка запуска:")

    def do_disconnect(self):
        if self.process:
            os.system(f"taskkill /PID {get_pid_by_port(3000)} /F")
        self.button_conn.setDisabled(False)
        self.button_create.setDisabled(True)
        self.button_adddata.setDisabled(True)
        self.button_showdb.setDisabled(True)
        self.button_disconn.setDisabled(True)
        self.button_alterdb.setDisabled(True)
        self.button_jointable.setDisabled(True)
        makeLog("Соединение закрыто.")

    def reset_db(self):
        main = self.window()  # <-- было parent().parent()
        if getattr(main, "engine", None) is None:
            QMessageBox.warning(self, "Схема", "Нет подключения к БД.")
            makeLog("Нет подключения к БД.")
            return
        '''if drop_and_create_schema_sa(main.engine, main.md):
            pass
            makeLog("Схема БД создана: students, courses, enrollments.")
        else:
            QMessageBox.critical(self, "Схема", "Ошибка при создании схемы.")
            makeLog("Ошибка при создании схемы.")'''

    def addData(self):
        dlg = AddDataWindow()
        dlg.exec()

    def showDataBase(self):
        dlg = ShowDataBaseWindow()
        dlg.exec()

    def alterTables(self):
        dlg = AlterTableWindow()
        dlg.exec()


app = QApplication(sys.argv)
app.setStyleSheet(Path('styles.qss').read_text())
window = MainWindow()
window.show()
sys.exit(app.exec())