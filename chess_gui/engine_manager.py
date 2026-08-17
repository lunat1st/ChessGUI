import chess
import chess.engine

class EngineManager:
    """
    管理AI引擎：启动/停止，引擎思考得到最佳走法或进行局面分析。
    """

    def __init__(self, engine_path=None):
        self.engine_path = engine_path
        self.engine = None

    def start_engine(self, engine_path=None):
        """
        启动引擎。如果 engine_path 不为空则更新路径。
        若已有引擎，则先关闭。
        """
        if engine_path:
            self.engine_path = engine_path
        if not self.engine_path:
            raise ValueError("未指定AI引擎路径")

        self.stop_engine()  # 先尝试关掉旧引擎
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        except Exception as e:
            self.engine = None
            raise RuntimeError(f"无法启动引擎: {e}")

    def stop_engine(self):
        """关闭引擎"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
            self.engine = None

    def get_best_move(self, board, time_limit=0.1):
        """
        让引擎在 board 上搜索并返回最佳走法 chess.Move.
        time_limit: 思考时间 (秒).
        """
        if not self.engine:
            raise RuntimeError("AI引擎尚未启动")

        result = self.engine.play(board, limit=chess.engine.Limit(time=time_limit))
        return result.move


    def analyse_position_multipv(self, board, depth=25, multipv=1):
        """
        对 board 做多主变分析(MultiPV)并返回多条信息。
        multipv: 需要几条主变(1~5)，depth: 搜索深度。
        返回: 一个列表，每个元素是一个字典，
             例如 [{ 'pv': [moves...], 'score': ..., 'multipv': 1}, {...}, ...]
        """
        if not self.engine:
            raise RuntimeError("AI引擎尚未启动")

        # 设置 MultiPV 选项
        #self.engine.configure({"MultiPV": multipv})
 
       # python-chess 提供两种方式：
       # 1) engine.analyse() 一次只能返回最佳线(不支持多线路?)
       # 2) engine.analysis() 生成器模式
       # 这里演示 2) 的用法
        infos = []
        with self.engine.analysis(
            board, limit=chess.engine.Limit(depth=depth), multipv=multipv
        ) as analysis:
            for info in analysis:
                # info 是个字典，包含 "score", "pv", "multipv" 等
                if "multipv" in info:
                    # 说明是一次完整的多pv输出
                    # 复制想要的字段
                    data = {
                        "multipv": info["multipv"],
                        "score": info.get("score"),
                        "pv": info.get("pv", []),
                    }
                    infos.append(data)
                # 当收集到 multipv 条后可以 break
                if len(infos) >= multipv:
                    break
        return infos

    def __del__(self):
        self.stop_engine()