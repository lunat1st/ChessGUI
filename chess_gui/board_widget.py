import chess
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QPushButton


class BoardWidget(QWidget):
    """
    一个棋盘控件，用PNG图像来绘制棋子。支持鼠标拖拽落子，发射 moveMade 信号。
    
    Attributes:
        moveMade (pyqtSignal): 当用户在棋盘上完成一次落子(松开鼠标)后，会发射一个
                               moveMade(chess.Move) 信号，让上层处理。
        chess_game: 一个外部的对象，包含 self.chess_game.board (chess.Board) 和对局信息。
        
    Usage:
        1. 在 __init__ 里加载PNG图像到 self.piece_images。
        2. 在 paintEvent() -> drawBoard() / drawPieces() / drawHighlights()
           绘制出棋盘格、棋子、高亮。
        3. 在鼠标事件里维护拖拽信息，松开时发射 moveMade 信号。
    """

    # 当用户释放鼠标形成一个走法后发射的信号
    # 由外部 (main_window) 连接来决定怎么 push_move 等逻辑
    moveMade = pyqtSignal(chess.Move)

    # 每个格子的像素大小
    SQUARE_SIZE = 60

    def __init__(self, chess_game, parent=None):
        super().__init__(parent)
        self.chess_game = chess_game

        # 拖拽状态
        self.drag_start_square = None
        self.dragging_piece = None
        self.drag_offset = QPoint(0, 0)
        self.current_pos = QPoint(0, 0)

        # 高亮用：存储某些目标格子
        self.highlight_squares = []

        # 固定控件大小为 8×8
        self.setFixedSize(self.SQUARE_SIZE * 8, self.SQUARE_SIZE * 8)

        # --- 加载PNG图像 ---
        # 请在项目里确保这些路径和文件都存在
        self.piece_images = {
            'P': QPixmap("chess_gui/assets/white_pawn.png"),
            'R': QPixmap("chess_gui/assets/white_rook.png"),
            'N': QPixmap("chess_gui/assets/white_knight.png"),
            'B': QPixmap("chess_gui/assets/white_bishop.png"),
            'Q': QPixmap("chess_gui/assets/white_queen.png"),
            'K': QPixmap("chess_gui/assets/white_king.png"),
            'p': QPixmap("chess_gui/assets/black_pawn.png"),
            'r': QPixmap("chess_gui/assets/black_rook.png"),
            'n': QPixmap("chess_gui/assets/black_knight.png"),
            'b': QPixmap("chess_gui/assets/black_bishop.png"),
            'q': QPixmap("chess_gui/assets/black_queen.png"),
            'k': QPixmap("chess_gui/assets/black_king.png"),
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawBoard(painter)
        self.drawHighlights(painter)
        self.drawPieces(painter)

    def drawBoard(self, painter):
        """ 绘制8×8棋格 """
        for row in range(8):
            for col in range(8):
                # 浅色与深色
                color_light = QColor(238, 238, 210)  # 米黄色
                color_dark  = QColor(118, 150, 86)   # 绿色
                color = color_light if (row + col) % 2 else color_dark
                painter.fillRect(
                    col * self.SQUARE_SIZE,
                    (7 - row) * self.SQUARE_SIZE,
                    self.SQUARE_SIZE,
                    self.SQUARE_SIZE,
                    color
                )

    def drawHighlights(self, painter):
        """
        使用半透明颜色高亮 self.highlight_squares 中的目标格子
        """
        highlight_color = QColor(255, 255, 0, 100)
        for sq in self.highlight_squares:
            file_ = chess.square_file(sq)
            rank_ = chess.square_rank(sq)
            rect = QRect(
                file_ * self.SQUARE_SIZE,
                (7 - rank_) * self.SQUARE_SIZE,
                self.SQUARE_SIZE,
                self.SQUARE_SIZE
            )
            painter.fillRect(rect, highlight_color)

    def drawPieces(self, painter):
        """
        根据 self.chess_game.board 显示所有棋子。
        若某个棋子正在被拖拽，则在原位置留空，改到鼠标处画该棋子。
        """
        board = self.chess_game.board

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue

            # 如果此棋子正在被拖拽，就不画在原地
            if self.dragging_piece and square == self.drag_start_square:
                continue

            file_ = chess.square_file(square)
            rank_ = chess.square_rank(square)
            rect = QRect(
                file_ * self.SQUARE_SIZE,
                (7 - rank_) * self.SQUARE_SIZE,
                self.SQUARE_SIZE,
                self.SQUARE_SIZE
            )

            symbol = piece.symbol()  # 'P','R','N','B','Q','K' (大写=白)
            pixmap = self.piece_images.get(symbol)
            if pixmap:
                # 根据格子大小适当缩放
                scaled = pixmap.scaled(
                    self.SQUARE_SIZE, self.SQUARE_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                painter.drawPixmap(rect, scaled)

        # 如果有正在被拖动的棋子，在鼠标处绘制
        if self.dragging_piece:
            piece_rect = QRect(
                self.current_pos.x() - self.drag_offset.x() - self.SQUARE_SIZE // 2,
                self.current_pos.y() - self.drag_offset.y() - self.SQUARE_SIZE // 2,
                self.SQUARE_SIZE,
                self.SQUARE_SIZE
            )
            symbol = self.dragging_piece.symbol()
            pixmap = self.piece_images.get(symbol)
            if pixmap:
                scaled = pixmap.scaled(
                    self.SQUARE_SIZE, self.SQUARE_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                painter.drawPixmap(piece_rect, scaled)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        file_ = event.x() // self.SQUARE_SIZE
        rank_ = 7 - (event.y() // self.SQUARE_SIZE)
        # 防越界
        file_ = max(0, min(7, file_))
        rank_ = max(0, min(7, rank_))
        square = chess.square(file_, rank_)

        board = self.chess_game.board
        piece = board.piece_at(square)

        # 若有棋子且是当前行棋方，则开始拖拽
        if piece and piece.color == board.turn:
            self.drag_start_square = square
            self.dragging_piece = piece
            # 计算鼠标点击点相对格子中心的偏移
            square_rect = QRect(
                file_ * self.SQUARE_SIZE,
                (7 - rank_) * self.SQUARE_SIZE,
                self.SQUARE_SIZE,
                self.SQUARE_SIZE
            )
            center = square_rect.center()
            self.drag_offset = event.pos() - center

            # 高亮可能走到的格子
            self.highlight_squares = []
            for mv in board.legal_moves:
                if mv.from_square == square:
                    self.highlight_squares.append(mv.to_square)

            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging_piece:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.dragging_piece:
            return

        file_ = event.x() // self.SQUARE_SIZE
        rank_ = 7 - (event.y() // self.SQUARE_SIZE)
        file_ = max(0, min(7, file_))
        rank_ = max(0, min(7, rank_))
        target_square = chess.square(file_, rank_)

        piece = self.dragging_piece
        move = chess.Move(self.drag_start_square, target_square)

        # 检查兵升变
        if piece.piece_type == chess.PAWN:
            # 判断是否到达末行
            target_rank = chess.square_rank(target_square)
            if (piece.color == chess.WHITE and target_rank == 7) or \
               (piece.color == chess.BLACK and target_rank == 0):
                promotion_piece = self.showPromotionDialog()
                if promotion_piece is not None:
                    move = chess.Move(self.drag_start_square, target_square, promotion=promotion_piece)

        # 发射信号，让上层处理是否 push_move()
        self.moveMade.emit(move)

        # 清理拖拽状态
        self.drag_start_square = None
        self.dragging_piece = None
        self.highlight_squares = []
        self.update()

    def showPromotionDialog(self):
        """
        简单对话框，让用户选择升变为: Q,R,B,N
        若用户取消则返回None
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Promotion")
        layout = QHBoxLayout()
        dialog.setLayout(layout)

        promotions = [
            ("Queen", chess.QUEEN),
            ("Rook", chess.ROOK),
            ("Bishop", chess.BISHOP),
            ("Knight", chess.KNIGHT),
        ]
        dialog.selected_piece = None

        def onSelect(piece_type):
            dialog.selected_piece = piece_type
            dialog.accept()

        for label, pt in promotions:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, x=pt: onSelect(x))
            layout.addWidget(btn)

        dialog.exec_()
        return dialog.selected_piece