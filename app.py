import sys

from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)


class WaterSortConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("水排序工具")
        self.setGeometry(300, 300, 300, 100)


class WaterSortConfigApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.wsc = WaterSortConfigWidget()
        self.wsc.show()
        sys.exit(self.exec())
