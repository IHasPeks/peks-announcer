import os
import random
import logging
import time
import typing

from .constants import SOUND_PACKS, SOUNDS_DIR_LOCAL
from .events import Event

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, QUrl, Qt, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


logger = logging.getLogger(__name__)


class FIFOMediaPlayer(QMediaPlayer, QObject):
    def append_events(self, events: str):
        if not events:
            return
        self.sound_pack = events.split(";")[0]
        self.events.extend(events.split(";")[1:])
        while self.events:
            while self.position() != self.duration():
                continue

            event_sounds = os.path.join(
                SOUND_PACKS[self.sound_pack],
                self.events.pop(0),
            )

            try:
                sound = random.choice(os.listdir(event_sounds))
            except IndexError as e:
                logger.exception(e)
                return
            except FileNotFoundError as e:
                logger.exception(e)
                return
            sound_path = os.path.join(event_sounds, sound)
            url = QUrl.fromLocalFile(sound_path)
            content = QMediaContent(url)
            self.setMedia(content)
            self.play()

            # TODO: Fix race condition
            time.sleep(0.1)

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
        self.setWindowTitle("Peks Announcer")
        self.setFixedSize(300, 120)

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
        self.sound_pack = QtWidgets.QComboBox()
        self.sound_pack.addItems(SOUND_PACKS)
        self.sound_link = QtWidgets.QLabel(
            "<a href='https://github.com/IHasPeks/peks-announcer#create-sound-packs'>More Soundpacks</a>"
        )
        self.sound_link.setOpenExternalLinks(True)
        self.open_pack_button = QtWidgets.QPushButton("Open Packs")
        self.open_pack_button.clicked.connect(self.open_appdata)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QGridLayout(self.central_widget)
        self.layout.addWidget(self.volume_level_label, 0, 1, 1, 1)
        self.layout.addWidget(self.volume_slider, 1, 0, 1, 3)
        self.layout.addWidget(self.mute_button, 0, 0, 1, 1)
        self.layout.addWidget(self.test_volume_button, 0, 2, 1, 1)
        self.layout.addWidget(self.packlabel, 2, 0, 1, 1)
        self.layout.addWidget(self.sound_pack, 2, 1, 1, 2)
        self.layout.addWidget(self.sound_link, 3, 0, 1, 2)
        self.layout.addWidget(self.open_pack_button, 3, 2, 1, 1)

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

        self.mute_button.clicked.connect(self.mute)
        self.test_volume_button.clicked.connect(self.play_random_sound)

    def mute(self):
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

    def update_volume(self):
        self.media_player.setVolume(self.volume_slider.value())

    def update_volume_level(self):
        volume_level = self.volume_slider.value()
        self.volume_level_label.setText(f"Volume: {volume_level}%")

    def play_random_sound(self):
        sound_pack_dir = SOUND_PACKS[self.sound_pack.currentText()]
        events = os.listdir(sound_pack_dir)
        try:
            event = random.choice(events)
        except IndexError as e:
            logger.exception(e)
            return
        self.send_events(event)

    def send_events(self, events: str):
        if not events:
            return
        events = self.sound_pack.currentText() + ";" + events
        self.events.emit(events)

    def open_appdata(self):
        if os.name == "nt":
            os.startfile(SOUNDS_DIR_LOCAL)
        else:
            logger.warning("Your system if not compatible")
