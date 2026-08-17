from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFileDialog, QSpinBox,
    QCheckBox
)

from language_manager import tr

class ControlPanel(QWidget):
    """
    包含:
      - 白方/黑方: 人类 / AI
      - AI引擎路径编辑 + 浏览按钮
      - 新对局、保存PGN、加载PGN 按钮
      - 时间限制(分钟) & 加秒(秒)
      - Analysis 多PV设置
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        grid = QGridLayout()

        # --- 白方 ---
        self.white_label = QLabel(tr("WHITE_LABEL"))  # "白方:" / "White:"
        grid.addWidget(self.white_label, 0, 0)

        self.white_combo = QComboBox()
        # Combo内容: [人类, AI] / [Human, AI]
        self.white_combo.addItems([tr("HUMAN"), tr("AI")])
        grid.addWidget(self.white_combo, 0, 1)

        self.white_path_edit = QLineEdit()
        self.white_path_edit.setPlaceholderText(tr("WHITE_PATH_HINT"))
        grid.addWidget(self.white_path_edit, 1, 0, 1, 2)

        self.white_browse_btn = QPushButton(tr("BROWSE"))
        self.white_browse_btn.clicked.connect(self.onBrowseWhite)
        grid.addWidget(self.white_browse_btn, 1, 2)

        # --- 黑方 ---
        self.black_label = QLabel(tr("BLACK_LABEL"))
        grid.addWidget(self.black_label, 2, 0)

        self.black_combo = QComboBox()
        self.black_combo.addItems([tr("HUMAN"), tr("AI")])
        grid.addWidget(self.black_combo, 2, 1)

        self.black_path_edit = QLineEdit()
        self.black_path_edit.setPlaceholderText(tr("BLACK_PATH_HINT"))
        grid.addWidget(self.black_path_edit, 3, 0, 1, 2)

        self.black_browse_btn = QPushButton(tr("BROWSE"))
        self.black_browse_btn.clicked.connect(self.onBrowseBlack)
        grid.addWidget(self.black_browse_btn, 3, 2)

        # --- 分析相关 ---
        self.analysis_checkbox = QCheckBox(tr("ANALYSIS_ENABLE"))
        grid.addWidget(self.analysis_checkbox, 6, 0, 1, 2)

        label_analysis_engine = QLabel(tr("ANALYSIS_ENGINE"))
        grid.addWidget(label_analysis_engine, 7, 0)
        self.analysis_engine_combo = QComboBox()
        # 这里"Stockfish"/"Lc0"可保持英文,或在 language_manager 里也写多语言
        self.analysis_engine_combo.addItems(["Stockfish", "Lc0"])
        grid.addWidget(self.analysis_engine_combo, 7, 1)

        label_multipv = QLabel(tr("MULTIPV_LABEL"))
        grid.addWidget(label_multipv, 8, 0)
        self.analysis_multipv_spin = QSpinBox()
        self.analysis_multipv_spin.setRange(1, 5)
        self.analysis_multipv_spin.setValue(2)
        grid.addWidget(self.analysis_multipv_spin, 8, 1)

        # --- 时间与加秒 ---
        label_time = QLabel(tr("TIME_LIMIT"))
        grid.addWidget(label_time, 4, 0)
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 180)
        self.time_spin.setValue(5)
        grid.addWidget(self.time_spin, 4, 1)

        label_increment = QLabel(tr("INCREMENT_LABEL"))
        grid.addWidget(label_increment, 5, 0)
        self.increment_spin = QSpinBox()
        self.increment_spin.setRange(0, 60)
        self.increment_spin.setValue(2)
        grid.addWidget(self.increment_spin, 5, 1)

        layout.addLayout(grid)

        # --- 按钮: 新对局、保存、加载 ---
        self.new_game_btn = QPushButton(tr("NEW_GAME"))
        self.save_btn = QPushButton(tr("SAVE_PGN"))
        self.load_btn = QPushButton(tr("LOAD_PGN"))

        layout.addWidget(self.new_game_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.load_btn)
        layout.addStretch()

    def onBrowseWhite(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("BROWSE"), "",
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        if filepath:
            self.white_path_edit.setText(filepath)

    def onBrowseBlack(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("BROWSE"), "",
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        if filepath:
            self.black_path_edit.setText(filepath)

    def refreshUI(self):
        """
        在语言切换后，重新设置文本.
        由外部调用, e.g. parent().refreshUI() -> self.refreshUI()
        """
        self.white_label.setText(tr("WHITE_LABEL"))
        current_white_idx = self.white_combo.currentIndex()
        self.white_combo.clear()
        self.white_combo.addItems([tr("HUMAN"), tr("AI")])
        self.white_combo.setCurrentIndex(current_white_idx)
        self.white_path_edit.setPlaceholderText(tr("WHITE_PATH_HINT"))
        self.white_browse_btn.setText(tr("BROWSE"))

        self.black_label.setText(tr("BLACK_LABEL"))
        current_black_idx = self.black_combo.currentIndex()
        self.black_combo.clear()
        self.black_combo.addItems([tr("HUMAN"), tr("AI")])
        self.black_combo.setCurrentIndex(current_black_idx)
        self.black_path_edit.setPlaceholderText(tr("BLACK_PATH_HINT"))
        self.black_browse_btn.setText(tr("BROWSE"))

        self.analysis_checkbox.setText(tr("ANALYSIS_ENABLE"))
        # 如果 label_analysis_engine / label_multipv / label_time / label_increment
        # 想要在这里更新, 需要在 initUI() 里把它们定义为 self.xxx。
        # 演示：
        # self.label_analysis_engine.setText(tr("ANALYSIS_ENGINE"))
        # self.label_multipv.setText(tr("MULTIPV_LABEL"))
        # etc.

        self.new_game_btn.setText(tr("NEW_GAME"))
        self.save_btn.setText(tr("SAVE_PGN"))
        self.load_btn.setText(tr("LOAD_PGN"))
