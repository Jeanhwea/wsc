import enum
import sys
import os
from typing import Dict, List, Any

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
    QComboBox,
    QFormLayout,
    QSpinBox,
    QRadioButton,
)


class LastLevelCondEnum(enum.StrEnum):
    E00 = "0"
    E01 = "a"
    E02 = "b"


LastLevelCondEnumDict = {
    LastLevelCondEnum.E00: "胜利/失败",
    LastLevelCondEnum.E01: "胜利/失败/有效操作次数>n",
    LastLevelCondEnum.E02: "胜利/失败/用户操作次数>n",
}

LastLevelCondOptionList = [{"label": f"{LastLevelCondEnumDict[e]}", "value": e} for e in LastLevelCondEnum]

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


class JxFileLocationEdit(QWidget):
    locationChanged = Signal(str)

    _layout: QHBoxLayout
    _location: QLineEdit

    def __init__(self, desc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._desc = desc
        self._location = QLineEdit(self)
        self._layout = QHBoxLayout(self)
        self._initUI()

    def _initUI(self):
        # self.setFixedWidth(200)
        layout = self._layout
        layout.setContentsMargins(0, 0, 0, 0)

        if self._desc:
            self._layout.addWidget(QLabel(self._desc))

        btn_open_dir = QPushButton("选择文件", parent=self)
        self._layout.addWidget(btn_open_dir, 1)
        btn_open_dir.clicked.connect(self.on_btn_open_dir_clicked)

        btn_open_cls = QPushButton("清空", parent=self)
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


class JxOptionSelector(QComboBox):
    _options: List[Dict[str, Any]]

    currentValueChanged = Signal(Any)

    def __init__(self, options: List[Dict] = None, init_value=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._options = options or []
        self._init_value = init_value
        self._initUI()

    def _initUI(self):
        options = self._options
        self.addOptions(options)

        if self._init_value and options:
            for i, item in enumerate(options):
                if item.get("value") == self._init_value:
                    self.setCurrentIndex(i)
                    break

        self.currentIndexChanged.connect(self._set_value)

    def addOptions(self, options: List[Dict]):
        for index, option in enumerate(options):
            if "label" not in option:
                raise Exception("JxOptionSelector miss label field.")
            self.addItem(option["label"], index)

    def _set_value(self, index):
        value = self._options[index].get("value")
        self.currentValueChanged.emit(value)


class JxSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class JxRadioButton(QRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WaterSortConfigWidget(QWidget):
    _layout: QVBoxLayout
    _props: Dict[str, Any]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = QVBoxLayout(self)
        self._props = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("水排序配置制作工具")
        self.setGeometry(100, 100, 600, 200)

        layout = self._layout

        layout.addWidget(self._init_group_01())
        layout.addWidget(self._init_group_02())
        layout.addWidget(self._init_group_03())
        layout.addWidget(self._init_group_04())
        layout.addLayout(self._init_operation_area())

        layout.addStretch()

    def _init_group_01(self):
        group = QGroupBox("1. 标题图片")
        layout = QVBoxLayout(group)

        edit01 = JxFileLocationEdit(desc="关卡1：", parent=self)
        layout.addWidget(edit01)

        edit02 = JxFileLocationEdit(desc="关卡2：", parent=self)
        layout.addWidget(edit02)

        edit03 = JxFileLocationEdit(desc="关卡3：", parent=self)
        layout.addWidget(edit03)

        return group

    def _init_group_02(self):
        group = QGroupBox("2. 关卡文件")
        layout = QVBoxLayout(group)

        edit01 = JxFileLocationEdit(desc="关卡1：", parent=self)
        layout.addWidget(edit01)

        edit02 = JxFileLocationEdit(desc="关卡2：", parent=self)
        layout.addWidget(edit02)

        edit03 = JxFileLocationEdit(desc="关卡3：", parent=self)
        layout.addWidget(edit03)

        return group

    def _init_group_03(self):
        group = QGroupBox("3. 最后一关的结束条件")
        layout = QFormLayout(parent=group)

        selector = JxOptionSelector(
            options=LastLevelCondOptionList, init_value=LastLevelCondEnum.E00, parent=self
        )
        layout.addRow("结束条件类型", selector)

        edit01 = JxSpinBox(self)
        edit01.setRange(0, 99)
        layout.addRow("n 值", edit01)

        return group

    def _init_group_04(self):
        group = QGroupBox("4. 其他确认项")
        layout = QFormLayout(parent=group)

        edit01 = JxFileLocationEdit(desc=None, parent=self)
        layout.addRow("结束页", edit01)

        edit02 = JxFileLocationEdit(desc=None, parent=self)
        layout.addRow("下载按钮图片", edit02)

        check = JxRadioButton(parent=self)
        layout.addRow("是否有新手", check)

        return group

    def _init_operation_area(self):
        layout = QHBoxLayout()
        layout.addStretch()

        btn_export_data = QPushButton("导出", parent=self)
        layout.addWidget(btn_export_data)

        return layout


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
