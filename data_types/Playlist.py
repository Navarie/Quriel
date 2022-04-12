from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import database.queries as db


class Playlist(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(Playlist, self).__init__(*args, *kwargs)
        self._data = db.getPlaylists()

    def getID(self, index):
        return self._data[index.row()][0]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][1]

    def rowCount(self, parent=QModelIndex):
        return len(self._data)

    def requestUpdate(self):
        self.layoutAboutToBeChanged.emit()
        self._data = db.getPlaylists()
        self.layoutChanged.emit()
