import streamlit as st

# =========================================================
# TRACE - Streamlit Prototype
# =========================================================

st.set_page_config(
    page_title="TRACE",
    page_icon="⏳",
    layout="centered",
)

# ---------------------------------------------------------
# ステージ定義
# ---------------------------------------------------------

# 0 = 床
# 1 = 壁
# 2 = スイッチ
# 3 = ドア
# 4 = ゴール
# 5 = スタート

LEVEL = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 5, 0, 0, 0, 0, 0, 4, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 2, 0, 3, 1],
    [1, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
]

ROWS = len(LEVEL)
COLS = len(LEVEL[0])

START_POS = (1, 1)
GOAL_POS = (1, 7)
SWITCH_POS = (3, 5)
DOOR_POS = (3, 7)


# ---------------------------------------------------------
# 初期化
# ---------------------------------------------------------

def initialize_game():
    st.session_state.player = START_POS

    # ゴーストの行動履歴
    st.session_state.recorded_moves = []

    # 現在ゴーストが再生している位置
    st.session_state.ghost = None

    # ゴーストの再生位置
    st.session_state.ghost_step = 0

    # フェーズ
    # record = 1回目の行動を記録
    # replay = ゴーストを再生しながらプレイ
    st.session_state.phase = "record"

    st.session_state.switch_active = False
    st.session_state.cleared = False

    st.session_state.message = (
        "まず自由に動いてください。"
        "行動を記録したら「記録終了」を押します。"
    )


if "player" not in st.session_state:
    initialize_game()


# ---------------------------------------------------------
# リセット
# ---------------------------------------------------------

def reset_game():
    initialize_game()


# ---------------------------------------------------------
# マップ判定
# ---------------------------------------------------------

def is_walkable(row, col):
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return False

    tile = LEVEL[row][col]

    # 壁
    if tile == 1:
        return False

    # ドア
    if tile == 3 and not st.session_state.switch_active:
        return False

    return True


# ---------------------------------------------------------
# ゴーストを1ステップ進める
# ---------------------------------------------------------

def move_ghost():
    if st.session_state.phase != "replay":
        return

    moves = st.session_state.recorded_moves

    if st.session_state.ghost_step >= len(moves):
        return

    direction = moves[st.session_state.ghost_step]

    if st.session_state.ghost is None:
        st.session_state.ghost = START_POS

    r, c = st.session_state.ghost

    dr, dc = direction

    nr = r + dr
    nc = c + dc

    # ゴーストも同じマップを移動
    if is_walkable(nr, nc):
        st.session_state.ghost = (nr, nc)

    st.session_state.ghost_step += 1

    # ゴーストがスイッチに乗ったらドアを開く
    if st.session_state.ghost == SWITCH_POS:
        st.session_state.switch_active = True


# ---------------------------------------------------------
# プレイヤー移動
# ---------------------------------------------------------

def move_player(dr, dc):

    # クリア後は操作しない
    if st.session_state.cleared:
        return

    # ゴーストフェーズなら、まずゴーストを1ステップ進める
    if st.session_state.phase == "replay":
        move_ghost()

    r, c = st.session_state.player

    nr = r + dr
    nc = c + dc

    if not is_walkable(nr, nc):
        st.session_state.message = "そこには移動できません。"
        return

    st.session_state.player = (nr, nc)

    # -----------------------------------------------------
    # 記録フェーズ
    # -----------------------------------------------------

    if st.session_state.phase == "record":
        st.session_state.recorded_moves.append((dr, dc))

        if st.session_state.player == SWITCH_POS:
            st.session_state.switch_active = True

        if st.session_state.player == GOAL_POS:
            st.session_state.message = (
                "ゴールに到達しました。"
                "「記録終了」を押してゴーストを作成できます。"
            )

    # -----------------------------------------------------
    # リプレイフェーズ
    # -----------------------------------------------------

    elif st.session_state.phase == "replay":

        if st.session_state.player == GOAL_POS:
            st.session_state.cleared = True
            st.session_state.message = (
                "🎉 CLEAR!\n\n"
                "過去の自分を利用してゴールしました！"
            )


# ---------------------------------------------------------
# 記録終了
# ---------------------------------------------------------

def finish_recording():

    if len(st.session_state.recorded_moves) == 0:
        st.session_state.message = "まだ行動が記録されていません。"
        return

    st.session_state.phase = "replay"

    st.session_state.player = START_POS
    st.session_state.ghost = START_POS
    st.session_state.ghost_step = 0

    st.session_state.switch_active = False

    st.session_state.message = (
        "ゴーストが作成されました！\n\n"
        "今度はゴーストが過去の行動を再生します。"
        "ゴーストにスイッチを押させ、その隙にゴールへ向かいましょう。"
    )


# ---------------------------------------------------------
# マップ描画
# ---------------------------------------------------------

def render_map():

    player = st.session_state.player
    ghost = st.session_state.ghost

    html = """
    <style>
    .trace-board {
        display: grid;
        grid-template-columns: repeat(9, 42px);
        grid-template-rows: repeat(7, 42px);
        gap: 3px;
        justify-content: center;
        margin: 20px 0;
    }

    .tile {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-size: 23px;
        box-sizing: border-box;
    }

    .wall {
        background: #333;
    }

    .floor {
        background: #e8e8e8;
    }

    .switch {
        background: #ffd966;
    }

    .door {
        background: #9fc5e8;
    }

    .door-open {
        background: #b6d7a8;
    }

    .goal {
        background: #d9ead3;
    }

    .player {
        background: #6fa8dc;
        color: white;
        font-weight: bold;
    }

    .ghost {
        background: #b4a7d6;
        color: white;
        font-weight: bold;
        opacity: 0.65;
    }

    .both {
        background: #8e7cc3;
        color: white;
        font-weight: bold;
    }
    """

    html += '<div class="trace-board">'

    for r in range(ROWS):

        for c in range(COLS):

            tile = LEVEL[r][c]

            # 壁
            if tile == 1:
                html += '<div class="tile wall">⬛</div>'
                continue

            # プレイヤーとゴーストの位置
            is_player = player == (r, c)
            is_ghost = ghost == (r, c)

            if is_player and is_ghost:
                html += '<div class="tile both">👤👻</div>'
                continue

            if is_player:
                html += '<div class="tile player">●</div>'
                continue

            if is_ghost:
                html += '<div class="tile ghost">◌</div>'
                continue

            # 通常タイル
            if tile == 2:
                html += '<div class="tile switch">●</div>'

            elif tile == 3:

                if st.session_state.switch_active:
                    html += '<div class="tile door-open">🚪</div>'
                else:
                    html += '<div class="tile door">🔒</div>'

            elif tile == 4:
                html += '<div class="tile goal">⭐</div>'

            else:
                html += '<div class="tile floor"></div>'

    html += "</div>"

    html += """
    <div style="text-align:center; font-size:14px;">
        <b>●</b> プレイヤー　
        <b>◌</b> ゴースト　
        <b>●</b> スイッチ　
        ⭐ ゴール
    </div>
    """

    st.components.v1.html(html, height=380)


# ---------------------------------------------------------
# タイトル
# ---------------------------------------------------------

st.title("⏳ TRACE")

st.caption(
    "「過去の自分」を利用して、現在の自分をゴールへ導くパズル"
)


# ---------------------------------------------------------
# ステータス
# ---------------------------------------------------------

if st.session_state.phase == "record":

    st.info("🔵 RECORD PHASE — 自分の行動を記録しています")

else:

    st.info("🟣 REPLAY PHASE — 過去の自分が動いています")


# ---------------------------------------------------------
# マップ
# ---------------------------------------------------------

render_map()


# ---------------------------------------------------------
# メッセージ
# ---------------------------------------------------------

st.write(st.session_state.message)


# ---------------------------------------------------------
# ステータス情報
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "記録ステップ",
        len(st.session_state.recorded_moves)
    )

with col2:
    if st.session_state.phase == "replay":
        st.metric(
            "ゴースト",
            f"{st.session_state.ghost_step}/"
            f"{len(st.session_state.recorded_moves)}"
        )
    else:
        st.metric("ゴースト", "未作成")

with col3:
    st.metric(
        "スイッチ",
        "ON" if st.session_state.switch_active else "OFF"
    )


# ---------------------------------------------------------
# 操作
# ---------------------------------------------------------

st.subheader("操作")

# 上
col1, col2, col3 = st.columns(3)

with col2:
    if st.button("⬆️", use_container_width=True):
        move_player(-1, 0)
        st.rerun()

# 左・下・右
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️", use_container_width=True):
        move_player(0, -1)
        st.rerun()

with col2:
    if st.button("⬇️", use_container_width=True):
        move_player(1, 0)
        st.rerun()

with col3:
    if st.button("➡️", use_container_width=True):
        move_player(0, 1)
        st.rerun()


# ---------------------------------------------------------
# フェーズ操作
# ---------------------------------------------------------

st.divider()

if st.session_state.phase == "record":

    if st.button(
        "⏺️ 記録終了 → ゴーストを作成",
    ):
    
