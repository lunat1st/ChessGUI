LANG_DICT = {
    "en": {
        # --- Window Titles / Buttons ---
        "APP_TITLE":          "PyChess - AI vs Human",
        "GLOBAL_ANALYSIS":    "Game Analysis",

        # --- Clock Labels ---
        "WHITE_CLOCK":        "White: ",
        "BLACK_CLOCK":        "Black: ",

        # --- Table Headers ---
        "TABLE_WHITE":        "White",
        "TABLE_BLACK":        "Black",

        # --- Analysis Text Placeholder ---
        "ANALYSIS_HINT":      "If analysis is enabled, multiPV results appear here...",

        # --- MessageBox Titles ---
        "ERROR":              "Error",
        "WARNING":            "Warning",
        "INFO":               "Information",

        # --- MessageBox Content ---
        "WHITE_ENGINE_FAIL":  "White engine failed to start: ",
        "BLACK_ENGINE_FAIL":  "Black engine failed to start: ",
        "WHITE_AI_PATH_EMPTY":"White AI path is empty, treating as Human.",
        "BLACK_AI_PATH_EMPTY":"Black AI path is empty, treating as Human.",
        "GAME_OVER":          "Game Over",
        "GAME_ENDED":         "The game has ended",
        "ILLEGAL_MOVE":       "Illegal move!",
        "AI_TIME_UP":         "AI's time is up!",
        "SAVE_FAILED":        "Failed to save PGN: ",
        "LOAD_FAILED":        "Failed to load PGN: ",
        "AI_NO_MOVE":         "AI returned an empty move!",
        "AI_ILLEGAL_MOVE":    "AI made an illegal move?",
        "ANALYSIS_FAIL":      "Analysis failed or no result.",

        # ------------------------------
        # The following are specifically for control_panel.py
        # ------------------------------
        "WHITE_LABEL":        "White:",
        "BLACK_LABEL":        "Black:",
        "HUMAN":              "Human",
        "AI":                 "AI",
        "WHITE_PATH_HINT":    "Engine Path (optional)",
        "BLACK_PATH_HINT":    "Engine Path (optional)",
        "BROWSE":             "Browse",
        "ANALYSIS_ENABLE":    "Enable Analysis",
        "ANALYSIS_ENGINE":    "Analysis Engine:",
        "MULTIPV_LABEL":      "MultiPV:",
        "TIME_LIMIT":         "Time (minutes):",
        "INCREMENT_LABEL":    "Increment (seconds):",
        "NEW_GAME":           "New Game",
        "SAVE_PGN":           "Save PGN",
        "LOAD_PGN":           "Load PGN",

        "LANG_TOGGLE": "中文",

        "ANALYSIS_WINDOW_TITLE":   "Game Analysis Window",
        "CLOSE_ANALYSIS_WINDOW":   "Close Analysis Window",
        "BEST_MOVE_LABEL":         "Best Move: (none)",
        "SUMMARY_LABEL":           "Analysis not done yet.",
        "AX_TITLE":                "Score from White's Perspective (clamped ±5)",
        "AX_XLABEL":               "Move index",
        "AX_YLABEL":               "White advantage(+) / Black advantage(-)",
        "ANALYSIS_FAILED_OR_EMPTY":"Analysis failed or interrupted.",
        "WHITE_SCORE_PREFIX":  "White Score:",
        "BLACK_SCORE_PREFIX":  "Black Score:",
        "CAT_GREAT":           "great",
        "CAT_PERFECT":         "perfect",
        "CAT_GOOD":            "good",
        "CAT_MISTAKE":         "mistake",
        "CAT_BLUNDER":         "blunder",
    },

    "zh": {
        # --- Window Titles / Buttons ---
        "APP_TITLE":          "PyChess - AI vs Human(中文)",
        "GLOBAL_ANALYSIS":    "全局分析",

        # --- Clock Labels ---
        "WHITE_CLOCK":        "白方：",
        "BLACK_CLOCK":        "黑方：",

        # --- Table Headers ---
        "TABLE_WHITE":        "白方",
        "TABLE_BLACK":        "黑方",

        # --- Analysis Text Placeholder ---
        "ANALYSIS_HINT":      "若启用分析，可在此处查看多PV结果...",

        # --- MessageBox Titles ---
        "ERROR":              "错误",
        "WARNING":            "警告",
        "INFO":               "提示",

        # --- MessageBox Content ---
        "WHITE_ENGINE_FAIL":  "白方引擎启动失败: ",
        "BLACK_ENGINE_FAIL":  "黑方引擎启动失败: ",
        "WHITE_AI_PATH_EMPTY":"白方AI路径为空，视为人类。",
        "BLACK_AI_PATH_EMPTY":"黑方AI路径为空，视为人类。",
        "GAME_OVER":          "游戏结束",
        "GAME_ENDED":         "棋局已结束",
        "ILLEGAL_MOVE":       "非法走法!",
        "AI_TIME_UP":         "AI时间耗尽!",
        "SAVE_FAILED":        "PGN保存失败: ",
        "LOAD_FAILED":        "PGN加载失败: ",
        "AI_NO_MOVE":         "AI返回空走法!",
        "AI_ILLEGAL_MOVE":    "AI走了不合法招?",
        "ANALYSIS_FAIL":      "分析失败或无结果。",

        # ------------------------------
        # The following are specifically for control_panel.py
        # ------------------------------
        "WHITE_LABEL":        "白方:",
        "BLACK_LABEL":        "黑方:",
        "HUMAN":              "人类",
        "AI":                 "AI",
        "WHITE_PATH_HINT":    "AI引擎路径(可选)",
        "BLACK_PATH_HINT":    "AI引擎路径(可选)",
        "BROWSE":             "浏览",
        "ANALYSIS_ENABLE":    "启用局面分析",
        "ANALYSIS_ENGINE":    "分析引擎:",
        "MULTIPV_LABEL":      "MultiPV:",
        "TIME_LIMIT":         "时限(分钟):",
        "INCREMENT_LABEL":    "加秒:",
        "NEW_GAME":           "开始新对局",
        "SAVE_PGN":           "保存PGN",
        "LOAD_PGN":           "加载PGN",

        "LANG_TOGGLE": "English",

        "ANALYSIS_WINDOW_TITLE":   "全局分析窗口",
        "CLOSE_ANALYSIS_WINDOW":   "关闭分析窗口",
        "BEST_MOVE_LABEL":         "最佳走法: (未选中)",
        "SUMMARY_LABEL":           "对局评价: 尚未完成分析",
        "AX_TITLE":                "以白方视角显示评分(±5封顶)",
        "AX_XLABEL":               "回合数",
        "AX_YLABEL":               "白方优势(+) / 黑方优势(-)",
        "ANALYSIS_FAILED_OR_EMPTY":"分析失败或中断。",
        "WHITE_SCORE_PREFIX":  "白方得分:",
        "BLACK_SCORE_PREFIX":  "黑方得分:",
        "CAT_GREAT":           "绝佳",
        "CAT_PERFECT":         "完美",
        "CAT_GOOD":            "正常",
        "CAT_MISTAKE":         "失误",
        "CAT_BLUNDER":         "严重失误",
    }
}

current_language = "en"

def tr(key):
    """Return the current language translation for the given key."""
    return LANG_DICT[current_language].get(key, key)

def setLanguage(lang):
    """Switch language: 'en' or 'zh'."""
    global current_language
    if lang in LANG_DICT:
        current_language = lang
