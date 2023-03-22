import sys
import os
import subprocess
import random
import logging
import time

from .constants import SOUND_PACKS, SOUNDS_DIR_LOCAL
from .events import Event

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, QUrl, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

logger = logging.getLogger(__name__)

class FIFOMediaPlayer(QMediaPlayer, QObject):
    error_occurred = pyqtSignal(str)
    def append_events(self, events: str):
        if not events:
            return
        self.sound_pack = events.split(";")[0]
        self.events.extend(events.split(";")[1:])
        logger.debug(f"Events before loop: {self.events}")
        while self.events:
            if self.position() != self.duration():
                continue
            event_sounds = os.path.join(
                SOUND_PACKS[self.sound_pack]["path"],
                self.events.pop(0),
            )
            try:
                sound = random.choice(os.listdir(event_sounds))
            except IndexError as e:
                logger.exception(e)
                self.error_occurred.emit("No sound files found in the specified directory. Skipping this event.")
                continue
            except FileNotFoundError as e:
                logger.exception(e)
                self.error_occurred.emit("The specified directory was not found.")
                return
            sound_path = os.path.join(event_sounds, sound)
            url = QUrl.fromLocalFile(sound_path)
            content = QMediaContent(url)
            self.setMedia(content)
            logger.debug(f"Before play: {url}")
            self.play()
            logger.debug(f"After play: {url}")

            # TODO: Fix race condition
            time.sleep(0.25)


    def play_event_sound(self):
        self.events = []
        self.setVolume(50)

class EventPlayer(QObject):
    # finished = pyqtSignal()
    events = pyqtSignal(str)

    def poll_league(self):
        self.lol_events = Event()
        while True:
            events_in_string = ";".join(self.lol_events.event_polling())
            self.events.emit(events_in_string)
        # self.finished.emit()

class MainWindow(QtWidgets.QMainWindow):
    events = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedSize(350, 175)
        self.t = 0
        self.volume_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.mute_button = QtWidgets.QPushButton("Mute")
        self.is_muted = False
        self.previous_volume = self.volume_slider.value()
        self.test_volume_button = QtWidgets.QPushButton("Test sound")
        self.volume_level_label = QtWidgets.QLabel("Volume: 50%")
        self.volume_level_label.setAlignment(Qt.AlignCenter)
        self.packlabel = QtWidgets.QLabel("Sound Pack:")
        self.pack_info = QtWidgets.QLabel("")
        self.pack_info.setWordWrap(True)
        self.pack_info.setAlignment(Qt.AlignRight)
        self.sound_pack = QtWidgets.QComboBox()
        self.sound_pack.addItems(list(SOUND_PACKS.keys()))
        self.sound_link = QtWidgets.QLabel(
            "<a href='https://github.com/IHasPeks/peks-announcer#create-sound-packs'>More Soundpacks</a>"
        )
        self.sound_link.setOpenExternalLinks(True)
        self.open_pack_button = QtWidgets.QPushButton("Open Packs")
        self.open_pack_button.clicked.connect(self.open_local_sounds_dir)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.update_description()

        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.addWidget(self.volume_level_label, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.volume_slider, 1, 0, 1, 3)
        self.grid_layout.addWidget(self.mute_button, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.test_volume_button, 0, 2, 1, 1)
        self.grid_layout.addWidget(self.packlabel, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.sound_pack, 2, 1, 1, 2)
        self.grid_layout.addWidget(self.pack_info, 3, 1, 1, 2)
        self.grid_layout.addWidget(self.sound_link, 4, 0, 1, 2)
        self.grid_layout.addWidget(self.open_pack_button, 4, 2, 1, 1)

        # Media Player Thread
        self.media_player = FIFOMediaPlayer()
        self.media_player_thread = QThread()
        self.media_player.moveToThread(self.media_player_thread)

        self.media_player_thread.started.connect(self.media_player.play_event_sound)
        self.media_player_thread.finished.connect(self.media_player_thread.quit)
        self.media_player_thread.finished.connect(self.media_player_thread.deleteLater)
        self.events.connect(self.media_player.append_events)
        # self.media_player.setVolume(50)

        # Event Polling Thread
        self.event_player = EventPlayer()
        self.event_player_thread = QThread()
        self.event_player.moveToThread(self.event_player_thread)

        self.event_player_thread.started.connect(self.event_player.poll_league)
        self.event_player_thread.finished.connect(self.event_player_thread.quit)
        self.event_player_thread.finished.connect(self.event_player_thread.deleteLater)
        self.event_player.events.connect(self.send_events)

        self.media_player_thread.start()
        self.event_player_thread.start()

    def setup_connections(self):
        self.volume_slider.valueChanged.connect(self.update_volume)
        self.volume_slider.valueChanged.connect(self.update_volume_level)
        self.mute_button.clicked.connect(self.toggle_mute)
        self.test_volume_button.clicked.connect(self.play_random_sound)
        self.sound_pack.currentIndexChanged.connect(self.update_description)
        self.media_player.error_occurred.connect(self.show_error_message)

    @pyqtSlot()
    def toggle_mute(self):
        if self.is_muted:
            self.media_player.setVolume(self.previous_volume)
            self.volume_slider.setValue(self.previous_volume)
            self.is_muted = False
            self.mute_button.setText("Mute")
        else:
            self.previous_volume = self.media_player.volume()
            self.media_player.setVolume(0)
            self.volume_slider.setValue(0)
            self.is_muted = True
            self.mute_button.setText("Unmute")

    @pyqtSlot()
    def update_volume(self):
        self.media_player.setVolume(self.volume_slider.value())

    @pyqtSlot()
    def update_volume_level(self):
        volume_level = self.volume_slider.value()
        self.volume_level_label.setText(f"Volume: {volume_level}%")

    @pyqtSlot()
    def play_random_sound(self):
        sound_pack_dir = SOUND_PACKS[self.sound_pack.currentText()]["path"]
        events = os.listdir(sound_pack_dir)
        events = list(filter(lambda x: os.path.isdir(x), events))
        try:
            event = random.choice(events)
        except IndexError as e:
            logger.exception(e)
            return
        self.send_events(event)

    @pyqtSlot(str)
    def send_events(self, events: str):
        if not events:
            return
        events = self.sound_pack.currentText() + ";" + events
        logger.info
        (f"Random event: {events} sent")
        self.events.emit(events)

    @pyqtSlot()
    def update_description(self):
        pack_key = self.sound_pack.currentText()
        pack_description = SOUND_PACKS[pack_key]['description']
        self.pack_info.setText(pack_description)

    @pyqtSlot()
    def open_local_sounds_dir(self):
        if sys.platform == "win32":
            os.startfile(SOUNDS_DIR_LOCAL)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, SOUNDS_DIR_LOCAL])

    @pyqtSlot(str)
    def show_error_message(self, message: str):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("An error occurred:")
        error_dialog.setInformativeText(message)
        error_dialog.exec_()
