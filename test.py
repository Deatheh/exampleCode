import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QComboBox, QPushButton, QLabel)
from PySide6.QtCore import Qt


class MultiComboBoxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComboBox с множественным выбором")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.selected_label = QLabel("Выбрано: ничего")
        layout.addWidget(self.selected_label)

        # Создаем ComboBox
        self.combo_box = QComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setReadOnly(True)
        self.combo_box.lineEdit().setAlignment(Qt.AlignCenter)

        items = ["Элемент 1", "Элемент 2", "Элемент 3", "Элемент 4"]
        self.combo_box.addItems(items)

        # Модель для хранения выбранных элементов
        self.selected_items = set()

        # Кнопка для выбора
        self.select_button = QPushButton("Выбрать элементы")
        self.select_button.clicked.connect(self.show_selection_dialog)

        layout.addWidget(self.combo_box)
        layout.addWidget(self.select_button)

    def show_selection_dialog(self):
        # В реальном приложении здесь можно создать диалоговое окно
        # с множественным выбором
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QListWidget

        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите элементы")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.MultiSelection)
        list_widget.addItems([self.combo_box.itemText(i) for i in range(self.combo_box.count())])

        # Выделяем уже выбранные элементы
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() in self.selected_items:
                item.setSelected(True)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(list_widget)
        layout.addWidget(button_box)

        if dialog.exec():
            selected_items = [item.text() for item in list_widget.selectedItems()]
            self.selected_items = set(selected_items)
            self.update_display()

    def update_display(self):
        if self.selected_items:
            selected_text = ", ".join(self.selected_items)
            self.combo_box.lineEdit().setText(selected_text)
            self.selected_label.setText(f"Выбрано: {selected_text}")
        else:
            self.combo_box.lineEdit().setText("")
            self.selected_label.setText("Выбрано: ничего")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiComboBoxWindow()
    window.show()
    sys.exit(app.exec())