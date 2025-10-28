# -*- coding: utf-8 -*-
import copy
import enum
import json
import shutil
import sys
import os
from os import PathLike
from typing import Dict, List, Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
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


class PropKeyEnum(enum.StrEnum):
    G1_FILE_01 = "G1_PNG_01"
    G1_FILE_02 = "G1_PNG_02"
    G1_FILE_03 = "G1_PNG_03"
    G2_FILE_01 = "G2_JSON_F01"
    G2_FILE_02 = "G2_JSON_F02"
    G2_FILE_03 = "G2_JSON_F03"
    G3_OPT_TYP = "G3_OPT_TYPE"
    G3_OPT_NUM = "G3_OPT_NUMBER"
    G4_FILE_01 = "G4_FILE_01"
    G4_FILE_02 = "G4_FILE_02"
    G4_IS_TUTOR = "G4_IS_TUTOR"


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
    "ResultJumpType": "0",
    "ResultJumpNumber": 0,
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
        global _LAST_OPEN_DIR
        if _LAST_OPEN_DIR:
            return _LAST_OPEN_DIR
        return os.getcwd()

    @staticmethod
    def _set_last_open_dir(path):
        global _LAST_OPEN_DIR
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

    def __init__(self, desc, suffix=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._desc = desc
        self._suffix = suffix
        self._location = QLineEdit(self)
        self._layout = QHBoxLayout(self)
        self._initUI()

    def _initUI(self):
        layout = self._layout
        layout.setContentsMargins(0, 0, 0, 0)

        if self._desc:
            label = QLabel(self._desc)
            label.setFixedWidth(32)
            self._layout.addWidget(label)

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
        path = JxFileDialog.open_single_file(filter=f"File (*.{self._suffix})")
        if path:
            self.set_location(path)

    def on_btn_open_cls_clicked(self):
        self.set_location(None)

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


class DataCollector:
    _ASSET_INIT = {
        PropKeyEnum.G1_FILE_01: f"{_CONFIG_TEMPLATE['LevelData'][0]['titleImage']}",
        PropKeyEnum.G1_FILE_02: f"{_CONFIG_TEMPLATE['LevelData'][1]['titleImage']}",
        PropKeyEnum.G1_FILE_03: f"{_CONFIG_TEMPLATE['LevelData'][2]['titleImage']}",
        PropKeyEnum.G2_FILE_01: "1-1",
        PropKeyEnum.G2_FILE_02: "2-1",
        PropKeyEnum.G2_FILE_03: "3-1",
        PropKeyEnum.G4_FILE_01: f"{_CONFIG_TEMPLATE['ResultJumpImageURL']}",
        PropKeyEnum.G4_FILE_02: f"{_CONFIG_TEMPLATE['DownButtomInfo']['imageUrl']}",
    }

    _ASSET_LIST = {
        PropKeyEnum.G1_FILE_01: f"{_CONFIG_TEMPLATE['LevelData'][0]['titleImage']}.png",
        PropKeyEnum.G1_FILE_02: f"{_CONFIG_TEMPLATE['LevelData'][1]['titleImage']}.png",
        PropKeyEnum.G1_FILE_03: f"{_CONFIG_TEMPLATE['LevelData'][2]['titleImage']}.png",
        PropKeyEnum.G2_FILE_01: "lv1-1.json",
        PropKeyEnum.G2_FILE_02: "lv2-1.json",
        PropKeyEnum.G2_FILE_03: "lv3-1.json",
        PropKeyEnum.G4_FILE_01: f"{_CONFIG_TEMPLATE['ResultJumpImageURL']}.png",
        PropKeyEnum.G4_FILE_02: f"{_CONFIG_TEMPLATE['DownButtomInfo']['imageUrl']}.png",
    }

    _ERROR_MSG = {
        PropKeyEnum.G1_FILE_01: "1. 标题图片/关卡1",
        PropKeyEnum.G1_FILE_02: "1. 标题图片/关卡2",
        PropKeyEnum.G1_FILE_03: "1. 标题图片/关卡3",
        PropKeyEnum.G2_FILE_01: "2. 关卡文件/关卡1",
        PropKeyEnum.G2_FILE_02: "2. 关卡文件/关卡2",
        PropKeyEnum.G2_FILE_03: "2. 关卡文件/关卡3",
        PropKeyEnum.G3_OPT_TYP: "3. 最后一关的结束条件/结束条件类型",
        PropKeyEnum.G3_OPT_NUM: "3. 最后一关的结束条件/n 值",
        PropKeyEnum.G4_FILE_01: "4. 其他确认项/结束页",
        PropKeyEnum.G4_FILE_02: "4. 其他确认项/下载按钮图片",
        PropKeyEnum.G4_IS_TUTOR: "4. 其他确认项/是否有新手",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_file_exist(self, props: Dict[PropKeyEnum, Any]):
        for key in self._ASSET_LIST.keys():
            path = props.get(key)
            if path is not None and path != "" and not os.path.exists(path):
                QMessageBox.warning(None, "错误", f"参数【{self._ERROR_MSG[key]} 】的文件已删除")
                return False

        return True

    def check_n_value(self, props: Dict[PropKeyEnum, Any]):
        opt_type = props.get(PropKeyEnum.G3_OPT_TYP, LastLevelCondEnum.E00)
        opt_n_value = props.get(PropKeyEnum.G3_OPT_NUM, 0)

        if opt_type != LastLevelCondEnum.E00 and opt_n_value == 0:
            QMessageBox.warning(
                None, "错误", f"参数【{self._ERROR_MSG[PropKeyEnum.G3_OPT_NUM]} 】的值必须大于 0"
            )
            return False

        return True

    @staticmethod
    def check_level_file(props: Dict[PropKeyEnum, Any]):
        data = [
            props.get(PropKeyEnum.G2_FILE_01),
            props.get(PropKeyEnum.G2_FILE_02),
            props.get(PropKeyEnum.G2_FILE_03),
        ]

        end = False
        for i, path in enumerate(data):
            if path is None or len(path) == 0:
                end = True
            if end and not (path is None or len(path) == 0):
                QMessageBox.warning(None, "错误", f"必须配置连续的关卡，不可中断")
                return False

        return True

    def sanity_check(self, props: Dict[PropKeyEnum, Any]):
        if not self.check_n_value(props):
            return False

        if not self.check_file_exist(props):
            return False

        if not self.check_level_file(props):
            return False

        return True

    @staticmethod
    def select_target_dir():
        dir_path = JxFileDialog.open_single_dir("导出文件到文件夹")
        if not dir_path:
            QMessageBox.warning(None, "错误", f"未选择导出的文件夹")
            return dir_path

        return dir_path

    @staticmethod
    def copy_file(src: PathLike, target_dir: PathLike, name: str):
        if src is None or not os.path.exists(src):
            return
        dst = os.path.join(target_dir, f"{name}")
        shutil.copyfile(src, dst)

    def get_path_value(self, props: Dict[PropKeyEnum, Any], key: PropKeyEnum) -> str:
        if props.get(key) is None or not os.path.exists(props.get(key)):
            return ""
        return self._ASSET_INIT[key]

    @staticmethod
    def get_level_count(props: Dict[PropKeyEnum, Any]):
        data = [
            props.get(PropKeyEnum.G2_FILE_01),
            props.get(PropKeyEnum.G2_FILE_02),
            props.get(PropKeyEnum.G2_FILE_03),
        ]

        count = 0
        for i, path in enumerate(data):
            if path is None or len(path) == 0:
                continue

            count += 1

        return count

    def store_config(self, props: Dict[PropKeyEnum, Any], target_dir: PathLike):
        config_file = os.path.join(target_dir, "GameConfig.json")
        exp_config = copy.deepcopy(_CONFIG_TEMPLATE)

        exp_config["LevelData"][0]["titleImage"] = self.get_path_value(props, PropKeyEnum.G1_FILE_01)
        exp_config["LevelData"][1]["titleImage"] = self.get_path_value(props, PropKeyEnum.G1_FILE_02)
        exp_config["LevelData"][2]["titleImage"] = self.get_path_value(props, PropKeyEnum.G1_FILE_03)
        exp_config["LevelLength"] = self.get_level_count(props)

        exp_config["LevelData"][0]["levle"] = self.get_path_value(props, PropKeyEnum.G2_FILE_01)
        exp_config["LevelData"][1]["levle"] = self.get_path_value(props, PropKeyEnum.G2_FILE_02)
        exp_config["LevelData"][2]["levle"] = self.get_path_value(props, PropKeyEnum.G2_FILE_03)

        exp_config["ResultJumpType"] = f"{props.get(PropKeyEnum.G3_OPT_TYP, LastLevelCondEnum.E00)}"
        exp_config["ResultJumpNumber"] = props.get(PropKeyEnum.G3_OPT_NUM, 0)
        exp_config["ResultJumpImageURL"] = self.get_path_value(props, PropKeyEnum.G4_FILE_01)

        exp_config["DownButtomInfo"]["imageUrl"] = self.get_path_value(props, PropKeyEnum.G4_FILE_02)
        exp_config["IsOpenTutorial"] = props.get(PropKeyEnum.G4_IS_TUTOR, True)

        with open(config_file, "w") as f:
            json.dump(exp_config, f, indent=4, ensure_ascii=False)

    def store_assets(self, props: Dict[PropKeyEnum, Any], target_dir: PathLike):
        for key, value in self._ASSET_LIST.items():
            self.copy_file(
                src=props.get(key),
                target_dir=target_dir,
                name=value,
            )

        self.store_config(props, target_dir)

    def echo(self):
        QMessageBox.information(None, "成功", f"{self._ASSET_LIST}")

    def export(self, props: Dict[PropKeyEnum, Any]):
        if not self.sanity_check(props):
            return

        target_dir = self.select_target_dir()
        if target_dir is None or not os.path.exists(target_dir):
            return

        self.store_assets(props, target_dir)

        QMessageBox.information(None, "成功", f"成功导出到：{target_dir}")


class WaterSortConfigWidget(QWidget):
    _layout: QVBoxLayout
    _props: Dict[PropKeyEnum, Any]
    _collector: DataCollector

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = QVBoxLayout(self)
        self._props = {}
        self._collector = DataCollector()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("水排序配置制作工具")
        self.setMinimumWidth(600)
        # self.setGeometry(100, 100, 600, 200)

        layout = self._layout

        layout.addWidget(self._init_group_01())
        layout.addWidget(self._init_group_02())
        layout.addWidget(self._init_group_03())
        layout.addWidget(self._init_group_04())
        layout.addStretch()
        layout.addLayout(self._init_operation_area())

    def _init_group_01(self):
        group = QGroupBox("1. 标题图片")
        layout = QVBoxLayout(group)

        edit01 = JxFileLocationEdit(desc="关卡1：", suffix="png", parent=self)
        edit01.locationChanged.connect(
            lambda value, key=PropKeyEnum.G1_FILE_01: self._set_props(key, value)
        )
        layout.addWidget(edit01)

        edit02 = JxFileLocationEdit(desc="关卡2：", suffix="png", parent=self)
        edit02.locationChanged.connect(
            lambda value, key=PropKeyEnum.G1_FILE_02: self._set_props(key, value)
        )
        layout.addWidget(edit02)

        edit03 = JxFileLocationEdit(desc="关卡3：", suffix="png", parent=self)
        edit03.locationChanged.connect(
            lambda value, key=PropKeyEnum.G1_FILE_03: self._set_props(key, value)
        )
        layout.addWidget(edit03)

        return group

    def _init_group_02(self):
        group = QGroupBox("2. 关卡文件")
        layout = QVBoxLayout(group)

        edit01 = JxFileLocationEdit(desc="关卡1：", suffix="json", parent=self)
        edit01.locationChanged.connect(
            lambda value, key=PropKeyEnum.G2_FILE_01: self._set_props(key, value)
        )
        layout.addWidget(edit01)

        edit02 = JxFileLocationEdit(desc="关卡2：", suffix="json", parent=self)
        edit02.locationChanged.connect(
            lambda value, key=PropKeyEnum.G2_FILE_02: self._set_props(key, value)
        )
        layout.addWidget(edit02)

        edit03 = JxFileLocationEdit(desc="关卡3：", suffix="json", parent=self)
        edit03.locationChanged.connect(
            lambda value, key=PropKeyEnum.G2_FILE_03: self._set_props(key, value)
        )
        layout.addWidget(edit03)

        return group

    def _init_group_03(self):
        group = QGroupBox("3. 最后一关的结束条件")
        layout = QFormLayout(parent=group)

        selector = JxOptionSelector(
            options=LastLevelCondOptionList, init_value=LastLevelCondEnum.E00, parent=self
        )
        selector.currentValueChanged.connect(
            lambda value, key=PropKeyEnum.G3_OPT_TYP: self._set_props(key, value)
        )
        layout.addRow("结束条件类型", selector)

        edit01 = JxSpinBox(self)
        edit01.setRange(0, 99)
        edit01.valueChanged.connect(lambda value, key=PropKeyEnum.G3_OPT_NUM: self._set_props(key, value))
        layout.addRow("n 值", edit01)

        return group

    def _init_group_04(self):
        group = QGroupBox("4. 其他确认项")
        layout = QFormLayout(parent=group)

        edit01 = JxFileLocationEdit(desc=None, suffix="png", parent=self)
        edit01.locationChanged.connect(
            lambda value, key=PropKeyEnum.G4_FILE_01: self._set_props(key, value)
        )
        layout.addRow("结束页", edit01)

        edit02 = JxFileLocationEdit(desc=None, suffix="png", parent=self)
        edit02.locationChanged.connect(
            lambda value, key=PropKeyEnum.G4_FILE_02: self._set_props(key, value)
        )
        layout.addRow("下载按钮图片", edit02)

        check = JxRadioButton(parent=self)
        check.clicked.connect(lambda state, key=PropKeyEnum.G4_IS_TUTOR: self._set_props(key, value=state))
        check.setChecked(True)
        layout.addRow("是否有新手", check)

        return group

    def _init_operation_area(self):
        layout = QHBoxLayout()
        layout.addStretch()

        # btn_debug_props = QPushButton("調試", parent=self)
        # btn_debug_props.clicked.connect(self._on_dbg_btn_clicked)
        # layout.addWidget(btn_debug_props)

        btn_export_data = QPushButton("导出", parent=self)
        btn_export_data.clicked.connect(self._on_exp_btn_clicked)
        layout.addWidget(btn_export_data)

        return layout

    def _set_props(self, key: str, value: Any):
        self._props.update({key: value})
        print(f"Update Props: {key=}, {value=}")

    def _on_exp_btn_clicked(self):
        self._collector.export(self._props)

    def _on_dbg_btn_clicked(self):
        print(f"{self._props=}")


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
