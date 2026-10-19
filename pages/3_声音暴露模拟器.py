"""
HearGuard Campus · 声护校园
声音暴露模拟器 V1.3

主要功能：
1. 声音水平、每日时长、每周天数输入
2. WHO–ITU成人参考暴露模型
3. 相对声音暴露百分比
4. 交互式声音暴露仪表盘
5. 声音水平与参考暴露时间曲线
6. 不同声音水平参考时间对比
7. 个性化情景说明
8. 与声音暴露图谱联动入口
9. HearGuard Campus V1.3统一主题

科学边界：
本页面仅用于安全聆听健康教育。
输入声级是假设值，不是设备实际测量值。
不用于医学诊断或个体疾病风险预测。
"""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# 01 项目路径与公共主题
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.theme import apply_theme, style_plotly, COLORS


# ============================================================
# 02 页面配置
# ============================================================

st.set_page_config(
    page_title="声音暴露模拟器 | HearGuard Campus",
    page_icon="🔊",
    layout="wide",
)

apply_theme()


# ============================================================
# 03 页面专属CSS
# ============================================================

st.markdown(
    """
<style>

.hg-sim-hero {
    background:
        radial-gradient(
            circle at 85% 20%,
            rgba(71,199,243,0.20),
            transparent 35%
        ),
        linear-gradient(
            125deg,
            #081729,
            #102b49 55%,
            #123d58
        );

    border: 1px solid rgba(71,199,243,0.28);
    border-radius: 20px;

    padding: 34px 36px;
    margin-bottom: 22px;
}

.hg-sim-title {
    font-size: clamp(27px,3.5vw,38px);
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 14px;
}

.hg-sim-description {
    color: #c5e2ee;
    font-size: 15px;
    line-height: 1.9;
    max-width: 850px;
}

.hg-section-label {
    color: #43bad7;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.6px;
    margin-bottom: 8px;
}

.hg-reference-card {
    background: rgba(32,167,187,0.08);
    border: 1px solid rgba(71,199,243,0.22);
    border-radius: 14px;
    padding: 18px 22px;
    margin-top: 10px;
    margin-bottom: 16px;
}

.hg-reference-title {
    font-size: 13px;
    font-weight: 700;
    color: #39b9d4;
    margin-bottom: 8px;
}

.hg-reference-value {
    font-size: 24px;
    font-weight: 800;
    color: #39b9d4;
}

.hg-reference-description {
    font-size: 13px;
    opacity: 0.8;
    margin-top: 8px;
    line-height: 1.8;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 04 模型配置
# ============================================================

REFERENCE_DB = 80.0

REFERENCE_WEEKLY_HOURS = 40.0

EXCHANGE_RATE_DB = 3.0


# ============================================================
# 05 辅助函数
# ============================================================

def section_label(number, english):
    """
    统一章节标签。
    """

    st.markdown(
        (
            '<div class="hg-section-label">'
            f'{number} / {english}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def calculate_reference_hours(
    sound_db,
    reference_db=REFERENCE_DB,
    reference_hours=REFERENCE_WEEKLY_HOURS,
):
    """
    计算某一假设声级对应的
    每周参考暴露时间。

    教育性近似换算：

    T = 40 × 2^((80-L)/3)

    其中：
    L：输入的假设声级（dBA）
    T：相对参考等能量时间（小时）
    """

    allowed_hours = (
        reference_hours
        * (
            2 ** (
                (reference_db - sound_db)
                / EXCHANGE_RATE_DB
            )
        )
    )

    return allowed_hours


def calculate_exposure(
    sound_db,
    hours_per_day,
    days_per_week,
):
    """
    计算累计时长和相对参考暴露量。

    不推断听力损失概率。
    """

    weekly_hours = (
        hours_per_day
        * days_per_week
    )

    allowed_hours = calculate_reference_hours(
        sound_db
    )

    exposure_ratio = (
        weekly_hours / allowed_hours
    )

    exposure_percent = (
        exposure_ratio * 100
    )

    return {
        "weekly_hours": weekly_hours,
        "allowed_hours": allowed_hours,
        "exposure_ratio": exposure_ratio,
        "exposure_percent": exposure_percent,
    }


def exposure_description(percent):
    """
    生成中性、教育性的参考比较说明。
    """

    if percent < 50:

        return (
            "当前假设情景的相对参考暴露量"
            "低于50%。"
            "这不代表实际聆听一定安全。"
        )

    elif percent < 100:

        return (
            "当前假设情景的相对参考暴露量"
            "介于50%与100%之间。"
            "可以继续关注声级和累计时间。"
        )

    elif percent < 200:

        return (
            "当前假设情景的相对参考暴露量"
            "已经达到或超过100%。"
            "建议关注声音水平与累计使用时间。"
        )

    else:

        return (
            "当前假设情景的相对参考暴露量"
            "达到或超过200%。"
            "这一结果明显高于模型参考量，"
            "需要重新审视当前模拟参数。"
        )


def hours_display(value):
    """
    小于1小时显示分钟，
    其他情况显示小时。
    """

    if value < 1:

        return f"{value * 60:.0f} 分钟"

    elif value < 10:

        return f"{value:.2f} 小时"

    else:

        return f"{value:.1f} 小时"


# ============================================================
# 06 页面主视觉
# ============================================================

hero_html = (
    '<div class="hg-sim-hero">'

    '<div class="hg-sim-title">'
    '🔊 声音暴露模拟器'
    '</div>'

    '<div class="hg-sim-description">'
    '调节假设声音水平、每天聆听时间和每周使用天数，'
    '观察不同情景下的相对声音能量暴露。'
    '<br>'
    '通过可视化模型理解声音水平与累计时间之间的关系。'
    '</div>'

    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)

st.caption(
    "HEARGUARD CAMPUS · SOUND EXPOSURE SIMULATOR"
)

st.info(
    "本页面采用教育性声音暴露参考模型。"
    "输入的dBA数值是假设声级，"
    "并非手机、耳机或专业仪器的实际测量结果。"
    "本模块不提供医学诊断。"
)

st.divider()


# ============================================================
# 07 输入参数
# ============================================================

section_label(
    "01",
    "EXPOSURE PARAMETERS",
)

st.header("① 设置声音暴露情景")

st.write(
    "调整下方三个参数，"
    "图表与结果会自动更新。"
)

col1, col2 = st.columns(2)

with col1:

    db = st.slider(
        "假设声音水平（dBA）",
        min_value=60,
        max_value=100,
        value=80,
        step=1,
        key="hg_sim_db",
        help=(
            "dBA表示A计权声级。"
            "这里由用户设置假设值，"
            "并非实际耳机输出测量。"
        ),
    )

    hours_per_day = st.slider(
        "每天暴露时间（小时）",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.5,
        key="hg_sim_hours",
    )

with col2:

    days_per_week = st.slider(
        "每周暴露天数",
        min_value=1,
        max_value=7,
        value=7,
        step=1,
        key="hg_sim_days",
    )

    with st.container(border=True):

        st.markdown(
            "**模型参考点**"
        )

        st.metric(
            "成人参考声级",
            "80 dBA",
        )

        st.caption(
            "对应每周40小时的参考暴露时间。"
        )

st.caption(
    "为了便于理解，本模型假设"
    "每次暴露期间声音水平保持不变。"
    "现实中的声音通常会随时间变化。"
)

st.divider()


# ============================================================
# 08 计算结果
# ============================================================

result = calculate_exposure(
    sound_db=db,
    hours_per_day=hours_per_day,
    days_per_week=days_per_week,
)

weekly_hours = result["weekly_hours"]

allowed_weekly_hours = result["allowed_hours"]

exposure_percent = result["exposure_percent"]

exposure_ratio = result["exposure_ratio"]


# ============================================================
# 09 核心指标
# ============================================================

section_label(
    "02",
    "EXPOSURE SUMMARY",
)

st.header("② 本周声音暴露模拟结果")

m1, m2, m3 = st.columns(3)

m1.metric(
    "每周累计模拟暴露",
    f"{weekly_hours:.1f} 小时",
)

m2.metric(
    "该声级参考时间",
    hours_display(allowed_weekly_hours),
)

m3.metric(
    "相对参考暴露量",
    f"{exposure_percent:.1f}%",
)

progress_value = min(
    exposure_percent / 100,
    1.0,
)

st.progress(
    float(progress_value)
)

st.caption(
    "进度条以100%为显示上限。"
    "实际相对参考量可能超过100%，"
    "请以右侧百分比数值为准。"
)


# ============================================================
# 10 教育性提示
# ============================================================

message = exposure_description(
    exposure_percent
)

if exposure_percent < 50:

    st.info(message)

elif exposure_percent < 100:

    st.info(message)

elif exposure_percent < 200:

    st.warning(message)

else:

    st.warning(message)


# ============================================================
# 11 参考参数说明
# ============================================================

reference_html = (
    '<div class="hg-reference-card">'

    '<div class="hg-reference-title">'
    'ADULT EDUCATIONAL REFERENCE'
    '</div>'

    '<div class="hg-reference-value">'
    '80 dBA × 40 h/week'
    '</div>'

    '<div class="hg-reference-description">'
    '采用约3 dB交换规则：'
    '声音水平每提高约3 dB，'
    '相同相对声音能量暴露对应的时间约减半。'
    '此参考值不代表个体安全保证或疾病诊断阈值。'
    '</div>'

    '</div>'
)

st.markdown(
    reference_html,
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# 12 Plotly声音暴露仪表盘
# ============================================================

section_label(
    "03",
    "EXPOSURE GAUGE",
)

st.header("③ 相对声音暴露仪表盘")

gauge_max = max(
    300,
    exposure_percent * 1.15,
)

gauge = go.Figure()

gauge.add_trace(
    go.Indicator(
        mode="gauge+number",

        value=exposure_percent,

        number={
            "suffix": "%",
            "font": {
                "size": 42,
                "color": COLORS["cyan_light"],
            },
        },

        title={
            "text": "相对参考暴露量",
        },

        gauge={
            "axis": {
                "range": [0, gauge_max],
                "tickwidth": 1,
            },

            "bar": {
                "color": COLORS["cyan"],
                "thickness": 0.32,
            },

            "bgcolor": "rgba(0,0,0,0)",

            "steps": [
                {
                    "range": [0, 50],
                    "color": "rgba(56,191,166,0.18)",
                },
                {
                    "range": [50, 100],
                    "color": "rgba(71,199,243,0.20)",
                },
                {
                    "range": [100, 200],
                    "color": "rgba(243,179,94,0.22)",
                },
                {
                    "range": [200, gauge_max],
                    "color": "rgba(231,121,121,0.18)",
                },
            ],

            "threshold": {
                "line": {
                    "color": COLORS["orange"],
                    "width": 5,
                },
                "thickness": 0.8,
                "value": 100,
            },
        },
    )
)

gauge = style_plotly(
    gauge,
    height=385,
)

gauge.update_layout(
    margin=dict(
        l=35,
        r=35,
        t=65,
        b=20,
    ),
)

st.plotly_chart(
    gauge,
    use_container_width=True,
)

st.caption(
    "仪表盘颜色仅用于区分"
    "相对参考量的不同区间。"
    "100%是模型比较参考点，"
    "不代表低于100%即可确保安全。"
)

st.divider()


# ============================================================
# 13 动态结果解释
# ============================================================

section_label(
    "04",
    "RESULT INTERPRETATION",
)

st.header("④ 如何理解这次模拟？")

with st.container(border=True):

    st.subheader(
        "声音水平与暴露时间"
    )

    if db < 80:

        st.write(
            f"当前设置为 **{db} dBA**，"
            "低于模型的80 dBA参考点。"
        )

        st.write(
            "按该模型计算，"
            "相同相对声音能量暴露对应的"
            "参考时间会更长。"
        )

    elif db == 80:

        st.write(
            "当前设置为 **80 dBA**，"
            "与模型参考声级相同。"
        )

        st.write(
            "此时40小时/周对应"
            "100%的相对参考暴露量。"
        )

    else:

        st.write(
            f"当前设置为 **{db} dBA**，"
            "高于模型的80 dBA参考点。"
        )

        st.write(
            "声音水平越高，"
            "相同相对声音能量暴露对应的"
            "参考时间越短。"
        )


with st.container(border=True):

    st.subheader(
        "累计时间与参考时间"
    )

    st.write(
        f"本次设置的累计暴露时间为 "
        f"**{weekly_hours:.1f}小时/周**。"
    )

    st.write(
        f"当前声级对应的模型参考时间为 "
        f"**{hours_display(allowed_weekly_hours)}/周**。"
    )

    if weekly_hours > allowed_weekly_hours:

        excess = (
            weekly_hours
            - allowed_weekly_hours
        )

        st.write(
            f"模拟累计时间比参考时间"
            f"多约 **{hours_display(excess)}**。"
        )

    elif weekly_hours < allowed_weekly_hours:

        remaining = (
            allowed_weekly_hours
            - weekly_hours
        )

        st.write(
            f"模拟累计时间比参考时间"
            f"少约 **{hours_display(remaining)}**。"
        )

    else:

        st.write(
            "模拟累计时间与参考时间相同。"
        )


st.divider()


# ============================================================
# 14 声级与参考暴露时间曲线
# ============================================================

section_label(
    "05",
    "LEVEL-TIME RELATIONSHIP",
)

st.header("⑤ 声音水平与参考暴露时间关系")

db_values = list(
    range(60, 101)
)

allowed_values = [
    calculate_reference_hours(value)
    for value in db_values
]

curve_df = pd.DataFrame({
    "声音水平（dBA）": db_values,
    "参考每周时间（小时）": allowed_values,
})

curve = go.Figure()

curve.add_trace(
    go.Scatter(
        x=curve_df["声音水平（dBA）"],
        y=curve_df["参考每周时间（小时）"],

        mode="lines",

        name="模型参考时间",

        line=dict(
            color=COLORS["cyan_light"],
            width=3,
        ),

        fill="tozeroy",

        fillcolor="rgba(71,199,243,0.10)",

        hovertemplate=(
            "声级：%{x} dBA<br>"
            "参考时间：%{y:.2f} 小时/周"
            "<extra></extra>"
        ),
    )
)

curve.add_trace(
    go.Scatter(
        x=[db],
        y=[allowed_weekly_hours],

        mode="markers",

        marker=dict(
            color=COLORS["orange"],
            size=14,
            line=dict(
                color="#ffffff",
                width=2,
            ),
        ),

        name="当前设置",

        hovertemplate=(
            f"当前：{db} dBA<br>"
            f"参考时间：{allowed_weekly_hours:.2f} 小时/周"
            "<extra></extra>"
        ),
    )
)

curve = style_plotly(
    curve,
    height=450,
)

curve.update_layout(
    xaxis_title="假设声音水平（dBA）",
    yaxis_title="参考每周时间（小时）",

    hovermode="closest",

    showlegend=True,

    margin=dict(
        l=45,
        r=35,
        t=60,
        b=50,
    ),
)

st.plotly_chart(
    curve,
    use_container_width=True,
)

st.caption(
    "曲线反映近似等能量换算关系，"
    "不表示所有声级都存在可以保证安全的暴露时间。"
    "低声级区域的数学外推值尤其不应解释为"
    "无限制或建议的聆听时长。"
)

st.divider()


# ============================================================
# 15 不同声音水平比较
# ============================================================

section_label(
    "06",
    "REFERENCE COMPARISON",
)

st.header("⑥ 不同声音水平下的参考时间")

comparison_levels = [
    80,
    83,
    86,
    89,
    92,
    95,
]

comparison_data = []

for level in comparison_levels:

    allowed = calculate_reference_hours(
        level
    )

    comparison_data.append({
        "声音水平（dBA）": level,
        "参考每周时间（小时）": allowed,
        "显示": hours_display(allowed),
    })

comparison_df = pd.DataFrame(
    comparison_data
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "声音水平（dBA）": st.column_config.NumberColumn(
            "声音水平（dBA）",
            format="%d",
        ),
        "参考每周时间（小时）": st.column_config.NumberColumn(
            "参考每周时间（小时）",
            format="%.2f",
        ),
        "显示": "易读时间",
    },
)

# ------------------------------------------------------------
# 参考时间柱状图
# ------------------------------------------------------------

comparison_chart = go.Figure()

comparison_chart.add_trace(
    go.Bar(
        x=[
            f"{level} dBA"
            for level in comparison_levels
        ],

        y=[
            calculate_reference_hours(level)
            for level in comparison_levels
        ],

        marker_color=COLORS["cyan_light"],

        text=[
            hours_display(
                calculate_reference_hours(level)
            )
            for level in comparison_levels
        ],

        textposition="outside",

        hovertemplate=(
            "%{x}<br>"
            "参考时间：%{y:.2f} 小时/周"
            "<extra></extra>"
        ),
    )
)

comparison_chart = style_plotly(
    comparison_chart,
    height=385,
)

comparison_chart.update_layout(
    xaxis_title="声音水平",
    yaxis_title="参考每周时间（小时）",

    showlegend=False,

    margin=dict(
        l=40,
        r=30,
        t=55,
        b=50,
    ),
)

st.plotly_chart(
    comparison_chart,
    use_container_width=True,
)

st.caption(
    "以上数值采用80 dBA、40小时/周"
    "和近似3 dB交换规则计算，"
    "仅用于理解参考声级与时间的关系。"
)

st.divider()


# ============================================================
# 16 安全聆听教育建议
# ============================================================

section_label(
    "07",
    "LISTENING GUIDANCE",
)

st.header("⑦ 安全聆听提示")

with st.container(border=True):

    if exposure_percent >= 100:

        st.warning(
            "本次假设情景的相对参考暴露量"
            "达到或超过100%。"
        )

        st.write(
            "可以考虑以下日常行为调整："
        )

    else:

        st.info(
            "本次假设情景的相对参考暴露量"
            "低于100%，但这不代表实际暴露没有风险。"
        )

        st.write(
            "仍可以保持以下安全聆听习惯："
        )

    st.markdown(
        """
- 避免不必要的高音量聆听。
- 留意连续佩戴耳机的时间，适当安排无耳机休息。
- 嘈杂环境中避免持续调高音量以掩盖背景噪声。
- 在校园道路及公共交通等场景注意环境安全提示。
        """
    )


# ============================================================
# 17 与声音暴露图谱联动
# ============================================================

st.divider()

section_label(
    "08",
    "EXPLORE MORE",
)

st.header("⑧ 继续探索声音暴露图谱")

st.write(
    "如果希望进一步了解"
    "声音水平与时间之间的关系，"
    "可以进入交互式声音暴露图谱，"
    "查看热力图、等能量参考线"
    "以及不同聆听场景的比较。"
)

if st.button(
    "🌊 打开交互式声音暴露图谱 →",
    type="primary",
    use_container_width=True,
    key="hg_sim_open_atlas",
):

    st.switch_page(
        "pages/7_声音暴露图谱.py"
    )


# ============================================================
# 18 模型说明
# ============================================================

st.divider()

with st.expander(
    "📖 查看模型原理与适用限制"
):

    st.markdown(
        """
### 一、模型参考

本页面使用以下成人教育性参考参数：

**80 dBA × 40小时/周**

并采用近似3 dB交换规则。

数学表达式为：

\[
T(L)=40\times2^{\frac{80-L}{3}}
\]

其中：

- \(L\)：输入的假设声级（dBA）
- \(T(L)\)：该声级下的模型参考时间（小时/周）

### 二、参考换算示例

- 80 dBA → 约40小时/周
- 83 dBA → 约20小时/周
- 86 dBA → 约10小时/周
- 89 dBA → 约5小时/周
- 92 dBA → 约2.5小时/周
- 95 dBA → 约1.25小时/周

### 三、相对参考暴露量

将每周模拟累计时间除以
当前声级对应的模型参考时间：

\[
R=\frac{t}{T(L)}\times100\%
\]

其中：

- \(t\)：模拟累计时间
- \(T(L)\)：模型参考时间
- \(R\)：相对参考暴露百分比

### 四、模型限制

本模型假设声音水平在暴露期间保持不变。

现实中的声音暴露通常会随时间变化。

设备音量百分比不能直接换算成固定dBA。

低于100%不能保证没有听觉健康风险，
高于100%也不能直接判定已经发生听力损伤。

本页面没有进行校准声级测量，
也没有进行临床有效性验证。

### 五、项目用途

本模块用于安全聆听健康教育、
等能量参考关系可视化和假设情景探索。

不提供医学诊断、
个人听力损失概率预测或医疗建议。
        """
    )


# ============================================================
# 19 页脚
# ============================================================

st.caption(
    "HearGuard Campus · 声音暴露模拟器"
)

st.caption(
    "For educational and research communication purposes only."
)