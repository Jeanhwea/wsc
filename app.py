import sys
import os
from os import PathLike

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
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
            caption = "打开文件"

        directory = JxFileDialog._get_last_open_dir()
        file_path, _ = JxFileDialog.getOpenFileName(None, caption, directory, filter)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(os.path.dirname(file_path))

        return file_path

    @staticmethod
    def open_single_dir(caption=None, init_dir=None):
        if caption is None:
            caption = "打开文件夹"

        directory = init_dir or JxFileDialog._get_last_open_dir()
        file_path = JxFileDialog.getExistingDirectory(None, caption, directory)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(file_path)

        return file_path

    @staticmethod
    def save_single_file(caption=None, filter="All Files (*.*)", default_filename=None):
        if caption is None:
            caption = "保存文件"

        directory = JxFileDialog._get_last_open_dir()
        if default_filename is not None:
            directory = os.path.join(directory, default_filename)

        file_path, _ = JxFileDialog.getSaveFileName(None, caption, directory, filter)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(os.path.dirname(file_path))

        return file_path


class FileLocationEdit(QWidget):
    locationChanged = Signal(str)

    _layout: QHBoxLayout
    _location: QLineEdit

    def __init__(self, desc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._desc = desc or "???"
        self._location = QLineEdit(self)
        self._layout = QHBoxLayout(self)
        self._initUI()

    def _initUI(self):
        # self.setFixedWidth(200)

        self._layout.addWidget(QLabel(self._desc))

        btn_open_dir = QPushButton("选择文件", parent=self)
        self._layout.addWidget(btn_open_dir, 1)
        btn_open_dir.clicked.connect(self.on_btn_open_dir_clicked)

        btn_open_cls = QPushButton("清空文件", parent=self)
        self._layout.addWidget(btn_open_cls, 1)
        btn_open_cls.clicked.connect(self.on_btn_open_cls_clicked)

        edit_dir = self._location
        edit_dir.setReadOnly(True)
        self._layout.addWidget(edit_dir, 8)

    def on_btn_open_dir_clicked(self):
        path = JxFileDialog.open_single_file()
        if path:
            self.set_location(path)

    def on_btn_open_cls_clicked(self):
        self.set_location("")

    def set_location(self, path):
        self._location.setText(path)
        self.locationChanged.emit(path)


class WaterSortConfigWidget(QWidget):
    _layout: QHBoxLayout

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = QHBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("水排序工具")
        self.setGeometry(300, 300, 600, 300)

        layout = self._layout

        layout.addWidget(self.create_group_01())

    def create_group_01(self):
        group = QGroupBox("标题图片")
        layout = QVBoxLayout(group)

        edit01 = FileLocationEdit(desc="关卡1", parent=self)
        layout.addWidget(edit01)

        return group


class WaterSortConfigApp(QApplication):

    def __init__(self):
        super().__init__(sys.argv)
        self.setStyle("Fusion")
        self.wsc = WaterSortConfigWidget()
        self.wsc.show()

    def run(self):
        sys.exit(self.exec())


def main():
    app = WaterSortConfigApp()
    app.run()


if __name__ == "__main__":
    main()
