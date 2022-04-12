import sys
import random
import database.queries as db

from tinytag import TinyTag
from data_types.Queue import *
from data_types.Library import *
from data_types.Playlist import *
from MainWindow import Ui_MainWindow
from database.quotes import quotes


# noinspection PyArgumentList
class Applet(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(Applet, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.addFiles.triggered.connect(self.openFiles)
        self.randomQuote.pressed.connect(self.generateRandomQuote)

        # Construction
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist(self.player)
        self.player.setPlaylist(self.playlist)
        self.queue = Queue(self.playlist)
        self.playlistView.setModel(self.queue)
        self.playlists = Playlist()

        # Playback
        self.play.pressed.connect(lambda: self.updateStateOnResume())
        self.pause.pressed.connect(lambda: self.updateStateOnPause())
        self.shuffle.setChecked(False)
        self.shuffle.pressed.connect(self.updatePlaybackMode)
        self.durationSlider.valueChanged.connect(self.player.setPosition)
        self.player.durationChanged.connect(self.updateDuration)
        self.player.positionChanged.connect(self.updatePosition)

        # Playlist
        self.previous.pressed.connect(self.playlist.previous)
        self.next.pressed.connect(self.playlist.next)
        self.playlist.currentIndexChanged.connect(self.playlistChanged)
        self.playlistView.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.player.mediaStatusChanged.connect(self.updateMetaData)
        self.removePlaylist.pressed.connect(self.removePlaylistFromDB)
        self.addTrack.pressed.connect(self.addTrackToQueue)

        # Library
        self.library = Library()
        self.songListProxyModel = QSortFilterProxyModel()
        self.songListProxyModel.setSourceModel(self.library)
        self.songs.setModel(self.songListProxyModel)
        self.songs.setSortingEnabled(True)
        self.removeTrack.pressed.connect(self.removeTracksFromDB)

        # Queue
        self.moveTrackDown.pressed.connect(lambda: self.moveTrackInQueue("down"))
        self.moveTrackUp.pressed.connect(lambda: self.moveTrackInQueue("up"))
        self.removeFromQueue.pressed.connect(lambda: self.moveTrackInQueue("trash"))
        self.insertPlaylist.pressed.connect(self.queuePlaylist)
        self.savePlayListButton.pressed.connect(self.saveQueueAsPlaylist)
        self.clearPlayListButton.pressed.connect(self.clearQueue)

        self.setAcceptDrops(True)
        self.songs.resizeColumnsToContents()
        self.show()

    # Playback methods.
    def updatePlaybackMode(self):
        if not self.shuffle.isChecked():
            self.playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Random)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Sequential)

    def updateStateOnPause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.pause.setText("||")
            self.play.setText("Resume")

    def updateStateOnResume(self):
        if self.player.state() == QMediaPlayer.PausedState or self.player.state() == QMediaPlayer.StoppedState:
            self.player.play()
            self.pause.setText("Pause")
            self.play.setText("♫")

    def updateDuration(self, duration):
        self.durationSlider.blockSignals(True)
        self.durationSlider.setMaximum(duration)
        self.durationSlider.setValue(0)
        self.durationSlider.blockSignals(False)

    def updatePosition(self, position):
        self.durationSlider.blockSignals(True)
        self.durationSlider.setValue(position)
        self.durationSlider.blockSignals(False)

    def generateRandomQuote(self):
        self.randomQuote.setText(random.choice(quotes))

    # Queue methods.
    def addTrackToQueue(self):
        for index in sorted(self.songs.selectionModel().selectedRows()):
            index = self.songListProxyModel.mapToSource(index)

            # Indices: ["Title", "Artist", "Year", "Album", "Genre", "Address"]
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(
                self.library.data(self.library.index(index.row(), 5)))))

        self.queue.layoutChanged.emit()

    def moveTrackInQueue(self, direction):
        for index in sorted(self.playlistView.selectionModel().selectedRows()):
            i = index.row()
            if direction == "up" and i >= 1:
                self.playlist.setCurrentIndex(i - 1)
                self.playlist.moveMedia(i, i - 1)
            elif direction == "down" and i < self.playlist.mediaCount():
                self.playlist.setCurrentIndex(i + 1)
                self.playlist.moveMedia(i, i + 1)
            elif direction == "trash" and i >= 0:
                self.playlist.removeMedia(i)
        self.queue.layoutChanged.emit()

    def saveQueueAsPlaylist(self):
        text, ok = QInputDialog.getText(None, "Creating new playlist", "Enter playlist name", QLineEdit.Normal)
        if ok:
            songs = []
            for index in range(self.playlist.mediaCount()):

                # Remove prefix \
                path = self.playlist.media(index).canonicalUrl().path()[1:]
                identifier = db.getTrackByPath(path)[0][0]
                songs.append(identifier)
            db.addPlaylist(text, songs)

        self.playlists.requestUpdate()

    def queuePlaylist(self):
        for index in sorted(self.playlistList.selectionModel().selectedRows()):
            playlist = db.getPlaylist(self.playlists.getID(index))
            for track in playlist:
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(track[1])))

        self.queue.layoutChanged.emit()

    def clearQueue(self):
        self.playlist.clear()
        self.queue.layoutChanged.emit()

    # Event handling.
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.player.state() == QMediaPlayer.State.PlayingState:
                self.updateStateOnPause()
            else:
                self.updateStateOnResume()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for URL in event.mimeData().urls():
            self.addFileToDB(URL.path())
            self.playlist.addMedia(QMediaContent(URL))

        self.queue.layoutChanged.emit()

    # Database methods.
    def addFileToDB(self, address):

        if len(db.getTrackByPath(address)) == 0:
            metadata = TinyTag.get(address)
            db.addTrack(metadata.title, metadata.artist, metadata.album, metadata.genre, metadata.year, address)
            self.library.requestUpdate()

    def removeTracksFromDB(self):
        for index in sorted(self.songs.selectionModel().selectedRows(0)):
            index = self.songListProxyModel.mapToSource(index)
            db.deleteTracksByID(self.library.getID(index))
        self.library.requestUpdate()

    def removePlaylistFromDB(self):
        for index in sorted(self.playlistList.selectionModel().selectedRows()):
            db.deletePlaylist(self.playlists.getID(index))
        self.playlists.requestUpdate()

    def openFiles(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilters(["MP3 (*.mp3)", "FLAC (*.flac)", "WAV (*.wav)"])
        files = []

        if dialog.exec_():
            files = dialog.selectedFiles()

        for f in files:
            print("Opening file... " + str(f))
            self.addFileToDB(f)
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(f)))

        self.songs.resizeColumnsToContents()
        self.queue.layoutChanged.emit()

    # Playlist methods.
    def updateMetaData(self, status):
        # QMediaPlayer::UnknownMedia	0	The status of the media cannot be determined.
        # QMediaPlayer::NoMedia	        1	There is no current media. The player is in the StoppedState.
        # QMediaPlayer::LoadingMedia	2	The current media is being loaded. The player may be in any state.
        # QMediaPlayer::LoadedMedia	    3	The current media has been loaded. The player is in the StoppedState.
        # QMediaPlayer::StalledMedia	4	Media has stalled due to insufficient buffering or some other interruption.
        #                                   The player is in PlayingState or PausedState.
        # QMediaPlayer::BufferingMedia	5	Has enough data buffered for playback to continue for the immediate future.
        #                                   The player is in PlayingState or PausedState.
        # QMediaPlayer::BufferedMedia	6	Fully buffered current media. The player is in PlayingState or PausedState.
        # QMediaPlayer::EndOfMedia	    7	Playback has reached the end. The player is in the StoppedState.
        # QMediaPlayer::InvalidMedia	8	The current media cannot be played. The player is in the StoppedState.

        print("Status enumeration: " + str(status))
        print("0: UnknownMedia - 1: NoMedia - 2: LoadingMedia - 3: LoadedMedia - 4: StalledMedia")
        print("5: BufferingMedia - 6: BufferedMedia - 7: EndOfMedia - 8: InvalidMedia")
        if status == QMediaPlayer.LoadedMedia or status == QMediaPlayer.LoadingMedia \
                or status == QMediaPlayer.BufferedMedia or status == QMediaPlayer.BufferingMedia:
            self.trackInformation.setText(self.player.metaData(QMediaMetaData.Title))

        if self.player.state() == QMediaPlayer.PausedState or self.player.state() == QMediaPlayer.StoppedState:
            i = self.playlist.mediaCount() - len(self.songs.selectionModel().selectedRows())
            self.playlist.setCurrentIndex(i)
            self.updateStateOnResume()

        self.generateRandomQuote()

    def playlistChanged(self, index):
        if index >= 0:
            i = self.queue.index(index)
            self.playlistView.setCurrentIndex(i)

    def selectionChanged(self, index):
        i = index.indexes()[0].row()
        self.playlist.setCurrentIndex(i)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Quriel: An experimental music player!")

    window = Applet()
    app.exec_()
