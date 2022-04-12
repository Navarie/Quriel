from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import database.queries as db


class Library(QAbstractTableModel):

    libraryColumns = ["Title", "Artist", "Album", "Genre", "Year", "Address"]

    def __init__(self, *args, **kwargs):
        super(Library, self).__init__(*args, *kwargs)
        self._data = db.getTracks()

    def getID(self, index):
        return self._data[index.row()][0]

    def rowCount(self, parent=QModelIndex):
        return len(self._data)

    def columnCount(self, parent=QModelIndex):
        if len(self._data) >= 1:
            return len(self._data[0]) - 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()

            return self._data[row][col + 1]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.libraryColumns[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def requestUpdate(self):
        self.layoutAboutToBeChanged.emit()
        self._data = db.getTracks()
        self.layoutChanged.emit()
