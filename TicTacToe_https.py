import streamlit as st
from time import time

# 自定义样式（直接嵌入到代码中）
def add_custom_styles():
    st.markdown("""
    <style>
    /* 全局样式 */
    body {
        background-color: #f4f4f9;
        font-family: 'Arial', sans-serif;
    }

    h1 {
        color: #333;
        text-align: center;
    }

    /* 棋盘容器 */
    .board-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        width: 100%;
        max-width: 300px; /* 限制棋盘总宽度 */
        margin: 0 auto;
    }

    /* 按钮样式 */
    div.stButton > button {
        width: 80px; /* 按钮宽度 */
        height: 80px; /* 按钮高度 */
        font-size: 24px;
        font-weight: bold;
        border: 2px solid #ddd;
        border-radius: 8px;
        background-color: #fff;
        color: #333;
        transition: all 0.3s ease;
        margin: 5px; /* 按钮间距 */
    }

    div.stButton > button:hover {
        background-color: #f0f0f0;
        transform: scale(1.05);
    }

    div.stButton > button:disabled {
        background-color: #e0e0e0;
        cursor: not-allowed;
    }

    /* 响应式布局 */
    @media (max-width: 768px) {
        div.stButton > button {
            width: 60px; /* 手机端按钮宽度 */
            height: 60px; /* 手机端按钮高度 */
            font-size: 18px; /* 手机端字体大小 */
        }
    }

    /* 游戏结果提示 */
    .game-result {
        font-size: 16px;
        text-align: center;
        margin-top: 20px;
        padding: 10px;
        border-radius: 5px;
    }

    .success {
        background-color: #d4edda;
        color: #155724;
    }

    .error {
        background-color: #f8d7da;
        color: #721c24;
    }

    .info {
        background-color: #cce5ff;
        color: #0c5460;
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化游戏状态
class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9  # 棋盘状态
        self.current_player = 'X'  # 当前玩家
        self.human = 'X'  # 人类玩家
        self.ai = 'O'  # AI玩家
        self.total_time = 0  # 总时间

    def is_winner(self, player):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 横向
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 纵向
            [0, 4, 8], [2, 4, 6]              # 对角线
        ]
        for condition in win_conditions:
            if all(self.board[i] == player for i in condition):
                return True
        return False

    def is_draw(self):
        return ' ' not in self.board

    def is_game_over(self):
        return self.is_winner(self.human) or self.is_winner(self.ai) or self.is_draw()

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def make_move(self, move, player):
        self.board[move] = player

    def undo_move(self, move):
        self.board[move] = ' '

# Alpha-Beta 剪枝搜索
def alpha_beta_search(game, depth, alpha, beta, maximizing_player):
    if game.is_winner(game.ai):
        return 10 - depth
    if game.is_winner(game.human):
        return depth - 10
    if game.is_draw() or depth == 0:
        return 0

    if maximizing_player:
        max_eval = float('-inf')
        for move in game.available_moves():
            game.make_move(move, game.ai)
            eval = alpha_beta_search(game, depth - 1, alpha, beta, False)
            game.undo_move(move)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in game.available_moves():
            game.make_move(move, game.human)
            eval = alpha_beta_search(game, depth - 1, alpha, beta, True)
            game.undo_move(move)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def best_move(game):
    start_time = time()
    best_score = float('-inf')
    move = None
    for possible_move in game.available_moves():
        game.make_move(possible_move, game.ai)
        score = alpha_beta_search(game, 9, float('-inf'), float('inf'), False)
        game.undo_move(possible_move)
        if score > best_score:
            best_score = score
            move = possible_move
    end_time = time()
    print(f"AI思考时间: {end_time - start_time:.4f}秒")
    game.total_time += end_time - start_time
    return move

# Streamlit 应用
def main():
    # 添加自定义样式
    add_custom_styles()

    # 设置标题
    st.title("井字棋 🎮")
    st.markdown('<p style="text-align: center; font-size: 16px;">和 AI 对弈，点击空格开始操作！</p>', unsafe_allow_html=True)

    # 初始化游戏状态
    if "game" not in st.session_state:
        st.session_state.game = TicTacToe()

    game = st.session_state.game

    # 创建棋盘布局
    st.markdown('<div class="board-container">', unsafe_allow_html=True)
    cols = st.columns(3)
    for i in range(9):
        row, col = divmod(i, 3)
        with cols[col]:
            button_label = "❌" if game.board[i] == 'X' else "⭕" if game.board[i] == 'O' else ""
            if st.button(button_label or " ", key=f"button_{i}", disabled=game.board[i] != ' ' or game.is_game_over()):
                if game.board[i] == ' ' and not game.is_game_over():
                    game.make_move(i, game.human)
                    if not game.is_game_over():
                        ai_move = best_move(game)
                        game.make_move(ai_move, game.ai)
    st.markdown('</div>', unsafe_allow_html=True)

    # 显示游戏结果
    result_class = ""
    if game.is_winner(game.human):
        result_class = "success"
        result_message = "🎉 你赢了！🎉"
    elif game.is_winner(game.ai):
        result_class = "error"
        result_message = "🤖 AI赢了！🤖（多练练哈）🤲"
    elif game.is_draw():
        result_class = "info"
        result_message = "🤝 平局！🤝"
    else:
        result_message = f"总时间: {game.total_time:.4f}秒"

    if result_class:
        st.markdown(f'<div class="game-result {result_class}">{result_message}</div>', unsafe_allow_html=True)
    else:
        st.write(result_message)

    # 重置按钮
    if st.button("重新开始"):
        st.session_state.game = TicTacToe()

if __name__ == "__main__":
    main()