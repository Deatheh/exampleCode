
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
    QLineEdit, QGridLayout, QTabWidget, QComboBox, QScrollArea, QDialog, QSplitter, QTextEdit, QHeaderView, QLabel, \
    QCheckBox, QListWidget, QDateEdit, QSpinBox, \
    QTableView, QAbstractSpinBox, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QStandardItemModel, QStandardItem
# ===== SQLAlchemy =====

from datetime import datetime


def makeLog(str):
    f = open('log.txt', 'a')
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
    dbname: str = "outsourse"
    user: str = "postgres"
    password: str = "root"
    sslmode: str = "prefer"
    connect_timeout: int = 5


query = ""


def SaveQuery(q):
    global query
    query = q

CTEquery = ""
CTEarr = []

def SaveCTEQuery(q, arr):
    global CTEquery
    global CTEarr
    CTEquery = q
    CTEarr = arr

def GetCTEquery():
    global CTEquery
    return CTEquery

def GetCTEarr():
    global CTEarr
    return CTEarr

def ClearCTEarr():
    global CTEarr
    CTEarr = []

def GetQuery():
    global query
    return query


# -------------------------------
# Окно Добавления данных в БД
# -------------------------------
class RemoveConstraintColWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить ограничения")
        self.setGeometry(400, 400, 400, 400)
        self.tab = QTabWidget()

        # ----------------------

        self.employee_form = QFormLayout()

        self.employeeRenameCol = QComboBox()

        self.employee_col_full = requests.get('http://localhost:3000/employee/constrains').json()
        for col in self.employee_col_full:
            if col[0] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                self.employeeRenameCol.addItem(col)
        self.employee_form.addRow("Удаляемое ограничение: ", self.employeeRenameCol)

        self.add_employee_button = QPushButton('Удалить ограничение')
        self.add_employee_button.clicked.connect(self.employee_remove_constraint_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addLayout(self.employee_form)
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addStretch()

        self.employee_box = QGroupBox()
        self.employee_box.setLayout(self.employee_layout)

        self.tab.insertTab(0, self.employee_box, 'Сотрудники')

        # ----------------------

        self.task_form = QFormLayout()

        self.taskRenameCol = QComboBox()

        self.task_col_full = requests.get('http://localhost:3000/task/constrains').json()
        for col in self.task_col_full:
            if col[0] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                self.taskRenameCol.addItem(col)
        self.task_form.addRow("Удаляемое ограничение: ", self.taskRenameCol)

        self.add_task_button = QPushButton('Удалить ограничение')
        self.add_task_button.clicked.connect(self.task_remove_constraint_col)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.add_task_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox()
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        # ----------------------

        self.project_form = QFormLayout()

        self.projectRenameCol = QComboBox()

        self.project_col_full = requests.get('http://localhost:3000/project/constrains').json()
        for col in self.project_col_full:
            if col[0] not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                self.projectRenameCol.addItem(col)
        self.project_form.addRow("Удаляемое ограничение: ", self.projectRenameCol)

        self.add_project_button = QPushButton('Удалить ограничение')
        self.add_project_button.clicked.connect(self.project_remove_constraint_col)

        self.project_layout = QVBoxLayout()
        self.project_layout.addLayout(self.project_form)
        self.project_layout.addWidget(self.add_project_button)
        self.project_layout.addStretch()

        self.project_box = QGroupBox()
        self.project_box.setLayout(self.project_layout)

        self.tab.insertTab(2, self.project_box, 'Проекты')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def employee_remove_constraint_col(self):
        col = self.employeeRenameCol.currentText()
        json_string = '{"alter_string": "DROP CONSTRAINT ' + col + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/employee/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def project_remove_constraint_col(self):
        col = self.projectRenameCol.currentText()
        json_string = '{"alter_string": "DROP CONSTRAINT ' + col + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/project/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def task_remove_constraint_col(self):
        col = self.taskRenameCol.currentText()
        json_string = '{"alter_string": "DROP CONSTRAINT ' + col + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/task/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")


class ConstraintColWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить ограничение")
        self.setGeometry(400, 400, 400, 400)
        self.tab = QTabWidget()

        # ----------------------

        self.employee_form = QFormLayout()

        self.employeeRenameCol = QComboBox()

        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()[1:]
        for col in self.employee_col_full:
            self.employeeRenameCol.addItem(col[0])
        self.employee_form.addRow("Колонка: ", self.employeeRenameCol)

        self.employeeColName = QLineEdit()
        self.employeeColName.setMaxLength(300)
        self.employeeColName.setPlaceholderText("id > 1 && id < 1000")
        self.employee_form.addRow("Сheck: ", self.employeeColName)

        self.not_null_employee_chk = QCheckBox()
        self.employee_form.addRow("Добавить NOT NULL: ", self.not_null_employee_chk)

        self.unique_employee_chk = QCheckBox()
        self.employee_form.addRow("Добавить UNIQUE: ", self.unique_employee_chk)

        self.employeeForeignCol = QComboBox()
        self.employeeForeignCol.addItem("None")
        self.employee_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.employee_col_full:
            self.employeeForeignCol.addItem("task(" + col[0] + ")")
        self.employee_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.employee_col_full:
            self.employeeForeignCol.addItem("project(" + col[0] + ")")
        self.employee_form.addRow("Foreign: ", self.employeeForeignCol)

        self.add_employee_button = QPushButton('Изменить колонку')
        self.add_employee_button.clicked.connect(self.employee_constraint_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addLayout(self.employee_form)
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addStretch()

        self.employee_box = QGroupBox()
        self.employee_box.setLayout(self.employee_layout)

        self.tab.insertTab(0, self.employee_box, 'Сотрудники')

        # -------------------------

        self.task_form = QFormLayout()

        self.taskRenameCol = QComboBox()

        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()[1:]
        for col in self.task_col_full:
            self.taskRenameCol.addItem(col[0])
        self.task_form.addRow("Колонка: ", self.taskRenameCol)

        self.taskColName = QLineEdit()
        self.taskColName.setMaxLength(300)
        self.taskColName.setPlaceholderText("id > 1 && id < 1000")
        self.task_form.addRow("Сheck: ", self.taskColName)

        self.not_null_task_chk = QCheckBox()
        self.task_form.addRow("Добавить NOT NULL: ", self.not_null_task_chk)

        self.unique_task_chk = QCheckBox()
        self.task_form.addRow("Добавить UNIQUE: ", self.unique_task_chk)

        self.taskForeignCol = QComboBox()
        self.taskForeignCol.addItem("None")
        self.task_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.task_col_full:
            self.taskForeignCol.addItem("task(" + col[0] + ")")
        self.task_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.task_col_full:
            self.taskForeignCol.addItem("project(" + col[0] + ")")
        self.task_form.addRow("Foreign: ", self.taskForeignCol)

        self.add_task_button = QPushButton('Изменить колонку')
        self.add_task_button.clicked.connect(self.task_constraint_col)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.add_task_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox()
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        # -------------------------

        self.project_form = QFormLayout()

        self.projectRenameCol = QComboBox()

        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()[1:]
        for col in self.project_col_full:
            self.projectRenameCol.addItem(col[0])
        self.project_form.addRow("Колонка: ", self.projectRenameCol)

        self.projectColName = QLineEdit()
        self.projectColName.setMaxLength(300)
        self.projectColName.setPlaceholderText("id > 1 && id < 1000")
        self.project_form.addRow("Сheck: ", self.projectColName)

        self.not_null_project_chk = QCheckBox()
        self.project_form.addRow("Добавить NOT NULL: ", self.not_null_project_chk)

        self.unique_project_chk = QCheckBox()
        self.project_form.addRow("Добавить UNIQUE: ", self.unique_project_chk)

        self.projectForeignCol = QComboBox()
        self.projectForeignCol.addItem("None")
        self.project_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.project_col_full:
            self.projectForeignCol.addItem("project(" + col[0] + ")")
        self.project_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.project_col_full:
            self.projectForeignCol.addItem("project(" + col[0] + ")")
        self.project_form.addRow("Foreign: ", self.projectForeignCol)

        self.add_project_button = QPushButton('Изменить колонку')
        self.add_project_button.clicked.connect(self.project_constraint_col)

        self.project_layout = QVBoxLayout()
        self.project_layout.addLayout(self.project_form)
        self.project_layout.addWidget(self.add_project_button)
        self.project_layout.addStretch()

        self.project_box = QGroupBox()
        self.project_box.setLayout(self.project_layout)

        self.tab.insertTab(2, self.project_box, 'Проекты')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def employee_constraint_col(self):
        col = self.employeeRenameCol.currentText()
        check = self.employeeColName.text().strip()
        not_null = self.not_null_employee_chk.isChecked()
        unique = self.unique_employee_chk.isChecked()
        foreign = self.employeeForeignCol.currentText()
        if not check:
            pass
        else:
            json_string = '{"alter_string": "ADD CHECK' + check + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/employee/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if not_null:
            json_string = '{"alter_string": " ' + col + ' SET NOT NULL"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/employee/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if unique:
            json_string = '{"alter_string": "ADD UNIQUE (' + col + ')"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/employee/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if foreign == "None":
            pass
        else:
            json_string = '{"alter_string": "ADD FOREIGN KEY (' + col + ') REFERENCES ' + foreign + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/employee/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")

    def task_constraint_col(self):
        col = self.taskRenameCol.currentText()
        check = self.taskColName.text().strip()
        not_null = self.not_null_task_chk.isChecked()
        unique = self.unique_task_chk.isChecked()
        foreign = self.taskForeignCol.currentText()
        if not check:
            pass
        else:
            json_string = '{"alter_string": "ADD CHECK' + check + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/task/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if not_null:
            json_string = '{"alter_string": " ' + col + ' SET NOT NULL"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/task/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if unique:
            json_string = '{"alter_string": "ADD UNIQUE (' + col + ')"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/task/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if foreign == "None":
            pass
        else:
            json_string = '{"alter_string": "ADD FOREIGN KEY (' + col + ') REFERENCES ' + foreign + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/task/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")

    def project_constraint_col(self):
        col = self.projectRenameCol.currentText()
        check = self.projectColName.text().strip()
        not_null = self.not_null_project_chk.isChecked()
        unique = self.unique_project_chk.isChecked()
        foreign = self.projectForeignCol.currentText()
        if not check:
            pass
        else:
            json_string = '{"alter_string": "ADD CHECK' + check + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/project/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if not_null:
            json_string = '{"alter_string": " ' + col + ' SET NOT NULL"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/project/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if unique:
            json_string = '{"alter_string": "ADD UNIQUE (' + col + ')"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/project/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")
        if foreign == "None":
            pass
        else:
            json_string = '{"alter_string": "ADD FOREIGN KEY (' + col + ') REFERENCES ' + foreign + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/project/alter', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при добавлении!")
            else:
                makeLog("Изменения добавлены!")


class TypeColWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Изменить тип данных")
        self.setGeometry(400, 400, 400, 400)

        self.tab = QTabWidget()

        # ----------------------

        self.employee_form = QFormLayout()

        self.employeeRenameCol = QComboBox()

        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()[1:]
        for col in self.employee_col_full:
            self.employeeRenameCol.addItem(col[0])
        self.employee_form.addRow("Колонка: ", self.employeeRenameCol)

        self.employeeType = QComboBox()
        self.employeeType.addItem("VARCHAR")
        self.employeeType.addItem("TEXT")
        self.employeeType.addItem("DATE")
        self.employeeType.addItem("INTEGER")
        self.employeeType.addItem("BOOLEAN")
        self.employeeType.addItem("ARRAY")

        self.employee_form.addRow("Новый тип данных: ", self.employeeType)

        self.add_employee_button = QPushButton('Изменить колонку')
        self.add_employee_button.clicked.connect(self.employee_type_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addLayout(self.employee_form)
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addStretch()

        self.employee_box = QGroupBox()
        self.employee_box.setLayout(self.employee_layout)

        self.tab.insertTab(0, self.employee_box, 'Сотрудники')

        # ----------------------

        self.task_form = QFormLayout()

        self.taskRenameCol = QComboBox()

        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()[1:]
        for col in self.task_col_full:
            self.taskRenameCol.addItem(col[0])
        self.task_form.addRow("Колонка: ", self.taskRenameCol)

        self.taskType = QComboBox()
        self.taskType.addItem("VARCHAR")
        self.taskType.addItem("TEXT")
        self.taskType.addItem("DATE")
        self.taskType.addItem("INTEGER")
        self.taskType.addItem("BOOLEAN")
        self.taskType.addItem("ARRAY")

        self.task_form.addRow("Новый тип данных: ", self.taskType)

        self.add_task_button = QPushButton('Изменить колонку')
        self.add_task_button.clicked.connect(self.task_type_col)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.add_task_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox()
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        # ----------------------

        self.project_form = QFormLayout()

        self.projectRenameCol = QComboBox()

        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()[1:]
        for col in self.project_col_full:
            self.projectRenameCol.addItem(col[0])
        self.project_form.addRow("Колонка: ", self.projectRenameCol)

        self.projectType = QComboBox()
        self.projectType.addItem("VARCHAR")
        self.projectType.addItem("TEXT")
        self.projectType.addItem("DATE")
        self.projectType.addItem("INTEGER")
        self.projectType.addItem("BOOLEAN")
        self.projectType.addItem("ARRAY")

        self.project_form.addRow("Новый тип данных: ", self.projectType)

        self.add_project_button = QPushButton('Изменить колонку')
        self.add_project_button.clicked.connect(self.project_type_col)

        self.project_layout = QVBoxLayout()
        self.project_layout.addLayout(self.project_form)
        self.project_layout.addWidget(self.add_project_button)
        self.project_layout.addStretch()

        self.project_box = QGroupBox()
        self.project_box.setLayout(self.project_layout)

        self.tab.insertTab(2, self.project_box, 'Проекты')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def employee_type_col(self):
        col = self.employeeRenameCol.currentText()
        type = self.employeeType.currentText()
        json_string = '{"alter_string": "ALTER COLUMN ' + col + ' TYPE ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/employee/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def task_type_col(self):
        col = self.taskRenameCol.currentText()
        type = self.taskType.currentText()
        json_string = '{"alter_string": "ALTER COLUMN ' + col + ' TYPE ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/task/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def project_type_col(self):
        col = self.projectRenameCol.currentText()
        type = self.projectType.currentText()
        json_string = '{"alter_string": "ALTER COLUMN ' + col + ' TYPE ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/project/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")


class RenameColWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Переименовать колонку")
        self.setGeometry(400, 400, 400, 400)

        self.tab = QTabWidget()

        # ----------------------

        self.empl_form = QFormLayout()

        self.emplRenameCol = QComboBox()

        self.empl_col_full = requests.get('http://localhost:3000/employee/columns').json()[1:]
        for col in self.empl_col_full:
            self.emplRenameCol.addItem(col[0])
        self.empl_form.addRow("Переименовать колонку: ", self.emplRenameCol)

        self.colName = QLineEdit()
        self.colName.setMaxLength(300)
        self.colName.setPlaceholderText("id")
        self.empl_form.addRow("Новое название: ", self.colName)

        self.add_employee_button = QPushButton('Изменить колонку')
        self.add_employee_button.clicked.connect(self.employee_rename_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addLayout(self.empl_form)
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addStretch()

        self.empl_box = QGroupBox()
        self.empl_box.setLayout(self.employee_layout)

        self.tab.insertTab(0, self.empl_box, 'Сотрудники')

        # ----------------------

        self.task_form = QFormLayout()

        self.taskRenameCol = QComboBox()

        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()[1:]
        for col in self.task_col_full:
            self.taskRenameCol.addItem(col[0])
        self.task_form.addRow("Переименовать колонку: ", self.taskRenameCol)

        self.taskColName = QLineEdit()
        self.taskColName.setMaxLength(300)
        self.taskColName.setPlaceholderText("id")
        self.task_form.addRow("Новое название: ", self.taskColName)

        self.add_task_button = QPushButton('Изменить колонку')
        self.add_task_button.clicked.connect(self.task_rename_col)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.add_task_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox()
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        # ----------------------

        self.project_form = QFormLayout()

        self.projectRenameCol = QComboBox()

        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()[1:]
        for col in self.project_col_full:
            self.projectRenameCol.addItem(col[0])
        self.project_form.addRow("Переименовать колонку: ", self.projectRenameCol)

        self.projectColName = QLineEdit()
        self.projectColName.setMaxLength(300)
        self.projectColName.setPlaceholderText("id")
        self.project_form.addRow("Новое название: ", self.projectColName)

        self.add_project_button = QPushButton('Изменить колонку')
        self.add_project_button.clicked.connect(self.project_rename_col)

        self.project_layout = QVBoxLayout()
        self.project_layout.addLayout(self.project_form)
        self.project_layout.addWidget(self.add_project_button)
        self.project_layout.addStretch()

        self.project_box = QGroupBox()
        self.project_box.setLayout(self.project_layout)

        self.tab.insertTab(2, self.project_box, 'Проекты')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def employee_rename_col(self):
        type = self.emplRenameCol.currentText()
        colName = self.colName.text().strip()
        if not colName:
            return
        json_string = '{"alter_string": "RENAME COLUMN ' + type + ' TO ' + colName + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/employee/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def task_rename_col(self):
        type = self.taskRenameCol.currentText()
        colName = self.taskColName.text().strip()
        if not colName:
            return
        json_string = '{"alter_string": "RENAME COLUMN ' + type + ' TO ' + colName + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/task/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def project_rename_col(self):
        type = self.projectRenameCol.currentText()
        colName = self.projectColName.text().strip()
        if not colName:
            return
        json_string = '{"alter_string": "RENAME COLUMN ' + type + ' TO ' + colName + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/project/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")


class RemoveColWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Удалить колонку")
        self.setGeometry(400, 400, 400, 400)

        self.tab = QTabWidget()

        # -------------------
        self.empl_form = QFormLayout()

        self.emplDelCol = QComboBox()

        self.empl_col_full = requests.get('http://localhost:3000/employee/columns').json()[1:]
        for col in self.empl_col_full:
            self.emplDelCol.addItem(col[0])
        self.empl_form.addRow("Удаляемая колонка: ", self.emplDelCol)

        self.add_employee_button = QPushButton('Убрать колонку')
        self.add_employee_button.clicked.connect(self.employee_del_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addLayout(self.empl_form)
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addStretch()

        self.empl_box = QGroupBox()
        self.empl_box.setLayout(self.employee_layout)

        self.tab.insertTab(0, self.empl_box, 'Сотрудники')

        # ----------------------

        self.task_form = QFormLayout()

        self.taskDelCol = QComboBox()

        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()[1:]
        for col in self.task_col_full:
            self.taskDelCol.addItem(col[0])
        self.task_form.addRow("Удаляемая колонка: ", self.taskDelCol)

        self.add_task_button = QPushButton('Убрать колонку')
        self.add_task_button.clicked.connect(self.task_del_col)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.add_task_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox()
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        self.project_form = QFormLayout()

        self.projectDelCol = QComboBox()

        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()[1:]
        for col in self.project_col_full:
            self.projectDelCol.addItem(col[0])
        self.project_form.addRow("Удаляемая колонка: ", self.projectDelCol)

        self.add_project_button = QPushButton('Убрать колонку')
        self.add_project_button.clicked.connect(self.project_del_col)

        self.project_layout = QVBoxLayout()
        self.project_layout.addLayout(self.project_form)
        self.project_layout.addWidget(self.add_project_button)
        self.project_layout.addStretch()

        self.project_box = QGroupBox()
        self.project_box.setLayout(self.project_layout)

        self.tab.insertTab(2, self.project_box, 'Проекты')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def employee_del_col(self):
        type = self.emplDelCol.currentText()
        json_string = '{"alter_string": "DROP COLUMN ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/employee/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def task_del_col(self):
        type = self.taskDelCol.currentText()
        json_string = '{"alter_string": "DROP COLUMN ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/task/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def project_del_col(self):
        type = self.projectDelCol.currentText()
        json_string = '{"alter_string": "DROP COLUMN ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/project/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")


class AddColWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить колонку")
        self.setGeometry(400, 400, 400, 400)

        self.tab = QTabWidget()

        # -------------------
        self.empl_form = QFormLayout()

        self.colName = QLineEdit()
        self.colName.setMaxLength(300)
        self.colName.setPlaceholderText("id")

        self.type = QComboBox()
        self.type.addItem("VARCHAR")
        self.type.addItem("TEXT")
        self.type.addItem("DATE")
        self.type.addItem("INTEGER")
        self.type.addItem("BOOLEAN")
        self.type.addItem("ARRAY")

        self.empl_form.addRow("Название колонки: ", self.colName)
        self.empl_form.addRow("Тип данных: ", self.type)

        self.add_employee_button = QPushButton('Добавить колонку')
        self.add_employee_button.clicked.connect(self.employee_add_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addLayout(self.empl_form)
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addStretch()

        self.empl_box = QGroupBox()
        self.empl_box.setLayout(self.employee_layout)

        self.tab.insertTab(0, self.empl_box, 'Сотрудники')

        # -------------------
        self.task_form = QFormLayout()

        self.taskColName = QLineEdit()
        self.taskColName.setMaxLength(300)
        self.taskColName.setPlaceholderText("id")

        self.taskType = QComboBox()
        self.taskType.addItem("VARCHAR")
        self.taskType.addItem("TEXT")
        self.taskType.addItem("DATE")
        self.taskType.addItem("INTEGER")
        self.taskType.addItem("BOOLEAN")
        self.taskType.addItem("ARRAY")

        self.task_form.addRow("Название колонки: ", self.taskColName)
        self.task_form.addRow("Тип данных: ", self.taskType)

        self.add_task_button = QPushButton('Добавить колонку')
        self.add_task_button.clicked.connect(self.task_add_col)

        self.task_layout = QVBoxLayout()
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addWidget(self.add_task_button)
        self.task_layout.addStretch()

        self.task_box = QGroupBox()
        self.task_box.setLayout(self.task_layout)

        self.tab.insertTab(1, self.task_box, 'Задачи')

        # -------------------------------

        self.project_form = QFormLayout()

        self.projectColName = QLineEdit()
        self.projectColName.setMaxLength(300)
        self.projectColName.setPlaceholderText("id")

        self.projectType = QComboBox()
        self.projectType.addItem("VARCHAR")
        self.projectType.addItem("TEXT")
        self.projectType.addItem("DATE")
        self.projectType.addItem("INTEGER")
        self.projectType.addItem("BOOLEAN")
        self.projectType.addItem("ARRAY")

        self.project_form.addRow("Название колонки: ", self.projectColName)
        self.project_form.addRow("Тип данных: ", self.projectType)

        self.add_project_button = QPushButton('Добавить колонку')
        self.add_project_button.clicked.connect(self.project_add_col)

        self.project_layout = QVBoxLayout()
        self.project_layout.addLayout(self.project_form)
        self.project_layout.addWidget(self.add_project_button)
        self.project_layout.addStretch()

        self.project_box = QGroupBox()
        self.project_box.setLayout(self.project_layout)

        self.tab.insertTab(2, self.project_box, 'Проекты')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def employee_add_col(self):
        colName = self.colName.text().strip()
        type = self.type.currentText()
        if not colName:
            return

        json_string = '{"alter_string": "ADD COLUMN ' + colName + ' ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/employee/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def task_add_col(self):
        colName = self.taskColName.text().strip()
        type = self.taskType.currentText()
        if not colName:
            return

        json_string = '{"alter_string": "ADD COLUMN ' + colName + ' ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/task/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def project_add_col(self):
        colName = self.projectColName.text().strip()
        type = self.projectType.currentText()
        if not colName:
            return

        json_string = '{"alter_string": "ADD COLUMN ' + colName + ' ' + type + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/project/alter', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")


class AlterTableWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Alter Table')
        self.setGeometry(300, 300, 600, 220)

        self.add_employee_button = QPushButton('Добавить колонку')
        self.add_employee_button.clicked.connect(self.employee_add_col)
        self.remove_employee_button = QPushButton('Убрать колонку')
        self.remove_employee_button.clicked.connect(self.remove_col)
        self.rename_employee_button = QPushButton('Переименовать колонку')
        self.rename_employee_button.clicked.connect(self.rename_col)
        self.type_employee_button = QPushButton('Изменить тип данных колонки')
        self.type_employee_button.clicked.connect(self.type_col)
        self.constraint_employee_button = QPushButton('Добавить ограничения')
        self.constraint_employee_button.clicked.connect(self.constraint_col)
        self.remove_constraint_employee_button = QPushButton('Убрать ограничения')
        self.remove_constraint_employee_button.clicked.connect(self.remove_constraint_col)

        self.employee_layout = QVBoxLayout()
        self.employee_layout.addWidget(self.add_employee_button)
        self.employee_layout.addWidget(self.remove_employee_button)
        self.employee_layout.addWidget(self.rename_employee_button)
        self.employee_layout.addWidget(self.type_employee_button)
        self.employee_layout.addWidget(self.constraint_employee_button)
        self.employee_layout.addWidget(self.remove_constraint_employee_button)
        self.employee_layout.addStretch()

        self.empl_box = QGroupBox("Изменить таблицу сотрудник")
        self.empl_box.setLayout(self.employee_layout)  # установка макета в блок

        # Конец создания вкладок

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.empl_box)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def employee_add_col(self):
        dlg = AddColWindow()
        dlg.exec()

    def remove_col(self):
        dlg = RemoveColWindow()
        dlg.exec()

    def rename_col(self):
        dlg = RenameColWindow()
        dlg.exec()

    def type_col(self):
        dlg = TypeColWindow()
        dlg.exec()

    def constraint_col(self):
        dlg = ConstraintColWindow()
        dlg.exec()

    def remove_constraint_col(self):
        dlg = RemoveConstraintColWindow()
        dlg.exec()


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
            if ob[2] == "bintree":
                self.employee_input.append(QSpinBox())
                self.employee_input[-1].setButtonSymbols(QAbstractSpinBox.NoButtons)
                self.employee_input[-1].setRange(1, 2147483647)
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "duty":
                self.employee_input.append(QComboBox())
                self.employee_input[-1].addItem('Frontend');
                self.employee_input[-1].addItem('Backend');
                self.employee_input[-1].addItem('DevOps')
                self.employee_input[-1].addItem('Teamlead');
                self.employee_input[-1].addItem('HR');
                self.employee_input[-1].addItem('PM')
                self.employee_input[-1].addItem('CEO')
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
            if ob[2] == "status":
                self.employee_input.append(QComboBox())
                self.employee_input[-1].addItem('Новая');
                self.employee_input[-1].addItem('В работе');
                self.employee_input[-1].addItem('Можно проверять')
                self.employee_input[-1].addItem('Завершена');
                self.empl_form.addRow(ob[0] + ": ", self.employee_input[-1])
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

        self.empl_add_button = QPushButton('Добавить данные')  # кнопка добавления данных
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
                self.task_input[-1].addItem('Frontend');
                self.task_input[-1].addItem('Backend');
                self.task_input[-1].addItem('DevOps')
                self.task_input[-1].addItem('Teamlead');
                self.task_input[-1].addItem('HR');
                self.task_input[-1].addItem('PM')
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
            if ob[2] == "bintree":
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
        self.close_button.clicked.connect(self.close)  # при нажатии кнопки окно будет закрываться

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
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
                    return
                json_string += '"' + self.employee_col[i][0] + '": "' + text + '", '
            if self.employee_col[i][2] == "integer":
                num = self.employee_input[i].value()
                if self.employee_col[i][1] == "NO" and not num:
                    QMessageBox.warning(self, "Ввод", f"Поле {self.employee_col[i][0]} обязательно для ввода")
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
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
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
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
                    makeLog(
                        f"Ошибка при добавления записи сотрудника. Обязательное поле {self.employee_col[i][0]} не заполнено")
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
        json_data = json.loads(json_string)

        r = requests.post('http://localhost:3000/project', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Проект успешно добавлен!")


# -------------------------------
# Окно отображения данных из БД
# -------------------------------
class EmployeeTableModel(QAbstractTableModel):
    def __init__(self, data=None, headers=None):
        super().__init__()
        self._data = data or []
        self._headers = headers or []

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def update_data(self, data, headers):
        self.beginResetModel()
        self._data = data
        self._headers = headers
        self.endResetModel()


class ColumnFunctionWidget(QWidget):
    def __init__(self, column_name, display_name):
        super().__init__()
        self.column_name = column_name
        self.display_name = display_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox(self.display_name)

        self.function_combo = QComboBox()
        self.function_combo.addItems([
            "Без функции",
            "UPPER",
            "LOWER",
            "SUBSTRING",
            "TRIM",
            "LTRIM",
            "RTRIM",
            "LPAD",
            "RPAD",
            "CONCAT"
        ])

        self.param1 = QLineEdit()
        self.param1.setPlaceholderText("Параметр 1")
        self.param1.setVisible(False)
        self.param1.setMaxLength(30)

        self.param2 = QLineEdit()
        self.param2.setPlaceholderText("Параметр 2")
        self.param2.setVisible(False)
        self.param2.setMaxLength(30)

        layout.addWidget(self.checkbox)
        layout.addWidget(QLabel("Функция:"))
        layout.addWidget(self.function_combo)
        layout.addWidget(self.param1)

        layout.addWidget(self.param2)
        layout.addStretch()

        self.function_combo.currentTextChanged.connect(self.on_function_changed)

    def on_function_changed(self, function_name):
        self.param1.setVisible(False)
        self.param2.setVisible(False)

        if function_name == "SUBSTRING":
            self.param1.setPlaceholderText("Начало")
            self.param2.setPlaceholderText("Длина")
            self.param1.setVisible(True)
            self.param2.setVisible(True)
        elif function_name in ["LPAD", "RPAD"]:
            self.param1.setPlaceholderText("Длина")
            self.param2.setPlaceholderText("Символ")
            self.param1.setVisible(True)
            self.param2.setVisible(True)
        elif function_name == "CONCAT":
            self.param1.setPlaceholderText("Текст")
            self.param1.setVisible(True)
        elif function_name in ["TRIM", "LTRIM", "RTRIM"]:
            self.param1.setPlaceholderText("Символы")
            self.param1.setVisible(True)

    def get_column_expression(self):
        if not self.checkbox.isChecked():
            return None

        function_name = self.function_combo.currentText()
        column = self.column_name

        if function_name == "Без функции":
            return column
        elif function_name == "UPPER":
            return f"UPPER({column})"
        elif function_name == "LOWER":
            return f"LOWER({column})"
        elif function_name == "SUBSTRING":
            start = self.param1.text() or "1"
            length = self.param2.text() or f"LENGTH({column})"
            return f"SUBSTRING({column} FROM {start} FOR {length})"
        elif function_name == "TRIM":
            chars = self.param1.text()
            if chars:
                return f"TRIM('{chars}' FROM {column})"
            else:
                return f"TRIM({column})"
        elif function_name == "LTRIM":
            chars = self.param1.text()
            if chars:
                return f"LTRIM({column}, '{chars}')"
            else:
                return f"LTRIM({column})"
        elif function_name == "RTRIM":
            chars = self.param1.text()
            if chars:
                return f"RTRIM({column}, '{chars}')"
            else:
                return f"RTRIM({column})"
        elif function_name == "LPAD":
            length = self.param1.text() or "10"
            pad_char = self.param2.text() or "' '"
            return f"LPAD({column}, {length}, '{pad_char}')"
        elif function_name == "RPAD":
            length = self.param1.text() or "10"
            pad_char = self.param2.text() or "' '"
            return f"RPAD({column}, {length}, '{pad_char}')"
        elif function_name == "CONCAT":
            text = self.param1.text() or "''"
            return f"CONCAT({column}, {text})"

        return column


class JoinWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.join_type = QComboBox()
        self.join_type.addItems(["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"])

        self.join_table = QComboBox()
        self.join_table.addItems(["employee", "task", "project"])

        self.join_condition = QLineEdit()
        self.join_condition.setPlaceholderText("employee.department_id = departments.id")

        layout.addWidget(QLabel("Тип:"))
        layout.addWidget(self.join_type)
        layout.addWidget(QLabel("Таблица:"))
        layout.addWidget(self.join_table)
        layout.addWidget(QLabel("Условие:"))
        layout.addWidget(self.join_condition)

    def get_join_expression(self):
        if self.join_condition.text().strip():
            return f"{self.join_type.currentText()} {self.join_table.currentText()} ON {self.join_condition.text()}"
        return ""


class CaseWidget(QWidget):
    def __init__(self, columns_name):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.column_name = QComboBox()
        self.column_name.addItems(columns_name)
        self.operator = QComboBox()
        self.operator.addItems(
            ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*", "SIMILAR TO"])
        self.expression_result = QLineEdit()
        self.result = QLineEdit()

        layout.addWidget(QLabel("WHEN "))
        layout.addWidget(self.column_name)
        layout.addWidget(self.operator)
        layout.addWidget(self.expression_result)
        layout.addWidget(QLabel("THEN "))
        layout.addWidget(self.result)

    def get_case_expression(self):
        if (not self.column_name.currentText().strip() or
                not self.expression_result.text().strip() or
                not self.result.text().strip()):
            return ""
        column = self.column_name.currentText().strip()
        operator = self.operator.currentText().strip()
        expr_value = self.expression_result.text().strip()
        result_value = self.result.text().strip()
        if operator in ["LIKE", "NOT LIKE", "SIMILAR TO", "~", "~*", "!~", "!~*"]:
            expr_value = f"'{expr_value}'"
        return f"WHEN {column} {operator} {expr_value} THEN '{result_value}'"


class SelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр данных - Employee Database")
        self.setModal(True)
        self.setGeometry(100, 100, 600, 900)
        self.column_widgets = {}
        self.join_widgets = []
        self.case_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.columns = []
        self.columns_name = []
        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.employee_col_full:
            self.columns.append(col[0])
            self.columns_name.append("employee." + col[0])
        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.project_col_full:
            self.columns.append(col[0])
            self.columns_name.append("project." + col[0])
        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.task_col_full:
            self.columns.append(col[0])
            self.columns_name.append("task." + col[0])

        splitter = QSplitter(Qt.Horizontal)

        left_panel = self.create_query_builder()
        splitter.addWidget(left_panel)

        layout.addWidget(splitter)

    def create_query_builder(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        table_group = QGroupBox("FROM - Выбор таблицы")
        table_layout = QHBoxLayout(table_group)

        self.main_table = QComboBox()
        self.main_table.addItems(["employee", "task", "project"])
        self.main_table.setCurrentText("employee")

        table_layout.addWidget(QLabel("Основная таблица:"))
        table_layout.addWidget(self.main_table)
        table_layout.addStretch()

        join_group = QGroupBox("JOIN - Объединение таблиц")
        join_layout = QVBoxLayout(join_group)

        self.joins_container = QVBoxLayout()

        self.add_join_btn = QPushButton("+ Добавить JOIN")
        self.add_join_btn.clicked.connect(self.add_join_widget)

        join_layout.addLayout(self.joins_container)
        join_layout.addWidget(self.add_join_btn)

        case_group = QGroupBox("CASE - Объединение таблиц")
        case_layout = QVBoxLayout(case_group)

        self.cases_container = QVBoxLayout()

        self.add_case_btn = QPushButton("+ Добавить WHEN ... THEN")
        self.add_case_btn.clicked.connect(self.add_case_widget)

        self.case_as_name = QLineEdit()
        self.case_as_name.setMaxLength(100)
        self.case_else = QLineEdit()
        self.case_else.setMaxLength(100)

        self.case_desc_form = QFormLayout()
        self.case_desc_form.addRow("AS", self.case_as_name)
        self.case_desc_form.addRow("ELSE", self.case_else)

        case_layout.addLayout(self.case_desc_form)
        case_layout.addLayout(self.cases_container)

        case_layout.addWidget(self.add_case_btn)

        select_group = QGroupBox("SELECT - Выбор столбцов и функции")
        select_layout = QVBoxLayout(select_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)  # Ограничиваем высоту и включаем скролл
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        columns_info = []

        for i in range(len(self.columns)):
            columns_info.append((self.columns_name[i], self.columns_name[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        select_layout.addWidget(scroll_area)

        where_group = QGroupBox("WHERE - Фильтрация")
        where_layout = QVBoxLayout(where_group)
        where_input_layout = QHBoxLayout()
        self.where_field = QComboBox()
        self.where_field.addItems(self.columns_name)
        self.where_operator = QComboBox()
        self.where_operator.addItems(
            ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*", "SIMILAR TO"])
        self.where_value = QLineEdit()
        self.where_input_data = QComboBox()
        self.where_input_data.addItems(["Поле Ввода", "SQL подзапрос"])
        self.where_value_label = QLabel("Значение:")
        self.where_value_select = QPushButton("Задать")
        self.where_selector = QComboBox()
        self.where_selector.addItems(["", "ANY", "ALL", "EXIST"])
        self.where_value_select.setVisible(False)
        self.where_selector.setVisible(False)
        self.where_value.setPlaceholderText("Значение для фильтра")
        where_input_layout.addWidget(QLabel("Поле:"))
        where_input_layout.addWidget(self.where_field)
        where_input_layout.addWidget(QLabel("Оператор:"))
        where_input_layout.addWidget(self.where_operator)
        where_input_layout.addWidget(QLabel("Ввод данных:"))
        where_input_layout.addWidget(self.where_input_data)
        where_input_layout.addWidget(self.where_value_label)
        where_input_layout.addWidget(self.where_value)
        where_input_layout.addWidget(self.where_selector)
        where_input_layout.addWidget(self.where_value_select)
        where_layout.addLayout(where_input_layout)

        self.where_value_select.clicked.connect(self.on_select_where)
        self.where_input_data.currentTextChanged.connect(self.on_operator_changed)

        order_group = QGroupBox("ORDER BY - Сортировка")
        order_layout = QVBoxLayout(order_group)
        order_input_layout = QHBoxLayout()
        self.order_field = QComboBox()
        self.order_field.addItems([""] + self.columns_name)
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])

        order_input_layout.addWidget(QLabel("Сортировать по:"))
        order_input_layout.addWidget(self.order_field)
        order_input_layout.addWidget(QLabel("Направление:"))
        order_input_layout.addWidget(self.order_direction)
        order_layout.addLayout(order_input_layout)

        group_group = QGroupBox("GROUP BY - Группировка")
        group_layout = QVBoxLayout(group_group)
        group_input_layout = QHBoxLayout()

        self.group_by_type = QComboBox()
        self.group_by_type.addItems(["", "GROUPING SETS", "ROLLUP", "CUBE"])
        self.group_by_type.currentTextChanged.connect(self.on_group_by_changed)

        self.group_field = QComboBox()
        self.group_field.addItems([""] + self.columns_name)

        self.aggregate_function = QComboBox()
        aggArr = ["", "COUNT(*)"]
        for name in self.columns_name:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        # Контейнер для расширенной группировки
        self.grouping_container = QVBoxLayout()

        # Создаем label для расширенной группировки
        self.grouping_label = QLabel("Выберите поля для группировки:")
        self.grouping_label.setVisible(False)  # Изначально скрыт

        self.grouping_list_widget = QListWidget()
        self.grouping_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.grouping_list_widget.setVisible(False)  # Изначально скрыт

        # Добавляем тестовые данные

        self.grouping_list_widget.addItems(self.columns_name)

        group_input_layout.addWidget(QLabel("Тип группировки:"))
        group_input_layout.addWidget(self.group_by_type)
        group_input_layout.addWidget(QLabel("Группировать по:"))
        group_input_layout.addWidget(self.group_field)

        # Сохраняем ссылки на элементы для легкого доступа
        self.aggregate_label = QLabel("Агрегатная функция:")
        group_input_layout.addWidget(self.aggregate_label)
        group_input_layout.addWidget(self.aggregate_function)

        group_layout.addLayout(group_input_layout)
        self.grouping_container.addWidget(self.grouping_label)
        self.grouping_container.addWidget(self.grouping_list_widget)
        group_layout.addLayout(self.grouping_container)

        having_group = QGroupBox("HAVING - Фильтрация групп")
        having_layout = QVBoxLayout(having_group)
        having_input_layout = QHBoxLayout()
        self.having_condition = QLineEdit()
        self.having_condition.setPlaceholderText("Например: COUNT(*) > 1 OR AVG(salary) > 50000")

        having_input_layout.addWidget(QLabel("Условие:"))
        having_input_layout.addWidget(self.having_condition)
        having_layout.addLayout(having_input_layout)
        self.execute_btn = QPushButton("Задать WHERE SELECT условие")
        self.execute_btn.clicked.connect(self.execute_query)

        self.sql_preview = QTextEdit()
        self.sql_preview.setPlaceholderText("Здесь будет отображаться сгенерированный SQL запрос...")
        self.sql_preview.setMaximumHeight(100)

        layout.addWidget(table_group)
        layout.addWidget(join_group)
        layout.addWidget(case_group)
        layout.addWidget(select_group)
        layout.addWidget(where_group)
        layout.addWidget(order_group)
        layout.addWidget(group_group)
        layout.addWidget(having_group)
        layout.addWidget(self.execute_btn)
        layout.addWidget(self.sql_preview)

        return widget

    def on_group_by_changed(self, group_type):
        """Обработчик изменения типа группировки"""
        is_advanced_grouping = group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]

        # Показываем/скрываем обычное поле группировки
        self.group_field.setVisible(not is_advanced_grouping)

        # Показываем/скрываем список для расширенной группировки
        self.grouping_list_widget.setVisible(is_advanced_grouping)

        # Скрываем агрегатные функции и их лейбл при расширенной группировке
        self.aggregate_function.setVisible(not is_advanced_grouping)
        self.aggregate_label.setVisible(not is_advanced_grouping)

        # Показываем/скрываем label для расширенной группировки
        self.grouping_label.setVisible(is_advanced_grouping)

        # Обновляем подпись в зависимости от типа группировки
        if group_type == "GROUPING SETS":
            self.grouping_label.setText("Выберите наборы полей для группировки:")
        elif group_type == "ROLLUP":
            self.grouping_label.setText("Выберите иерархию полей для ROLLUP:")
        elif group_type == "CUBE":
            self.grouping_label.setText("Выберите поля для CUBE:")
        else:
            self.grouping_label.setText("Выберите поля для группировки:")

    def on_select_where(self):
        dlg = SelectDialog(self)
        dlg.exec()

    def on_operator_changed(self, function_name):
        if function_name == "Поле Ввода":
            self.where_value_label.setText("Значение:")
            self.where_value_select.setVisible(False)
            self.where_selector.setVisible(False)
            self.where_value.setVisible(True)
        elif function_name == "SQL подзапрос":
            self.where_value_label.setText("Запрос и селектор:")
            self.where_value.setVisible(False)
            self.where_selector.setVisible(True)
            self.where_value_select.setVisible(True)

    def add_join_widget(self):
        join_widget = JoinWidget()
        self.joins_container.addWidget(join_widget)
        self.join_widgets.append(join_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_join_widget(join_widget, remove_btn))

        join_container = QHBoxLayout()
        join_container.addWidget(join_widget)
        join_container.addWidget(remove_btn)

        self.joins_container.insertLayout(self.joins_container.count() - 1, join_container)

    def remove_join_widget(self, join_widget, remove_btn):
        for i in range(self.joins_container.count()):
            item = self.joins_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(join_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.joins_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.join_widgets.remove(join_widget)

    def add_case_widget(self):
        case_widget = CaseWidget(self.columns_name)
        self.cases_container.addWidget(case_widget)
        self.case_widgets.append(case_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_case_widget(case_widget, remove_btn))

        case_container = QHBoxLayout()
        case_container.addWidget(case_widget)
        case_container.addWidget(remove_btn)

        self.cases_container.insertLayout(self.cases_container.count() - 1, case_container)

    def remove_case_widget(self, case_widget, remove_btn):
        for i in range(self.cases_container.count()):
            item = self.cases_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(case_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.cases_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.case_widgets.remove(case_widget)

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)

        return widget

    def get_selected_columns(self):
        selected_columns = []
        for column_widget in self.column_widgets.values():
            expression = column_widget.get_column_expression()
            if expression:
                selected_columns.append(expression)
        return selected_columns

    def get_join_expressions(self):
        joins = []
        for join_widget in self.join_widgets:
            join_expr = join_widget.get_join_expression()
            if join_expr:
                joins.append(join_expr)
        return joins

    def get_case_expressions(self):
        cases = []
        for case_widget in self.case_widgets:
            case_expr = case_widget.get_case_expression()
            if case_expr:
                cases.append(case_expr)
        return cases

    def build_sql_query(self):
        # SELECT
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            selected_columns = ["*"]

        select_clause = "SELECT " + ", ".join(selected_columns)

        from_clause = f"FROM {self.main_table.currentText()}"

        join_clauses = self.get_join_expressions()

        case_clauses = ""
        if self.get_case_expressions() != []:
            case_clauses = f", CASE "
            for i in self.get_case_expressions():
                case_clauses += i + ", "
            else:
                case_clauses = case_clauses[:len(case_clauses) - 2]

            if self.case_else.text() != "":
                case_clauses += f" ELSE '{self.case_else.text()}' "
            case_clauses += " END "
            if self.case_as_name.text() != "":
                case_clauses += f"AS {self.case_as_name.text()} "

        where_clause = ""
        where_value = self.where_value.text().strip()
        if where_value:
            field = self.where_field.currentText()
            operator = self.where_operator.currentText()
            where_clause = f"WHERE {field} {operator} '{where_value}'"

        # Обработка расширенной группировки
        group_clause = ""
        group_type = self.group_by_type.currentText()
        aggregate = self.aggregate_function.currentText()

        if group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]:
            # Получаем выбранные поля из списка
            selected_grouping_fields = [item.text() for item in self.grouping_list_widget.selectedItems()]
            if selected_grouping_fields:
                if group_type == "GROUPING SETS":
                    group_clause = f"GROUP BY GROUPING SETS (({'), ('.join(selected_grouping_fields)}))"
                elif group_type == "ROLLUP":
                    group_clause = f"GROUP BY ROLLUP ({', '.join(selected_grouping_fields)})"
                elif group_type == "CUBE":
                    group_clause = f"GROUP BY CUBE ({', '.join(selected_grouping_fields)})"

                # Для расширенной группировки не используем агрегатные функции в SELECT
                # так как они скрыты в интерфейсе
        else:
            # Обычная группировка
            group_field = self.group_field.currentText()
            if group_field:
                group_clause = f"GROUP BY {group_field}"
                if aggregate:
                    select_clause = f"SELECT {group_field}, {aggregate}"

        having_clause = ""
        having_condition = self.having_condition.text().strip()
        if having_condition and group_clause:
            having_clause = f"HAVING {having_condition}"

        order_clause = ""
        order_field = self.order_field.currentText()
        order_dir = self.order_direction.currentText()
        if order_field:
            order_clause = f"ORDER BY {order_field} {order_dir}"

        query_parts = [select_clause + case_clauses, from_clause] + join_clauses + [where_clause, group_clause,
                                                                                    having_clause,
                                                                                    order_clause]
        full_query = " ".join(part for part in query_parts if part)

        return full_query

    def execute_query(self):
        query = self.build_sql_query()
        SaveQuery(query)
        self.close()

class CTEDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр данных - Employee Database")
        self.setModal(True)
        self.setGeometry(100, 100, 600, 900)
        self.column_widgets = {}
        self.join_widgets = []
        self.case_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.columns = []
        self.columns_name = []
        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.employee_col_full:
            self.columns.append(col[0])
            self.columns_name.append("employee." + col[0])
        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.project_col_full:
            self.columns.append(col[0])
            self.columns_name.append("project." + col[0])
        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.task_col_full:
            self.columns.append(col[0])
            self.columns_name.append("task." + col[0])

        splitter = QSplitter(Qt.Horizontal)

        left_panel = self.create_query_builder()
        splitter.addWidget(left_panel)

        layout.addWidget(splitter)

    def create_query_builder(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        table_group = QGroupBox("FROM - Выбор таблицы")
        table_layout = QHBoxLayout(table_group)

        self.main_table = QComboBox()
        self.main_table.addItems(["employee", "task", "project"])
        self.main_table.setCurrentText("employee")

        table_layout.addWidget(QLabel("Основная таблица:"))
        table_layout.addWidget(self.main_table)
        table_layout.addStretch()

        join_group = QGroupBox("JOIN - Объединение таблиц")
        join_layout = QVBoxLayout(join_group)

        self.joins_container = QVBoxLayout()

        self.add_join_btn = QPushButton("+ Добавить JOIN")
        self.add_join_btn.clicked.connect(self.add_join_widget)

        join_layout.addLayout(self.joins_container)
        join_layout.addWidget(self.add_join_btn)

        case_group = QGroupBox("CASE - Объединение таблиц")
        case_layout = QVBoxLayout(case_group)

        self.cases_container = QVBoxLayout()

        self.add_case_btn = QPushButton("+ Добавить WHEN ... THEN")
        self.add_case_btn.clicked.connect(self.add_case_widget)

        self.case_as_name = QLineEdit()
        self.case_as_name.setMaxLength(100)
        self.case_else = QLineEdit()
        self.case_else.setMaxLength(100)

        self.case_desc_form = QFormLayout()
        self.case_desc_form.addRow("AS", self.case_as_name)
        self.case_desc_form.addRow("ELSE", self.case_else)

        case_layout.addLayout(self.case_desc_form)
        case_layout.addLayout(self.cases_container)

        case_layout.addWidget(self.add_case_btn)

        select_group = QGroupBox("SELECT - Выбор столбцов и функции")
        select_layout = QVBoxLayout(select_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)  # Ограничиваем высоту и включаем скролл
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        columns_info = []

        for i in range(len(self.columns)):
            columns_info.append((self.columns_name[i], self.columns_name[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        select_layout.addWidget(scroll_area)

        where_group = QGroupBox("WHERE - Фильтрация")
        where_layout = QVBoxLayout(where_group)
        where_input_layout = QHBoxLayout()
        self.where_field = QComboBox()
        self.where_field.addItems(self.columns_name)
        self.where_operator = QComboBox()
        self.where_operator.addItems(
            ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*", "SIMILAR TO"])
        self.where_value = QLineEdit()
        self.where_input_data = QComboBox()
        self.where_input_data.addItems(["Поле Ввода", "SQL подзапрос"])
        self.where_value_label = QLabel("Значение:")
        self.where_value_select = QPushButton("Задать")
        self.where_selector = QComboBox()
        self.where_selector.addItems(["", "ANY", "ALL", "EXIST"])
        self.where_value_select.setVisible(False)
        self.where_selector.setVisible(False)
        self.where_value.setPlaceholderText("Значение для фильтра")
        where_input_layout.addWidget(QLabel("Поле:"))
        where_input_layout.addWidget(self.where_field)
        where_input_layout.addWidget(QLabel("Оператор:"))
        where_input_layout.addWidget(self.where_operator)
        where_input_layout.addWidget(QLabel("Ввод данных:"))
        where_input_layout.addWidget(self.where_input_data)
        where_input_layout.addWidget(self.where_value_label)
        where_input_layout.addWidget(self.where_value)
        where_input_layout.addWidget(self.where_selector)
        where_input_layout.addWidget(self.where_value_select)
        where_layout.addLayout(where_input_layout)

        self.where_value_select.clicked.connect(self.on_select_where)
        self.where_input_data.currentTextChanged.connect(self.on_operator_changed)

        order_group = QGroupBox("ORDER BY - Сортировка")
        order_layout = QVBoxLayout(order_group)
        order_input_layout = QHBoxLayout()
        self.order_field = QComboBox()
        self.order_field.addItems([""] + self.columns_name)
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])

        order_input_layout.addWidget(QLabel("Сортировать по:"))
        order_input_layout.addWidget(self.order_field)
        order_input_layout.addWidget(QLabel("Направление:"))
        order_input_layout.addWidget(self.order_direction)
        order_layout.addLayout(order_input_layout)

        group_group = QGroupBox("GROUP BY - Группировка")
        group_layout = QVBoxLayout(group_group)
        group_input_layout = QHBoxLayout()

        self.group_by_type = QComboBox()
        self.group_by_type.addItems(["", "GROUPING SETS", "ROLLUP", "CUBE"])
        self.group_by_type.currentTextChanged.connect(self.on_group_by_changed)

        self.group_field = QComboBox()
        self.group_field.addItems([""] + self.columns_name)

        self.aggregate_function = QComboBox()
        aggArr = ["", "COUNT(*)"]
        for name in self.columns_name:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        # Контейнер для расширенной группировки
        self.grouping_container = QVBoxLayout()

        # Создаем label для расширенной группировки
        self.grouping_label = QLabel("Выберите поля для группировки:")
        self.grouping_label.setVisible(False)  # Изначально скрыт

        self.grouping_list_widget = QListWidget()
        self.grouping_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.grouping_list_widget.setVisible(False)  # Изначально скрыт

        # Добавляем тестовые данные

        self.grouping_list_widget.addItems(self.columns_name)

        group_input_layout.addWidget(QLabel("Тип группировки:"))
        group_input_layout.addWidget(self.group_by_type)
        group_input_layout.addWidget(QLabel("Группировать по:"))
        group_input_layout.addWidget(self.group_field)

        # Сохраняем ссылки на элементы для легкого доступа
        self.aggregate_label = QLabel("Агрегатная функция:")
        group_input_layout.addWidget(self.aggregate_label)
        group_input_layout.addWidget(self.aggregate_function)

        group_layout.addLayout(group_input_layout)
        self.grouping_container.addWidget(self.grouping_label)
        self.grouping_container.addWidget(self.grouping_list_widget)
        group_layout.addLayout(self.grouping_container)

        having_group = QGroupBox("HAVING - Фильтрация групп")
        having_layout = QVBoxLayout(having_group)
        having_input_layout = QHBoxLayout()
        self.having_condition = QLineEdit()
        self.having_condition.setPlaceholderText("Например: COUNT(*) > 1 OR AVG(salary) > 50000")

        having_input_layout.addWidget(QLabel("Условие:"))
        having_input_layout.addWidget(self.having_condition)
        having_layout.addLayout(having_input_layout)
        self.execute_btn = QPushButton("Сохрнать")
        self.execute_btn.clicked.connect(self.execute_query)

        self.sql_preview = QTextEdit()
        self.sql_preview.setPlaceholderText("Здесь будет отображаться сгенерированный SQL запрос...")
        self.sql_preview.setMaximumHeight(100)

        layout.addWidget(table_group)
        layout.addWidget(join_group)
        layout.addWidget(case_group)
        layout.addWidget(select_group)
        layout.addWidget(where_group)
        layout.addWidget(order_group)
        layout.addWidget(group_group)
        layout.addWidget(having_group)
        layout.addWidget(self.execute_btn)
        layout.addWidget(self.sql_preview)

        return widget

    def on_group_by_changed(self, group_type):
        """Обработчик изменения типа группировки"""
        is_advanced_grouping = group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]

        # Показываем/скрываем обычное поле группировки
        self.group_field.setVisible(not is_advanced_grouping)

        # Показываем/скрываем список для расширенной группировки
        self.grouping_list_widget.setVisible(is_advanced_grouping)

        # Скрываем агрегатные функции и их лейбл при расширенной группировке
        self.aggregate_function.setVisible(not is_advanced_grouping)
        self.aggregate_label.setVisible(not is_advanced_grouping)

        # Показываем/скрываем label для расширенной группировки
        self.grouping_label.setVisible(is_advanced_grouping)

        # Обновляем подпись в зависимости от типа группировки
        if group_type == "GROUPING SETS":
            self.grouping_label.setText("Выберите наборы полей для группировки:")
        elif group_type == "ROLLUP":
            self.grouping_label.setText("Выберите иерархию полей для ROLLUP:")
        elif group_type == "CUBE":
            self.grouping_label.setText("Выберите поля для CUBE:")
        else:
            self.grouping_label.setText("Выберите поля для группировки:")

    def on_select_where(self):
        dlg = SelectDialog(self)
        dlg.exec()

    def on_operator_changed(self, function_name):
        if function_name == "Поле Ввода":
            self.where_value_label.setText("Значение:")
            self.where_value_select.setVisible(False)
            self.where_selector.setVisible(False)
            self.where_value.setVisible(True)
        elif function_name == "SQL подзапрос":
            self.where_value_label.setText("Запрос и селектор:")
            self.where_value.setVisible(False)
            self.where_selector.setVisible(True)
            self.where_value_select.setVisible(True)

    def add_join_widget(self):
        join_widget = JoinWidget()
        self.joins_container.addWidget(join_widget)
        self.join_widgets.append(join_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_join_widget(join_widget, remove_btn))

        join_container = QHBoxLayout()
        join_container.addWidget(join_widget)
        join_container.addWidget(remove_btn)

        self.joins_container.insertLayout(self.joins_container.count() - 1, join_container)

    def remove_join_widget(self, join_widget, remove_btn):
        for i in range(self.joins_container.count()):
            item = self.joins_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(join_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.joins_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.join_widgets.remove(join_widget)

    def add_case_widget(self):
        case_widget = CaseWidget(self.columns_name)
        self.cases_container.addWidget(case_widget)
        self.case_widgets.append(case_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_case_widget(case_widget, remove_btn))

        case_container = QHBoxLayout()
        case_container.addWidget(case_widget)
        case_container.addWidget(remove_btn)

        self.cases_container.insertLayout(self.cases_container.count() - 1, case_container)

    def remove_case_widget(self, case_widget, remove_btn):
        for i in range(self.cases_container.count()):
            item = self.cases_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(case_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.cases_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.case_widgets.remove(case_widget)

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)

        return widget

    def get_selected_columns(self):
        selected_columns = []
        for column_widget in self.column_widgets.values():
            expression = column_widget.get_column_expression()
            if expression:
                selected_columns.append(expression)
        return selected_columns

    def get_join_expressions(self):
        joins = []
        for join_widget in self.join_widgets:
            join_expr = join_widget.get_join_expression()
            if join_expr:
                joins.append(join_expr)
        return joins

    def get_case_expressions(self):
        cases = []
        for case_widget in self.case_widgets:
            case_expr = case_widget.get_case_expression()
            if case_expr:
                cases.append(case_expr)
        return cases

    def build_sql_query(self):
        # SELECT
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            selected_columns = ["*"]

        select_clause = "SELECT " + ", ".join(selected_columns)

        from_clause = f"FROM {self.main_table.currentText()}"

        join_clauses = self.get_join_expressions()

        case_clauses = ""
        if self.get_case_expressions() != []:
            case_clauses = f", CASE "
            for i in self.get_case_expressions():
                case_clauses += i + ", "
            else:
                case_clauses = case_clauses[:len(case_clauses) - 2]

            if self.case_else.text() != "":
                case_clauses += f" ELSE '{self.case_else.text()}' "
            case_clauses += " END "
            if self.case_as_name.text() != "":
                case_clauses += f"AS {self.case_as_name.text()} "

        where_clause = ""
        where_value = self.where_value.text().strip()
        if where_value:
            field = self.where_field.currentText()
            operator = self.where_operator.currentText()
            where_clause = f"WHERE {field} {operator} '{where_value}'"

        # Обработка расширенной группировки
        group_clause = ""
        group_type = self.group_by_type.currentText()
        aggregate = self.aggregate_function.currentText()

        if group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]:
            # Получаем выбранные поля из списка
            selected_grouping_fields = [item.text() for item in self.grouping_list_widget.selectedItems()]
            if selected_grouping_fields:
                if group_type == "GROUPING SETS":
                    group_clause = f"GROUP BY GROUPING SETS (({'), ('.join(selected_grouping_fields)}))"
                elif group_type == "ROLLUP":
                    group_clause = f"GROUP BY ROLLUP ({', '.join(selected_grouping_fields)})"
                elif group_type == "CUBE":
                    group_clause = f"GROUP BY CUBE ({', '.join(selected_grouping_fields)})"

                # Для расширенной группировки не используем агрегатные функции в SELECT
                # так как они скрыты в интерфейсе
        else:
            # Обычная группировка
            group_field = self.group_field.currentText()
            if group_field:
                group_clause = f"GROUP BY {group_field}"
                if aggregate:
                    select_clause = f"SELECT {group_field}, {aggregate}"

        having_clause = ""
        having_condition = self.having_condition.text().strip()
        if having_condition and group_clause:
            having_clause = f"HAVING {having_condition}"

        order_clause = ""
        order_field = self.order_field.currentText()
        order_dir = self.order_direction.currentText()
        if order_field:
            order_clause = f"ORDER BY {order_field} {order_dir}"

        query_parts = [select_clause + case_clauses, from_clause] + join_clauses + [where_clause, group_clause,
                                                                                    having_clause,
                                                                                    order_clause]
        full_query = " ".join(part for part in query_parts if part)

        return full_query

    def execute_query(self):
        query = self.build_sql_query()
        SaveCTEQuery(query, self.get_selected_columns())
        self.close()

class DataViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр данных - Employee Database")
        self.setModal(True)
        self.setGeometry(100, 100, 1700, 900)
        self.column_widgets = {}
        self.join_widgets = []
        self.case_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.columns = []
        self.columns_name = []
        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.employee_col_full:
            self.columns.append(col[0])
            self.columns_name.append("employee." + col[0])
        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.project_col_full:
            self.columns.append(col[0])
            self.columns_name.append("project." + col[0])
        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.task_col_full:
            self.columns.append(col[0])
            self.columns_name.append("task." + col[0])

        splitter = QSplitter(Qt.Horizontal)

        left_panel = self.create_query_builder()
        splitter.addWidget(left_panel)

        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([850, 850])
        layout.addWidget(splitter)

    def create_query_builder(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        CTE_group = QGroupBox("CTE - Вспомогательная таблица")
        CTE_layout = QHBoxLayout(CTE_group)

        self.CTE_name = QLineEdit()
        self.CTE_value = QPushButton("Задать")
        self.CTE_save = QPushButton("Сохранить")

        self.CTE_value.clicked.connect(self.on_CTE_value)
        self.CTE_save.clicked.connect(self.on_CTE_save)

        CTE_layout.addWidget(QLabel("Название:"))
        CTE_layout.addWidget(self.CTE_name)
        CTE_layout.addWidget(QLabel("Задать:"))
        CTE_layout.addWidget(self.CTE_value)
        CTE_layout.addWidget(QLabel("Сохранить (нажать после задания запроса):"))
        CTE_layout.addWidget(self.CTE_save)

        table_group = QGroupBox("FROM - Выбор таблицы")
        table_layout = QHBoxLayout(table_group)

        self.main_table = QComboBox()
        self.main_table.addItems(["employee", "task", "project"])
        self.main_table.setCurrentText("employee")

        table_layout.addWidget(QLabel("Основная таблица:"))
        table_layout.addWidget(self.main_table)
        table_layout.addStretch()

        join_group = QGroupBox("JOIN - Объединение таблиц")
        join_layout = QVBoxLayout(join_group)

        self.joins_container = QVBoxLayout()

        self.add_join_btn = QPushButton("+ Добавить JOIN")
        self.add_join_btn.clicked.connect(self.add_join_widget)

        join_layout.addLayout(self.joins_container)
        join_layout.addWidget(self.add_join_btn)

        case_group = QGroupBox("CASE - Объединение таблиц")
        case_layout = QVBoxLayout(case_group)

        self.cases_container = QVBoxLayout()

        self.add_case_btn = QPushButton("+ Добавить WHEN ... THEN")
        self.add_case_btn.clicked.connect(self.add_case_widget)

        self.case_as_name = QLineEdit()
        self.case_as_name.setMaxLength(100)
        self.case_else = QLineEdit()
        self.case_else.setMaxLength(100)

        self.case_desc_form = QFormLayout()
        self.case_desc_form.addRow("AS", self.case_as_name)
        self.case_desc_form.addRow("ELSE", self.case_else)

        case_layout.addLayout(self.case_desc_form)
        case_layout.addLayout(self.cases_container)

        case_layout.addWidget(self.add_case_btn)

        select_group = QGroupBox("SELECT - Выбор столбцов и функции")
        select_layout = QVBoxLayout(select_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)  # Ограничиваем высоту и включаем скролл
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        columns_info = []

        for i in range(len(self.columns)):
            columns_info.append((self.columns_name[i], self.columns_name[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        select_layout.addWidget(scroll_area)

        where_group = QGroupBox("WHERE - Фильтрация")
        where_layout = QVBoxLayout(where_group)
        where_input_layout = QHBoxLayout()
        self.where_field = QComboBox()
        self.where_field.addItems(self.columns_name)
        self.where_operator = QComboBox()
        self.where_operator.addItems(
            ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*", "SIMILAR TO"])
        self.where_value = QLineEdit()
        self.where_input_data = QComboBox()
        self.where_input_data.addItems(["Поле Ввода", "SQL подзапрос"])
        self.where_value_label = QLabel("Значение:")
        self.where_value_select = QPushButton("Задать")
        self.where_selector = QComboBox()
        self.where_selector.addItems(["", "ANY", "ALL", "EXIST"])
        self.where_value_select.setVisible(False)
        self.where_selector.setVisible(False)
        self.where_value.setPlaceholderText("Значение для фильтра")
        where_input_layout.addWidget(QLabel("Поле:"))
        where_input_layout.addWidget(self.where_field)
        where_input_layout.addWidget(QLabel("Оператор:"))
        where_input_layout.addWidget(self.where_operator)
        where_input_layout.addWidget(QLabel("Ввод данных:"))
        where_input_layout.addWidget(self.where_input_data)
        where_input_layout.addWidget(self.where_value_label)
        where_input_layout.addWidget(self.where_value)
        where_input_layout.addWidget(self.where_selector)
        where_input_layout.addWidget(self.where_value_select)
        where_layout.addLayout(where_input_layout)

        self.where_value_select.clicked.connect(self.on_select_where)
        self.where_input_data.currentTextChanged.connect(self.on_operator_changed)

        order_group = QGroupBox("ORDER BY - Сортировка")
        order_layout = QVBoxLayout(order_group)
        order_input_layout = QHBoxLayout()
        self.order_field = QComboBox()
        self.order_field.addItems([""] + self.columns_name)
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])

        order_input_layout.addWidget(QLabel("Сортировать по:"))
        order_input_layout.addWidget(self.order_field)
        order_input_layout.addWidget(QLabel("Направление:"))
        order_input_layout.addWidget(self.order_direction)
        order_layout.addLayout(order_input_layout)

        group_group = QGroupBox("GROUP BY - Группировка")
        group_layout = QVBoxLayout(group_group)
        group_input_layout = QHBoxLayout()

        self.group_by_type = QComboBox()
        self.group_by_type.addItems(["", "GROUPING SETS", "ROLLUP", "CUBE"])
        self.group_by_type.currentTextChanged.connect(self.on_group_by_changed)

        self.group_field = QComboBox()
        self.group_field.addItems([""] + self.columns_name)

        self.aggregate_function = QComboBox()
        aggArr = ["", "COUNT(*)"]
        for name in self.columns_name:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        # Контейнер для расширенной группировки
        self.grouping_container = QVBoxLayout()

        # Создаем label для расширенной группировки
        self.grouping_label = QLabel("Выберите поля для группировки:")
        self.grouping_label.setVisible(False)  # Изначально скрыт

        self.grouping_list_widget = QListWidget()
        self.grouping_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.grouping_list_widget.setVisible(False)  # Изначально скрыт

        self.grouping_list_widget.addItems(self.columns_name)

        group_input_layout.addWidget(QLabel("Тип группировки:"))
        group_input_layout.addWidget(self.group_by_type)
        self.group_field_label = QLabel("Группировать по:")
        group_input_layout.addWidget(self.group_field_label)
        group_input_layout.addWidget(self.group_field)

        # Сохраняем ссылки на элементы для легкого доступа
        self.aggregate_label = QLabel("Агрегатная функция:")
        group_input_layout.addWidget(self.aggregate_label)
        group_input_layout.addWidget(self.aggregate_function)

        group_layout.addLayout(group_input_layout)
        self.grouping_container.addWidget(self.grouping_label)
        self.grouping_container.addWidget(self.grouping_list_widget)
        group_layout.addLayout(self.grouping_container)

        having_group = QGroupBox("HAVING - Фильтрация групп")
        having_layout = QVBoxLayout(having_group)
        having_input_layout = QHBoxLayout()
        self.having_condition = QLineEdit()
        self.having_condition.setPlaceholderText("Например: COUNT(*) > 1 OR AVG(salary) > 50000")

        having_input_layout.addWidget(QLabel("Условие:"))
        having_input_layout.addWidget(self.having_condition)
        having_layout.addLayout(having_input_layout)
        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_query)

        self.sql_preview = QTextEdit()
        self.sql_preview.setPlaceholderText("Здесь будет отображаться сгенерированный SQL запрос...")
        self.sql_preview.setMaximumHeight(100)

        layout.addWidget(CTE_group)
        layout.addWidget(table_group)
        layout.addWidget(join_group)
        layout.addWidget(case_group)
        layout.addWidget(select_group)
        layout.addWidget(where_group)
        layout.addWidget(order_group)
        layout.addWidget(group_group)
        layout.addWidget(having_group)
        layout.addWidget(self.execute_btn)
        layout.addWidget(self.sql_preview)

        return widget

    def on_CTE_save(self):
        arr = GetCTEarr()
        name = self.CTE_name.text()
        for i in range(len(arr)):
            arr[i] = arr[i][arr[i].find(".") + 1:]
            arr[i] = name + "." + arr[i]
        self.main_table.addItems([name])
        columns_info = []

        for i in range(len(arr)):
            columns_info.append((arr[i], arr[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.where_field.addItems(arr)

        self.order_direction.addItems(arr)

        self.group_field.addItems(arr)

        aggArr = []
        for name in arr:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        ClearCTEarr()

    def on_select_where(self):
        dlg = SelectDialog(self)
        dlg.exec()

    def on_CTE_value(self):
        dlg = CTEDialog(self)
        dlg.exec()

    def on_operator_changed(self, function_name):
        if function_name == "Поле Ввода":
            self.where_value_label.setText("Значение:")
            self.where_value_select.setVisible(False)
            self.where_selector.setVisible(False)
            self.where_value.setVisible(True)
        elif function_name == "SQL подзапрос":
            self.where_value_label.setText("Запрос и селектор:")
            self.where_value.setVisible(False)
            self.where_selector.setVisible(True)
            self.where_value_select.setVisible(True)

    def on_group_by_changed(self, group_type):
        """Обработчик изменения типа группировки"""
        is_advanced_grouping = group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]

        # Показываем/скрываем обычное поле группировки
        self.group_field.setVisible(not is_advanced_grouping)

        # Показываем/скрываем список для расширенной группировки
        self.grouping_list_widget.setVisible(is_advanced_grouping)
        self.group_field_label.setVisible(not is_advanced_grouping)
        # Скрываем агрегатные функции и их лейбл при расширенной группировке
        self.aggregate_function.setVisible(not is_advanced_grouping)
        self.aggregate_label.setVisible(not is_advanced_grouping)

        # Показываем/скрываем label для расширенной группировки
        self.grouping_label.setVisible(is_advanced_grouping)

        # Обновляем подпись в зависимости от типа группировки
        if group_type == "GROUPING SETS":
            self.grouping_label.setText("Выберите наборы полей для группировки:")
        elif group_type == "ROLLUP":
            self.grouping_label.setText("Выберите иерархию полей для ROLLUP:")
        elif group_type == "CUBE":
            self.grouping_label.setText("Выберите поля для CUBE:")
        else:
            self.grouping_label.setText("Выберите поля для группировки:")

    def add_join_widget(self):
        join_widget = JoinWidget()
        self.joins_container.addWidget(join_widget)
        self.join_widgets.append(join_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_join_widget(join_widget, remove_btn))

        join_container = QHBoxLayout()
        join_container.addWidget(join_widget)
        join_container.addWidget(remove_btn)

        self.joins_container.insertLayout(self.joins_container.count() - 1, join_container)

    def remove_join_widget(self, join_widget, remove_btn):
        for i in range(self.joins_container.count()):
            item = self.joins_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(join_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.joins_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.join_widgets.remove(join_widget)

    def add_case_widget(self):
        case_widget = CaseWidget(self.columns_name)
        self.cases_container.addWidget(case_widget)
        self.case_widgets.append(case_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_case_widget(case_widget, remove_btn))

        case_container = QHBoxLayout()
        case_container.addWidget(case_widget)
        case_container.addWidget(remove_btn)

        self.cases_container.insertLayout(self.cases_container.count() - 1, case_container)

    def remove_case_widget(self, case_widget, remove_btn):
        for i in range(self.cases_container.count()):
            item = self.cases_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(case_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.cases_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.case_widgets.remove(case_widget)

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)

        return widget

    def get_selected_columns(self):
        selected_columns = []
        for column_widget in self.column_widgets.values():
            expression = column_widget.get_column_expression()
            if expression:
                selected_columns.append(expression)
        return selected_columns

    def get_join_expressions(self):
        joins = []
        for join_widget in self.join_widgets:
            join_expr = join_widget.get_join_expression()
            if join_expr:
                joins.append(join_expr)
        return joins

    def get_case_expressions(self):
        cases = []
        for case_widget in self.case_widgets:
            case_expr = case_widget.get_case_expression()
            if case_expr:
                cases.append(case_expr)
        return cases

    def build_sql_query(self):
        #CTE

        CTE_name = self.CTE_name.text().strip()
        CTE_clause = ""
        if GetCTEquery() != "":
            CTE_clause = f"WITH RECURSIVE {CTE_name} AS ({GetCTEquery()}) "

        # SELECT
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            selected_columns = ["*"]

        select_clause = "SELECT " + ", ".join(selected_columns)

        from_clause = f"FROM {self.main_table.currentText()}"

        join_clauses = self.get_join_expressions()

        case_clauses = ""
        if self.get_case_expressions() != []:
            case_clauses = f", CASE "
            for i in self.get_case_expressions():
                case_clauses += i + ", "
            else:
                case_clauses = case_clauses[:len(case_clauses) - 2]

            if self.case_else.text() != "":
                case_clauses += f" ELSE '{self.case_else.text()}' "
            case_clauses += " END "
            if self.case_as_name.text() != "":
                case_clauses += f"AS {self.case_as_name.text()} "

        where_clause = ""
        where_value = self.where_value.text().strip()
        if where_value:
            field = self.where_field.currentText()
            operator = self.where_operator.currentText()
            where_clause = f"WHERE {field} {operator} '{where_value}'"

        # Обработка расширенной группировки
        group_clause = ""
        group_type = self.group_by_type.currentText()
        aggregate = self.aggregate_function.currentText()

        if group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]:
            # Получаем выбранные поля из списка
            selected_grouping_fields = [item.text() for item in self.grouping_list_widget.selectedItems()]
            if selected_grouping_fields:
                if group_type == "GROUPING SETS":
                    group_clause = f"GROUP BY GROUPING SETS (({'), ('.join(selected_grouping_fields)}))"
                elif group_type == "ROLLUP":
                    group_clause = f"GROUP BY ROLLUP ({', '.join(selected_grouping_fields)})"
                elif group_type == "CUBE":
                    group_clause = f"GROUP BY CUBE ({', '.join(selected_grouping_fields)})"

                # Для расширенной группировки не используем агрегатные функции в SELECT
                # так как они скрыты в интерфейсе
        else:
            # Обычная группировка
            group_field = self.group_field.currentText()
            if group_field:
                group_clause = f"GROUP BY {group_field}"
                if aggregate:
                    select_clause = f"SELECT {group_field}, {aggregate}"

        having_clause = ""
        having_condition = self.having_condition.text().strip()
        if having_condition and group_clause:
            having_clause = f"HAVING {having_condition}"

        order_clause = ""
        order_field = self.order_field.currentText()
        order_dir = self.order_direction.currentText()
        if order_field:
            order_clause = f"ORDER BY {order_field} {order_dir}"

        query_parts = [CTE_clause + select_clause + case_clauses, from_clause] + join_clauses + [where_clause, group_clause,
                                                                                    having_clause,
                                                                                    order_clause]
        full_query = " ".join(part for part in query_parts if part)

        return full_query

    def execute_query(self):
        try:
            query = self.build_sql_query()
            self.sql_preview.setText(f"Сгенерированный SQL:\n{query}")
            self.json_data = requests.get(f'http://localhost:3000/project/filters?col_string="{query}"').json()
            print(self.json_data)
            if (type(self.json_data) == str):
                return
            demo_data = []
            if self.json_data is None:
                return
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)
            print(demo_data)

            processed_data = demo_data

            '''processed_data = []
            for row in demo_data:
                processed_row = []
                k = 0
                for i, (column_name, column_widget) in enumerate(self.column_widgets.items()):
                    if column_widget.checkbox.isChecked():
                        original_value = str(row[k])
                        k += 1
                        function_name = column_widget.function_combo.currentText()

                        if function_name == "Без функции":
                            processed_row.append(original_value)
                        elif function_name == "UPPER":
                            processed_row.append(original_value.upper())
                        elif function_name == "LOWER":
                            processed_row.append(original_value.lower())
                        elif function_name == "TRIM":
                            processed_row.append(original_value.strip())
                        elif function_name == "LTRIM":
                            processed_row.append(original_value.lstrip())
                        elif function_name == "RTRIM":
                            processed_row.append(original_value.rstrip())
                        else:
                            processed_row.append(original_value)

                if processed_row:
                    processed_data.append(processed_row)'''

            headers = list(self.json_data[0].keys())
            print(processed_data, headers)
            self.model.update_data(processed_data, headers)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")


class FieldWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.field_name = QLineEdit()
        self.field_name.setPlaceholderText('name')
        self.field_name.setMaxLength(300)

        self.data_type = QComboBox()
        my_attribute = self.getTypes()
        self.data_type.addItems(["VARCHAR", "TEXT", "DATE", "INTEGER", "BOOLEAN", "ARRAY"] + my_attribute)

        layout.addWidget(QLabel("Имя поля: "))
        layout.addWidget(self.field_name)
        layout.addWidget(QLabel("Тип поля: "))
        layout.addWidget(self.data_type)

    def get_field_expression(self):
        pass

    def getTypes(self):
        try:
            self.json_data = requests.get('http://localhost:3000/user_type').json()
            print(self.json_data)
            if (type(self.json_data) == str):
                return
            demo_data = []
            if self.json_data is None:
                return
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)

            processed_data = demo_data

            for i in range(len(processed_data)):
                processed_data[i] = processed_data[i][1].replace("'", '"')

            return processed_data

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")


class AddTypeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.field_widgets = []

        self.setWindowTitle("Добавление пользовательского типа")
        self.setGeometry(300, 300, 400, 400)

        self.typeName = QLineEdit()
        self.typeName.setPlaceholderText('name')
        self.typeName.setMaxLength(300)

        self.typeType = QComboBox()
        self.typeType.addItems(["ENUM", "Составной тип"])
        self.typeType.currentTextChanged.connect(self.on_type_changed)

        self.enumList = QLineEdit()
        self.enumList.setPlaceholderText('mon, tue, wed')
        self.enumList.setVisible(True)

        self.compoAdd = QPushButton('Добавить поле')
        self.compoAdd.clicked.connect(self.add_field_widget)
        self.compoAdd.setVisible(False)

        self.addForm = QFormLayout()
        self.addForm.addRow('Список значений', self.enumList)
        self.addForm.addWidget(self.compoAdd)

        self.typeForm = QFormLayout()
        self.typeForm.addRow('Название типа', self.typeName)
        self.typeForm.addRow('Подвид типа', self.typeType)

        self.data_box = QGroupBox()
        self.data_box.setLayout(self.addForm)

        self.addButton = QPushButton('Создать тип')
        self.addButton.clicked.connect(self.createSQLquery)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.typeForm)
        self.layout.addWidget(self.data_box)
        self.layout.addWidget(self.addButton)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def on_type_changed(self, type):
        if type == "ENUM":
            self.compoAdd.setVisible(False)
            for item in self.field_widgets:
                self.remove_field_widget(item[0], item[1])
            self.enumList = QLineEdit()
            self.enumList.setPlaceholderText('mon, tue, wed')
            self.addForm.addRow('Список значений', self.enumList)
        elif type == "Составной тип":
            self.addForm.removeRow(self.enumList)
            self.compoAdd.setVisible(True)

    def add_field_widget(self):
        field_widget = FieldWidget()
        self.addForm.addWidget(field_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_field_widget(field_widget, remove_btn))

        self.field_widgets.append([field_widget, remove_btn])

        field_container = QHBoxLayout()
        field_container.addWidget(field_widget)
        field_container.addWidget(remove_btn)

        self.addForm.insertRow(self.addForm.count() - 1, field_container)

    def remove_field_widget(self, field_widget, remove_btn):
        for i in range(self.addForm.count()):
            item = self.addForm.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(field_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.addForm.takeAt(i)
                    layout_to_remove.deleteLater()
                    break

        self.field_widgets.remove([field_widget, remove_btn])

    def employee_remove_constraint_col(self):
        col = self.employeeRenameCol.currentText()

    def createSQLquery(self):
        query = f"CREATE TYPE {self.typeName.text().strip()} AS"
        if self.typeType.currentText() == "ENUM":
            query += " ENUM("
            arr_str = [f"'{i}'" for i in self.enumList.text().split(", ")]
            for i in arr_str:
                query += f"{i}, "
            query = query[:-2] + ");"
        else:
            query += " ("
            for i in self.field_widgets:
                query += f"{i[0].field_name.text().strip()} {i[0].data_type.currentText().strip()}, "
            query = query[:-2] + ");"
        print(query)
        json_string = '{"alter_string": "' + query + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/user_type', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")


class DropTypeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Удалить пользовательский тип')
        self.setGeometry(300, 300, 300, 100)

        self.types = self.getTypes()

        self.dropBox = QGroupBox()

        self.dropForm = QFormLayout()

        self.dropUDT = QComboBox()
        for col in self.types:
            self.dropUDT.addItem(col)
        self.dropForm.addRow("Тип: ", self.dropUDT)

        self.dropButton = QPushButton('Расстрелять тип💥')
        self.dropButton.clicked.connect(self.dropType)
        self.dropForm.addWidget(self.dropButton)

        self.dropBox.setLayout(self.dropForm)
        layout = QVBoxLayout()
        layout.addWidget(self.dropBox)
        self.setLayout(layout)

    def dropType(self):
        query = f"DROP TYPE {self.dropUDT.currentText()}"
        json_string = '{"alter_string": "' + query + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/user_type', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при удалении!")
        else:
            makeLog("Изменения добавлены!")

    def getTypes(self):
        try:
            self.json_data = requests.get('http://localhost:3000/user_type').json()
            print(self.json_data)
            if (type(self.json_data) == str):
                return
            demo_data = []
            if self.json_data is None:
                return
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)

            processed_data = demo_data

            for i in range(len(processed_data)):
                processed_data[i] = processed_data[i][1]

            return processed_data

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")


class ShowTypesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Посмотреть пользовательские типы')
        self.setGeometry(300, 300, 400, 300)

        layout = QHBoxLayout(self)

        panel = self.create_results_panel()
        layout.addWidget(panel)
        self.execute_query()

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)

        return widget

    def execute_query(self):
        try:
            self.json_data = requests.get('http://localhost:3000/user_type').json()
            print(self.json_data)
            if (type(self.json_data) == str):
                return
            demo_data = []
            if self.json_data is None:
                return
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)
            print(demo_data)

            processed_data = demo_data

            for i in range(len(processed_data)):
                if processed_data[i][0] == "E":
                    processed_data[i][0] = "Enum"
                else:
                    processed_data[i][0] = "Composite"

            headers = list(self.json_data[0].keys())
            print(processed_data, headers)
            self.model.update_data(processed_data, headers)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")


class AlterTypesDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Редактирование пользовательских типов")
        self.setGeometry(300, 300, 400, 220)

        self.types = self.getTypes()

        self.tab = QTabWidget()

        # ----------------------

        self.renameForm = QFormLayout()

        self.renameUDT = QComboBox()

        for col in self.types:
            self.renameUDT.addItem(col)
        self.renameForm.addRow("Тип: ", self.renameUDT)

        self.typeName = QLineEdit()
        self.typeName.setMaxLength(300)
        self.typeName.setPlaceholderText("name")

        self.renameForm.addRow("Переименовать в: ", self.typeName)

        self.renameUDT_button = QPushButton('Переименовать тип')
        self.renameUDT_button.clicked.connect(self.renameType)

        self.rename_layout = QVBoxLayout()
        self.rename_layout.addLayout(self.renameForm)
        self.rename_layout.addWidget(self.renameUDT_button)
        self.rename_layout.addStretch()

        self.rename_box = QGroupBox()
        self.rename_box.setLayout(self.rename_layout)

        self.tab.insertTab(0, self.rename_box, 'Переименовать тип')

        # ----------------------

        self.add_form = QFormLayout()

        self.addUDT = QComboBox()

        for col in self.types:
            self.addUDT.addItem(col)
        self.add_form.addRow("Тип: ", self.addUDT)

        self.addType = QComboBox()
        my_attribute = self.getTypes()
        self.addType.addItems(["VARCHAR", "TEXT", "DATE", "INTEGER", "BOOLEAN", "ARRAY"] + my_attribute)

        self.add_form.addRow("Тип нового аттрибута: ", self.addType)

        self.add_name = QLineEdit()
        self.add_form.addRow("Название  аттрибута: ", self.add_name)

        self.add_button = QPushButton('Добавить аттрибут')
        self.add_button.clicked.connect(self.AddProperty)

        self.add_layout = QVBoxLayout()
        self.add_layout.addLayout(self.add_form)
        self.add_layout.addWidget(self.add_button)
        self.add_layout.addStretch()

        self.add_box = QGroupBox()
        self.add_box.setLayout(self.add_layout)

        self.tab.insertTab(1, self.add_box, 'Добавить аттрибут')

        # ----------------------

        self.drop_form = QFormLayout()

        self.dropUDT = QComboBox()

        for col in self.types:
            self.dropUDT.addItem(col)
        self.dropUDT.currentTextChanged.connect(self.ChangeAttribute)
        self.drop_form.addRow("Тип: ", self.dropUDT)

        self.dropCol = QComboBox()
        self.ChangeAttribute()
        self.drop_form.addRow("Удаляемый аттрибут: ", self.dropCol)

        self.drop_button = QPushButton('Изменить колонку')
        self.drop_button.clicked.connect(self.DropAttribute)

        self.drop_layout = QVBoxLayout()
        self.drop_layout.addLayout(self.drop_form)
        self.drop_layout.addWidget(self.drop_button)
        self.drop_layout.addStretch()

        self.drop_box = QGroupBox()
        self.drop_box.setLayout(self.drop_layout)

        self.tab.insertTab(2, self.drop_box, 'Удалить аттрибут')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tab)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def getTypes(self):
        try:
            self.json_data = requests.get('http://localhost:3000/user_type').json()
            if (type(self.json_data) == str):
                return
            demo_data = []
            if self.json_data is None:
                return
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)

            processed_data = demo_data

            for i in range(len(processed_data)):
                processed_data[i] = processed_data[i][1]

            return processed_data

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")

    def renameType(self):
        query = f"ALTER TYPE {self.renameUDT.currentText()} RENAME TO {self.typeName.text()}"
        print(query)
        json_string = '{"alter_string": "' + query + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/user_type', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при переименовании!")
        else:
            makeLog("Изменения добавлены!")

    def AddProperty(self):
        query = f"ALTER TYPE {self.addUDT.currentText()} ADD ATTRIBUTE {self.add_name.text()} {self.addType.currentText()}"
        json_string = '{"alter_string": "' + query + '"}'
        json_data = json.loads(json_string)
        r = requests.post('http://localhost:3000/user_type', json=json_data)
        if r.status_code != 200:
            makeLog("Ошибка при добавлении!")
        else:
            makeLog("Изменения добавлены!")

    def ChangeAttribute(self):
        self.dropCol.clear()
        data = self.GetAttribute()
        for col in data:
            self.dropCol.addItem(col)

    def GetAttribute(self):
        try:
            self.json_data = requests.get('http://localhost:3000/user_type/values').json()
            if (type(self.json_data) == str):
                return
            demo_data = []
            if self.json_data is None:
                return
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)

            processed_data = []

            for i in demo_data:
                if i[3] == self.dropUDT.currentText():
                    if i[2] == 'ENUM':
                        processed_data = [j[1:-1] for j in i[1][1:-1].split(", ")]
                        break
                    else:
                        processed_data = [j[1:-1] for j in i[0][1:-1].split(", ")]
                        break

            return processed_data

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")

    def DropAttribute(self):
        self.json_data = requests.get('http://localhost:3000/user_type/values').json()
        if (type(self.json_data) == str):
            return
        demo_data = []
        if self.json_data is None:
            return
        for col in self.json_data:
            info = []
            for item in col.values():
                info.append(item)
            demo_data.append(info)

        processed_data = []

        for i in demo_data:
            if i[3] == self.dropUDT.currentText():
                if i[2] == 'ENUM':
                    query = f"DROP TYPE {self.dropUDT.currentText()}"
                    print(query)
                    json_string = '{"alter_string": "' + query + '"}'
                    json_data = json.loads(json_string)
                    r = requests.post('http://localhost:3000/user_type', json=json_data)
                    if r.status_code != 200:
                        makeLog("Ошибка при удалении!")
                    else:
                        makeLog("Изменения добавлены!")
                    query = f"CREATE TYPE {self.dropUDT.currentText()} AS"
                    query += " ENUM("
                    processed_data = [f"'{j[1:-1]}'" for j in i[1][1:-1].split(", ")]
                    for i in processed_data:
                        if i != f"'{self.dropCol.currentText()}'":
                            query += f"{i}, "
                    query = query[:-2] + ");"
                    print(query)
                    json_string = '{"alter_string": "' + query + '"}'
                    json_data = json.loads(json_string)
                    r = requests.post('http://localhost:3000/user_type', json=json_data)
                    if r.status_code != 200:
                        makeLog("Ошибка при удалении!")
                    else:
                        makeLog("Изменения добавлены!")
                else:
                    query = f"ALTER TYPE {self.dropUDT.currentText()} DROP ATTRIBUTE {self.dropCol.currentText()}"
                    json_string = '{"alter_string": "' + query + '"}'
                    json_data = json.loads(json_string)
                    r = requests.post('http://localhost:3000/user_type', json=json_data)
                    if r.status_code != 200:
                        makeLog("Ошибка при удаление!")
                    else:
                        makeLog("Изменения добавлены!")
                break


class UDTDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Окно пользовательских типов")
        self.setModal(True)
        self.setGeometry(200, 200, 600, 220)
        self.init_ui()

    def init_ui(self):
        self.show_button = QPushButton('Отобразить типы')
        self.show_button.clicked.connect(self.showUDT)
        self.add_button = QPushButton('Добавить тип')
        self.add_button.clicked.connect(self.addUDT)
        self.drop_button = QPushButton('Удалить тип')
        self.drop_button.clicked.connect(self.dropUDT)
        self.alter_button = QPushButton('Изменить типы')
        self.alter_button.clicked.connect(self.alterUDT)

        self.UDT_layout = QVBoxLayout()
        self.UDT_layout.addWidget(self.show_button)
        self.UDT_layout.addWidget(self.add_button)
        self.UDT_layout.addWidget(self.drop_button)
        self.UDT_layout.addWidget(self.alter_button)
        self.UDT_layout.addStretch()

        self.empl_box = QGroupBox("Пользовательские типы")
        self.empl_box.setLayout(self.UDT_layout)  # установка макета в блок

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.empl_box)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def alterUDT(self):
        dlg = AlterTypesDialog()
        dlg.exec()

    def showUDT(self):
        dlg = ShowTypesDialog()
        dlg.exec()

    def addUDT(self):
        dlg = AddTypeDialog()
        dlg.exec()

    def dropUDT(self):
        dlg = DropTypeDialog()
        dlg.exec()


class CreateViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание VIEW")
        self.setModal(True)
        self.setGeometry(100, 100, 1000, 900)
        self.column_widgets = {}
        self.join_widgets = []
        self.case_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.columns = []
        self.columns_name = []
        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.employee_col_full:
            self.columns.append(col[0])
            self.columns_name.append("employee." + col[0])
        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.project_col_full:
            self.columns.append(col[0])
            self.columns_name.append("project." + col[0])
        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.task_col_full:
            self.columns.append(col[0])
            self.columns_name.append("task." + col[0])

        left_panel = self.create_query_builder()

        layout.addWidget(left_panel)

    def create_query_builder(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Блок для названия VIEW
        view_name_group = QGroupBox("Название VIEW")
        view_name_layout = QHBoxLayout(view_name_group)

        self.view_name_edit = QLineEdit()
        self.view_name_edit.setPlaceholderText("Введите название представления")
        self.view_name_edit.setMaxLength(100)

        view_name_layout.addWidget(QLabel("Название:"))
        view_name_layout.addWidget(self.view_name_edit)
        view_name_layout.addStretch()

        # Остальные блоки из DataViewerDialog
        CTE_group = QGroupBox("CTE - Вспомогательная таблица")
        CTE_layout = QHBoxLayout(CTE_group)

        self.CTE_name = QLineEdit()
        self.CTE_value = QPushButton("Задать")
        self.CTE_save = QPushButton("Сохранить")

        self.CTE_value.clicked.connect(self.on_CTE_value)
        self.CTE_save.clicked.connect(self.on_CTE_save)

        CTE_layout.addWidget(QLabel("Название:"))
        CTE_layout.addWidget(self.CTE_name)
        CTE_layout.addWidget(QLabel("Задать:"))
        CTE_layout.addWidget(self.CTE_value)
        CTE_layout.addWidget(QLabel("Сохранить (нажать после задания запроса):"))
        CTE_layout.addWidget(self.CTE_save)

        table_group = QGroupBox("FROM - Выбор таблицы")
        table_layout = QHBoxLayout(table_group)

        self.main_table = QComboBox()
        self.main_table.addItems(["employee", "task", "project"])
        self.main_table.setCurrentText("employee")

        table_layout.addWidget(QLabel("Основная таблица:"))
        table_layout.addWidget(self.main_table)
        table_layout.addStretch()

        join_group = QGroupBox("JOIN - Объединение таблиц")
        join_layout = QVBoxLayout(join_group)

        self.joins_container = QVBoxLayout()

        self.add_join_btn = QPushButton("+ Добавить JOIN")
        self.add_join_btn.clicked.connect(self.add_join_widget)

        join_layout.addLayout(self.joins_container)
        join_layout.addWidget(self.add_join_btn)

        case_group = QGroupBox("CASE - Объединение таблиц")
        case_layout = QVBoxLayout(case_group)

        self.cases_container = QVBoxLayout()

        self.add_case_btn = QPushButton("+ Добавить WHEN ... THEN")
        self.add_case_btn.clicked.connect(self.add_case_widget)

        self.case_as_name = QLineEdit()
        self.case_as_name.setMaxLength(100)
        self.case_else = QLineEdit()
        self.case_else.setMaxLength(100)

        self.case_desc_form = QFormLayout()
        self.case_desc_form.addRow("AS", self.case_as_name)
        self.case_desc_form.addRow("ELSE", self.case_else)

        case_layout.addLayout(self.case_desc_form)
        case_layout.addLayout(self.cases_container)

        case_layout.addWidget(self.add_case_btn)

        select_group = QGroupBox("SELECT - Выбор столбцов и функции")
        select_layout = QVBoxLayout(select_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        columns_info = []

        for i in range(len(self.columns)):
            columns_info.append((self.columns_name[i], self.columns_name[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        select_layout.addWidget(scroll_area)

        where_group = QGroupBox("WHERE - Фильтрация")
        where_layout = QVBoxLayout(where_group)
        where_input_layout = QHBoxLayout()
        self.where_field = QComboBox()
        self.where_field.addItems(self.columns_name)
        self.where_operator = QComboBox()
        self.where_operator.addItems(
            ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*", "SIMILAR TO"])
        self.where_value = QLineEdit()
        self.where_input_data = QComboBox()
        self.where_input_data.addItems(["Поле Ввода", "SQL подзапрос"])
        self.where_value_label = QLabel("Значение:")
        self.where_value_select = QPushButton("Задать")
        self.where_selector = QComboBox()
        self.where_selector.addItems(["", "ANY", "ALL", "EXIST"])
        self.where_value_select.setVisible(False)
        self.where_selector.setVisible(False)
        self.where_value.setPlaceholderText("Значение для фильтра")
        where_input_layout.addWidget(QLabel("Поле:"))
        where_input_layout.addWidget(self.where_field)
        where_input_layout.addWidget(QLabel("Оператор:"))
        where_input_layout.addWidget(self.where_operator)
        where_input_layout.addWidget(QLabel("Ввод данных:"))
        where_input_layout.addWidget(self.where_input_data)
        where_input_layout.addWidget(self.where_value_label)
        where_input_layout.addWidget(self.where_value)
        where_input_layout.addWidget(self.where_selector)
        where_input_layout.addWidget(self.where_value_select)
        where_layout.addLayout(where_input_layout)

        self.where_value_select.clicked.connect(self.on_select_where)
        self.where_input_data.currentTextChanged.connect(self.on_operator_changed)

        order_group = QGroupBox("ORDER BY - Сортировка")
        order_layout = QVBoxLayout(order_group)
        order_input_layout = QHBoxLayout()
        self.order_field = QComboBox()
        self.order_field.addItems([""] + self.columns_name)
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])

        order_input_layout.addWidget(QLabel("Сортировать по:"))
        order_input_layout.addWidget(self.order_field)
        order_input_layout.addWidget(QLabel("Направление:"))
        order_input_layout.addWidget(self.order_direction)
        order_layout.addLayout(order_input_layout)

        group_group = QGroupBox("GROUP BY - Группировка")
        group_layout = QVBoxLayout(group_group)
        group_input_layout = QHBoxLayout()

        self.group_by_type = QComboBox()
        self.group_by_type.addItems(["", "GROUPING SETS", "ROLLUP", "CUBE"])
        self.group_by_type.currentTextChanged.connect(self.on_group_by_changed)

        self.group_field = QComboBox()
        self.group_field.addItems([""] + self.columns_name)

        self.aggregate_function = QComboBox()
        aggArr = ["", "COUNT(*)"]
        for name in self.columns_name:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        self.grouping_container = QVBoxLayout()
        self.grouping_label = QLabel("Выберите поля для группировки:")
        self.grouping_label.setVisible(False)

        self.grouping_list_widget = QListWidget()
        self.grouping_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.grouping_list_widget.setVisible(False)

        self.grouping_list_widget.addItems(self.columns_name)

        group_input_layout.addWidget(QLabel("Тип группировки:"))
        group_input_layout.addWidget(self.group_by_type)
        self.group_field_label = QLabel("Группировать по:")
        group_input_layout.addWidget(self.group_field_label)
        group_input_layout.addWidget(self.group_field)

        self.aggregate_label = QLabel("Агрегатная функция:")
        group_input_layout.addWidget(self.aggregate_label)
        group_input_layout.addWidget(self.aggregate_function)

        group_layout.addLayout(group_input_layout)
        self.grouping_container.addWidget(self.grouping_label)
        self.grouping_container.addWidget(self.grouping_list_widget)
        group_layout.addLayout(self.grouping_container)

        having_group = QGroupBox("HAVING - Фильтрация групп")
        having_layout = QVBoxLayout(having_group)
        having_input_layout = QHBoxLayout()
        self.having_condition = QLineEdit()
        self.having_condition.setPlaceholderText("Например: COUNT(*) > 1 OR AVG(salary) > 50000")

        having_input_layout.addWidget(QLabel("Условие:"))
        having_input_layout.addWidget(self.having_condition)
        having_layout.addLayout(having_input_layout)

        self.create_view_btn = QPushButton("Создать VIEW")
        self.create_view_btn.clicked.connect(self.create_view)

        self.sql_preview = QTextEdit()
        self.sql_preview.setPlaceholderText("Здесь будет отображаться сгенерированный SQL запрос...")
        self.sql_preview.setMaximumHeight(100)

        layout.addWidget(view_name_group)
        layout.addWidget(CTE_group)
        layout.addWidget(table_group)
        layout.addWidget(join_group)
        layout.addWidget(case_group)
        layout.addWidget(select_group)
        layout.addWidget(where_group)
        layout.addWidget(order_group)
        layout.addWidget(group_group)
        layout.addWidget(having_group)
        layout.addWidget(self.create_view_btn)
        layout.addWidget(self.sql_preview)

        return widget

    def on_CTE_save(self):
        arr = GetCTEarr()
        name = self.CTE_name.text()
        for i in range(len(arr)):
            arr[i] = arr[i][arr[i].find(".") + 1:]
            arr[i] = name + "." + arr[i]
        self.main_table.addItems([name])
        columns_info = []

        for i in range(len(arr)):
            columns_info.append((arr[i], arr[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.where_field.addItems(arr)
        self.order_field.addItems([""] + arr)
        self.group_field.addItems([""] + arr)

        aggArr = []
        for name in arr:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        ClearCTEarr()

    def on_select_where(self):
        dlg = SelectDialog(self)
        dlg.exec()

    def on_CTE_value(self):
        dlg = CTEDialog(self)
        dlg.exec()

    def on_operator_changed(self, function_name):
        if function_name == "Поле Ввода":
            self.where_value_label.setText("Значение:")
            self.where_value_select.setVisible(False)
            self.where_selector.setVisible(False)
            self.where_value.setVisible(True)
        elif function_name == "SQL подзапрос":
            self.where_value_label.setText("Запрос и селектор:")
            self.where_value.setVisible(False)
            self.where_selector.setVisible(True)
            self.where_value_select.setVisible(True)

    def on_group_by_changed(self, group_type):
        is_advanced_grouping = group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]
        self.group_field.setVisible(not is_advanced_grouping)
        self.grouping_list_widget.setVisible(is_advanced_grouping)
        self.group_field_label.setVisible(not is_advanced_grouping)
        self.aggregate_function.setVisible(not is_advanced_grouping)
        self.aggregate_label.setVisible(not is_advanced_grouping)
        self.grouping_label.setVisible(is_advanced_grouping)

        if group_type == "GROUPING SETS":
            self.grouping_label.setText("Выберите наборы полей для группировки:")
        elif group_type == "ROLLUP":
            self.grouping_label.setText("Выберите иерархию полей для ROLLUP:")
        elif group_type == "CUBE":
            self.grouping_label.setText("Выберите поля для CUBE:")
        else:
            self.grouping_label.setText("Выберите поля для группировки:")

    def add_join_widget(self):
        join_widget = JoinWidget()
        self.joins_container.addWidget(join_widget)
        self.join_widgets.append(join_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_join_widget(join_widget, remove_btn))

        join_container = QHBoxLayout()
        join_container.addWidget(join_widget)
        join_container.addWidget(remove_btn)

        self.joins_container.insertLayout(self.joins_container.count() - 1, join_container)

    def remove_join_widget(self, join_widget, remove_btn):
        for i in range(self.joins_container.count()):
            item = self.joins_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(join_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.joins_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break
        self.join_widgets.remove(join_widget)

    def add_case_widget(self):
        case_widget = CaseWidget(self.columns_name)
        self.cases_container.addWidget(case_widget)
        self.case_widgets.append(case_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_case_widget(case_widget, remove_btn))

        case_container = QHBoxLayout()
        case_container.addWidget(case_widget)
        case_container.addWidget(remove_btn)

        self.cases_container.insertLayout(self.cases_container.count() - 1, case_container)

    def remove_case_widget(self, case_widget, remove_btn):
        for i in range(self.cases_container.count()):
            item = self.cases_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(case_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.cases_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break
        self.case_widgets.remove(case_widget)

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)
        return widget

    def get_selected_columns(self):
        selected_columns = []
        for column_widget in self.column_widgets.values():
            expression = column_widget.get_column_expression()
            if expression:
                selected_columns.append(expression)
        return selected_columns

    def get_join_expressions(self):
        joins = []
        for join_widget in self.join_widgets:
            join_expr = join_widget.get_join_expression()
            if join_expr:
                joins.append(join_expr)
        return joins

    def get_case_expressions(self):
        cases = []
        for case_widget in self.case_widgets:
            case_expr = case_widget.get_case_expression()
            if case_expr:
                cases.append(case_expr)
        return cases

    def build_sql_query(self):
        CTE_name = self.CTE_name.text().strip()
        CTE_clause = ""
        if GetCTEquery() != "":
            CTE_clause = f"WITH RECURSIVE {CTE_name} AS ({GetCTEquery()}) "

        selected_columns = self.get_selected_columns()
        if not selected_columns:
            selected_columns = ["*"]

        select_clause = "SELECT " + ", ".join(selected_columns)
        from_clause = f"FROM {self.main_table.currentText()}"
        join_clauses = self.get_join_expressions()

        case_clauses = ""
        if self.get_case_expressions() != []:
            case_clauses = f", CASE "
            for i in self.get_case_expressions():
                case_clauses += i + ", "
            else:
                case_clauses = case_clauses[:len(case_clauses) - 2]

            if self.case_else.text() != "":
                case_clauses += f" ELSE '{self.case_else.text()}' "
            case_clauses += " END "
            if self.case_as_name.text() != "":
                case_clauses += f"AS {self.case_as_name.text()} "

        where_clause = ""
        where_value = self.where_value.text().strip()
        if where_value:
            field = self.where_field.currentText()
            operator = self.where_operator.currentText()
            where_clause = f"WHERE {field} {operator} '{where_value}'"

        group_clause = ""
        group_type = self.group_by_type.currentText()
        aggregate = self.aggregate_function.currentText()

        if group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]:
            selected_grouping_fields = [item.text() for item in self.grouping_list_widget.selectedItems()]
            if selected_grouping_fields:
                if group_type == "GROUPING SETS":
                    group_clause = f"GROUP BY GROUPING SETS (({'), ('.join(selected_grouping_fields)}))"
                elif group_type == "ROLLUP":
                    group_clause = f"GROUP BY ROLLUP ({', '.join(selected_grouping_fields)})"
                elif group_type == "CUBE":
                    group_clause = f"GROUP BY CUBE ({', '.join(selected_grouping_fields)})"
        else:
            group_field = self.group_field.currentText()
            if group_field:
                group_clause = f"GROUP BY {group_field}"
                if aggregate:
                    select_clause = f"SELECT {group_field}, {aggregate}"

        having_clause = ""
        having_condition = self.having_condition.text().strip()
        if having_condition and group_clause:
            having_clause = f"HAVING {having_condition}"

        order_clause = ""
        order_field = self.order_field.currentText()
        order_dir = self.order_direction.currentText()
        if order_field:
            order_clause = f"ORDER BY {order_field} {order_dir}"

        query_parts = [CTE_clause + select_clause + case_clauses, from_clause] + join_clauses + [where_clause,
                                                                                                 group_clause,
                                                                                                 having_clause,
                                                                                                 order_clause]
        full_query = " ".join(part for part in query_parts if part)

        return full_query

    def create_view(self):
        view_name = self.view_name_edit.text().strip()
        query = self.build_sql_query()
        create_view_query = f"CREATE VIEW {view_name} AS ({query})"

        self.sql_preview.setText(f"Создание VIEW:\n{create_view_query}")

        try:
            # Отправка запроса на создание VIEW
            json_string = '{"alter_string": "' + create_view_query + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/user_type', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при удалении!")
            else:
                makeLog("Изменения добавлены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании VIEW: {str(e)}")
            makeLog(f"Ошибка при создании VIEW: {str(e)}")


class ShowViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр VIEW")
        self.setModal(True)
        self.setGeometry(100, 100, 1200, 900)



        self.init_ui()



    def init_ui(self):
        layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal)

        self.columns = []
        self.columns_name = ['view_name']
        self.employee_col_full = requests.get('http://localhost:3000/user_type/view').json()
        for col in self.employee_col_full:
            self.columns.append(col['view_name'])

        left_panel = self.create_view_selector()
        splitter.addWidget(left_panel)

        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 900])
        layout.addWidget(splitter)

    def create_view_selector(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        view_group = QGroupBox("Выбор VIEW")
        view_layout = QVBoxLayout(view_group)

        self.view_combo = QComboBox()
        self.view_combo.addItems(self.columns)


        self.show_btn = QPushButton("Показать данные")
        self.show_btn.clicked.connect(self.show_view_data)

        view_layout.addWidget(QLabel("Выберите VIEW:"))
        view_layout.addWidget(self.view_combo)
        view_layout.addWidget(self.show_btn)
        view_layout.addStretch()

        layout.addWidget(view_group)
        return widget

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)
        return widget


    def show_view_data(self):
        selected_view = self.view_combo.currentText()
        if not selected_view:
            QMessageBox.warning(self, "Ошибка", "Выберите VIEW для просмотра")
            return

        try:
            query = f"SELECT * FROM {selected_view}"
            self.json_data = requests.get(f'http://localhost:3000/project/filters?col_string="{query}"').json()

            if isinstance(self.json_data, str):
                QMessageBox.warning(self, "Ошибка", self.json_data)
                return

            if self.json_data is None or len(self.json_data) == 0:
                QMessageBox.information(self, "Информация", "VIEW не содержит данных")
                return

            demo_data = []
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)

            headers = list(self.json_data[0].keys())
            self.model.update_data(demo_data, headers)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")


class DropViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление VIEW")
        self.setModal(True)
        self.setGeometry(300, 300, 400, 200)

        self.columns = []
        self.columns_name = ['view_name']
        self.employee_col_full = requests.get('http://localhost:3000/user_type/view').json()
        for col in self.employee_col_full:
            self.columns.append(col['view_name'])

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        view_group = QGroupBox("Удаление VIEW")
        view_layout = QVBoxLayout(view_group)

        self.view_combo = QComboBox()
        self.view_combo.addItems(self.columns)


        self.drop_btn = QPushButton("Удалить выбранный VIEW")
        self.drop_btn.clicked.connect(self.drop_view)

        view_layout.addWidget(QLabel("Выберите VIEW для удаления:"))
        view_layout.addWidget(self.view_combo)
        view_layout.addWidget(self.drop_btn)

        layout.addWidget(view_group)
        self.setLayout(layout)


    def drop_view(self):
        selected_view = self.view_combo.currentText()
        if not selected_view:
            QMessageBox.warning(self, "Ошибка", "Выберите VIEW для удаления")
            return

        try:
            query = f"DROP VIEW {selected_view}"
            json_string = '{"alter_string": "' + query + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/user_type', json=json_data)

            if r.status_code == 200:
                QMessageBox.information(self, "Успех", f"VIEW '{selected_view}' успешно удален!")
                makeLog(f"Удален VIEW: {selected_view}")
            else:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении VIEW: {r.text}")
                makeLog(f"Ошибка при удалении VIEW: {r.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении VIEW: {str(e)}")
            makeLog(f"Ошибка при удалении VIEW: {str(e)}")


class ViewManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление VIEW")
        self.setModal(True)
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.create_button = QPushButton('Создать VIEW')
        self.create_button.clicked.connect(self.create_view)

        self.show_button = QPushButton('Просмотреть VIEW')
        self.show_button.clicked.connect(self.show_view)

        self.drop_button = QPushButton('Удалить VIEW')
        self.drop_button.clicked.connect(self.drop_view)

        self.close_button = QPushButton('Закрыть')
        self.close_button.clicked.connect(self.close)

        view_layout = QVBoxLayout()
        view_layout.addWidget(self.create_button)
        view_layout.addWidget(self.show_button)
        view_layout.addWidget(self.drop_button)
        view_layout.addWidget(self.close_button)
        view_layout.addStretch()

        view_box = QGroupBox("Управление представлениями (VIEW)")
        view_box.setLayout(view_layout)

        layout.addWidget(view_box)
        self.setLayout(layout)

    def create_view(self):
        dlg = CreateViewDialog(self)
        dlg.exec()

    def show_view(self):
        dlg = ShowViewDialog(self)
        dlg.exec()

    def drop_view(self):
        dlg = DropViewDialog(self)
        dlg.exec()


class CreateMatViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание VIEW")
        self.setModal(True)
        self.setGeometry(100, 100, 1000, 900)
        self.column_widgets = {}
        self.join_widgets = []
        self.case_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.columns = []
        self.columns_name = []
        self.employee_col_full = requests.get('http://localhost:3000/employee/columns').json()
        for col in self.employee_col_full:
            self.columns.append(col[0])
            self.columns_name.append("employee." + col[0])
        self.project_col_full = requests.get('http://localhost:3000/project/columns').json()
        for col in self.project_col_full:
            self.columns.append(col[0])
            self.columns_name.append("project." + col[0])
        self.task_col_full = requests.get('http://localhost:3000/task/columns').json()
        for col in self.task_col_full:
            self.columns.append(col[0])
            self.columns_name.append("task." + col[0])

        left_panel = self.create_query_builder()

        layout.addWidget(left_panel)

    def create_query_builder(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        view_name_group = QGroupBox("Название MATERIALIZE VIEW")
        view_name_layout = QHBoxLayout(view_name_group)

        self.view_name_edit = QLineEdit()
        self.view_name_edit.setPlaceholderText("Введите название материального представления")
        self.view_name_edit.setMaxLength(100)

        view_name_layout.addWidget(QLabel("Название:"))
        view_name_layout.addWidget(self.view_name_edit)
        view_name_layout.addStretch()

        # Остальные блоки из DataViewerDialog
        CTE_group = QGroupBox("CTE - Вспомогательная таблица")
        CTE_layout = QHBoxLayout(CTE_group)

        self.CTE_name = QLineEdit()
        self.CTE_value = QPushButton("Задать")
        self.CTE_save = QPushButton("Сохранить")

        self.CTE_value.clicked.connect(self.on_CTE_value)
        self.CTE_save.clicked.connect(self.on_CTE_save)

        CTE_layout.addWidget(QLabel("Название:"))
        CTE_layout.addWidget(self.CTE_name)
        CTE_layout.addWidget(QLabel("Задать:"))
        CTE_layout.addWidget(self.CTE_value)
        CTE_layout.addWidget(QLabel("Сохранить (нажать после задания запроса):"))
        CTE_layout.addWidget(self.CTE_save)

        table_group = QGroupBox("FROM - Выбор таблицы")
        table_layout = QHBoxLayout(table_group)

        self.main_table = QComboBox()
        self.main_table.addItems(["employee", "task", "project"])
        self.main_table.setCurrentText("employee")

        table_layout.addWidget(QLabel("Основная таблица:"))
        table_layout.addWidget(self.main_table)
        table_layout.addStretch()

        join_group = QGroupBox("JOIN - Объединение таблиц")
        join_layout = QVBoxLayout(join_group)

        self.joins_container = QVBoxLayout()

        self.add_join_btn = QPushButton("+ Добавить JOIN")
        self.add_join_btn.clicked.connect(self.add_join_widget)

        join_layout.addLayout(self.joins_container)
        join_layout.addWidget(self.add_join_btn)

        case_group = QGroupBox("CASE - Объединение таблиц")
        case_layout = QVBoxLayout(case_group)

        self.cases_container = QVBoxLayout()

        self.add_case_btn = QPushButton("+ Добавить WHEN ... THEN")
        self.add_case_btn.clicked.connect(self.add_case_widget)

        self.case_as_name = QLineEdit()
        self.case_as_name.setMaxLength(100)
        self.case_else = QLineEdit()
        self.case_else.setMaxLength(100)

        self.case_desc_form = QFormLayout()
        self.case_desc_form.addRow("AS", self.case_as_name)
        self.case_desc_form.addRow("ELSE", self.case_else)

        case_layout.addLayout(self.case_desc_form)
        case_layout.addLayout(self.cases_container)

        case_layout.addWidget(self.add_case_btn)

        select_group = QGroupBox("SELECT - Выбор столбцов и функции")
        select_layout = QVBoxLayout(select_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        columns_info = []

        for i in range(len(self.columns)):
            columns_info.append((self.columns_name[i], self.columns_name[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        select_layout.addWidget(scroll_area)

        where_group = QGroupBox("WHERE - Фильтрация")
        where_layout = QVBoxLayout(where_group)
        where_input_layout = QHBoxLayout()
        self.where_field = QComboBox()
        self.where_field.addItems(self.columns_name)
        self.where_operator = QComboBox()
        self.where_operator.addItems(
            ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*", "SIMILAR TO"])
        self.where_value = QLineEdit()
        self.where_input_data = QComboBox()
        self.where_input_data.addItems(["Поле Ввода", "SQL подзапрос"])
        self.where_value_label = QLabel("Значение:")
        self.where_value_select = QPushButton("Задать")
        self.where_selector = QComboBox()
        self.where_selector.addItems(["", "ANY", "ALL", "EXIST"])
        self.where_value_select.setVisible(False)
        self.where_selector.setVisible(False)
        self.where_value.setPlaceholderText("Значение для фильтра")
        where_input_layout.addWidget(QLabel("Поле:"))
        where_input_layout.addWidget(self.where_field)
        where_input_layout.addWidget(QLabel("Оператор:"))
        where_input_layout.addWidget(self.where_operator)
        where_input_layout.addWidget(QLabel("Ввод данных:"))
        where_input_layout.addWidget(self.where_input_data)
        where_input_layout.addWidget(self.where_value_label)
        where_input_layout.addWidget(self.where_value)
        where_input_layout.addWidget(self.where_selector)
        where_input_layout.addWidget(self.where_value_select)
        where_layout.addLayout(where_input_layout)

        self.where_value_select.clicked.connect(self.on_select_where)
        self.where_input_data.currentTextChanged.connect(self.on_operator_changed)

        order_group = QGroupBox("ORDER BY - Сортировка")
        order_layout = QVBoxLayout(order_group)
        order_input_layout = QHBoxLayout()
        self.order_field = QComboBox()
        self.order_field.addItems([""] + self.columns_name)
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])

        order_input_layout.addWidget(QLabel("Сортировать по:"))
        order_input_layout.addWidget(self.order_field)
        order_input_layout.addWidget(QLabel("Направление:"))
        order_input_layout.addWidget(self.order_direction)
        order_layout.addLayout(order_input_layout)

        group_group = QGroupBox("GROUP BY - Группировка")
        group_layout = QVBoxLayout(group_group)
        group_input_layout = QHBoxLayout()

        self.group_by_type = QComboBox()
        self.group_by_type.addItems(["", "GROUPING SETS", "ROLLUP", "CUBE"])
        self.group_by_type.currentTextChanged.connect(self.on_group_by_changed)

        self.group_field = QComboBox()
        self.group_field.addItems([""] + self.columns_name)

        self.aggregate_function = QComboBox()
        aggArr = ["", "COUNT(*)"]
        for name in self.columns_name:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        self.grouping_container = QVBoxLayout()
        self.grouping_label = QLabel("Выберите поля для группировки:")
        self.grouping_label.setVisible(False)

        self.grouping_list_widget = QListWidget()
        self.grouping_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.grouping_list_widget.setVisible(False)

        self.grouping_list_widget.addItems(self.columns_name)

        group_input_layout.addWidget(QLabel("Тип группировки:"))
        group_input_layout.addWidget(self.group_by_type)
        self.group_field_label = QLabel("Группировать по:")
        group_input_layout.addWidget(self.group_field_label)
        group_input_layout.addWidget(self.group_field)

        self.aggregate_label = QLabel("Агрегатная функция:")
        group_input_layout.addWidget(self.aggregate_label)
        group_input_layout.addWidget(self.aggregate_function)

        group_layout.addLayout(group_input_layout)
        self.grouping_container.addWidget(self.grouping_label)
        self.grouping_container.addWidget(self.grouping_list_widget)
        group_layout.addLayout(self.grouping_container)

        having_group = QGroupBox("HAVING - Фильтрация групп")
        having_layout = QVBoxLayout(having_group)
        having_input_layout = QHBoxLayout()
        self.having_condition = QLineEdit()
        self.having_condition.setPlaceholderText("Например: COUNT(*) > 1 OR AVG(salary) > 50000")

        having_input_layout.addWidget(QLabel("Условие:"))
        having_input_layout.addWidget(self.having_condition)
        having_layout.addLayout(having_input_layout)

        self.create_view_btn = QPushButton("Создать MATERIALIZE VIEW")
        self.create_view_btn.clicked.connect(self.create_view)

        self.sql_preview = QTextEdit()
        self.sql_preview.setPlaceholderText("Здесь будет отображаться сгенерированный SQL запрос...")
        self.sql_preview.setMaximumHeight(100)

        layout.addWidget(view_name_group)
        layout.addWidget(CTE_group)
        layout.addWidget(table_group)
        layout.addWidget(join_group)
        layout.addWidget(case_group)
        layout.addWidget(select_group)
        layout.addWidget(where_group)
        layout.addWidget(order_group)
        layout.addWidget(group_group)
        layout.addWidget(having_group)
        layout.addWidget(self.create_view_btn)
        layout.addWidget(self.sql_preview)

        return widget

    def on_CTE_save(self):
        arr = GetCTEarr()
        name = self.CTE_name.text()
        for i in range(len(arr)):
            arr[i] = arr[i][arr[i].find(".") + 1:]
            arr[i] = name + "." + arr[i]
        self.main_table.addItems([name])
        columns_info = []

        for i in range(len(arr)):
            columns_info.append((arr[i], arr[i]))

        for column_name, display_name in columns_info:
            column_widget = ColumnFunctionWidget(column_name, display_name)
            self.column_widgets[column_name] = column_widget
            self.scroll_layout.addWidget(column_widget)

        self.where_field.addItems(arr)
        self.order_field.addItems([""] + arr)
        self.group_field.addItems([""] + arr)

        aggArr = []
        for name in arr:
            aggArr.append("COUNT(" + name + ")")
            aggArr.append("AVG(" + name + ")")
            aggArr.append("SUM(" + name + ")")
            aggArr.append("MIN(" + name + ")")
            aggArr.append("MAX(" + name + ")")
        self.aggregate_function.addItems(aggArr)

        ClearCTEarr()

    def on_select_where(self):
        dlg = SelectDialog(self)
        dlg.exec()

    def on_CTE_value(self):
        dlg = CTEDialog(self)
        dlg.exec()

    def on_operator_changed(self, function_name):
        if function_name == "Поле Ввода":
            self.where_value_label.setText("Значение:")
            self.where_value_select.setVisible(False)
            self.where_selector.setVisible(False)
            self.where_value.setVisible(True)
        elif function_name == "SQL подзапрос":
            self.where_value_label.setText("Запрос и селектор:")
            self.where_value.setVisible(False)
            self.where_selector.setVisible(True)
            self.where_value_select.setVisible(True)

    def on_group_by_changed(self, group_type):
        is_advanced_grouping = group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]
        self.group_field.setVisible(not is_advanced_grouping)
        self.grouping_list_widget.setVisible(is_advanced_grouping)
        self.group_field_label.setVisible(not is_advanced_grouping)
        self.aggregate_function.setVisible(not is_advanced_grouping)
        self.aggregate_label.setVisible(not is_advanced_grouping)
        self.grouping_label.setVisible(is_advanced_grouping)

        if group_type == "GROUPING SETS":
            self.grouping_label.setText("Выберите наборы полей для группировки:")
        elif group_type == "ROLLUP":
            self.grouping_label.setText("Выберите иерархию полей для ROLLUP:")
        elif group_type == "CUBE":
            self.grouping_label.setText("Выберите поля для CUBE:")
        else:
            self.grouping_label.setText("Выберите поля для группировки:")

    def add_join_widget(self):
        join_widget = JoinWidget()
        self.joins_container.addWidget(join_widget)
        self.join_widgets.append(join_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_join_widget(join_widget, remove_btn))

        join_container = QHBoxLayout()
        join_container.addWidget(join_widget)
        join_container.addWidget(remove_btn)

        self.joins_container.insertLayout(self.joins_container.count() - 1, join_container)

    def remove_join_widget(self, join_widget, remove_btn):
        for i in range(self.joins_container.count()):
            item = self.joins_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(join_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.joins_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break
        self.join_widgets.remove(join_widget)

    def add_case_widget(self):
        case_widget = CaseWidget(self.columns_name)
        self.cases_container.addWidget(case_widget)
        self.case_widgets.append(case_widget)

        remove_btn = QPushButton("+")
        remove_btn.setFixedSize(20, 20)
        remove_btn.clicked.connect(lambda: self.remove_case_widget(case_widget, remove_btn))

        case_container = QHBoxLayout()
        case_container.addWidget(case_widget)
        case_container.addWidget(remove_btn)

        self.cases_container.insertLayout(self.cases_container.count() - 1, case_container)

    def remove_case_widget(self, case_widget, remove_btn):
        for i in range(self.cases_container.count()):
            item = self.cases_container.itemAt(i)
            if isinstance(item, QHBoxLayout):
                if item.indexOf(case_widget) != -1:
                    for j in reversed(range(item.count())):
                        widget = item.itemAt(j).widget()
                        if widget:
                            widget.setParent(None)
                    layout_to_remove = self.cases_container.takeAt(i)
                    layout_to_remove.deleteLater()
                    break
        self.case_widgets.remove(case_widget)

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)
        return widget

    def get_selected_columns(self):
        selected_columns = []
        for column_widget in self.column_widgets.values():
            expression = column_widget.get_column_expression()
            if expression:
                selected_columns.append(expression)
        return selected_columns

    def get_join_expressions(self):
        joins = []
        for join_widget in self.join_widgets:
            join_expr = join_widget.get_join_expression()
            if join_expr:
                joins.append(join_expr)
        return joins

    def get_case_expressions(self):
        cases = []
        for case_widget in self.case_widgets:
            case_expr = case_widget.get_case_expression()
            if case_expr:
                cases.append(case_expr)
        return cases

    def build_sql_query(self):
        CTE_name = self.CTE_name.text().strip()
        CTE_clause = ""
        if GetCTEquery() != "":
            CTE_clause = f"WITH RECURSIVE {CTE_name} AS ({GetCTEquery()}) "

        selected_columns = self.get_selected_columns()
        if not selected_columns:
            selected_columns = ["*"]

        select_clause = "SELECT " + ", ".join(selected_columns)
        from_clause = f"FROM {self.main_table.currentText()}"
        join_clauses = self.get_join_expressions()

        case_clauses = ""
        if self.get_case_expressions() != []:
            case_clauses = f", CASE "
            for i in self.get_case_expressions():
                case_clauses += i + ", "
            else:
                case_clauses = case_clauses[:len(case_clauses) - 2]

            if self.case_else.text() != "":
                case_clauses += f" ELSE '{self.case_else.text()}' "
            case_clauses += " END "
            if self.case_as_name.text() != "":
                case_clauses += f"AS {self.case_as_name.text()} "

        where_clause = ""
        where_value = self.where_value.text().strip()
        if where_value:
            field = self.where_field.currentText()
            operator = self.where_operator.currentText()
            where_clause = f"WHERE {field} {operator} '{where_value}'"

        group_clause = ""
        group_type = self.group_by_type.currentText()
        aggregate = self.aggregate_function.currentText()

        if group_type in ["GROUPING SETS", "ROLLUP", "CUBE"]:
            selected_grouping_fields = [item.text() for item in self.grouping_list_widget.selectedItems()]
            if selected_grouping_fields:
                if group_type == "GROUPING SETS":
                    group_clause = f"GROUP BY GROUPING SETS (({'), ('.join(selected_grouping_fields)}))"
                elif group_type == "ROLLUP":
                    group_clause = f"GROUP BY ROLLUP ({', '.join(selected_grouping_fields)})"
                elif group_type == "CUBE":
                    group_clause = f"GROUP BY CUBE ({', '.join(selected_grouping_fields)})"
        else:
            group_field = self.group_field.currentText()
            if group_field:
                group_clause = f"GROUP BY {group_field}"
                if aggregate:
                    select_clause = f"SELECT {group_field}, {aggregate}"

        having_clause = ""
        having_condition = self.having_condition.text().strip()
        if having_condition and group_clause:
            having_clause = f"HAVING {having_condition}"

        order_clause = ""
        order_field = self.order_field.currentText()
        order_dir = self.order_direction.currentText()
        if order_field:
            order_clause = f"ORDER BY {order_field} {order_dir}"

        query_parts = [CTE_clause + select_clause + case_clauses, from_clause] + join_clauses + [where_clause,
                                                                                                 group_clause,
                                                                                                 having_clause,
                                                                                                 order_clause]
        full_query = " ".join(part for part in query_parts if part)

        return full_query

    def create_view(self):
        view_name = self.view_name_edit.text().strip()
        query = self.build_sql_query()
        create_view_query = f"CREATE MATERIALIZED VIEW {view_name} AS ({query}) WITH DATA"

        self.sql_preview.setText(f"Создание VIEW:\n{create_view_query}")

        try:
            # Отправка запроса на создание VIEW
            json_string = '{"alter_string": "' + create_view_query + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/user_type', json=json_data)
            if r.status_code != 200:
                makeLog("Ошибка при удалении!")
            else:
                makeLog("Изменения добавлены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании VIEW: {str(e)}")
            makeLog(f"Ошибка при создании VIEW: {str(e)}")


class ShowMatViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр MATERIALIZE VIEW")
        self.setModal(True)
        self.setGeometry(100, 100, 1200, 900)



        self.init_ui()



    def init_ui(self):
        layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal)

        self.columns = []
        self.columns_name = ['view_name']
        self.employee_col_full = requests.get('http://localhost:3000/user_type/matview').json()
        for col in self.employee_col_full:
            self.columns.append(col['view_name'])

        left_panel = self.create_view_selector()
        splitter.addWidget(left_panel)

        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 900])
        layout.addWidget(splitter)

    def create_view_selector(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        view_group = QGroupBox("Выбор MATERIALIZE VIEW")
        view_layout = QVBoxLayout(view_group)

        self.view_combo = QComboBox()
        self.view_combo.addItems(self.columns)


        self.show_btn = QPushButton("Показать данные")
        self.show_btn.clicked.connect(self.show_view_data)

        view_layout.addWidget(QLabel("Выберите MATERIALIZE VIEW:"))
        view_layout.addWidget(self.view_combo)
        view_layout.addWidget(self.show_btn)
        view_layout.addStretch()

        layout.addWidget(view_group)
        return widget

    def create_results_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableView()
        self.model = EmployeeTableModel()
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.results_table)
        return widget


    def show_view_data(self):
        selected_view = self.view_combo.currentText()
        if not selected_view:
            QMessageBox.warning(self, "Ошибка", "Выберите MATERIALIZE VIEW для просмотра")
            return

        try:
            query = f"SELECT * FROM {selected_view}"
            self.json_data = requests.get(f'http://localhost:3000/project/filters?col_string="{query}"').json()

            if isinstance(self.json_data, str):
                QMessageBox.warning(self, "Ошибка", self.json_data)
                return

            if self.json_data is None or len(self.json_data) == 0:
                QMessageBox.information(self, "Информация", "VIEW не содержит данных")
                return

            demo_data = []
            for col in self.json_data:
                info = []
                for item in col.values():
                    info.append(item)
                demo_data.append(info)

            headers = list(self.json_data[0].keys())
            self.model.update_data(demo_data, headers)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")


class UpdateMatViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обновить MATERIALIZE VIEW")
        self.setModal(True)
        self.setGeometry(300, 300, 400, 200)

        self.columns = []
        self.columns_name = ['view_name']
        self.employee_col_full = requests.get('http://localhost:3000/user_type/view').json()
        for col in self.employee_col_full:
            self.columns.append(col['view_name'])

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        view_group = QGroupBox("Обновление MATERIALIZE VIEW")
        view_layout = QVBoxLayout(view_group)

        self.view_combo = QComboBox()
        self.view_combo.addItems(self.columns)


        self.drop_btn = QPushButton("Обновить выбранный MATERIALIZE VIEW")
        self.drop_btn.clicked.connect(self.drop_view)

        view_layout.addWidget(QLabel("Выберите MATERIALIZE VIEW для обновления:"))
        view_layout.addWidget(self.view_combo)
        view_layout.addWidget(self.drop_btn)

        layout.addWidget(view_group)
        self.setLayout(layout)


    def drop_view(self):
        selected_view = self.view_combo.currentText()
        if not selected_view:
            QMessageBox.warning(self, "Ошибка", "Выберите MATERIALIZE VIEW для обновления")
            return

        try:
            query = f"REFRESH MATERIALIZE VIEW {selected_view}"
            json_string = '{"alter_string": "' + query + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/user_type', json=json_data)

            if r.status_code == 200:
                QMessageBox.information(self, "Успех", f"MATERIALIZE VIEW '{selected_view}' успешно обновлён!")
                makeLog(f"Обновлён VIEW: {selected_view}")
            else:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении MATERIALIZE VIEW: {r.text}")
                makeLog(f"Ошибка при обновлении VIEW: {r.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении MATERIALIZE VIEW: {str(e)}")
            makeLog(f"Ошибка при обновлении VIEW: {str(e)}")



class DropMatViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление MATERIALIZE VIEW")
        self.setModal(True)
        self.setGeometry(300, 300, 400, 200)

        self.columns = []
        self.columns_name = ['view_name']
        self.employee_col_full = requests.get('http://localhost:3000/user_type/view').json()
        for col in self.employee_col_full:
            self.columns.append(col['view_name'])

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        view_group = QGroupBox("Удаление MATERIALIZE VIEW")
        view_layout = QVBoxLayout(view_group)

        self.view_combo = QComboBox()
        self.view_combo.addItems(self.columns)


        self.drop_btn = QPushButton("Удалить выбранный MATERIALIZE VIEW")
        self.drop_btn.clicked.connect(self.drop_view)

        view_layout.addWidget(QLabel("Выберите MATERIALIZE VIEW для удаления:"))
        view_layout.addWidget(self.view_combo)
        view_layout.addWidget(self.drop_btn)

        layout.addWidget(view_group)
        self.setLayout(layout)


    def drop_view(self):
        selected_view = self.view_combo.currentText()
        if not selected_view:
            QMessageBox.warning(self, "Ошибка", "Выберите MATERIALIZE VIEW для удаления")
            return

        try:
            query = f"DROP MATERIALIZE VIEW {selected_view}"
            json_string = '{"alter_string": "' + query + '"}'
            json_data = json.loads(json_string)
            r = requests.post('http://localhost:3000/user_type', json=json_data)

            if r.status_code == 200:
                QMessageBox.information(self, "Успех", f"MATERIALIZE VIEW '{selected_view}' успешно удален!")
                makeLog(f"Удален VIEW: {selected_view}")
            else:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении MATERIALIZE VIEW: {r.text}")
                makeLog(f"Ошибка при удалении VIEW: {r.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении MATERIALIZE VIEW: {str(e)}")
            makeLog(f"Ошибка при удалении VIEW: {str(e)}")


class MatViewManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление MATERIALIZE VIEW")
        self.setModal(True)
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.create_button = QPushButton('Создать MATERIALIZE VIEW')
        self.create_button.clicked.connect(self.create_view)

        self.show_button = QPushButton('Просмотреть MATERIALIZE VIEW')
        self.show_button.clicked.connect(self.show_view)

        self.update_button = QPushButton('Обновить MATERIALIZE VIEW')
        self.update_button.clicked.connect(self.update_view)

        self.drop_button = QPushButton('Удалить MATERIALIZE VIEW')
        self.drop_button.clicked.connect(self.drop_view)

        self.close_button = QPushButton('Закрыть')
        self.close_button.clicked.connect(self.close)

        view_layout = QVBoxLayout()
        view_layout.addWidget(self.create_button)
        view_layout.addWidget(self.show_button)
        view_layout.addWidget(self.update_button)
        view_layout.addWidget(self.drop_button)
        view_layout.addWidget(self.close_button)
        view_layout.addStretch()

        view_box = QGroupBox("Управление представлениями (MATERIALIZE VIEW)")
        view_box.setLayout(view_layout)

        layout.addWidget(view_box)
        self.setLayout(layout)

    def create_view(self):
        dlg = CreateMatViewDialog(self)
        dlg.exec()

    def show_view(self):
        dlg = ShowMatViewDialog(self)
        dlg.exec()

    def update_view(self):
        dlg = UpdateMatViewDialog(self)
        dlg.exec()

    def drop_view(self):
        dlg = DropMatViewDialog(self)
        dlg.exec()



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IT Outsource DB')
        self.setGeometry(200, 200, 1000, 500)
        self.process = None

        self.conn_form = QFormLayout()  # макет для блока подключения
        # текстовые поля для блока подключения
        self.lineedit_host = QLineEdit("localhost")
        self.lineedit_port = QLineEdit("5436")
        self.lineedit_dbname = QLineEdit("outsourse")
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
        self.conn_box.setLayout(self.conn_form)  # установка макета в блок

        self.w_layout = QVBoxLayout()  # общий макет всего окна
        self.w_layout.addWidget(self.conn_box)  # добавление блока подключения в общий макет

        self.newdb_grid_buttons = QGridLayout()  # сетка-макет кнопок для работы с подключением и созданием бд
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
        self.w_layout.addLayout(self.newdb_grid_buttons)  # добавление сетки кнопок в общий макет

        self.button_viewdb = QPushButton('Управление VIEW')
        self.button_viewdb.clicked.connect(self.manageViews)
        self.button_viewdb.setDisabled(True)

        self.button_mat_viewdb = QPushButton('Управление MATERIALIZE VIEW')
        self.button_mat_viewdb.clicked.connect(self.manageMatViews)
        self.button_mat_viewdb.setDisabled(True)

        # В сетке curdb_grid_buttons добавьте новую кнопку:


        self.w_layout.addSpacing(30)  # пробел между кнопками создания таблицы и работы с таблицей

        self.button_adddata = QPushButton('Добавить данные')
        self.button_showdb = QPushButton('Вывести данные')
        self.button_alterdb = QPushButton('Изменить таблицу')
        self.button_udtdb = QPushButton('Пользовательские типы')
        self.button_adddata.clicked.connect(self.addData)
        self.button_showdb.clicked.connect(self.showDataBase)
        self.button_alterdb.clicked.connect(self.alterTables)
        self.button_udtdb.clicked.connect(self.userTypes)
        self.button_adddata.setDisabled(True)
        self.button_showdb.setDisabled(True)
        self.button_alterdb.setDisabled(True)
        self.button_udtdb.setDisabled(True)

        self.curdb_grid_buttons = QGridLayout()  # сетка-макет кнопок для работы с нынешней бд
        self.curdb_grid_buttons.addWidget(self.button_adddata, 0, 0)
        self.curdb_grid_buttons.addWidget(self.button_showdb, 0, 1)
        self.curdb_grid_buttons.addWidget(self.button_alterdb, 2, 0, 1, 2)
        self.curdb_grid_buttons.addWidget(self.button_udtdb, 3, 0, 1, 2)
        self.curdb_grid_buttons.addWidget(self.button_viewdb, 4, 0, 1, 2)
        self.curdb_grid_buttons.addWidget(self.button_mat_viewdb, 5, 0, 1, 2)
        self.w_layout.addLayout(self.curdb_grid_buttons)  # добавление сетки кнопок в общий макет



        self.w_layout.addStretch()  # объекты прилипают друг к другу, поэтому блок подключения не растягивается при расширении окна
        self.setLayout(self.w_layout)  # установка общего макета

    def manageViews(self):
        dlg = ViewManagementDialog(self)
        dlg.exec()

    def manageMatViews(self):
        dlg = MatViewManagementDialog(self)
        dlg.exec()

    def current_cfg(self) -> PgConfig:
        try:
            port = int(self.lineedit_port.text().strip())
        except ValueError:
            port = 5432
        return PgConfig(
            host=self.lineedit_host.text().strip() or "localhost",
            port=port,
            dbname=self.lineedit_dbname.text().strip() or "outsource",
            user=self.lineedit_user.text().strip() or "postgres",
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
        f.write(
            f'#Application \nPRODUCTION_TYPE=prod\nCRYPTOGRAPHY_SECRET_KEY="1234567890123456" \nPOSTGRES_HOST={cfg.host} \nPOSTGRES_PORT={cfg.port} \nPOSTGRES_USER={cfg.user} \nPOSTGRES_PASSWORD={cfg.password} \nPOSTGRES_DB={cfg.dbname}\nPGDATA_PATH="/var/lib/postgresql/data/pgdata"')
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
            self.button_udtdb.setDisabled(False)
            self.button_viewdb.setDisabled(False)
            self.button_mat_viewdb.setDisabled(False)
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
        self.button_udtdb.setDisabled(True)
        self.button_viewdb.setDisabled(True)
        self.button_mat_viewdb.setDisabled(True)
        makeLog("Соединение закрыто.")

    def reset_db(self):
        r = requests.delete('http://localhost:3000/drop')
        self.button_create.setDisabled(True)
        self.button_adddata.setDisabled(True)
        self.button_showdb.setDisabled(True)
        self.button_alterdb.setDisabled(True)

    def addData(self):
        dlg = AddDataWindow()
        dlg.exec()

    def showDataBase(self):
        dlg = DataViewerDialog()
        dlg.exec()

    def alterTables(self):
        dlg = AlterTableWindow()
        dlg.exec()

    def userTypes(self):
        dlg = UDTDialog()
        dlg.exec()


app = QApplication(sys.argv)
app.setStyleSheet(Path('styles.qss').read_text())
window = MainWindow()
window.show()
sys.exit(app.exec())