import chess
import chess.engine

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

from board_widget import BoardWidget
from engine_manager import EngineManager
from chess_game import ChessGame

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from language_manager import tr

import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  
matplotlib.rcParams['axes.unicode_minus'] = False

def get_white_perspective_score(score_obj):
    """
    将引擎score统一转换为“白方视角”的兵值(±999=mate)。
    """
    s = score_obj.pov(chess.WHITE)
    if s.is_mate():
        val = s.mate()
        if val is not None:
            return 999 if val > 0 else -999
        else:
            return 0
    else:
        return s.cp / 100.0

def classify_move(actual_move, best_move, best_score_white, second_best_score_white, actual_score_white):
    """
    根据：
      - actual_move vs best_move
      - best_score_white vs second_best_score_white
      - diff = best_score_white - actual_score_white
    来判定:
      "great"/"perfect"/"good"/"mistake"/"blunder" + 对应颜色
    """
    diff = best_score_white - actual_score_white
    abs_diff = abs(diff)

    if actual_move == best_move:
        # 比较best与次佳的差:
        gap = best_score_white - second_best_score_white
        if gap >= 1.5:
            return ("great", "blue")   # 只有此招显著强于次佳
        else:
            return ("perfect", "green")
    else:
        # 不同走法 => 旧逻辑
        if abs_diff >= 2.0:
            return ("blunder", "red")
        elif abs_diff >= 1.0:
            return ("mistake", "orange")
        else:
            return ("good", "black")

class GameAnalysisWorker(QObject):
    """
    后台线程：逐步分析整局，对每一步做分类、统计(包括MultiPV=2, "great"判定)。
    """
    analysisDone = pyqtSignal(dict)

    def __init__(self, chess_game: ChessGame, engine_path: str, depth=12, parent=None):
        super().__init__(parent)
        self.chess_game = chess_game
        self.engine_path = engine_path
        self.depth = depth
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        """
        遍历对局中的每一步：
          1) 未push时 => 用 analyse_once() 获取 (best, second) 评分(白方视角)
          2) push实际走后 => 获取实际评分
          3) 比较 => 分类 => 统计
        """
        engine_mgr = EngineManager(self.engine_path)
        try:
            engine_mgr.start_engine()
        except Exception as e:
            print("分析引擎启动失败:", e)
            self.analysisDone.emit({})
            return

        moves = list(self.chess_game.game.mainline_moves())
        temp_board = chess.Board()

        analysis_moves = []
        # 白/黑误差统计
        white_sum_diff = 0.0
        black_sum_diff = 0.0
        white_count = 0
        black_count = 0

        # 分类次数
        categories = ["great","perfect","good","mistake","blunder"]
        cat_count_white = {k: 0 for k in categories}
        cat_count_black = {k: 0 for k in categories}

        for i, move in enumerate(moves):
            if self._stop_flag:
                break

            side_is_white = temp_board.turn

            # (A) 获取(最佳,次佳)分
            info_best = self.analyse_once(engine_mgr, temp_board)
            if not info_best:
                continue
            best_move = info_best["best_move"]
            best_score_white = info_best["best_score_white"]
            second_score_white = info_best["second_best_score_white"]

            # 为了拿best_move_san
            board_for_san = temp_board.copy()
            try:
                best_move_san = board_for_san.san(best_move)
            except:
                best_move_san = best_move.uci() if best_move else "(None)"

            # (B) 推实际走 => 分析实际评分
            after_board = temp_board.copy()
            after_board.push(move)
            info_actual = self.analyse_once(engine_mgr, after_board)
            if not info_actual:
                continue
            actual_score_white = info_actual["best_score_white"]

            diff = best_score_white - actual_score_white
            diff_abs = abs(diff)

            # (C) 分类
            cat, color = classify_move(
                move,
                best_move,
                best_score_white,
                second_score_white,
                actual_score_white
            )

            # (D) 统计
            if side_is_white:
                white_sum_diff += diff_abs
                white_count += 1
                cat_count_white[cat] += 1
            else:
                black_sum_diff += diff_abs
                black_count += 1
                cat_count_black[cat] += 1

            # (E) 记录
            analysis_moves.append({
                "index": i,
                "move": move,
                "best_move_san": best_move_san,
                "best_score_white": best_score_white,
                "second_best_score_white": second_score_white,
                "actual_score_white": actual_score_white,
                "diff": diff,
                "category": cat,
                "color": color,
                "side_white": side_is_white
            })

            temp_board.push(move)

        engine_mgr.stop_engine()

        # (F) 分开计算平均误差 => 评分(0~10)
        white_avg = (white_sum_diff / white_count) if white_count>0 else 0.0
        black_avg = (black_sum_diff / black_count) if black_count>0 else 0.0
        white_score = max(0, min(10, 10 - white_avg))
        black_score = max(0, min(10, 10 - black_avg))

        result_data = {
            "analysis_moves": analysis_moves,
            "white_score": white_score,
            "black_score": black_score,
            "cat_count_white": cat_count_white,
            "cat_count_black": cat_count_black,
            "moves": moves
        }
        self.analysisDone.emit(result_data)

    def analyse_once(self, engine_mgr, board):
        """
        对 board 用 MultiPV=2 进行一次分析。
        返回: {
            "best_move": Move,
            "best_score_white": float,
            "second_best_score_white": float
        }
        若只得到1条主变，则 second_best_score_white=best_score_white
        """
        try:
            # 注意: 若 python-chess 的 engine.analyse() 不支持多主变,
            #  需要 engine.analysis() 生成器. 这里只是示例:
            info_list = engine_mgr.engine.analyse(
                board,
                limit=chess.engine.Limit(depth=self.depth),
                multipv=2
            )
            if not info_list:
                return None

            # 若 info_list 不是list, 可能 python-chess返回单dict
            if not isinstance(info_list, list):
                # 只有1条
                best_move = info_list.get("pv",[None])[0]
                sc = info_list.get("score")
                scw = get_white_perspective_score(sc) if sc else 0
                return {
                    "best_move": best_move,
                    "best_score_white": scw,
                    "second_best_score_white": scw
                }

            # 可能list: [pv1, pv2, ...]
            best_info = None
            second_info = None
            for it in info_list:
                mpv = it.get("multipv",1)
                if mpv == 1:
                    best_info = it
                elif mpv == 2:
                    second_info = it

            if not best_info:
                return None
            best_move = best_info.get("pv",[None])[0]
            best_score_obj = best_info.get("score",None)
            best_scw = get_white_perspective_score(best_score_obj) if best_score_obj else 0

            if not second_info:
                second_scw = best_scw
            else:
                s2 = second_info.get("score",None)
                second_scw = get_white_perspective_score(s2) if s2 else best_scw

            return {
                "best_move": best_move,
                "best_score_white": best_scw,
                "second_best_score_white": second_scw
            }

        except Exception as e:
            print("analyse_once error:", e)
            return None


class GlobalAnalysisWindow(QWidget):
    def __init__(self, chess_game: ChessGame, analysis_engine_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("ANALYSIS_WINDOW_TITLE"))
        self.resize(1400, 800)

        self.chess_game = chess_game
        self.analysis_engine_path = analysis_engine_path

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # 左: 棋盘
        self.board_widget = BoardWidget(self.chess_game, parent=self)
        main_layout.addWidget(self.board_widget, 3)

        # 中: 棋谱表 + 最佳走法 + 关闭
        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, 2)

        self.move_table = QTableWidget()
        self.move_table.setColumnCount(2)
        self.move_table.setHorizontalHeaderLabels([tr("TABLE_WHITE"), tr("TABLE_BLACK")])
        self.move_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.move_table.cellClicked.connect(self.onTableCellClicked)
        center_layout.addWidget(self.move_table, 4)

        self.label_best_move = QLabel(tr("BEST_MOVE_LABEL"))
        center_layout.addWidget(self.label_best_move, 0)

        self.btn_close = QPushButton(tr("CLOSE_ANALYSIS_WINDOW"))
        self.btn_close.clicked.connect(self.onCloseClicked)
        center_layout.addWidget(self.btn_close, 0)

        # 右: 图表 + 评价
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 3)

        self.figure = Figure(figsize=(5,4))
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas, 4)
        self.ax = self.figure.add_subplot(111)

        self.label_summary = QLabel(tr("SUMMARY_LABEL"))
        right_layout.addWidget(self.label_summary, 1)

        self.cid = self.canvas.mpl_connect("button_press_event", self.onChartClicked)
        self.current_step_line = None

        self.analysis_thread = QThread(self)
        self.analysis_worker = GameAnalysisWorker(
            self.chess_game,
            self.analysis_engine_path,
            depth=12
        )
        self.analysis_worker.moveToThread(self.analysis_thread)
        self.analysis_worker.analysisDone.connect(self.onAnalysisDone)
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_thread.start()

        self.fen_list = []
        self.prepareFenList()

        self.analysis_moves = []

    def prepareFenList(self):
        temp_board = chess.Board()
        self.fen_list.append(temp_board.fen())
        for mv in self.chess_game.game.mainline_moves():
            temp_board.push(mv)
            self.fen_list.append(temp_board.fen())

    def onAnalysisDone(self, result_data):
        if not result_data:
            self.label_summary.setText(tr("ANALYSIS_FAILED_OR_EMPTY"))
            return

        self.analysis_moves = result_data["analysis_moves"]
        moves = result_data["moves"]
        white_score = result_data["white_score"]
        black_score = result_data["black_score"]
        cat_white = result_data["cat_count_white"]
        cat_black = result_data["cat_count_black"]

        # 1) 填充棋谱表
        self.move_table.setRowCount(0)
        temp_board = chess.Board()
        row = 0
        for i, mv in enumerate(moves):
            is_white = temp_board.turn
            san_str = temp_board.san(mv)
            temp_board.push(mv)

            if is_white:
                row = self.move_table.rowCount()
                self.move_table.insertRow(row)
                self.move_table.setItem(row, 0, QTableWidgetItem(san_str))
                self.move_table.setItem(row, 1, QTableWidgetItem(""))
            else:
                self.move_table.setItem(row, 1, QTableWidgetItem(san_str))

        # 2) 绘制评估曲线
        x_vals = []
        y_vals = []
        c_vals = []
        for item in self.analysis_moves:
            x = item["index"] + 1
            y = item["actual_score_white"]
            if y>5: y=5
            if y<-5: y=-5
            x_vals.append(x)
            y_vals.append(y)
            c_vals.append(item["color"])

        self.ax.clear()
        self.ax.set_title(tr("AX_TITLE"))
        self.ax.set_xlabel(tr("AX_XLABEL"))
        self.ax.set_ylabel(tr("AX_YLABEL"))
        self.ax.set_ylim(-5, 5)

        for i in range(len(x_vals)):
            self.ax.scatter(x_vals[i], y_vals[i], color=c_vals[i])
        self.ax.plot(x_vals, y_vals, linestyle='-', color='gray', alpha=0.3)
        self.canvas.draw()

        # 3) 显示统计
        #   用 tr("WHITE_SCORE_PREFIX")、"BLACK_SCORE_PREFIX"、"CAT_GREAT"等
        txt = (
            f"{tr('WHITE_SCORE_PREFIX')} {white_score:.2f}\n"
            f"  {tr('CAT_GREAT')}={cat_white['great']}, {tr('CAT_PERFECT')}={cat_white['perfect']}, "
            f"{tr('CAT_GOOD')}={cat_white['good']}, {tr('CAT_MISTAKE')}={cat_white['mistake']}, {tr('CAT_BLUNDER')}={cat_white['blunder']}\n\n"
            f"{tr('BLACK_SCORE_PREFIX')} {black_score:.2f}\n"
            f"  {tr('CAT_GREAT')}={cat_black['great']}, {tr('CAT_PERFECT')}={cat_black['perfect']}, "
            f"{tr('CAT_GOOD')}={cat_black['good']}, {tr('CAT_MISTAKE')}={cat_black['mistake']}, {tr('CAT_BLUNDER')}={cat_black['blunder']}\n"
        )
        self.label_summary.setText(txt)

    def onChartClicked(self, event):
        if event.xdata is None:
            return
        move_idx = int(round(event.xdata))
        if move_idx<0:
            move_idx=0

        self.updateCurrentStepLine(move_idx)

        if move_idx>=len(self.fen_list):
            move_idx=len(self.fen_list)-1
        fen = self.fen_list[move_idx]
        self.board_widget.chess_game.board.set_fen(fen)
        self.board_widget.update()

        if move_idx>0:
            row = (move_idx-1)//2
            col = (move_idx-1)%2
            self.move_table.setCurrentCell(row,col)

        self.showBestMove(move_idx)

    def onTableCellClicked(self, row, col):
        move_idx = row*2 + col + 1
        if move_idx>=len(self.fen_list):
            move_idx=len(self.fen_list)-1
        self.updateCurrentStepLine(move_idx)

        fen = self.fen_list[move_idx]
        self.board_widget.chess_game.board.set_fen(fen)
        self.board_widget.update()

        self.showBestMove(move_idx)

    def showBestMove(self, move_idx):
        idx = move_idx - 1
        if idx<0 or idx>=len(self.analysis_moves):
            self.label_best_move.setText(tr("BEST_MOVE_LABEL"))
            return
        best_san = self.analysis_moves[idx]["best_move_san"]
        cat = self.analysis_moves[idx]["category"]
        self.label_best_move.setText(
            f"{tr('BEST_MOVE_LABEL')} {best_san} (分类: {cat})"
        )

    def updateCurrentStepLine(self, x):
        if self.current_step_line is not None:
            self.current_step_line.remove()
            self.current_step_line = None
        self.current_step_line = self.ax.axvline(x, color='green', linestyle='--', lw=2)
        self.canvas.draw()

    def onCloseClicked(self):
        self.close()

    def closeEvent(self, event):
        if self.analysis_thread.isRunning():
            self.analysis_worker.stop()
            self.analysis_thread.quit()
            self.analysis_thread.wait()
        super().closeEvent(event)

    def refreshUI(self):
        """
        在语言切换后, 重设窗口标题、按钮文字、表头、图表标题等.
        """
        self.setWindowTitle(tr("ANALYSIS_WINDOW_TITLE"))
        self.btn_close.setText(tr("CLOSE_ANALYSIS_WINDOW"))
        self.label_best_move.setText(tr("BEST_MOVE_LABEL"))
        self.label_summary.setText(tr("SUMMARY_LABEL"))

        # 表头
        self.move_table.setHorizontalHeaderLabels([tr("TABLE_WHITE"), tr("TABLE_BLACK")])

        # 图表标题
        self.ax.set_title(tr("AX_TITLE"))
        self.ax.set_xlabel(tr("AX_XLABEL"))
        self.ax.set_ylabel(tr("AX_YLABEL"))
        self.canvas.draw()