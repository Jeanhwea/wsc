# -*- coding: utf-8 -*-
import copy
import enum
import glob
import hashlib
import json
import os
import random
import shutil
import sys
from typing import Any, Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
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
    G4_IS_TUTR = "G4_IS_TUTOR"
    G4_YXP_DIR = "G4_YXP_DIR"


class YxpSuffixEnum(enum.StrEnum):
    SKEL = "skel"
    ATLAS = "atlas"
    PNG = "png"
    CSV = "csv"


class LastLevelCondEnum(enum.StrEnum):
    E00 = "0"
    E01 = "a"
    E02 = "b"


LastLevelCondEnumDict = {
    LastLevelCondEnum.E00: "胜利/失败",
    LastLevelCondEnum.E01: "胜利/失败/有效操作次数>n",
    LastLevelCondEnum.E02: "胜利/失败/用户操作次数>n",
}

LastLevelCondOptionList = [
    {
        "label": f"{LastLevelCondEnumDict[e]}",
        "value": e,
    }
    for e in LastLevelCondEnum
]

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
    "md5": "",
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
    def open_single_file(caption=None, filter=None):
        caption = caption or "打开文件"
        filter = filter or "All Files (*.*)"

        directory = JxFileDialog._get_last_open_dir()
        file_path, _ = JxFileDialog.getOpenFileName(None, caption, directory, filter)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(os.path.dirname(file_path))

        return file_path

    @staticmethod
    def open_single_dir(caption=None, init_dir=None):
        caption = caption or "打开文件夹"

        directory = init_dir or JxFileDialog._get_last_open_dir()
        file_path = JxFileDialog.getExistingDirectory(None, caption, directory)
        if file_path is not None:
            JxFileDialog._set_last_open_dir(file_path)

        return file_path

    @staticmethod
    def save_single_file(caption=None, filter=None, default_filename=None):
        caption = caption or "保存文件"
        filter = filter or "All Files (*.*)"

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

    def __init__(self, desc=None, suffix=None, choose_dir=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._desc = desc
        self._suffix = suffix
        self._choose_dir = choose_dir
        self._location = QLineEdit(self)
        self._layout = QHBoxLayout(self)
        self._initUI()

    def _initUI(self):
        layout = self._layout
        layout.setContentsMargins(0, 0, 0, 0)

        if self._desc:
            label = QLabel(self._desc)
            label.setFixedWidth(40)
            layout.addWidget(label)

        btn_text = "选择文件夹" if self._choose_dir else "选择文件"
        btn_open_dir = QPushButton(btn_text, parent=self)
        layout.addWidget(btn_open_dir, 1)
        btn_open_dir.clicked.connect(self.on_btn_open_dir_clicked)

        btn_text_cls = QPushButton("清空", parent=self)
        layout.addWidget(btn_text_cls, 1)
        btn_text_cls.clicked.connect(self.on_btn_text_cls_clicked)

        edit_dir = self._location
        edit_dir.setReadOnly(True)
        layout.addWidget(edit_dir, 8)

    def on_btn_open_dir_clicked(self):
        if self._choose_dir:
            path = JxFileDialog.open_single_dir()
        else:
            path = JxFileDialog.open_single_file(filter=f"File (*.{self._suffix})")

        if path:
            self.set_location(path)

    def on_btn_text_cls_clicked(self):
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
        self.add_options(options)

        if self._init_value and options:
            for i, item in enumerate(options):
                if item.get("value") == self._init_value:
                    self.setCurrentIndex(i)
                    break

        self.currentIndexChanged.connect(self._set_value)

    def add_options(self, options: List[Dict]):
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
        PropKeyEnum.G2_FILE_01: f"{_CONFIG_TEMPLATE['LevelData'][0]['levle']}",
        PropKeyEnum.G2_FILE_02: f"{_CONFIG_TEMPLATE['LevelData'][1]['levle']}",
        PropKeyEnum.G2_FILE_03: f"{_CONFIG_TEMPLATE['LevelData'][2]['levle']}",
        PropKeyEnum.G4_FILE_01: f"{_CONFIG_TEMPLATE['ResultJumpImageURL']}",
        PropKeyEnum.G4_FILE_02: f"{_CONFIG_TEMPLATE['DownButtomInfo']['imageUrl']}",
    }

    _ASSET_LIST = {
        PropKeyEnum.G1_FILE_01: f"{_CONFIG_TEMPLATE['LevelData'][0]['titleImage']}.png",
        PropKeyEnum.G1_FILE_02: f"{_CONFIG_TEMPLATE['LevelData'][1]['titleImage']}.png",
        PropKeyEnum.G1_FILE_03: f"{_CONFIG_TEMPLATE['LevelData'][2]['titleImage']}.png",
        PropKeyEnum.G2_FILE_01: f"lv{_CONFIG_TEMPLATE['LevelData'][0]['levle']}.json",
        PropKeyEnum.G2_FILE_02: f"lv{_CONFIG_TEMPLATE['LevelData'][1]['levle']}.json",
        PropKeyEnum.G2_FILE_03: f"lv{_CONFIG_TEMPLATE['LevelData'][2]['levle']}.json",
        PropKeyEnum.G4_FILE_01: f"{_CONFIG_TEMPLATE['ResultJumpImageURL']}.png",
        PropKeyEnum.G4_FILE_02: f"{_CONFIG_TEMPLATE['DownButtomInfo']['imageUrl']}.png",
    }

    _ASSET_YXP_FILES = {
        YxpSuffixEnum.SKEL: f"心形瓶子_接水.{YxpSuffixEnum.SKEL}",
        YxpSuffixEnum.ATLAS: f"心形瓶子_接水.{YxpSuffixEnum.ATLAS}",
        YxpSuffixEnum.PNG: f"心形瓶子_接水.{YxpSuffixEnum.PNG}",
        YxpSuffixEnum.CSV: f"SpecialBottleConfig.{YxpSuffixEnum.CSV}",
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
        PropKeyEnum.G4_IS_TUTR: "4. 其他确认项/是否有新手",
    }

    _CHAR_ALPHABETA = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

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

    def check_level_count(self, props: Dict[PropKeyEnum, Any]):
        count_level = self.get_level_count(props)
        if count_level == 0:
            QMessageBox.warning(None, "错误", f"必须配置至少 1 个关卡")
            return False
        return True

    @staticmethod
    def _is_valid_file(file_path: str):
        if file_path is None or len(file_path) == 0:
            return False
        return True

    def check_image_json_match(self, props: Dict[PropKeyEnum, Any]):
        file_tuple_list = [
            (PropKeyEnum.G1_FILE_01, PropKeyEnum.G2_FILE_01),
            (PropKeyEnum.G1_FILE_02, PropKeyEnum.G2_FILE_02),
            (PropKeyEnum.G1_FILE_03, PropKeyEnum.G2_FILE_03),
        ]
        for k1, k2 in file_tuple_list:
            f1, f2 = props.get(k1), props.get(k2)
            if self._is_valid_file(f1) and not self._is_valid_file(f2):
                QMessageBox.warning(
                    None, "错误", f"图片【{self._ERROR_MSG[k1]} 】没有匹配的关卡【{self._ERROR_MSG[k2]}】"
                )
                return False

        return True

    @staticmethod
    def _list_glob_files(folder: str, suffix: str):
        if folder is None or not os.path.exists(folder):
            return []
        glob_pattern = os.path.join(os.path.abspath(folder), f"*.{suffix}")
        return glob.glob(glob_pattern)

    def check_yxp_folder(self, props: Dict[PropKeyEnum, Any]):
        folder = props.get(PropKeyEnum.G4_YXP_DIR, "")

        if len(folder) == 0:
            return True

        if not os.path.exists(folder):
            QMessageBox.warning(None, "错误", f"异形屏文件夹【{folder} 】已删除")
            return False

        for suffix in self._ASSET_YXP_FILES.keys():
            files = self._list_glob_files(folder, suffix)
            if len(files) != 1:
                QMessageBox.warning(
                    None,
                    "错误",
                    f"异形屏文件夹数据错误：包含 {len(files)} 个 {suffix} 文件",
                )
                return False

        return True

    def sanity_check(self, props: Dict[PropKeyEnum, Any]):
        if not self.check_n_value(props):
            return False

        if not self.check_file_exist(props):
            return False

        if not self.check_level_file(props):
            return False

        if not self.check_level_count(props):
            return False

        if not self.check_image_json_match(props):
            return False

        if not self.check_yxp_folder(props):
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
    def copy_file(src: str, target_dir: str, name: str):
        if src is None or not os.path.exists(src):
            return
        dst = os.path.join(target_dir, f"{name}")

        print(f"Copy file: {src} => {dst}")
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

    @staticmethod
    def _replace_atlas_png_file(src: str, dst: str, png_name: str):
        if src is None or not os.path.exists(src):
            return ""

        with open(src, "r", encoding="utf-8") as f:
            text = f.read().lstrip()

        lines = text.splitlines()
        lines[0] = png_name
        text = "\n".join(lines)

        with open(dst, "w", encoding="utf-8") as f:
            f.write(text)

    @staticmethod
    def calc_file_md5_hash(target: str):
        with open(target, "rb") as f:
            md5_hash = hashlib.md5()
            while chunk := f.read(8192):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @classmethod
    def calc_my_md5_checksum(cls, target: str):
        if target is None or not os.path.exists(target):
            return ""

        A = cls.calc_file_md5_hash(target)
        n = len(A)

        B = ""
        for i in range(0, n // 2):
            B += f"{A[i + 1]}{A[i]}"

        alphabeta = list(cls._CHAR_ALPHABETA)

        C = ""
        for i in range(0, n // 2):
            C += f"{B[i : i + 2]}{random.choice(alphabeta)}"

        return C

    def store_config(self, props: Dict[PropKeyEnum, Any], target_dir: str):
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
        exp_config["IsOpenTutorial"] = props.get(PropKeyEnum.G4_IS_TUTR, True)

        exp_config["md5"] = self.calc_my_md5_checksum(props.get(PropKeyEnum.G4_FILE_02, ""))

        with open(config_file, "w") as f:
            json.dump(exp_config, f, indent=4, ensure_ascii=False)

    def store_yxp_files(self, props: Dict[PropKeyEnum, Any], target_dir: str):
        src_dir = props.get(PropKeyEnum.G4_YXP_DIR, "")
        if not os.path.exists(src_dir):
            return

        for key, value in self._ASSET_YXP_FILES.items():
            files = self._list_glob_files(src_dir, key)
            self.copy_file(
                src=files[0],
                target_dir=target_dir,
                name=value,
            )

        altla_file = os.path.join(target_dir, self._ASSET_YXP_FILES[YxpSuffixEnum.ATLAS])
        png_name = self._ASSET_YXP_FILES[YxpSuffixEnum.PNG]
        self._replace_atlas_png_file(altla_file, altla_file, png_name)

    def store_assets(self, props: Dict[PropKeyEnum, Any], target_dir: str):
        for key, value in self._ASSET_LIST.items():
            self.copy_file(
                src=props.get(key),
                target_dir=target_dir,
                name=value,
            )

        self.store_yxp_files(props, target_dir)
        self.store_config(props, target_dir)

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
        layout = QFormLayout(parent=group)

        edit01 = JxFileLocationEdit(suffix="png", parent=self)
        edit01.locationChanged.connect(
            lambda value, key=PropKeyEnum.G1_FILE_01: self._set_props(key, value)
        )
        layout.addRow("关卡1", edit01)

        edit02 = JxFileLocationEdit(suffix="png", parent=self)
        edit02.locationChanged.connect(
            lambda value, key=PropKeyEnum.G1_FILE_02: self._set_props(key, value)
        )
        layout.addRow("关卡2", edit02)

        edit03 = JxFileLocationEdit(suffix="png", parent=self)
        edit03.locationChanged.connect(
            lambda value, key=PropKeyEnum.G1_FILE_03: self._set_props(key, value)
        )
        layout.addRow("关卡3", edit03)

        return group

    def _init_group_02(self):
        group = QGroupBox("2. 关卡文件")
        layout = QFormLayout(parent=group)

        edit01 = JxFileLocationEdit(suffix="json", parent=self)
        edit01.locationChanged.connect(
            lambda value, key=PropKeyEnum.G2_FILE_01: self._set_props(key, value)
        )
        layout.addRow("关卡1", edit01)

        edit02 = JxFileLocationEdit(suffix="json", parent=self)
        edit02.locationChanged.connect(
            lambda value, key=PropKeyEnum.G2_FILE_02: self._set_props(key, value)
        )
        layout.addRow("关卡2", edit02)

        edit03 = JxFileLocationEdit(suffix="json", parent=self)
        edit03.locationChanged.connect(
            lambda value, key=PropKeyEnum.G2_FILE_03: self._set_props(key, value)
        )
        layout.addRow("关卡3", edit03)

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

        edit01 = JxFileLocationEdit(suffix="png", parent=self)
        edit01.locationChanged.connect(
            lambda value, key=PropKeyEnum.G4_FILE_01: self._set_props(key, value)
        )
        layout.addRow("结束页", edit01)

        edit02 = JxFileLocationEdit(suffix="png", parent=self)
        edit02.locationChanged.connect(
            lambda value, key=PropKeyEnum.G4_FILE_02: self._set_props(key, value)
        )
        layout.addRow("下载按钮图片", edit02)

        check = JxRadioButton(parent=self)
        check.clicked.connect(lambda state, key=PropKeyEnum.G4_IS_TUTR: self._set_props(key, value=state))
        check.setChecked(True)
        layout.addRow("是否有新手", check)

        edit03 = JxFileLocationEdit(choose_dir=True, parent=self)
        edit03.locationChanged.connect(
            lambda value, key=PropKeyEnum.G4_YXP_DIR: self._set_props(key, value)
        )
        layout.addRow("异形瓶文件夹", edit03)

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
