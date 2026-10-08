from pathlib import Path

code = r'''import streamlit as st
import time

# ============================================================
# TRACE - Complete Streamlit Prototype
# One-file game
# ============================================================

st.set_page_config(
    page_title="TRACE",
    page_icon="⏳",
    layout="centered",
)

# ------------------------------------------------------------
# Game constants
# ------------------------------------------------------------

WALL = "#"
FLOOR = "."
SWITCH = "S"
DOOR = "D"
GOAL = "G"
START = "P"
CRATE = "C"
HAZARD = "X"

TILE = {
    WALL: "⬛",
    FLOOR: "",
    SWITCH: "🟡",
    DOOR: "🚪",
    GOAL: "⭐",
    START: "◎",
    CRATE: "📦",
    HAZARD: "⚠️",
}

# Levels are deliberately small so they work well on phones.
# Legend:
# # wall, . floor, S switch, D door, G goal, P start, C crate, X hazard
LEVELS = [
    {
        "name": "First Echo",
        "map": [
            "#########",
            "#P.....G#",
            "#.#####.#",
            "#....S.D#",
            "#########",
        ],
        "hint": "最初の行動をゴーストに任せ、開いたドアを通ろう。",
    },
    {
        "name": "Two Timelines",
        "map": [
            "###########",
            "#P........#",
            "#.#######.#",
            "#....S....#",
            "#####D#####",
            "#.........#",
            "#........G#",
            "###########",
        ],
        "hint": "ゴーストがスイッチを踏むタイミングを利用しよう。",
    },
    {
        "name": "The Long Echo",
        "map": [
            "#############",
            "#P.........G#",
            "#.#########.#",
            "#...........#",
            "#.#########.#",
            "#...........#",
            "#####S.D#####",
            "#############",
        ],
        "hint": "長いルートを記録し、ゴーストをスイッチまで到達させよう。",
    },
    {
        "name": "Crossing",
        "map": [
            "#############",
            "#P....#.....#",
            "#.##..#..##.#",
            "#....S#.....#",
            "#######D#####",
            "#...........#",
            "#..........G#",
            "#############",
        ],
        "hint": "壁の向こうのスイッチをゴーストに押させよう。",
    },
    {
        "name": "Final Echo",
        "map": [
            "###############",
            "#P............#",
            "#.###########.#",
            "#.....S.......#",
            "#####.#####D###",
            "#.....#.......#",
            "#.###.#.#####.#",
            "#.............G",
            "###############",
        ],
        "hint": "最後のステージ。過去の自分のルートそのものが攻略法になる。",
    },
]

# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------

def load_level(index):
    level = LEVELS[index]
    grid = [list(row) for row in level["map"]]

    start = None
    goal = None

    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == START:
                start = (r, c)
                grid[r][c] = FLOOR
            elif value == GOAL:
                goal = (r, c)
                grid[r][c] = GOAL

    st.session_state.grid = grid
    st.session_state.start = start
    st.session_state.goal = goal
    st.session_state.player = start
    st.session_state.ghost = None

    st.session_state.moves = []
    st.session_state.ghost_index = 0

    st.session_state.phase = "record"
    st.session_state.switch_on = False
    st.session_state.cleared = False
    st.session_state.level_start_time = time.time()
    st.session_state.message = "青いPを操作して行動を記録してください。"


def new_game():
    st.session_state.level_index = 0
    load_level(0)


if "level_index" not in st.session_state:
    new_game()

# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def inside(pos):
    r, c = pos
    return (
        0 <= r < len(st.session_state.grid)
        and 0 <= c < len(st.session_state.grid[0])
    )


def tile_at(pos):
    r, c = pos
    return st.session_state.grid[r][c]


def walkable(pos):
    if not inside(pos):
        return False

    value = tile_at(pos)

    if value == WALL:
        return False

    if value == DOOR and not st.session_state.switch_on:
        return False

    if value == HAZARD:
        return False

    return True


def activate_switch_if_needed():
    # The switch remains active when either player or ghost is on it.
    p = st.session_state.player
    g = st.session_state.ghost

    st.session_state.switch_on = (
        tile_at(p) == SWITCH
        or (g is not None and tile_at(g) == SWITCH)
    )


def move_ghost():
    if st.session_state.phase != "replay":
        return

    moves = st.session_state.moves

    if st.session_state.ghost_index >= len(moves):
        return

    dr, dc = moves[st.session_state.ghost_index]

    if st.session_state.ghost is None:
        st.session_state.ghost = st.session_state.start

    r, c = st.session_state.ghost
    nxt = (r + dr, c + dc)

    if walkable(nxt):
        st.session_state.ghost = nxt

    st.session_state.ghost_index += 1
    activate_switch_if_needed()


def move_player(dr, dc):
    if st.session_state.cleared:
        return

    # In replay mode, one ghost action is played for every player action.
    if st.session_state.phase == "replay":
        move_ghost()

    r, c = st.session_state.player
    nxt = (r + dr, c + dc)

    if not walkable(nxt):
        st.session_state.message = "そこには移動できません。"
        return

    st.session_state.player = nxt

    if st.session_state.phase == "record":
        st.session_state.moves.append((dr, dc))
        activate_switch_if_needed()

    else:
        activate_switch_if_needed()

    # Goal check
    if st.session_state.player == st.session_state.goal:
        if st.session_state.phase == "replay":
            st.session_state.cleared = True
            st.session_state.message = (
                "🎉 CLEAR! 過去の自分を利用してゴールしました。"
            )
        else:
            st.session_state.message = (
                "ゴール地点です。記録終了後、同じルートをゴーストに任せて"
                "別の道からゴールしてみましょう。"
            )


def finish_recording():
    if not st.session_state.moves:
        st.session_state.message = "まず少なくとも1回移動してください。"
        return

    st.session_state.phase = "replay"
    st.session_state.player = st.session_state.start
    st.session_state.ghost = st.session_state.start
    st.session_state.ghost_index = 0
    st.session_state.switch_on = False
    st.session_state.message = (
        "👻 ゴースト生成完了。過去の自分と協力してゴールしてください。"
    )


def retry_level():
    load_level(st.session_state.level_index)


def next_level():
    if st.session_state.level_index + 1 < len(LEVELS):
        st.session_state.level_index += 1
        load_level(st.session_state.level_index)


def elapsed_seconds():
    return int(time.time() - st.session_state.level_start_time)


def score():
    # Higher is better.
    base = 1000
    penalty = len(st.session_state.moves) * 5
    time_penalty = elapsed_seconds() * 2
    return max(100, base - penalty - time_penalty)


# ------------------------------------------------------------
# Map renderer
# ------------------------------------------------------------

def render_map():
    grid = st.session_state.grid
    player = st.session_state.player
    ghost = st.session_state.ghost

    rows = len(grid)
    cols = len(grid[0])

    html = f"""
    <style>
    .trace-wrap {{
        display:flex;
        justify-content:center;
        overflow-x:auto;
        padding:8px 0 12px 0;
    }}
    .trace-map {{
        display:grid;
        grid-template-columns:repeat({cols}, 42px);
        gap:3px;
        background:#202020;
        padding:7px;
        border-radius:10px;
    }}
    .cell {{
        width:42px;
        height:42px;
        display:flex;
        align-items:center;
        justify-content:center;
        border-radius:5px;
        font-size:21px;
        box-sizing:border-box;
        user-select:none;
    }}
    .floor {{ background:#eeeeee; }}
    .wall {{ background:#333333; }}
    .goal {{ background:#ffe599; }}
    .switch {{ background:#ffd966; }}
    .door {{ background:#9fc5e8; }}
    .dooropen {{ background:#b6d7a8; }}
    .player {{
        background:#4285f4;
        color:white;
        font-size:20px;
        font-weight:bold;
        border:3px solid #174ea6;
    }}
    .ghost {{
        background:#a64d79;
        color:white;
        font-size:20px;
        font-weight:bold;
        opacity:.7;
    }}
    .both {{
        background:#674ea7;
        color:white;
        font-size:15px;
        font-weight:bold;
        border:3px solid #351c75;
    }}
    </style>
    <div class="trace-wrap">
    <div class="trace-map">
    """

    for r in range(rows):
        for c in range(cols):
            pos = (r, c)
            value = grid[r][c]
            is_p = pos == player
            is_g = pos == ghost

            if is_p and is_g:
                html += '<div class="cell both">P+G</div>'
            elif is_p:
                html += '<div class="cell player">P</div>'
            elif is_g:
                html += '<div class="cell ghost">G</div>'
            elif value == WALL:
                html += '<div class="cell wall">⬛</div>'
            elif value == GOAL:
                html += '<div class="cell goal">⭐</div>'
            elif value == SWITCH:
                html += '<div class="cell switch">🟡</div>'
            elif value == DOOR:
                cls = "dooropen" if st.session_state.switch_on else "door"
                symbol = "○" if st.session_state.switch_on else "🔒"
                html += f'<div class="cell {cls}">{symbol}</div>'
            elif value == CRATE:
                html += '<div class="cell floor">📦</div>'
            elif value == HAZARD:
                html += '<div class="cell floor">⚠️</div>'
            else:
                html += '<div class="cell floor"></div>'

    html += "</div></div>"

    st.components.v1.html(html, height=max(150, rows * 45 + 40))


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

level = LEVELS[st.session_state.level_index]

st.title("⏳ TRACE")
st.caption("過去の自分をゲームの駒として利用するタイムパズル")

st.progress(
    (st.session_state.level_index + 1) / len(LEVELS),
    text=f"STAGE {st.session_state.level_index + 1} / {len(LEVELS)}"
)

st.subheader(level["name"])
st.caption(level["hint"])

if st.session_state.phase == "record":
    st.info("🔵 RECORD — あなたの行動を記録中")
else:
    st.info("🟣 REPLAY — ゴーストが過去の行動を再生中")

# ------------------------------------------------------------
# Map
# ------------------------------------------------------------

render_map()

# ------------------------------------------------------------
# Position / status
# ------------------------------------------------------------

pr, pc = st.session_state.player

a, b, c = st.columns(3)

with a:
    st.metric("プレイヤー座標", f"({pr}, {pc})")

with b:
    st.metric("記録移動数", len(st.session_state.moves))

with c:
    st.metric("ドア", "OPEN" if st.session_state.switch_on else "LOCKED")

st.write(st.session_state.message)

# ------------------------------------------------------------
# Controls
# ------------------------------------------------------------

st.subheader("🎮 操作")

a, b, c = st.columns(3)

with b:
    if st.button("⬆️", use_container_width=True):
        move_player(-1, 0)
        st.rerun()

a, b, c = st.columns(3)

with a:
    if st.button("⬅️", use_container_width=True):
        move_player(0, -1)
        st.rerun()

with b:
    if st.button("⬇️", use_container_width=True):
        move_player(1, 0)
        st.rerun()

with c:
    if st.button("➡️", use_container_width=True):
        move_player(0, 1)
        st.rerun()

# ------------------------------------------------------------
# Main actions
# ------------------------------------------------------------

st.divider()

if st.session_state.phase == "record":
    if st.button(
        "⏺️ 記録終了 → ゴーストを作る",
        use_container_width=True,
        type="primary",
    ):
        finish_recording()
        st.rerun()

else:
    if not st.session_state.cleared:
        st.caption(
            "ゴーストは1回のプレイヤー操作につき1ステップ再生されます。"
        )

# ------------------------------------------------------------
# Clear screen
# ------------------------------------------------------------

if st.session_state.cleared:
    st.success(
        f"🏆 STAGE CLEAR!   Score: {score()}"
    )

    st.write(
        f"移動数: {len(st.session_state.moves)}  /  "
        f"時間: {elapsed_seconds()} 秒"
    )

    a, b = st.columns(2)

    with a:
        if st.button("🔄 もう一度", use_container_width=True):
            retry_level()
            st.rerun()

    with b:
        if st.session_state.level_index + 1 < len(LEVELS):
            if st.button("➡️ 次のステージ", use_container_width=True):
                next_level()
                st.rerun()
        else:
            st.balloons()
            st.write("🎉 全ステージ制覇！")

# ------------------------------------------------------------
# General reset
# ------------------------------------------------------------

if not st.session_state.cleared:
    if st.button("🔄 ステージを最初から", use_container_width=True):
        retry_level()
        st.rerun()

# ------------------------------------------------------------
# Level selector
# ------------------------------------------------------------

with st.expander("🗺️ ステージ選択"):
    names = [f"{i+1}. {x['name']}" for i, x in enumerate(LEVELS)]
    selected = st.selectbox(
        "プレイするステージ",
        names,
        index=st.session_state.level_index,
    )
    selected_index = names.index(selected)

    if st.button("このステージを開始"):
        st.session_state.level_index = selected_index
        load_level(selected_index)
        st.rerun()

# ------------------------------------------------------------
# Instructions
# ------------------------------------------------------------

with st.expander("📖 ルール"):
    st.markdown(
        """
### 目的
⭐ **ゴール**に到達してください。

### RECORD
最初のプレイでは、あなたの移動がすべて記録されます。

### REPLAY
「記録終了」を押すと、その行動を再現する **G（ゴースト）** が出現します。

あなたはゴーストとは別に動けます。

### スイッチ
🟡 スイッチの上にプレイヤーまたはゴーストがいると、ドアが開きます。

### 攻略の基本
1. 最初のターンでゴーストにスイッチを押させるルートを作る
2. 記録を終了する
3. ゴーストがスイッチへ向かっている間に自分を別ルートへ移動する
4. ドアが開いたらゴールへ進む

**「失敗した自分の行動」が、次の挑戦の攻略手段になります。**
"""
    )

# ------------------------------------------------------------
# Technical information
# ------------------------------------------------------------

with st.expander("🔧 デバッグ情報"):
    st.write("Phase:", st.session_state.phase)
    st.write("Player:", st.session_state.player)
    st.write("Ghost:", st.session_state.ghost)
    st.write("Ghost step:", st.session_state.ghost_index)
    st.write("Recorded moves:", st.session_state.moves)
    st.write("Switch:", st.session_state.switch_on)
'''
path = Path("/mnt/data/trace_streamlit_game.py")
path.write_text(code, encoding="utf-8")
print(f"作成しました: {path}")
