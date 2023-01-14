import sys
import logging
import logging.config
from .window import MainWindow
from .constants import LOGGING_DICT, SOUND_PACKS
from PyQt5 import QtWidgets

logging.config.dictConfig(LOGGING_DICT)
logger = logging.getLogger(__name__)


def main():
    logger.info(SOUND_PACKS)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setup_connections()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
