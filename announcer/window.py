import os
import random
import logging

from .constants import SOUND_PACKS
from .events import Event

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, QUrl, Qt, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


logger = logging.getLogger(__name__)


class EventPlayer(QObject):
    # finished = pyqtSignal()
    progress = pyqtSignal(str)

    def poll_league(self):
        self.lol_events = Event()
        while True:
            events_in_string = ";".join(self.lol_events.event_polling())
            self.progress.emit(events_in_string)
        # self.finished.emit()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Peks Announcer")
        self.setFixedSize(300, 120)

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
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QGridLayout(self.central_widget)
        self.layout.addWidget(self.volume_level_label, 0, 1, 1, 1)
        self.layout.addWidget(self.volume_slider, 1, 0, 1, 3)
        self.layout.addWidget(self.mute_button, 0, 0, 1, 1)
        self.layout.addWidget(self.test_volume_button, 0, 2, 1, 1)
        self.layout.addWidget(self.packlabel, 2, 0, 1, 1)
        self.layout.addWidget(self.sound_pack, 2, 1, 1, 2)

        self.media_player = QMediaPlayer()

        self.event_player = EventPlayer()
        self.event_player_thread = QThread()
        self.event_player.moveToThread(self.event_player_thread)

        self.event_player_thread.started.connect(self.event_player.poll_league)
        # self.event_player.finished.connect(self.thread.quit)
        # self.event_player.finished.connect(self.worker.deleteLater)
        self.event_player_thread.finished.connect(self.event_player_thread.deleteLater)
        self.event_player.progress.connect(self.play_events_sound)

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
        self.play_event_sound(event)

    def play_events_sound(self, events: str):
        logger.debug(events)
        for event in events.split(";"):
            if not event:
                break
            self.play_event_sound(event)

    def play_event_sound(self, event: str):
        event_sounds = os.path.join(SOUND_PACKS[self.sound_pack.currentText()], event)
        try:
            sound = random.choice(os.listdir(event_sounds))
        except IndexError as e:
            logger.exception(e)
            return
        sound_path = os.path.join(event_sounds, sound)
        logger.debug(sound_path)
        url = QUrl.fromLocalFile(sound_path)
        content = QMediaContent(url)
        self.media_player.setMedia(content)
        self.media_player.play()
