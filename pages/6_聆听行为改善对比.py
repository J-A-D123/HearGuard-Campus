"""
HearGuard Campus · 声护校园
聆听行为改善对比 V1.3

功能：
1. 情景模拟与实际行为记录
2. 自动导入个人听音画像
3. 两次行为记录比较
4. 行为变化可视化
5. 个性化行为反馈
6. 保存当前会话对比结果
7. 导出 CSV 报告
8. 应用 HearGuard Campus 公共科技风主题

科学边界：
本模块仅用于健康教育和自报行为比较。
不提供医学诊断或听力损失概率预测。
"""

import streamlit as st
import pandas as pd

from datetime import date, timedelta
from pathlib import Path
import sys


# ============================================================
# 01 项目路径与公共主题
# ============================================================

# 确保 Streamlit 从项目根目录或 pages 目录启动时，
# 都能找到 utils/theme.py。

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.theme import apply_theme


# ============================================================
# 02 页面配置
# ============================================================

st.set_page_config(
    page_title="聆听行为改善对比 | HearGuard Campus",
    page_icon="📈",
    layout="wide",
)

# 应用全站统一主题
apply_theme()


# ============================================================
# 03 共享数据配置
# ============================================================

PROFILE_KEY = "hearguard_shared_profile"

COMPARISON_KEY = "hearguard_comparison_result"

SAVED_COMPARISON_KEY = "hearguard_saved_comparison"


# ============================================================
# 04 本页面专属样式
# ============================================================

st.markdown(
    """
<style>

/* 页面英文辅助标签 */

.hg-small-label {
    color: #43bad7;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.6px;
    margin-bottom: 8px;
}

/* 页面模块间距 */

div[data-testid="stVerticalBlock"] {
    row-gap: 0.65rem;
}

/* 数据表格圆角 */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 05 辅助函数
# ============================================================

def section_label(number, english):
    """统一章节标签。"""

    st.markdown(
        (
            '<div class="hg-small-label">'
            f'{number} / {english}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def get_profile():
    """
    读取个人听音画像的数据。
    """

    profile = st.session_state.get(PROFILE_KEY)

    if not isinstance(profile, dict):
        return None

    return profile


def change_text(before, after, unit=""):
    """
    返回变化描述。
    """

    difference = after - before

    if difference < 0:
        return f"减少 {abs(difference):.1f}{unit}"

    if difference > 0:
        return f"增加 {difference:.1f}{unit}"

    return "没有变化"


def frequency_description(value):
    """
    频率等级解释。
    """

    descriptions = {
        1: "从不",
        2: "很少",
        3: "有时",
        4: "经常",
        5: "总是",
    }

    return descriptions.get(value, "未知")


def evaluate_changes(before, after):
    """
    比较两次行为记录。

    不计算疾病发生概率。
    不与画像页面的100分制直接换算。
    """

    fields = [
        {
            "name": "每日耳机使用时间",
            "key": "hours",
            "unit": " 小时",
        },
        {
            "name": "较高音量使用频率",
            "key": "volume",
            "unit": " 级",
        },
        {
            "name": "嘈杂环境调高音量频率",
            "key": "noise",
            "unit": " 级",
        },
        {
            "name": "连续使用期间主动休息次数",
            "key": "breaks",
            "unit": " 次",
        },
    ]

    results = []

    for field in fields:

        key = field["key"]

        old_value = before[key]
        new_value = after[key]

        difference = new_value - old_value

        if difference == 0:
            status = "未变化"

        elif key == "breaks":
            status = "休息次数发生变化"

        elif difference < 0:
            status = "朝建议方向变化"

        else:
            status = "建议继续关注"

        results.append({
            "行为维度": field["name"],
            "首次记录": old_value,
            "再次记录": new_value,
            "变化量": change_text(
                old_value,
                new_value,
                field["unit"],
            ),
            "变化说明": status,
        })

    return pd.DataFrame(results)


def generate_feedback(before, after):
    """
    自动生成行为变化反馈。
    """

    feedback = []

    # --------------------------------------------------------
    # 每日时长
    # --------------------------------------------------------

    if after["hours"] < before["hours"]:

        feedback.append(
            (
                "每日使用时长",
                "再次记录的每日耳机使用时间有所减少。"
                "可以继续关注实际音量和连续使用情况。",
            )
        )

    elif after["hours"] > before["hours"]:

        feedback.append(
            (
                "每日使用时长",
                "再次记录的使用时间有所增加。"
                "建议同时留意音量水平和主动休息情况。",
            )
        )

    else:

        feedback.append(
            (
                "每日使用时长",
                "两次记录的每日耳机使用时间相同。",
            )
        )

    # --------------------------------------------------------
    # 较高音量使用频率
    # --------------------------------------------------------

    if after["volume"] < before["volume"]:

        feedback.append(
            (
                "音量习惯",
                "较高音量使用频率有所下降。"
                "这属于自报行为变化，并非实际声级测量。",
            )
        )

    elif after["volume"] > before["volume"]:

        feedback.append(
            (
                "音量习惯",
                "较高音量使用频率有所增加。"
                "可以留意是否存在不必要的高音量聆听。",
            )
        )

    else:

        feedback.append(
            (
                "音量习惯",
                "较高音量使用频率没有变化。",
            )
        )

    # --------------------------------------------------------
    # 嘈杂环境
    # --------------------------------------------------------

    if after["noise"] < before["noise"]:

        feedback.append(
            (
                "使用环境",
                "在嘈杂环境中主动调高音量的频率有所下降。",
            )
        )

    elif after["noise"] > before["noise"]:

        feedback.append(
            (
                "使用环境",
                "在嘈杂环境中提高音量的频率有所增加。"
                "可以考虑暂停播放或选择更安静的环境。",
            )
        )

    else:

        feedback.append(
            (
                "使用环境",
                "嘈杂环境中调高音量的频率没有变化。",
            )
        )

    # --------------------------------------------------------
    # 主动休息
    # --------------------------------------------------------

    if after["breaks"] > before["breaks"]:

        feedback.append(
            (
                "主动休息",
                "再次记录的主动休息次数有所增加。"
                "应结合使用总时长判断休息安排是否合适。",
            )
        )

    elif after["breaks"] < before["breaks"]:

        feedback.append(
            (
                "主动休息",
                "再次记录的主动休息次数有所减少。"
                "这并不必然表示行为变差，"
                "还需要考虑使用时间是否同时减少。",
            )
        )

    else:

        feedback.append(
            (
                "主动休息",
                "两次记录的主动休息次数相同。",
            )
        )

    return feedback


def import_profile_hours():
    """
    从个人画像导入每日耳机使用时长。

    使用按钮回调修改 session_state，
    避免在组件创建之后修改其状态。
    """

    profile = get_profile()

    if profile is None:

        st.session_state[
            "hg_compare_import_message"
        ] = "当前会话中还没有个人听音画像。"

        return

    try:

        hours = float(profile.get("hours"))

    except (ValueError, TypeError):

        st.session_state[
            "hg_compare_import_message"
        ] = "个人画像中的使用时长无法读取。"

        return

    if not 0 <= hours <= 12:

        st.session_state[
            "hg_compare_import_message"
        ] = (
            "个人画像中的使用时长超出本页范围，"
            "请手动确认。"
        )

        return

    # 与滑块0.5小时的步长保持一致
    rounded_hours = round(hours * 2) / 2

    st.session_state[
        "hg_compare_before_hours"
    ] = rounded_hours

    st.session_state[
        "hg_compare_import_message"
    ] = (
        "已导入个人画像中的每日耳机使用时长。"
        "其他指标仍需要手动填写。"
    )


# ============================================================
# 06 初始化页面状态
# ============================================================

today = date.today()

DEFAULT_WIDGETS = {

    "hg_compare_mode": "情景模拟",

    "hg_compare_before_date": today - timedelta(days=7),
    "hg_compare_after_date": today,

    "hg_compare_before_hours": 4.0,
    "hg_compare_after_hours": 2.0,

    "hg_compare_before_volume": 4,
    "hg_compare_after_volume": 2,

    "hg_compare_before_noise": 4,
    "hg_compare_after_noise": 2,

    "hg_compare_before_breaks": 1,
    "hg_compare_after_breaks": 3,

}

for key, value in DEFAULT_WIDGETS.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 07 页面标题
# ============================================================

st.title("📈 聆听行为改善对比")

st.subheader("从行为认知到持续观察")

st.write(
    "记录两个时间点的日常聆听习惯，"
    "通过交互式图表观察使用时间、"
    "音量习惯、环境因素和主动休息行为的变化。"
)

st.info(
    "本页面用于自报行为记录、情景模拟和健康教育。"
    "比较结果不代表实际听力状况，"
    "也不能证明听力健康已经改善。"
)

st.divider()


# ============================================================
# 08 选择记录模式
# ============================================================

section_label(
    "01",
    "COMPARISON MODE",
)

st.header("① 选择对比方式")

mode = st.radio(
    "本次使用哪种记录模式？",
    [
        "情景模拟",
        "实际行为记录",
    ],
    horizontal=True,
    key="hg_compare_mode",
)

if mode == "情景模拟":

    st.info(
        "当前为情景模拟模式。"
        "你可以自由调整两组参数，"
        "观察不同行为情境之间的差异。"
        "这些参数不能被描述为真实用户干预效果。"
    )

else:

    st.warning(
        "当前为实际行为记录模式。"
        "请根据两个不同日期的实际使用情况填写。"
        "系统不验证自报内容，"
        "也不会自动把数据存入长期数据库。"
    )

st.divider()


# ============================================================
# 09 导入个人画像
# ============================================================

section_label(
    "02",
    "PROFILE CONNECTION",
)

st.header("② 导入个人听音画像")

profile = get_profile()

if profile is not None:

    st.success(
        "已检测到当前会话保存的个人听音画像。"
    )

    st.write(
        "画像中的每日耳机使用时长："
        f"**{profile.get('hours', '未知')} 小时**"
    )

    st.caption(
        "这里只自动导入每日使用时长。"
        "音量等级、较高音量出现频率"
        "和主动休息次数采用不同的定义，"
        "不能直接互相换算。"
    )

else:

    st.info(
        "当前会话中没有检测到已保存的个人画像。"
        "你仍可以手动填写两组对比数据。"
    )

st.button(
    "🎧 将个人画像的每日时长导入首次记录",
    on_click=import_profile_hours,
    use_container_width=True,
    disabled=(profile is None),
    key="hg_compare_import_button",
)

import_message = st.session_state.get(
    "hg_compare_import_message"
)

if import_message:
    st.caption(import_message)


# ============================================================
# 10 首次行为记录
# ============================================================

st.divider()

section_label(
    "03",
    "BASELINE",
)

st.header("③ 首次聆听行为记录")

with st.container(border=True):

    st.subheader("记录 A · 初始状态")

    before_date = st.date_input(
        "首次记录日期",
        key="hg_compare_before_date",
    )

    a1, a2 = st.columns(2)

    with a1:

        before_hours = st.slider(
            "每天使用耳机的时间（小时）",
            min_value=0.0,
            max_value=12.0,
            step=0.5,
            key="hg_compare_before_hours",
        )

        before_volume = st.slider(
            "使用较高音量的频率",
            min_value=1,
            max_value=5,
            key="hg_compare_before_volume",
            help=(
                "1=从不，2=很少，3=有时，"
                "4=经常，5=总是。"
            ),
        )

    with a2:

        before_noise = st.slider(
            "在嘈杂环境中调高音量的频率",
            min_value=1,
            max_value=5,
            key="hg_compare_before_noise",
        )

        before_breaks = st.slider(
            "连续使用耳机期间的主动休息次数",
            min_value=0,
            max_value=10,
            step=1,
            key="hg_compare_before_breaks",
        )

    st.caption(
        "频率定义：1=从不，2=很少，"
        "3=有时，4=经常，5=总是。"
        "休息次数为用户自行报告，"
        "不是统一时长下的标准化频率。"
    )


# ============================================================
# 11 再次行为记录
# ============================================================

st.divider()

section_label(
    "04",
    "FOLLOW-UP",
)

st.header("④ 再次聆听行为记录")

with st.container(border=True):

    st.subheader("记录 B · 对比状态")

    after_date = st.date_input(
        "再次记录日期",
        key="hg_compare_after_date",
    )

    b1, b2 = st.columns(2)

    with b1:

        after_hours = st.slider(
            "再次记录：每天使用耳机的时间（小时）",
            min_value=0.0,
            max_value=12.0,
            step=0.5,
            key="hg_compare_after_hours",
        )

        after_volume = st.slider(
            "再次记录：使用较高音量的频率",
            min_value=1,
            max_value=5,
            key="hg_compare_after_volume",
        )

    with b2:

        after_noise = st.slider(
            "再次记录：嘈杂环境中调高音量的频率",
            min_value=1,
            max_value=5,
            key="hg_compare_after_noise",
        )

        after_breaks = st.slider(
            "再次记录：主动休息次数",
            min_value=0,
            max_value=10,
            step=1,
            key="hg_compare_after_breaks",
        )

    st.caption(
        "两次记录采用相同的指标和等级定义，"
        "便于进行对比。"
    )


# ============================================================
# 12 整理输入数据
# ============================================================

before = {
    "hours": float(before_hours),
    "volume": int(before_volume),
    "noise": int(before_noise),
    "breaks": int(before_breaks),
}

after = {
    "hours": float(after_hours),
    "volume": int(after_volume),
    "noise": int(after_noise),
    "breaks": int(after_breaks),
}


# ============================================================
# 13 日期验证
# ============================================================

st.divider()

if (
    mode == "实际行为记录"
    and after_date <= before_date
):

    st.error(
        "实际行为记录模式要求再次记录日期"
        "晚于首次记录日期。"
        "请先修改日期，再进行比较。"
    )

    st.stop()


# ============================================================
# 14 生成行为变化结果
# ============================================================

section_label(
    "05",
    "BEHAVIOR ANALYSIS",
)

st.header("⑤ 行为变化分析")

summary_df = evaluate_changes(
    before,
    after,
)

improved_count = int(
    (
        summary_df["变化说明"]
        == "朝建议方向变化"
    ).sum()
)

unchanged_count = int(
    (
        summary_df["变化说明"]
        == "未变化"
    ).sum()
)

attention_count = int(
    (
        summary_df["变化说明"]
        == "建议继续关注"
    ).sum()
)


# ============================================================
# 15 结果概览
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "每日使用时间变化",
    change_text(
        before_hours,
        after_hours,
        " 小时",
    ),
)

c2.metric(
    "朝建议方向变化",
    f"{improved_count} 项",
)

c3.metric(
    "未变化指标",
    f"{unchanged_count} 项",
)

c4.metric(
    "建议继续关注",
    f"{attention_count} 项",
)

st.caption(
    "这里的统计基于自报或模拟行为变化。"
    "主动休息次数单独描述，不直接归类为"
    "听力健康改善。"
)


# ============================================================
# 16 每日使用时间对比
# ============================================================

st.divider()

st.header("⑥ 每日耳机使用时间对比")

hours_df = pd.DataFrame({
    "记录阶段": [
        "首次记录",
        "再次记录",
    ],
    "每日使用时间（小时）": [
        before_hours,
        after_hours,
    ],
})

st.bar_chart(
    hours_df,
    x="记录阶段",
    y="每日使用时间（小时）",
    color="#47C7F3",
    use_container_width=True,
)

st.caption(
    "图表展示用户填写的每日耳机使用时间。"
    "不代表设备自动测量结果。"
)


# ============================================================
# 17 行为频率对比
# ============================================================

st.divider()

st.header("⑦ 聆听行为频率对比")

frequency_df = pd.DataFrame({
    "行为维度": [
        "较高音量使用",
        "嘈杂环境调高音量",
    ],
    "首次记录": [
        before_volume,
        before_noise,
    ],
    "再次记录": [
        after_volume,
        after_noise,
    ],
})

st.bar_chart(
    frequency_df,
    x="行为维度",
    y=[
        "首次记录",
        "再次记录",
    ],
    color=[
        "#47C7F3",
        "#F3B35E",
    ],
    use_container_width=True,
)

st.caption(
    "频率等级为1至5级，属于顺序分类信息。"
    "级数之间不代表等间隔的声音能量差异。"
)


# ============================================================
# 18 主动休息对比
# ============================================================

st.divider()

st.header("⑧ 主动休息习惯对比")

rest_df = pd.DataFrame({
    "记录阶段": [
        "首次记录",
        "再次记录",
    ],
    "主动休息次数": [
        before_breaks,
        after_breaks,
    ],
})

st.bar_chart(
    rest_df,
    x="记录阶段",
    y="主动休息次数",
    color="#47C7F3",
    use_container_width=True,
)

st.caption(
    "休息次数应结合每日耳机使用时间理解。"
    "例如使用时间减少后，休息次数不一定需要增加。"
)


# ============================================================
# 19 完整行为变化摘要
# ============================================================

st.divider()

st.header("⑨ 完整行为变化摘要")

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)

if improved_count > 0:

    st.success(
        f"本次比较中，有 {improved_count} 项指标"
        "朝建议方向变化。"
    )

if attention_count > 0:

    st.warning(
        f"有 {attention_count} 项指标"
        "建议继续关注。"
    )

if (
    improved_count == 0
    and attention_count == 0
):

    st.info(
        "本次比较没有出现需要特别提示的"
        "时长或频率上升情况。"
    )


# ============================================================
# 20 个性化行为反馈
# ============================================================

st.divider()

st.header("⑩ 个性化行为反馈")

feedback = generate_feedback(
    before,
    after,
)

for title, description in feedback:

    with st.container(border=True):

        st.markdown(
            f"**{title}**"
        )

        st.write(description)


# ============================================================
# 21 保存本次对比
# ============================================================

st.divider()

st.header("⑪ 保存本次对比")

st.write(
    "可以将当前对比结果保存到"
    "本次 Streamlit 会话中。"
    "保存后，在同一会话内切换页面通常不会丢失结果。"
)

current_comparison = {
    "mode": mode,

    "before_date": str(before_date),
    "after_date": str(after_date),

    "before": before.copy(),
    "after": after.copy(),

    "summary": summary_df.to_dict(
        orient="records"
    ),

    "improved_count": improved_count,
    "unchanged_count": unchanged_count,
    "attention_count": attention_count,
}

if st.button(
    "💾 保存本次行为对比",
    type="primary",
    use_container_width=True,
    key="hg_compare_save_button",
):

    st.session_state[
        SAVED_COMPARISON_KEY
    ] = current_comparison.copy()

    st.session_state[
        COMPARISON_KEY
    ] = current_comparison.copy()

    st.success(
        "本次行为对比已保存到当前会话。"
    )


# ============================================================
# 22 查看已保存结果
# ============================================================

saved_comparison = st.session_state.get(
    SAVED_COMPARISON_KEY
)

if isinstance(saved_comparison, dict):

    with st.expander(
        "📂 查看当前会话最后保存的对比"
    ):

        st.write(
            "记录模式：",
            saved_comparison["mode"],
        )

        st.write(
            "首次记录日期：",
            saved_comparison["before_date"],
        )

        st.write(
            "再次记录日期：",
            saved_comparison["after_date"],
        )

        saved_df = pd.DataFrame(
            saved_comparison["summary"]
        )

        st.dataframe(
            saved_df,
            hide_index=True,
            use_container_width=True,
        )

        st.caption(
            "当前仅保留最后一次保存的对比。"
            "这里不是长期历史数据库。"
        )


# ============================================================
# 23 导出CSV
# ============================================================

st.divider()

st.header("⑫ 导出行为变化报告")

export_df = summary_df.copy()

export_df.insert(
    0,
    "记录方式",
    mode,
)

export_df.insert(
    1,
    "首次记录日期",
    str(before_date),
)

export_df.insert(
    2,
    "再次记录日期",
    str(after_date),
)

csv_content = (
    "\ufeff"
    + export_df.to_csv(index=False)
).encode("utf-8")

st.download_button(
    label="📥 下载行为变化摘要 CSV",
    data=csv_content,
    file_name="HearGuard_行为变化摘要.csv",
    mime="text/csv",
    use_container_width=True,
)

st.caption(
    "导出的文件只包含当前页面的"
    "自报或模拟行为对比数据，"
    "不包含126份校园原始问卷。"
)


# ============================================================
# 24 页面导航
# ============================================================

st.divider()

st.header("⑬ 继续探索 HearGuard Campus")

nav1, nav2 = st.columns(2)

with nav1:

    if st.button(
        "🎧 返回个人听音画像 →",
        use_container_width=True,
        key="hg_compare_profile_nav",
    ):

        st.switch_page(
            "pages/2_我的听音画像.py"
        )

with nav2:

    if st.button(
        "💡 查看个性化建议 →",
        use_container_width=True,
        key="hg_compare_advice_nav",
    ):

        st.switch_page(
            "pages/4_个性化建议.py"
        )


# ============================================================
# 25 科学性与研究边界
# ============================================================

st.divider()

st.header("🛡️ 科学性与研究边界")

with st.expander(
    "查看行为比较方法与适用限制"
):

    st.markdown(
        """
### 1. 行为变化不等于医学改善

本页面仅比较两个时间点的自报行为指标。

不能据此证明听力功能已经改善。

### 2. 情景模拟不是真实干预效果

情景模拟中的参数可以由用户自由设置。

模拟结果不能作为真实用户测试成果。

### 3. 自报数据存在不确定性

耳机使用时间、音量习惯、
使用环境和主动休息次数
可能存在记忆误差和主观判断偏差。

### 4. 不同模块的指标不能强行换算

个人画像使用主观音量水平，
本页面使用较高音量的出现频率。

两者不是同一个指标。

本页面也不使用个人画像的100分制，
不能直接比较不同模型的数值。

### 5. 实际声级需要可靠测量

手机或耳机显示的音量百分比
不能直接换算为固定dBA。

本模块没有进行实际声级测量。

### 6. 当前仅支持会话保存

保存的行为对比暂存在Streamlit会话中。

关闭会话、服务重启或连接中断后，
记录不保证保留。

用户如需保留结果，可以自行下载CSV。

### 7. 不提供医学诊断

本页面不能推断个体听力损失概率，
也不能替代专业听力检查。
        """
    )


# ============================================================
# 26 页脚
# ============================================================

st.caption(
    "HearGuard Campus · 聆听行为改善对比"
)

st.caption(
    "For educational and research communication purposes only."
)