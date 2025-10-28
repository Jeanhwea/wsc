import sys

from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)

_LAST_OPEN_DIR = None

_CONFIG_TEMPLATE = {
    "LevelData": [
        {"id": 1, "levle": "1-1", "titleImage": "TitleBg1"},
        {"id": 2, "levle": "2-1", "titleImage": "TitleBg2"},
        {"id": 3, "levle": "3-1", "titleImage": "TitleBg3"},
    ],
    "LevelLength": 3,
    "ResultJumpType": "a",
    "ResultJumpNumber": 2,
    "ResultJumpImageURL": "WinBg",
    "DownButtomInfo": {
        "imageUrl": "DownButtomBg",
        "scale": 1,
        "aniTime": 1,
        "delayTime": 1,
        "aniScale": [1, 1.3],
    },
    "IsOpenTutorial": True,
}


class JxFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_last_open_dir():
        if _LAST_OPEN_DIR:
            return _LAST_OPEN_DIR
        return os.getcwd()

    @staticmethod
    def _set_last_open_dir(path):
        _LAST_OPEN_DIR = path

    @staticmethod
    def open_single_file(caption=None, filter="All Files (*.*)"):
        if caption is None:
            caption = t(TextKey.DLOG_FILE_SINGLE_FILE)

        directory = JxFileDialog._get_last_open_dir()
        file_path, _ = JxFileDialog.getOpenFileName(None, caption, directory, filter)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(os.path.dirname(file_path))

        return file_path

    @staticmethod
    def open_single_dir(caption=None, init_dir=None):
        if caption is None:
            caption = t(TextKey.DLOG_FILE_SINGLE_DIR)

        directory = init_dir or JxFileDialog._get_last_open_dir()
        file_path = JxFileDialog.getExistingDirectory(None, caption, directory)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(file_path)

        return file_path

    @staticmethod
    def save_single_file(caption=None, filter="All Files (*.*)", default_filename=None):
        if caption is None:
            caption = t(TextKey.DLOG_FILE_SAVE_FILE)

        directory = JxFileDialog._get_last_open_dir()
        if default_filename is not None:
            directory = os.path.join(directory, default_filename)

        file_path, _ = JxFileDialog.getSaveFileName(None, caption, directory, filter)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(os.path.dirname(file_path))

        return file_path


class FileLocationEdit(QWidget):
    _layout: QHBoxLayout

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._desc = kwargs.get("desc", "???")
        self._layout = QHBoxLayout(self)
        self._initUI()

    def _initUI(self):
        self._layout.addWidget(QLabel(self._desc))

        btn_open_dir = QPushButton(self, "选择文件")
        self._layout.addWidget(btn_open_dir)

        btn_open_cls = QPushButton(self, "清空文件")
        self._layout.addWidget(btn_open_cls)

        edit_dir = QLineEdit(self)
        edit_dir.setReadOnly(True)
        self._layout.addWidget(edit_dir)


class WaterSortConfigWidget(QWidget):
    _layout: QHBoxLayout

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = QHBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("水排序工具")
        self.setGeometry(300, 300, 300, 100)

        self.create_group_01()

    def create_group_01(self):
        group = QGroupBox("标题图片")
        layout = QVBoxLayout(group)

        edit01 = WaterSortConfigWidget(self)
        layout.addWidget(edit01)

        return group


class WaterSortConfigApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.wsc = WaterSortConfigWidget()
        self.wsc.show()
        sys.exit(self.exec())
