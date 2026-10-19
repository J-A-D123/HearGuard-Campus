"""
HearGuard Campus · 声护校园
交互式声音暴露图谱 V1.3

功能：
1. 声级—时间交互式热力图
2. 成人与较保守参考模式
3. 双场景声音能量暴露对比
4. 校园聆听情境模拟
5. 多场景累计暴露分析
6. 场景添加、删除和清空
7. 公共科技风主题

科学边界：
本模块使用假设声音水平。
不进行实际声级测量。
不用于医学诊断或听力损失概率预测。
"""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
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
    page_title="声音暴露图谱 | HearGuard Campus",
    page_icon="🌊",
    layout="wide",
)

apply_theme()


# ============================================================
# 03 专属视觉样式
# ============================================================

st.markdown(
    """
<style>

.hg-atlas-hero {
    background:
        radial-gradient(
            circle at 85% 20%,
            rgba(71,199,243,0.19),
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

    padding: 36px;
    margin-bottom: 22px;
}

.hg-atlas-title {
    font-size: clamp(28px,3.5vw,40px);
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 12px;
}

.hg-atlas-description {
    color: #c5e2ee;
    font-size: 15px;
    line-height: 1.9;
}

.hg-section-label {
    color: #43bad7;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.6px;
    margin-bottom: 8px;
}

.hg-model-note {
    border-radius: 14px;
    padding: 18px 22px;
    background: rgba(32,167,187,0.08);
    border: 1px solid rgba(71,199,243,0.22);
}

.hg-model-value {
    font-size: 25px;
    font-weight: 800;
    color: #35bbd6;
}

.hg-model-description {
    font-size: 13px;
    line-height: 1.8;
    opacity: 0.85;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 04 全局参考参数
# ============================================================

REFERENCE_HOURS = 40.0
EXCHANGE_RATE = 3.0

ADULT_REFERENCE_DB = 80.0
CONSERVATIVE_REFERENCE_DB = 75.0

SCENE_STORAGE_KEY = "atlas_saved_scenes"


# ============================================================
# 05 通用函数
# ============================================================

def section_label(number, english):

    st.markdown(
        (
            '<div class="hg-section-label">'
            f'{number} / {english}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def reference_hours(db, reference_db):
    """
    每周参考等能量时长。

    T = 40 × 2^((Lref - L)/3)
    """

    return (
        REFERENCE_HOURS
        * 2 ** (
            (reference_db - db)
            / EXCHANGE_RATE
        )
    )


def exposure_percent(db, hours, reference_db):
    """
    相对参考声音能量暴露百分比。
    """

    allowed = reference_hours(
        db,
        reference_db,
    )

    return hours / allowed * 100


def format_hours(hours):

    if hours < 1:
        return f"{hours * 60:.1f} 分钟"

    return f"{hours:.2f} 小时"


def explain_exposure(percent):
    """
    教育性解释。
    """

    if percent < 50:

        return (
            "当前情境的相对参考暴露量低于50%。"
            "这不代表实际聆听一定安全。"
        )

    if percent < 100:

        return (
            "当前情境的相对参考暴露量"
            "介于50%与100%之间。"
            "建议继续关注声音水平与累计时间。"
        )

    if percent < 200:

        return (
            "当前情境达到或超过"
            "所选模型的100%参考等能量值。"
            "可以关注降低声级和减少累计时间。"
        )

    return (
        "当前情境的相对参考暴露量"
        "达到或超过200%。"
        "这表示模拟暴露明显高于参考量，"
        "并非听力损失概率。"
    )


# ============================================================
# 06 页面主视觉
# ============================================================

hero_html = (
    '<div class="hg-atlas-hero">'

    '<div class="hg-atlas-title">'
    '🌊 交互式声音暴露图谱'
    '</div>'

    '<div class="hg-atlas-description">'
    'Sound Exposure Atlas'
    '<br>'
    '通过声级—时间热力图、'
    '双场景比较和校园情境模拟，'
    '探索不同假设聆听条件下的'
    '相对声音能量暴露。'
    '</div>'

    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)

st.info(
    "本页面使用用户输入的假设声级。"
    "不会读取麦克风，也不会测量耳机实际声压级。"
    "图表用于健康教育，不能预测听力损失概率。"
)

st.divider()


# ============================================================
# 07 选择参考模型
# ============================================================

section_label(
    "01",
    "REFERENCE MODEL",
)

st.header("① 选择声音暴露参考模型")

reference_mode = st.radio(
    "请选择参考模式",
    [
        "成人参考模式",
        "较保守参考模式",
    ],
    horizontal=True,
    key="atlas_reference_mode",
)

if reference_mode == "成人参考模式":

    reference_db = ADULT_REFERENCE_DB

else:

    reference_db = CONSERVATIVE_REFERENCE_DB


model_html = (
    '<div class="hg-model-note">'

    '<div class="hg-model-value">'
    f'{reference_db:.0f} dBA × 40 h/week'
    '</div>'

    '<div class="hg-model-description">'
    '采用近似3 dB交换规则。'
    '这个参考点用于教育性等能量换算，'
    '不是个人安全保证或医学诊断阈值。'
    '</div>'

    '</div>'
)

st.markdown(
    model_html,
    unsafe_allow_html=True,
)

if reference_mode == "较保守参考模式":

    st.caption(
        "该设置可用于说明较保守的安全聆听参考，"
        "不代表系统已经对使用者进行了年龄评估。"
    )

st.divider()


# ============================================================
# 08 单场景输入
# ============================================================

section_label(
    "02",
    "INTERACTIVE HEATMAP",
)

st.header("② 声级—时间交互式热力图")

st.write(
    "调整下面两个参数，"
    "热力图中的白色标记和结果指标会自动更新。"
)

col1, col2 = st.columns(2)

with col1:

    selected_db = st.slider(
        "假设声音水平（dBA）",
        min_value=60,
        max_value=105,
        value=80,
        step=1,
        key="atlas_selected_db",
    )

with col2:

    selected_hours = st.slider(
        "每周累计聆听时间（小时）",
        min_value=0.5,
        max_value=60.0,
        value=20.0,
        step=0.5,
        key="atlas_selected_hours",
    )


# ============================================================
# 09 计算当前情境
# ============================================================

current_exposure = exposure_percent(
    selected_db,
    selected_hours,
    reference_db,
)

current_reference_hours = reference_hours(
    selected_db,
    reference_db,
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "假设声音水平",
    f"{selected_db} dBA",
)

m2.metric(
    "每周参考等能量时长",
    format_hours(current_reference_hours),
)

m3.metric(
    "相对参考暴露量",
    f"{current_exposure:.1f}%",
)

st.caption(
    "100%仅表示达到选定参考模型的等能量参考量，"
    "不能据此判断是否已经发生听力损伤。"
)


# ============================================================
# 10 生成热力图数据
# ============================================================

db_values = np.arange(
    60,
    106,
    1,
)

hour_values = np.arange(
    0.5,
    60.5,
    0.5,
)

db_grid, hours_grid = np.meshgrid(
    db_values,
    hour_values,
)

exposure_grid = (
    hours_grid
    / (
        REFERENCE_HOURS
        * np.power(
            2.0,
            (reference_db - db_grid)
            / EXCHANGE_RATE,
        )
    )
    * 100
)

# 对数色阶仅用于改善视觉对比。
color_grid = np.log10(
    1 + exposure_grid
)


# ============================================================
# 11 绘制声级—时间热力图
# ============================================================

heatmap = go.Figure()

heatmap.add_trace(
    go.Heatmap(
        x=db_values,
        y=hour_values,

        z=color_grid,
        customdata=exposure_grid,

        colorscale=[
            [0.00, "#10345B"],
            [0.20, "#176C93"],
            [0.40, "#20A7AE"],
            [0.60, "#E7BD58"],
            [0.80, "#E87B46"],
            [1.00, "#C84956"],
        ],

        colorbar=dict(
            title="对数色阶",
            thickness=16,
        ),

        hovertemplate=(
            "声音水平：%{x} dBA"
            "<br>每周时长：%{y:.1f} 小时"
            "<br>相对参考暴露量："
            "%{customdata:.1f}%"
            "<extra></extra>"
        ),
    )
)


# ============================================================
# 12 添加100%等能量边界
# ============================================================

boundary_x = np.linspace(
    60,
    105,
    400,
)

boundary_y = (
    REFERENCE_HOURS
    * np.power(
        2.0,
        (reference_db - boundary_x)
        / EXCHANGE_RATE,
    )
)

boundary_mask = (
    (boundary_y >= 0.5)
    & (boundary_y <= 60)
)

heatmap.add_trace(
    go.Scatter(
        x=boundary_x[boundary_mask],
        y=boundary_y[boundary_mask],

        mode="lines",

        name="100%参考边界",

        line=dict(
            color="#FFFFFF",
            width=3,
            dash="dash",
        ),

        hovertemplate=(
            "100%参考等能量边界"
            "<br>声级：%{x:.1f} dBA"
            "<br>每周时长：%{y:.2f} 小时"
            "<extra></extra>"
        ),
    )
)


# ============================================================
# 13 当前情境标记
# ============================================================

heatmap.add_trace(
    go.Scatter(
        x=[selected_db],
        y=[selected_hours],

        mode="markers+text",

        text=["当前情境"],
        textposition="top center",

        name="当前情境",

        marker=dict(
            color="#FFFFFF",
            size=15,
            symbol="circle",

            line=dict(
                color="#142C4B",
                width=3,
            ),
        ),

        textfont=dict(
            color="#FFFFFF",
        ),
    )
)


# ============================================================
# 14 热力图布局
# ============================================================

heatmap = style_plotly(
    heatmap,
    height=570,
)

heatmap.update_layout(
    xaxis=dict(
        title="假设声音水平（dBA）",
        range=[60, 105],
    ),

    yaxis=dict(
        title="每周累计聆听时间（小时）",
        range=[0.5, 60],
    ),

    plot_bgcolor="#10243C",

    legend=dict(
        orientation="h",
        y=1.16,
        x=0,
    ),

    margin=dict(
        l=55,
        r=35,
        t=85,
        b=55,
    ),
)

st.plotly_chart(
    heatmap,
    use_container_width=True,
)

st.caption(
    "颜色使用对数变换增强辨识度。"
    "悬停显示的百分比为未经过对数变换的计算结果。"
    "热力图颜色不是医学风险分级。"
)


# ============================================================
# 15 当前情境解读
# ============================================================

with st.container(border=True):

    st.subheader("📍 当前情境解读")

    st.write(
        f"假设在 **{selected_db} dBA** 下，"
        f"每周累计聆听 "
        f"**{selected_hours:.1f}小时**，"
        f"相对参考暴露量约为 "
        f"**{current_exposure:.1f}%**。"
    )

    if current_exposure < 100:

        st.info(
            explain_exposure(current_exposure)
        )

    else:

        st.warning(
            explain_exposure(current_exposure)
        )

st.divider()


# ============================================================
# 16 双场景输入
# ============================================================

section_label(
    "03",
    "SCENARIO COMPARISON",
)

st.header("③ 双场景声音暴露对比")

st.write(
    "设定两组不同的假设聆听条件，"
    "比较它们在同一参考模式下的"
    "相对声音能量暴露。"
)

a_col, b_col = st.columns(2)

with a_col:

    with st.container(border=True):

        st.subheader("🅰️ 场景 A")

        db_a = st.slider(
            "场景A声音水平（dBA）",
            min_value=60,
            max_value=105,
            value=80,
            key="atlas_db_a",
        )

        hours_a = st.slider(
            "场景A每周时长（小时）",
            min_value=0.5,
            max_value=60.0,
            value=20.0,
            step=0.5,
            key="atlas_hours_a",
        )

with b_col:

    with st.container(border=True):

        st.subheader("🅱️ 场景 B")

        db_b = st.slider(
            "场景B声音水平（dBA）",
            min_value=60,
            max_value=105,
            value=86,
            key="atlas_db_b",
        )

        hours_b = st.slider(
            "场景B每周时长（小时）",
            min_value=0.5,
            max_value=60.0,
            value=20.0,
            step=0.5,
            key="atlas_hours_b",
        )


# ============================================================
# 17 双场景暴露计算
# ============================================================

exposure_a = exposure_percent(
    db_a,
    hours_a,
    reference_db,
)

exposure_b = exposure_percent(
    db_b,
    hours_b,
    reference_db,
)

comparison_df = pd.DataFrame({
    "场景": [
        "场景 A",
        "场景 B",
    ],

    "相对参考暴露量": [
        exposure_a,
        exposure_b,
    ],
})

compare_fig = go.Figure()

compare_fig.add_trace(
    go.Bar(
        x=comparison_df["场景"],
        y=comparison_df["相对参考暴露量"],

        marker_color=[
            COLORS["cyan_light"],
            COLORS["orange"],
        ],

        text=[
            f"{exposure_a:.1f}%",
            f"{exposure_b:.1f}%",
        ],

        textposition="outside",

        hovertemplate=(
            "%{x}<br>"
            "相对参考暴露量：%{y:.1f}%"
            "<extra></extra>"
        ),
    )
)

compare_fig.add_hline(
    y=100,
    line_dash="dash",
    line_color=COLORS["muted"],
    annotation_text="100%参考等能量",
)

compare_fig = style_plotly(
    compare_fig,
    height=430,
)

compare_fig.update_layout(
    yaxis=dict(
        title="相对参考暴露量（%）",

        range=[
            0,
            max(
                150,
                exposure_a * 1.2,
                exposure_b * 1.2,
            ),
        ],
    ),

    showlegend=False,

    margin=dict(
        l=45,
        r=35,
        t=65,
        b=55,
    ),
)

st.plotly_chart(
    compare_fig,
    use_container_width=True,
)


# ============================================================
# 18 双场景比较结果
# ============================================================

ratio = exposure_b / exposure_a

c1, c2, c3 = st.columns(3)

c1.metric(
    "场景A相对暴露量",
    f"{exposure_a:.1f}%",
)

c2.metric(
    "场景B相对暴露量",
    f"{exposure_b:.1f}%",
)

c3.metric(
    "B相对于A",
    f"{ratio:.2f} 倍",
)

st.caption(
    "这个倍数比较的是等能量参考模型中的"
    "相对声音暴露量，"
    "不是听力损失概率的倍数。"
)

if ratio > 1:

    st.info(
        f"当前假设下，场景B的相对参考暴露量"
        f"约为场景A的 **{ratio:.2f}倍**。"
    )

elif ratio < 1:

    st.info(
        "当前假设下，场景B的相对参考暴露量"
        "低于场景A。"
    )

else:

    st.info(
        "两组情境对应相同的相对参考暴露量。"
    )

st.divider()


# ============================================================
# 19 校园场景信息
# ============================================================

SCENE_INFO = {
    "📚 教室／图书馆": (
        "适合关注学习期间的连续耳机使用。",
        "在自习间隙安排主动休息。",
    ),

    "🏠 学生宿舍": (
        "适合关注学习、游戏和娱乐时的聆听习惯。",
        "留意连续播放时间和常用音量。",
    ),

    "🍽️ 校园食堂": (
        "适合观察背景人声是否影响音量选择。",
        "不要为了掩盖周围人声持续提高音量。",
    ),

    "🚶 校园道路": (
        "适合关注移动场景下的聆听行为。",
        "保持对车辆、行人和安全提示的感知。",
    ),

    "🏃 运动场／健身场所": (
        "适合关注运动时的声音与环境感知。",
        "注意周围人员和设备的安全提示。",
    ),
}


# ============================================================
# 20 校园场景模拟
# ============================================================

section_label(
    "04",
    "CAMPUS SCENARIOS",
)

st.header("④ 校园聆听场景图谱")

st.write(
    "选择熟悉的校园场景，"
    "自行输入假设声级与每周聆听时间，"
    "探索不同情境的相对声音暴露量。"
)

st.warning(
    "以下场景不是校园噪声实测数据库。"
    "所有声级均由用户自行假设，"
    "不能据此判断某个校园地点的真实分贝值。"
)

selected_scene = st.selectbox(
    "选择校园场景",
    list(SCENE_INFO),
    key="atlas_selected_scene",
)

scene_description, scene_advice = SCENE_INFO[
    selected_scene
]

with st.container(border=True):

    st.subheader(selected_scene)

    st.write(scene_description)

    sc1, sc2 = st.columns(2)

    with sc1:

        scene_db = st.slider(
            "该情境的假设聆听声级（dBA）",
            min_value=60,
            max_value=105,
            value=78,
            step=1,
            key="atlas_scene_db",
        )

    with sc2:

        scene_hours = st.slider(
            "该情境每周累计聆听时间（小时）",
            min_value=0.5,
            max_value=60.0,
            value=10.0,
            step=0.5,
            key="atlas_scene_hours",
        )

    scene_exposure = exposure_percent(
        scene_db,
        scene_hours,
        reference_db,
    )

    st.metric(
        "当前模拟情境的相对参考暴露量",
        f"{scene_exposure:.1f}%",
    )

    st.info(
        "场景提示：" + scene_advice
    )

st.divider()


# ============================================================
# 21 场景汇总状态
# ============================================================

section_label(
    "05",
    "SCENARIO COLLECTION",
)

st.header("⑤ 我的校园声音暴露情境汇总")

st.write(
    "可以将不同校园场景加入列表，"
    "观察这些假设情境在同一周内的"
    "累计声音能量暴露。"
)

if SCENE_STORAGE_KEY not in st.session_state:

    st.session_state[
        SCENE_STORAGE_KEY
    ] = []


# ============================================================
# 22 添加场景
# ============================================================

if st.button(
    "➕ 添加当前场景到汇总",
    type="primary",
    use_container_width=True,
    key="atlas_add_scene",
):

    st.session_state[
        SCENE_STORAGE_KEY
    ].append({
        "场景": selected_scene,
        "假设声级（dBA）": scene_db,
        "每周时间（小时）": scene_hours,
    })

    st.success(
        "已添加当前模拟场景。"
    )


# ============================================================
# 23 整理已添加场景
# ============================================================

saved_scenes = st.session_state[
    SCENE_STORAGE_KEY
]

if saved_scenes:

    rows = []

    for index, item in enumerate(saved_scenes):

        item_db = item[
            "假设声级（dBA）"
        ]

        item_hours = item[
            "每周时间（小时）"
        ]

        percentage = exposure_percent(
            item_db,
            item_hours,
            reference_db,
        )

        rows.append({
            "编号": index + 1,
            **item,
            "相对参考暴露量（%）": percentage,
        })

    scene_df = pd.DataFrame(rows)

    st.dataframe(
        scene_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "编号": st.column_config.NumberColumn(
                "编号",
                format="%d",
            ),
            "假设声级（dBA）": st.column_config.NumberColumn(
                "假设声级（dBA）",
                format="%d",
            ),
            "每周时间（小时）": st.column_config.NumberColumn(
                "每周时间（小时）",
                format="%.1f",
            ),
            "相对参考暴露量（%）": st.column_config.NumberColumn(
                "相对参考暴露量（%）",
                format="%.1f",
            ),
        },
    )

    total_exposure = scene_df[
        "相对参考暴露量（%）"
    ].sum()

    total_hours = scene_df[
        "每周时间（小时）"
    ].sum()

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "已添加场景",
        f"{len(saved_scenes)} 个",
    )

    s2.metric(
        "累计模拟时长",
        f"{total_hours:.1f} 小时",
    )

    s3.metric(
        "合计相对参考暴露量",
        f"{total_exposure:.1f}%",
    )

    st.caption(
        "合计计算假设各场景发生在同一周、"
        "各段暴露时间互不重叠。"
        "这里只累计已加入的假设情境，"
        "不代表全部实际声音暴露。"
    )

    if total_hours > 168:

        st.warning(
            "场景累计时间超过一周的168小时。"
            "请检查是否重复添加了重叠时间段。"
        )


    # ========================================================
    # 24 场景累计柱状图
    # ========================================================

    scene_fig = go.Figure()

    scene_fig.add_trace(
        go.Bar(
            x=[
                f"{index + 1}. {item['场景']}"
                for index, item in enumerate(saved_scenes)
            ],

            y=scene_df[
                "相对参考暴露量（%）"
            ],

            marker_color=COLORS["cyan_light"],

            text=[
                f"{value:.1f}%"
                for value in scene_df[
                    "相对参考暴露量（%）"
                ]
            ],

            textposition="outside",

            hovertemplate=(
                "%{x}<br>"
                "相对参考暴露量：%{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    scene_fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=COLORS["muted"],
    )

    scene_fig = style_plotly(
        scene_fig,
        height=420,
    )

    scene_fig.update_layout(
        xaxis_title="校园假设情境",
        yaxis_title="相对参考暴露量（%）",

        yaxis_range=[
            0,
            max(
                150,
                scene_df[
                    "相对参考暴露量（%）"
                ].max() * 1.2,
            ),
        ],

        showlegend=False,

        margin=dict(
            l=45,
            r=35,
            t=55,
            b=80,
        ),
    )

    st.plotly_chart(
        scene_fig,
        use_container_width=True,
    )


    # ========================================================
    # 25 删除场景
    # ========================================================

    st.subheader("管理已添加场景")

    remove_options = [
        (
            f"{index + 1}. "
            f"{item['场景']}｜"
            f"{item['假设声级（dBA）']} dBA｜"
            f"{item['每周时间（小时）']:.1f} 小时"
        )
        for index, item in enumerate(saved_scenes)
    ]

    selected_remove_index = st.selectbox(
        "选择要删除的场景",
        options=list(range(len(saved_scenes))),
        format_func=lambda index: remove_options[index],
        key="atlas_remove_index",
    )

    remove_col, clear_col = st.columns(2)

    with remove_col:

        if st.button(
            "🗑️ 删除选中的场景",
            use_container_width=True,
            key="atlas_remove_scene",
        ):

            st.session_state[
                SCENE_STORAGE_KEY
            ].pop(selected_remove_index)

            st.rerun()

    with clear_col:

        if st.button(
            "清空全部场景",
            use_container_width=True,
            key="atlas_clear_all",
        ):

            st.session_state[
                SCENE_STORAGE_KEY
            ] = []

            st.rerun()

else:

    st.info(
        "当前还没有添加场景。"
        "可以先在上方选择一个校园情境，"
        "然后点击添加按钮。"
    )


# ============================================================
# 26 返回声音暴露模拟器
# ============================================================

st.divider()

section_label(
    "06",
    "CONTINUE EXPLORING",
)

st.header("⑥ 继续探索 HearGuard Campus")

st.write(
    "声音暴露图谱适合查看"
    "声级与时间的整体关系；"
    "声音暴露模拟器则适合"
    "调整每日时长和每周天数。"
)

if st.button(
    "🔊 返回声音暴露模拟器 →",
    type="primary",
    use_container_width=True,
    key="atlas_open_simulator",
):

    st.switch_page(
        "pages/3_声音暴露模拟器.py"
    )


# ============================================================
# 27 方法与适用限制
# ============================================================

st.divider()

with st.expander(
    "📖 查看科学计算方法与适用限制"
):

    st.markdown(
        """
### 一、参考模型

本页面提供两种教育性参考：

**成人参考模式：**

80 dBA × 40小时/周

**较保守参考模式：**

75 dBA × 40小时/周

### 二、等能量换算

采用近似3 dB交换规则。

每周参考时长：

`T = 40 × 2^((Lref - L)/3)`

其中：

- `Lref`：所选参考声级
- `L`：假设聆听声级
- `T`：对应的参考时间

### 三、相对参考暴露量

`E = 假设累计时间 / T × 100%`

例如：

成人模式下，

80 dBA × 40小时/周

对应100%的相对参考暴露量。

83 dBA × 40小时/周

对应200%的相对参考暴露量。

### 四、多场景累计

对于同一周内互不重叠的假设情境：

`E_total = E1 + E2 + ... + En`

每一段场景需要使用相同的参考模型。

如果场景时间重叠，直接累加可能造成重复计算。

### 五、重要限制

1. dBA代表A计权声级，不能从普通音量百分比直接换算。
2. 本页面不进行实际声级测量。
3. 全部情境均由用户自行设定。
4. 热力图颜色不是医学风险分级。
5. 100%不是医学意义上的绝对安全或危险边界。
6. 实际声音暴露可能来自耳机以外的其他声源。
7. 本计算不能用于听力损失概率预测。
8. 本模块不能替代专业听力检查。

### 六、参考来源

WHO–ITU：

*Safe Listening Devices and Systems: A WHO–ITU Standard*

可在项目的「方法与数据来源」页面查看
参考资料及研究边界。
        """
    )


# ============================================================
# 28 页脚
# ============================================================

st.caption(
    "HearGuard Campus · Sound Exposure Atlas"
)

st.caption(
    "For educational and research communication purposes only."
)