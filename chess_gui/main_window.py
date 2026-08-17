import sys
import time
import chess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QFileDialog, QApplication, QPlainTextEdit, QPushButton
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject

from chess_game import ChessGame
from engine_manager import EngineManager
from board_widget import BoardWidget
from control_panel import ControlPanel
from analysis_window import GlobalAnalysisWindow
from language_manager import tr
from language_manager import current_language, setLanguage

class AIWorker(QObject):
    moveReady = pyqtSignal(chess.Move)

    def __init__(self, engine_mgr, board, time_limit):
        super().__init__()
        self.engine_mgr = engine_mgr
        self.time_limit = time_limit
        self.board = board.copy()
        # 这个self.chess_game似乎没在AIWorker里真正用到,可酌情删除
        self.chess_game = ChessGame(initial_time=300, increment=2)

    def run(self):
        try:
            best_move = self.engine_mgr.get_best_move(self.board, time_limit=self.time_limit)
        except Exception:
            best_move = None
        if best_move is not None:
            self.moveReady.emit(best_move)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 2) 用 tr("APP_TITLE") 取代硬编码
        self.setWindowTitle(tr("APP_TITLE"))
        self.resize(1000, 600)

        self.chess_game = ChessGame(initial_time=300, increment=2)

        # 主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # 棋盘控件
        self.board_widget = BoardWidget(self.chess_game, parent=self)
        self.board_widget.moveMade.connect(self.onUserMadeMove)
        self.main_layout.addWidget(self.board_widget, 3)

        # 右侧布局
        right_layout = QVBoxLayout()

        # 控制面板
        self.control_panel = ControlPanel(self)
        right_layout.addWidget(self.control_panel, 0)

        # 时钟
        clock_layout = QHBoxLayout()
        # 默认先写 300s, 也可以等 refreshUI() 里再刷新
        self.white_clock_label = QLabel(tr("WHITE_CLOCK") + "300s")
        self.black_clock_label = QLabel(tr("BLACK_CLOCK") + "300s")
        clock_layout.addWidget(self.white_clock_label)
        clock_layout.addWidget(self.black_clock_label)
        right_layout.addLayout(clock_layout)

        # 走棋表格
        self.move_table = QTableWidget()
        self.move_table.setColumnCount(2)
        self.move_table.setHorizontalHeaderLabels([tr("TABLE_WHITE"), tr("TABLE_BLACK")])
        self.move_table.setEditTriggers(self.move_table.NoEditTriggers)
        right_layout.addWidget(self.move_table, 1)

        # 分析文本框
        self.analysis_text = QPlainTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setPlaceholderText(tr("ANALYSIS_HINT"))
        right_layout.addWidget(self.analysis_text, 1)

        self.main_layout.addLayout(right_layout, 1)

        self.lang_button = QPushButton(tr("LANG_TOGGLE"))
        right_layout.addWidget(self.lang_button)


        # AI引擎管理
        self.white_engine_mgr = None
        self.black_engine_mgr = None

        self.setupSignals()

        # 定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateClocks)
        self.timer.start(1000)

        # 全局分析按钮
        self.global_analysis_btn = QPushButton(tr("GLOBAL_ANALYSIS"), self)
        self.control_panel.layout().addWidget(self.global_analysis_btn)
        self.global_analysis_btn.clicked.connect(self.onGlobalAnalysis)
        #language
        self.lang_button.clicked.connect(self.onSwitchLanguage)

    def setupSignals(self):
        self.control_panel.new_game_btn.clicked.connect(self.onNewGame)
        self.control_panel.save_btn.clicked.connect(self.onSavePGN)
        self.control_panel.load_btn.clicked.connect(self.onLoadPGN)

    # ---------- 新对局 ----------
    def onNewGame(self):
        minutes = self.control_panel.time_spin.value()
        increment = self.control_panel.increment_spin.value()
        initial_time = minutes * 60

        # 停止旧引擎
        if self.white_engine_mgr:
            self.white_engine_mgr.stop_engine()
            self.white_engine_mgr = None
        if self.black_engine_mgr:
            self.black_engine_mgr.stop_engine()
            self.black_engine_mgr = None

        # 重建 ChessGame
        self.chess_game = ChessGame(initial_time=initial_time, increment=increment)
        self.board_widget.chess_game = self.chess_game

        # 清空走棋表
        self.move_table.setRowCount(0)
        self.board_widget.update()

        # 白方AI
        if self.control_panel.white_combo.currentText() == "AI":
            white_path = self.control_panel.white_path_edit.text()
            if white_path:
                self.white_engine_mgr = EngineManager(white_path)
                try:
                    self.white_engine_mgr.start_engine()
                except Exception as e:
                    QMessageBox.critical(self, tr("ERROR"), tr("WHITE_ENGINE_FAIL") + str(e))
                    self.control_panel.white_combo.setCurrentIndex(0)
                    self.white_engine_mgr = None
            else:
                QMessageBox.warning(self, tr("WARNING"), tr("WHITE_AI_PATH_EMPTY"))
                self.control_panel.white_combo.setCurrentIndex(0)

        # 黑方AI
        if self.control_panel.black_combo.currentText() == "AI":
            black_path = self.control_panel.black_path_edit.text()
            if black_path:
                self.black_engine_mgr = EngineManager(black_path)
                try:
                    self.black_engine_mgr.start_engine()
                except Exception as e:
                    QMessageBox.critical(self, tr("ERROR"), tr("BLACK_ENGINE_FAIL") + str(e))
                    self.control_panel.black_combo.setCurrentIndex(0)
                    self.black_engine_mgr = None
            else:
                QMessageBox.warning(self, tr("WARNING"), tr("BLACK_AI_PATH_EMPTY"))
                self.control_panel.black_combo.setCurrentIndex(0)

        # 如果是AI先走
        self.checkAutoMove()

    # ---------- 存PGN ----------
    def onSavePGN(self):
        filename, _ = QFileDialog.getSaveFileName(self, tr("SAVE_FAILED"), "", "PGN (*.pgn)")
        if filename:
            try:
                self.chess_game.save_pgn(filename)
            except Exception as e:
                QMessageBox.critical(self, tr("ERROR"), tr("SAVE_FAILED") + str(e))

    # ---------- 载PGN ----------
    def onLoadPGN(self):
        filename, _ = QFileDialog.getOpenFileName(self, tr("LOAD_FAILED"), "", "PGN (*.pgn)")
        if filename:
            try:
                self.chess_game.load_pgn(filename)
                self.refreshMoveTableFromGame()
                self.board_widget.update()
            except Exception as e:
                QMessageBox.critical(self, tr("ERROR"), tr("LOAD_FAILED") + str(e))

    # ---------- 用户落子 ----------
    def onUserMadeMove(self, move):
        san = self.chess_game.push_move(move)
        if san is None:
            QMessageBox.information(self, tr("INFO"), tr("ILLEGAL_MOVE"))
            self.board_widget.update()
            return

        self.updateMoveTable(move, san)
        self.board_widget.update()

        # 判断终局
        if self.chess_game.is_game_over():
            QMessageBox.information(self, tr("GAME_OVER"), tr("GAME_ENDED"))
            return

        # 看看AI是否要走
        self.checkAutoMove()
        self.triggerAnalysis()

    # ---------- AI自动走 ----------
    def checkAutoMove(self):
        if self.chess_game.is_game_over():
            return

        board = self.chess_game.board
        if board.turn == chess.WHITE and self.control_panel.white_combo.currentText() == "AI":
            self.aiMove(True)
        elif board.turn == chess.BLACK and self.control_panel.black_combo.currentText() == "AI":
            self.aiMove(False)

    def aiMove(self, is_white):
        engine_mgr = self.white_engine_mgr if is_white else self.black_engine_mgr
        if not engine_mgr:
            return

        w_time, b_time = self.chess_game.get_time_left()
        ai_time = w_time if is_white else b_time
        time_limit = min(ai_time, 5.0)
        if time_limit <= 0:
            QMessageBox.information(self, tr("GAME_OVER"), tr("AI_TIME_UP"))
            return

        self.ai_thread = QThread(self)
        self.ai_worker = AIWorker(engine_mgr, self.chess_game.board, time_limit=time_limit)
        self.ai_worker.moveReady.connect(self.onAIMoveReady)
        self.ai_thread.finished.connect(self.ai_thread.deleteLater)
        self.ai_thread.finished.connect(self.onAIFinished)

        self.ai_worker.moveToThread(self.ai_thread)
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_thread.start()

        self.board_widget.update()
        QApplication.processEvents()

    def onAIMoveReady(self, best_move):
        if not best_move:
            QMessageBox.information(self, tr("ERROR"), tr("AI_NO_MOVE"))
            return

        san = self.chess_game.push_move(best_move)
        if san is None:
            QMessageBox.information(self, tr("WARNING"), tr("AI_ILLEGAL_MOVE"))
            self.board_widget.update()
            return

        self.updateMoveTable(best_move, san)
        self.board_widget.update()

        if self.chess_game.is_game_over():
            QMessageBox.information(self, tr("GAME_OVER"), tr("GAME_ENDED"))
        else:
            self.checkAutoMove()

    def onAIFinished(self):
        self.ai_worker = None
        self.ai_thread = None

    # ---------- 走棋表 ----------
    def refreshMoveTableFromGame(self):
        self.move_table.setRowCount(0)
        temp_board = chess.Board()
        moves = list(self.chess_game.game.mainline_moves())

        for mv in moves:
            san = temp_board.san(mv)
            is_white = temp_board.turn
            temp_board.push(mv)
            if is_white:
                row = self.move_table.rowCount()
                self.move_table.insertRow(row)
                self.move_table.setItem(row, 0, QTableWidgetItem(san))
                self.move_table.setItem(row, 1, QTableWidgetItem(""))
            else:
                row = self.move_table.rowCount() - 1
                self.move_table.setItem(row, 1, QTableWidgetItem(san))

    def updateMoveTable(self, move, san):
        is_white_just_moved = not self.chess_game.board.turn
        if is_white_just_moved:
            row = self.move_table.rowCount()
            self.move_table.insertRow(row)
            self.move_table.setItem(row, 0, QTableWidgetItem(san))
            self.move_table.setItem(row, 1, QTableWidgetItem(""))
        else:
            row = self.move_table.rowCount() - 1
            self.move_table.setItem(row, 1, QTableWidgetItem(san))

        self.move_table.scrollToBottom()

    # ---------- 时钟刷新 ----------
    def updateClocks(self):
        w_time, b_time = self.chess_game.get_dynamic_time_left()
        self.white_clock_label.setText(tr("WHITE_CLOCK") + f"{int(w_time)}s")
        self.black_clock_label.setText(tr("BLACK_CLOCK") + f"{int(b_time)}s")

    # ---------- Analysis ----------
    def triggerAnalysis(self):
        if not self.control_panel.analysis_checkbox.isChecked():
            self.analysis_text.clear()
            return

        engine_name = self.control_panel.analysis_engine_combo.currentText()
        multipv = self.control_panel.analysis_multipv_spin.value()

        if engine_name == "Stockfish":
            engine_path = "model\\Stockfish\\stockfish-windows-x86-64-avx2.exe"
        else:
            engine_path = "model\\LC0\\lc0.exe"

        if hasattr(self, "analysis_engine_mgr") and self.analysis_engine_mgr:
            self.analysis_engine_mgr.stop_engine()

        from engine_manager import EngineManager
        self.analysis_engine_mgr = EngineManager(engine_path)
        try:
            self.analysis_engine_mgr.start_engine()
        except Exception as e:
            QMessageBox.warning(self, tr("WARNING"), tr("WHITE_ENGINE_FAIL") + str(e))
            return

        if hasattr(self, "analysis_thread") and self.analysis_thread:
            self.analysis_thread.quit()
            self.analysis_thread.wait()
            self.analysis_thread = None
            self.analysis_worker = None

        from PyQt5.QtCore import QThread
        self.analysis_thread = QThread(self)
        self.analysis_worker = AnalysisWorker(
            engine_mgr=self.analysis_engine_mgr,
            board=self.chess_game.board,
            depth=25,
            multipv=multipv
        )
        self.analysis_worker.analysisReady.connect(self.onAnalysisResult)
        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)
        self.analysis_worker.moveToThread(self.analysis_thread)
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_thread.start()

    def onAnalysisResult(self, infos):
        self.analysis_text.clear()
        if not infos:
            self.analysis_text.setPlainText(tr("ANALYSIS_FAIL"))
            return

        lines = []
        for item in infos:
            mpv = item["multipv"]
            score = item["score"]
            pv_moves = item["pv"]
            score_str = "?"
            if score is not None:
                if score.relative.mate() is not None:
                    mate_in = score.relative.mate()
                    score_str = f"# {mate_in}"
                else:
                    cp = score.relative.cp
                    score_str = f"{cp/100:.2f}"

            temp_board = self.chess_game.board.copy()
            pv_sans = []
            for mv in pv_moves:
                pv_sans.append(temp_board.san(mv))
                temp_board.push(mv)
            pv_str = " ".join(pv_sans)

            lines.append(f"PV{mpv} (score={score_str}): {pv_str}")

        self.analysis_text.setPlainText("\n".join(lines))

    def onGlobalAnalysis(self):
        engine_path = "model/Stockfish/stockfish-windows-x86-64-avx2.exe"
        self.analysis_window = GlobalAnalysisWindow(self.chess_game, engine_path)
        self.analysis_window.show()

    def onSwitchLanguage(self):
        """
        切换语言（en <-> zh），并刷新主窗口及子控件
        """
        from language_manager import current_language, setLanguage
        
        # 简单的toggle逻辑
        if current_language == "en":
            setLanguage("zh")
        else:
            setLanguage("en")
        
        # 让自身刷新UI文本
        self.refreshUI()
        
        # 让control_panel或其他子窗口也刷新
        self.control_panel.refreshUI()
        

    def refreshUI(self):
        # 1) 主窗口标题
        self.setWindowTitle(tr("APP_TITLE"))

        # 2) 时钟标签
        w_time, b_time = self.chess_game.get_dynamic_time_left()
        self.white_clock_label.setText(tr("WHITE_CLOCK") + f"{int(w_time)}s")
        self.black_clock_label.setText(tr("BLACK_CLOCK") + f"{int(b_time)}s")

        # 3) 走棋表头
        self.move_table.setHorizontalHeaderLabels([tr("TABLE_WHITE"), tr("TABLE_BLACK")])

        # 4) 分析文本的 Placeholder
        self.analysis_text.setPlaceholderText(tr("ANALYSIS_HINT"))

        # 5) 全局分析按钮
        self.global_analysis_btn.setText(tr("GLOBAL_ANALYSIS"))

        # 6) 语言切换按钮
        self.lang_button.setText(tr("LANG_TOGGLE"))

        # 7) 让 control_panel 也更新
        self.control_panel.refreshUI()

    def switchToChinese(self):
        setLanguage("zh")
        self.control_panel.refreshUI()
        # 如果 main_window 里也有 refreshUI(), 一并调用
        self.refreshUI()

    def switchToEnglish(self):
        setLanguage("en")
        self.control_panel.refreshUI()
        self.refreshUI()


class AnalysisWorker(QObject):
    analysisReady = pyqtSignal(list)  # 发射一个 list, 每个元素是 {'multipv', 'score', 'pv'}

    def __init__(self, engine_mgr, board, depth=25, multipv=1, parent=None):
        super().__init__(parent)
        self.engine_mgr = engine_mgr
        self.board = board.copy()
        self.depth = depth
        self.multipv = multipv

    def run(self):
        try:
            # 调用 engine_manager 里的多PV分析
            infos = self.engine_mgr.analyse_position_multipv(
                self.board, depth=self.depth, multipv=self.multipv
            )
        except Exception as e:
            infos = []  # 分析失败就返回空
        self.analysisReady.emit(infos)
