import streamlit as st

# =========================================================
# TRACE - Player Map Prototype
# =========================================================

st.set_page_config(
    page_title="TRACE",
    page_icon="⏳",
    layout="centered",
)

# =========================================================
# ステージ
# =========================================================

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


# =========================================================
# ゲーム初期化
# =========================================================

def initialize_game():

    st.session_state.player = START_POS

    st.session_state.recorded_moves = []

    st.session_state.ghost = None
    st.session_state.ghost_step = 0

    st.session_state.phase = "record"

    st.session_state.switch_active = False

    st.session_state.cleared = False

    st.session_state.message = (
        "プレイヤーを操作してください。"
    )


if "player" not in st.session_state:
    initialize_game()


# =========================================================
# リセット
# =========================================================

def reset_game():
    initialize_game()


# =========================================================
# 移動可能判定
# =========================================================

def is_walkable(row, col):

    if row < 0 or row >= ROWS:
        return False

    if col < 0 or col >= COLS:
        return False

    tile = LEVEL[row][col]

    # 壁
    if tile == 1:
        return False

    # ドア
    if tile == 3 and not st.session_state.switch_active:
        return False

    return True


# =========================================================
# ゴースト移動
# =========================================================

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

    if is_walkable(nr, nc):
        st.session_state.ghost = (nr, nc)

    st.session_state.ghost_step += 1

    # スイッチを踏んだ
    if st.session_state.ghost == SWITCH_POS:
        st.session_state.switch_active = True


# =========================================================
# プレイヤー移動
# =========================================================

def move_player(dr, dc):

    if st.session_state.cleared:
        return

    # リプレイ中はゴーストも1ステップ進む
    if st.session_state.phase == "replay":
        move_ghost()

    r, c = st.session_state.player

    nr = r + dr
    nc = c + dc

    if not is_walkable(nr, nc):

        st.session_state.message = (
            "そこには移動できません。"
        )

        return

    # プレイヤー位置更新
    st.session_state.player = (nr, nc)

    # -----------------------------------------------------
    # 記録フェーズ
    # -----------------------------------------------------

    if st.session_state.phase == "record":

        st.session_state.recorded_moves.append(
            (dr, dc)
        )

        # プレイヤーがスイッチを踏んだ
        if st.session_state.player == SWITCH_POS:
            st.session_state.switch_active = True

        # ゴール
        if st.session_state.player == GOAL_POS:

            st.session_state.message = (
                "ゴール地点に到達しました。"
                "記録終了を押すとゴーストを作成できます。"
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


# =========================================================
# 記録終了
# =========================================================

def finish_recording():

    if len(st.session_state.recorded_moves) == 0:

        st.session_state.message = (
            "まだ行動が記録されていません。"
        )

        return

    st.session_state.phase = "replay"

    st.session_state.player = START_POS

    st.session_state.ghost = START_POS

    st.session_state.ghost_step = 0

    st.session_state.switch_active = False

    st.session_state.message = (
        "ゴーストが作成されました。\n\n"
        "過去の自分が行動を再生しています。"
    )


# =========================================================
# マップ描画
# =========================================================

def render_map():

    player = st.session_state.player
    ghost = st.session_state.ghost

    # HTML + CSS
    html = """
    <style>

    .map-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .trace-map {

        display: grid;

        grid-template-columns:
        repeat(9, 45px);

        grid-template-rows:
        repeat(7, 45px);

        gap: 3px;

        padding: 8px;

        background: #222;

        border-radius: 10px;

        box-shadow:
        0 4px 12px rgba(0,0,0,0.25);
    }

    .tile {

        width: 45px;
        height: 45px;

        display: flex;

        align-items: center;
        justify-content: center;

        border-radius: 5px;

        font-size: 24px;

        font-weight: bold;

        box-sizing: border-box;
    }

    /* 床 */

    .floor {

        background: #eeeeee;

    }

    /* 壁 */

    .wall {

        background: #333333;

    }

    /* スタート */

    .start {

        background: #d9ead3;

    }

    /* ゴール */

    .goal {

        background: #ffe599;

    }

    /* スイッチ */

    .switch {

        background: #ffd966;

    }

    /* 閉じたドア */

    .door {

        background: #9fc5e8;

    }

    /* 開いたドア */

    .door-open {

        background: #b6d7a8;

    }

    /* プレイヤー */

    .player {

        background: #4285f4;

        color: white;

        border:
        4px solid #174ea6;

        animation:
        player-pulse 1s infinite;

    }

    /* ゴースト */

    .ghost {

        background: #a64d79;

        color: white;

        opacity: 0.65;

    }

    /* プレイヤーとゴーストが同じ場所 */

    .both {

        background: #674ea7;

        color: white;

        border: 4px solid #351c75;

    }

    @keyframes player-pulse {

        0% {
            transform: scale(1);
        }

        50% {
            transform: scale(0.92);
        }

        100% {
            transform: scale(1);
        }

    }

    </style>
    """

    html += '<div class="map-container">'
    html += '<div class="trace-map">'


    # =====================================================
    # 各マスを描画
    # =====================================================

    for r in range(ROWS):

        for c in range(COLS):

            tile = LEVEL[r][c]

            position = (r, c)

            is_player = position == player

            is_ghost = position == ghost


            # -------------------------------------------------
            # 壁
            # -------------------------------------------------

            if tile == 1:

                html += (
                    '<div class="tile wall">⬛</div>'
                )

                continue


            # -------------------------------------------------
            # プレイヤー＋ゴースト
            # -------------------------------------------------

            if is_player and is_ghost:

                html += (
                    '<div class="tile both">P/G</div>'
                )

                continue


            # -------------------------------------------------
            # プレイヤー
            # -------------------------------------------------

            if is_player:

                html += (
                    '<div class="tile player">P</div>'
                )

                continue


            # -------------------------------------------------
            # ゴースト
            # -------------------------------------------------

            if is_ghost:

                html += (
                    '<div class="tile ghost">G</div>'
                )

                continue


            # -------------------------------------------------
            # その他のオブジェクト
            # -------------------------------------------------

            if tile == 2:

                html += (
                    '<div class="tile switch">S</div>'
                )

            elif tile == 3:

                if st.session_state.switch_active:

                    html += (
                        '<div class="tile door-open">D</div>'
                    )

                else:

                    html += (
                        '<div class="tile door">🔒</div>'
                    )

            elif tile == 4:

                html += (
                    '<div class="tile goal">★</div>'
                )

            elif tile == 5:

                html += (
                    '<div class="tile start">START</div>'
                )

            else:

                html += (
                    '<div class="tile floor"></div>'
                )


    html += "</div>"
    html += "</div>"


    # 凡例
    html += """
    <div style="
        text-align:center;
        font-size:14px;
        margin-top:8px;
    ">

    <b>P</b> プレイヤー　
    <b>G</b> ゴースト　
    <b>S</b> スイッチ　
    <b>D</b> ドア　
    <b>★</b> ゴール

    </div>
    """

    st.components.v1.html(
        html,
        height=420
    )


# ======================
# プレイヤー位置情報
# =========================================================

def show_player_position():

    row, col = st.session_state.player

    st.subheader("📍 プレイヤー位置")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "行",
            row
        )

    with col2:

        st.metric(
            "列",
            col
        )

    with col3:

        st.metric(
            "座標",
            f"({row}, {col})"
        )


# =========================================================
# タイトル
# =========================================================

st.title("⏳ TRACE")

st.caption(
    "過去の自分を利用してゴールを目指すパズル"
)


# =========================================================
# フェーズ表示
# =========================================================

if st.session_state.phase == "record":

    st.info(
        "🔵 RECORD PHASE — "
        "プレイヤーの行動を記録しています"
    )

else:

    st.info(
        "🟣 REPLAY PHASE — "
        "ゴーストが過去の行動を再生しています"
    )


# =========================================================
# マップ
# =========================================================

render_map()


# =========================================================
# 現在位置
# =========================================================

show_player_position()


# =========================================================
# 状態
# =========================================================

st.write(
    st.session_state.message
)


# =========================================================
# ステータス
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "記録ステップ",
        len(
            st.session_state.recorded_moves
        )
    )

with col2:

    if st.session_state.phase == "replay":

        st.metric(
            "ゴースト",
            f"{st.session_state.ghost_step}/"
            f"{len(st.session_state.recorded_moves)}"
        )

    else:

        st.metric(
            "ゴースト",
            "未作成"
        )

with col3:

    st.metric(
        "スイッチ",
        "ON"
        if st.session_state.switch_active
        else "OFF"
    )


# =========================================================
# 操作
# =========================================================

st.subheader("🎮 操作")


# 上
col1, col2, col3 = st.columns(3)

with col2:

    if st.button(
        "⬆️",
        use_container_width=True
    ):

        move_player(-1, 0)

        st.rerun()


# 左・下・右
col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "⬅️",
        use_container_width=True
    ):

        move_player(0, -1)

        st.rerun()


with col2:

    if st.button(
        "⬇️",
        use_container_width=True
    ):

        move_player(1, 0)

        st.rerun()


with col3:

    if st.button(
        "➡️",
        use_container_width=True
    ):

        move_player(0, 1)

        st.rerun()


# =========================================================
# 記録終了 / リセット
# =========================================================

st.divider()

if st.session_state.phase == "record":

    if st.button(
        "⏺️ 記録終了 → ゴースト作成",
        use_container_width=True
    ):

        finish_recording()

        st.rerun()

else:

    if st.button(
        "🔄 最初からやり直す",
        use_container_width=True
    ):

        reset_game()

        st.rerun()


# =========================================================
# 座標情報
# =========================================================

with st.expander("🗺️ マップ座標"):

    st.write(
        "マップ左上を (0, 0) としています。"
    )

    st.code(
        f"""
プレイヤー:
行 = {st.session_state.player[0]}
列 = {st.session_state.player[1]}

座標:
{st.session_state.player}
        """
    )


# =========================================================
# 遊び方
# =========================================================

with st.expander("📖 遊び方"):

    st.markdown(
        """
### ① プレイヤーを操作

矢印ボタンで青い **P** を移動させます。

### ② 行動を記録

最初のプレイでは、プレイヤーの移動が自動的に記録されます。

### ③ 記録終了

「記録終了」を押すと、最初のプレイが **G（ゴースト）** になります。

### ④ ゴーストを利用

ゴーストは最初のプレイと同じ行動を繰り返します。

ゴーストが **S（スイッチ）** を踏んでいる間に、自分を移動させます。

### ⑤ ゴール

**★** のゴールへ到達すればクリアです。
"""
    )
