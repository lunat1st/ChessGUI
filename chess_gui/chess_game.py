import time
import chess
import chess.pgn

class ChessGame:
    """
    管理单一对局 + 棋钟功能。

    Attributes:
        board (chess.Board): 当前棋盘局面
        game (chess.pgn.Game): 保存整个PGN对局信息
        current_move (chess.pgn.GameNode): 指向PGN树中的最后一手
        initial_time (float): 每方起始时间(秒)
        increment (float): 每步走子后加秒数(秒)
        time_white (float): 白方剩余时间(秒)
        time_black (float): 黑方剩余时间(秒)
        current_side (bool): 当前执棋方, True=白方, False=黑方 (与 board.turn 同步)
        last_timestamp (float): 当前方开始计时时刻 (time.time() 值)
    """

    def __init__(self, initial_time=300, increment=2):
        """
        构造函数:
        :param initial_time: 每方起始时间(秒), 默认为300秒(5分钟).
        :param increment: 每步加秒数(秒), 默认为2秒.
        """
        self.initial_time = initial_time
        self.increment = increment

        # 初始化chess对象
        self.board = chess.Board()
        self.game = chess.pgn.Game()
        self.current_move = None

        # 初始化棋钟
        self.time_white = self.initial_time
        self.time_black = self.initial_time
        self.current_side = chess.WHITE
        self.last_timestamp = time.time()

    def reset(self):
        """
        重置棋盘和PGN信息, 并重置双方时间到初始值。
        """
        self.board.reset()
        self.game = chess.pgn.Game()
        self.current_move = None

        # 重置棋钟
        self.time_white = self.initial_time
        self.time_black = self.initial_time
        self.current_side = chess.WHITE
        self.last_timestamp = time.time()

    def push_move(self, move):
        """
        尝试走一步棋:
          1) 先根据当前方所用时间做扣减, 并加 increment。
          2) 调用 self.board.push(move), 并在 PGN 树中添加该步。
          3) 切换 self.current_side 到对手, 并更新时间戳。

        :param move: chess.Move 对象.
        :return: 该步的 SAN (str), 若不合法返回 None.
        """
        # 1) 检查合法性
        if move not in self.board.legal_moves:
            return None  # 或者 raise ValueError("非法走法")

        # 2) 结算当前方用时
        now = time.time()
        spent = now - self.last_timestamp
        if self.current_side == chess.WHITE:
            self.time_white -= spent
            self.time_white += self.increment
        else:
            self.time_black -= spent
            self.time_black += self.increment

        # 可以在此处判定是否超时(如 self.time_white <= 0)，并设置对局结束标志等

        # 3) 更新对局状态
        san = self.board.san(move)
        self.board.push(move)
        if self.current_move is None:
            # 还在棋谱根节点
            self.current_move = self.game.add_variation(move)
        else:
            self.current_move = self.current_move.add_variation(move)

        # 4) 切换方并更新计时起点
        self.current_side = self.board.turn
        self.last_timestamp = time.time()

        return san

    def pop_move(self):
        """
        撤销上一手(如果有):
        - 从 board.move_stack 中 pop
        - PGN 树回退到 parent
        - 简化: 并不回退时间 (如需完整回退, 需额外保存每步花费).

        :return: 被撤销的move, 若无则返回None。
        """
        if not self.board.move_stack:
            return None

        undone_move = self.board.pop()
        if self.current_move is not None:
            self.current_move = self.current_move.parent

        # 简化: 不恢复时间，如需完整回退, 需在 push_move() 时记录时间花费到栈里
        # 并在 pop_move() 中还原
        self.current_side = self.board.turn
        # 切换方后, 需要更新 last_timestamp, 否则下次扣减会不准确
        self.last_timestamp = time.time()

        return undone_move

    def load_pgn(self, filepath):
        """
        从指定文件加载 PGN 对局并重放到最后。重置时间到起始状态。

        :param filepath: PGN 文件路径
        """
        with open(filepath, "r", encoding="utf-8") as f:
            loaded_game = chess.pgn.read_game(f)
        if loaded_game is None:
            raise ValueError("无法读取PGN, 文件格式有误或为空.")

        self.game = loaded_game
        self.board.reset()
        self.current_move = None

        # 重置棋钟
        self.time_white = self.initial_time
        self.time_black = self.initial_time
        self.current_side = chess.WHITE
        self.last_timestamp = time.time()

        # 重放到主变例末尾 (不扣除用时, 因为这是加载历史棋局)
        for mv in self.game.mainline_moves():
            self.board.push(mv)
            if self.current_move is None:
                self.current_move = self.game.add_variation(mv)
            else:
                self.current_move = self.current_move.add_variation(mv)
        # board.turn 现在是谁，就把 self.current_side 设成谁:
        self.current_side = self.board.turn
        # 若想在重放时模拟时间流逝，需要额外逻辑，这里仅做最简单实现。

    def save_pgn(self, filepath):
        """
        将当前 self.game 写入指定文件。
        :param filepath: 保存PGN的文件路径
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(self.game))

    def is_game_over(self):
        """
        :return: bool, 棋局是否已自然结束(如将杀, 和棋, 等)
                 不包含时间判负, 需额外逻辑判断.
        """
        return self.board.is_game_over()

    def fen(self):
        """
        :return: 当前局面的FEN字符串 (调试或显示用)
        """
        return self.board.fen()

    def get_time_left(self):
        """
        :return: (white_time, black_time), 当前记录的剩余时间(秒),
                 不包含尚未结算的思考用时(即只在上一次 push_move() 后结算).
        """
        return (self.time_white, self.time_black)

    def get_dynamic_time_left(self):
        """
        适合在GUI定时刷新时, 实时获取双方的剩余时间, 包含当前计时方这一步
        尚未结算的用时(即模拟真实的倒计时效果).

        :return: (white_time, black_time), 单位秒
        """
        # 先复制一份
        w_time = self.time_white
        b_time = self.time_black

        now = time.time()
        spent = now - self.last_timestamp

        if self.current_side == chess.WHITE:
            # 白方正在走
            w_time -= spent
        else:
            # 黑方正在走
            b_time -= spent

        return (w_time, b_time)