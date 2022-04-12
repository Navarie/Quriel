from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


class Queue(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(Queue, self).__init__(*args, *kwargs)
        self.playlist = playlist

    def rowCount(self, parent=QModelIndex):
        return self.playlist.mediaCount()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            queue = self.playlist.media(index.row())
            return queue.canonicalUrl().fileName()
