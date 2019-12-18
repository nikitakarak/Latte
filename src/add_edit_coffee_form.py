import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QDesktopWidget
)
from ui.AddEditCoffeeForm import Ui_EditCoffeeForm


class AddEditCoffeeForm(QtWidgets.QDialog, Ui_EditCoffeeForm):
    def __init__(self, parent, db_connection, coffee_id):
        super().__init__(
            parent,
            QtCore.Qt.WindowSystemMenuHint | 
            QtCore.Qt.WindowTitleHint | 
            QtCore.Qt.WindowCloseButtonHint
        )
        self.setupUi(self)

        self._coffee_id = coffee_id
        self._db = db_connection

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.buttonBox.accepted.connect(self._save_handler)

        self._load_rosts_from_db()
        self._load_types_from_db()

        if self._coffee_id >= 0:
            self.setWindowTitle(r'Редактирование записи')
            self._load_coffee_from_db()
        else:
            self.setWindowTitle(r'Добавление новой записи')

    def _load_rosts_from_db(self):
        if self._db is None: return

        roasts = self._db.cursor().execute(
            r'SELECT Id, Name FROM Roast').fetchall()

        self.roast_type_cb.clear()
        for roast_id, roast_name in roasts:
            self.roast_type_cb.addItem(roast_name, roast_id)

    def _load_types_from_db(self):
        if self._db is None: return

        types = self._db.cursor().execute(
            r'SELECT Id, Name FROM Type').fetchall()

        self.type_cb.clear()
        for type_id, type_name in types:
            self.type_cb.addItem(type_name, type_id)

    def _load_coffee_from_db(self):
        if self._db is None: return

        if self._coffee_id >= 0:
            cur = self._db.cursor()
            coffee = cur.execute(
                r'''
                SELECT
                    GradeName, RoastId, TypeId, Price, Packing, Description
                FROM Coffee
                WHERE Id = ?
                ''', (self._coffee_id, )
            ).fetchone()

            if coffee:
                self.name_edit.setText(coffee[0])
                self.roast_type_cb.setCurrentIndex(self.roast_type_cb.findData(coffee[1]))
                self.type_cb.setCurrentIndex(self.type_cb.findData(coffee[2]))
                self.price_dsb.setValue(coffee[3])
                self.packing_sb.setValue(coffee[4])
                self.description_edit.setPlainText(coffee[5])

    def _save_coffee_to_db(self):
        '''Сохранение полей формы в базу данных'''
        sql = ''
        if self._coffee_id >= 0:
            sql = f'''
            UPDATE Coffee
            SET GradeName = ?, RoastId = ?, TypeId = ?, Price = ?, Packing = ?, Description = ?
            WHERE id = {self._coffee_id}'''
        else:
            sql = r'''
            INSERT INTO
               Coffee(GradeName, RoastId, TypeId, Price, Packing, Description)
            VALUES(?, ?, ?, ?, ?, ?)'''

        self._db.cursor().execute(sql, (
            self.name_edit.text(),
            self.roast_type_cb.currentData(),
            self.type_cb.currentData(),
            self.price_dsb.value(),
            self.packing_sb.value(),
            self.description_edit.toPlainText()
        ))
        self._db.commit()

    def _save_handler(self):
        self._save_coffee_to_db()
