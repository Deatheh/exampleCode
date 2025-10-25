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
    QLineEdit, QGridLayout, QTabWidget, QComboBox, QScrollArea, QDialog, QSplitter, QTextEdit, QHeaderView, QLabel, QCheckBox, QDateEdit, QSpinBox, \
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

        #-------------------------

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

        #----------------------

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

        #----------------------

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
        type = self. projectDelCol.currentText()
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

        #-------------------
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


        #-------------------------------

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
        colName =  self.colName.text().strip()
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
        colName =  self.taskColName.text().strip()
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
        colName =  self.projectColName.text().strip()
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
        self.employee_layout.addWidget(self.add_employee_button )
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


class DataViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр данных - Employee Database")
        self.setModal(True)
        self.setGeometry(100, 100, 1400, 900)
        self.column_widgets = {}
        self.join_widgets = []
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

        splitter.setSizes([500, 900])
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
        self.where_operator.addItems(["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "~", "~*", "!~", "!~*"])
        self.where_value = QLineEdit()
        self.where_value.setPlaceholderText("Значение для фильтра")
        where_input_layout.addWidget(QLabel("Поле:"))
        where_input_layout.addWidget(self.where_field)
        where_input_layout.addWidget(QLabel("Оператор:"))
        where_input_layout.addWidget(self.where_operator)
        where_input_layout.addWidget(QLabel("Значение:"))
        where_input_layout.addWidget(self.where_value)
        where_layout.addLayout(where_input_layout)

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
        group_input_layout.addWidget(QLabel("Группировать по:"))
        group_input_layout.addWidget(self.group_field)
        group_input_layout.addWidget(QLabel("Агрегатная функция:"))
        group_input_layout.addWidget(self.aggregate_function)
        group_layout.addLayout(group_input_layout)

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

        layout.addWidget(table_group)
        layout.addWidget(join_group)
        layout.addWidget(select_group)
        layout.addWidget(where_group)
        layout.addWidget(order_group)
        layout.addWidget(group_group)
        layout.addWidget(having_group)
        layout.addWidget(self.execute_btn)
        layout.addWidget(self.sql_preview)

        return widget

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

    def build_sql_query(self):
        # SELECT
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            selected_columns = ["*"]

        select_clause = "SELECT " + ", ".join(selected_columns)

        from_clause = f"FROM {self.main_table.currentText()}"

        join_clauses = self.get_join_expressions()

        where_clause = ""
        where_value = self.where_value.text().strip()
        if where_value:
            field = self.where_field.currentText()
            operator = self.where_operator.currentText()
            where_clause = f"WHERE {field} {operator} '{where_value}'"
        group_clause = ""
        group_field = self.group_field.currentText()
        aggregate = self.aggregate_function.currentText()

        if group_field:
            group_clause = f"GROUP BY {group_field}"
            if aggregate:
                # Для агрегатных функций используем обычные имена столбцов
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

        query_parts = [select_clause, from_clause] + join_clauses + [where_clause, group_clause, having_clause,
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


            processed_data = []
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
                    processed_data.append(processed_row)

            headers = list(self.json_data[0].keys())

            self.model.update_data(processed_data, headers)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {str(e)}")



'''
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
'''

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
        self.button_adddata.clicked.connect(self.addData)
        self.button_showdb.clicked.connect(self.showDataBase)
        self.button_alterdb.clicked.connect(self.alterTables)
        self.button_adddata.setDisabled(True)
        self.button_showdb.setDisabled(True)
        self.button_alterdb.setDisabled(True)

        self.curdb_grid_buttons = QGridLayout() # сетка-макет кнопок для работы с нынешней бд
        self.curdb_grid_buttons.addWidget(self.button_adddata, 0, 0)
        self.curdb_grid_buttons.addWidget(self.button_showdb, 0, 1)
        self.curdb_grid_buttons.addWidget(self.button_alterdb, 2, 0, 1, 2)
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


app = QApplication(sys.argv)
app.setStyleSheet(Path('styles.qss').read_text())
window = MainWindow()
window.show()
sys.exit(app.exec())