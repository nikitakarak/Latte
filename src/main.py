import sqlite3
from pathlib import PurePath
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QDesktopWidget
)
from ui.MainWindow import Ui_MainWindow
from add_edit_coffee_form import *


_DB_FILENAME = r'./data/coffee.sqlite'


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._db_filename = str(PurePath(__file__).parent.joinpath(_DB_FILENAME))
        self._db_connection = None

        self.add_btn.clicked.connect(self.add_coffee_handler)
        self.edit_btn.clicked.connect(self.edit_coffee_handler)
        self.table.currentItemChanged.connect(self.table_item_changed_handler)
        self.table.itemDoubleClicked.connect(self.table_item_dblclick_handler)

        self.statusbar.showMessage(self._db_filename)
        self.db_update_table()

    def center_window(self):
        qr = self.frameGeometry()
        qr.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(qr.topLeft())

    def add_coffee_handler(self):
        self.show_coffee_form(-1)

    def edit_coffee_handler(self):
        item = self.table.currentItem()
        if item:
            self.show_coffee_form(item.data(QtCore.Qt.UserRole))

    def show_coffee_form(self, coffee_id):
        form = AddEditCoffeeForm(self, self._db_connection, coffee_id)
        if form.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.db_update_table()
            if coffee_id >= 0:
                self.table_set_current(coffee_id)

    def table_item_changed_handler(self, current, previous):
        self.edit_btn.setEnabled(not(current is None))

    def table_item_dblclick_handler(self, item):
        if item:
            self.show_coffee_form(item.data(QtCore.Qt.UserRole))

    def db_get_connection(self):
        if not self._db_connection:
            self._db_connection = sqlite3.connect(self._db_filename)
        return self._db_connection

    def table_set_current(self, coffee_id):
        model = self.table.model()
        matches = model.match(model.index(0,0), QtCore.Qt.UserRole, coffee_id)
        if matches:
            index = matches[0]
            self.table.setCurrentItem(self.table.item(index.row(), index.column()))

    def db_update_table(self):
        coffees = tuple()
        headers = tuple()
        
        db = self.db_get_connection()
        if db:
            cur = db.cursor()
            coffees = cur.execute(
                r'''
                SELECT
                    Coffee.Id as "Идентификатор",
                    Coffee.GradeName as "Название",
                    Roast.Name as "Обжарка",
                    Type.Name as "Тип",
                    Coffee.Price as "Цена, руб.",
                    Coffee.Packing as "Вес, гр",
                    Coffee.Description as "Описание"
                FROM Coffee
                INNER JOIN Roast ON Roast.Id = Coffee.RoastId
                INNER JOIN Type ON Type.Id = Coffee.TypeId
                ORDER BY Coffee.GradeName
                ''').fetchall()

            headers = tuple(desc[0] for desc in cur.description)

        self.table.setColumnCount(len(headers) - 1)
        self.table.setHorizontalHeaderLabels(headers[1:])
        self.table.setRowCount(0)

        if coffees:
            for row, coffee in enumerate(coffees):
                self.table.setRowCount(self.table.rowCount() + 1)
                for col, coffee_property in enumerate(coffee[1:]):
                    item = QtWidgets.QTableWidgetItem(str(coffee_property))
                    item.setData(QtCore.Qt.UserRole, coffee[0])
                    self.table.setItem(row, col, item)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.center_window()
    win.show()
    sys.exit(app.exec())
