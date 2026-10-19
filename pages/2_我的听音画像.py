"""
HearGuard Campus · 声护校园
我的听音画像 V1.3

主要功能：
1. 四项核心聆听习惯
2. 100分教育性行为评分
3. 五项可选深度画像
4. 四维雷达图
5. 行为评分构成可视化
6. 校园场景化行为反馈
7. 与个性化建议页面共享数据
8. HearGuard Campus V1.3 公共主题

科学说明：
本模块仅用于安全聆听健康教育。
不进行医学诊断，不预测听力损失概率。
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
    page_title="我的听音画像 | HearGuard Campus",
    page_icon="🎧",
    layout="wide",
)

apply_theme()


# ============================================================
# 03 页面专属视觉
# ============================================================

st.markdown(
    """
<style>

.hg-profile-hero {
    background: linear-gradient(
        125deg,
        #081729 0%,
        #102b49 55%,
        #123d58 100%
    );

    border: 1px solid rgba(71,199,243,0.25);
    border-radius: 18px;

    padding: 30px 32px;
    margin-bottom: 20px;
}

.hg-profile-hero-title {
    font-size: clamp(25px, 3vw, 34px);
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 12px;
}

.hg-profile-hero-description {
    font-size: 15px;
    line-height: 1.9;
    color: #c5e2ee;
}

.hg-section-label {
    color: #43bad7;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.6px;
    margin-bottom: 8px;
}

.hg-profile-note {
    font-size: 13px;
    opacity: 0.8;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 04 共享数据配置
# ============================================================

PROFILE_KEY = "hearguard_shared_profile"

PROFILE_RESULT_KEY = "hearguard_profile_result"


# ============================================================
# 05 选项配置
# ============================================================

VOLUME_OPTIONS = [
    "较低",
    "中等",
    "较高",
    "很高",
]

ENVIRONMENT_OPTIONS = [
    "安静室内",
    "宿舍",
    "校园",
    "公共交通",
    "其他嘈杂环境",
]

BREAK_OPTIONS = [
    "经常",
    "有时",
    "很少",
    "几乎没有",
]

HEADPHONE_OPTIONS = [
    "入耳式",
    "半入耳式",
    "耳夹式",
    "骨传导",
    "头戴式",
    "其他／不确定",
]

MODE_OPTIONS = [
    "主动降噪（ANC）",
    "通透模式",
    "普通模式／关闭降噪",
    "设备不支持",
    "不确定",
]

SCENE_OPTIONS = [
    "教室／图书馆",
    "宿舍",
    "食堂",
    "校园道路",
    "运动场／健身场所",
    "公共交通",
    "其他",
]

REMOVE_OPTIONS = [
    "主动安排休息，即使没有不适",
    "感到耳部不适或听觉疲劳",
    "需要与他人交流",
    "从嘈杂环境进入安静环境",
    "到达目的地或活动结束",
    "需要注意周围环境或安全提示",
    "通常很少主动摘下耳机",
    "其他",
]

DISCOMFORT_OPTIONS = [
    "从未出现",
    "偶尔出现",
    "经常出现",
    "不确定",
]

ONSET_OPTIONS = [
    "30分钟以内",
    "30分钟至1小时",
    "1至2小时",
    "超过2小时",
    "不固定",
]


# ============================================================
# 06 默认画像
# ============================================================

DEFAULT_PROFILE = {
    "hours": 2.0,
    "volume": "中等",
    "environment": "安静室内",
    "breaks": "有时",

    "extra_enabled": False,

    "headphone_type": "入耳式",
    "sound_mode": "不确定",

    "campus_scenes": [],
    "remove_reasons": [],

    "discomfort": "不确定",
    "discomfort_onset": None,
}


# ============================================================
# 07 通用函数
# ============================================================

def section_label(number, english):
    """
    统一章节标签。
    """

    html = (
        '<div class="hg-section-label">'
        f'{number} / {english}'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def saved_profile():
    """
    读取当前会话中的完整画像。

    保留旧版本字段及深度画像信息。
    """

    data = st.session_state.get(PROFILE_KEY)

    profile = DEFAULT_PROFILE.copy()

    if isinstance(data, dict):

        profile.update({
            key: value
            for key, value in data.items()
            if key in profile
        })

    for key in [
        "campus_scenes",
        "remove_reasons",
    ]:

        if isinstance(profile.get(key), list):
            profile[key] = profile[key].copy()
        else:
            profile[key] = []

    return profile


def init_widget(key, value, options=None):
    """
    仅在组件尚未创建时初始化状态。
    """

    if key not in st.session_state:

        if options is None or value in options:

            st.session_state[key] = value

        else:

            st.session_state[key] = options[0]


def create_profile_snapshot(profile):
    """
    生成共享画像的快照，用于识别其他页面
    是否更新了画像信息。
    """

    return (
        profile["hours"],
        profile["volume"],
        profile["environment"],
        profile["breaks"],
        profile["extra_enabled"],
        profile["headphone_type"],
        profile["sound_mode"],
        tuple(profile["campus_scenes"]),
        tuple(profile["remove_reasons"]),
        profile["discomfort"],
        profile["discomfort_onset"],
    )


# ============================================================
# 08 原有100分评分模型
# ============================================================

def calculate_profile(profile):
    """
    保留原有四维评分：

    使用时长：最高40分
    音量习惯：最高30分
    环境暴露：最高15分
    休息习惯：最高15分

    总分最高100分。

    分数是教育性行为关注指数，
    不是疾病风险概率。
    """

    hours = float(profile["hours"])

    # --------------------------------------------------------
    # 使用时长
    # --------------------------------------------------------

    if hours < 1:
        duration_score = 5

    elif hours < 2:
        duration_score = 10

    elif hours < 4:
        duration_score = 20

    elif hours < 6:
        duration_score = 30

    else:
        duration_score = 40

    # --------------------------------------------------------
    # 音量习惯
    # --------------------------------------------------------

    volume_scores = {
        "较低": 5,
        "中等": 10,
        "较高": 20,
        "很高": 30,
    }

    volume_score = volume_scores[
        profile["volume"]
    ]

    # --------------------------------------------------------
    # 环境暴露
    # --------------------------------------------------------

    environment_scores = {
        "安静室内": 0,
        "宿舍": 5,
        "校园": 8,
        "公共交通": 15,
        "其他嘈杂环境": 15,
    }

    environment_score = environment_scores[
        profile["environment"]
    ]

    # --------------------------------------------------------
    # 休息习惯
    # --------------------------------------------------------

    break_scores = {
        "经常": 0,
        "有时": 5,
        "很少": 10,
        "几乎没有": 15,
    }

    break_score = break_scores[
        profile["breaks"]
    ]

    # --------------------------------------------------------
    # 分维度结果
    # --------------------------------------------------------

    scores = {
        "使用时长": duration_score,
        "音量习惯": volume_score,
        "环境暴露": environment_score,
        "休息习惯": break_score,
    }

    maximums = {
        "使用时长": 40,
        "音量习惯": 30,
        "环境暴露": 15,
        "休息习惯": 15,
    }

    percentages = {
        key: scores[key] / maximums[key] * 100
        for key in scores
    }

    total = sum(scores.values())

    # --------------------------------------------------------
    # 教育性关注等级
    # --------------------------------------------------------

    if total < 30:

        level = "较低"

        message = (
            "当前填写的行为因素整体关注程度较低。"
        )

    elif total < 50:

        level = "一般"

        message = (
            "部分聆听习惯值得继续关注。"
        )

    elif total < 70:

        level = "需要关注"

        message = (
            "目前存在多个值得改善的聆听行为因素。"
        )

    else:

        level = "重点关注"

        message = (
            "当前多个聆听行为因素需要优先关注。"
        )

    return {
        "profile": profile.copy(),
        "scores": scores,
        "maximums": maximums,
        "percentages": percentages,
        "total_score": total,
        "risk_level": level,
        "risk_message": message,
    }


# ============================================================
# 09 初始化输入状态
# ============================================================

previous = saved_profile()

# ------------------------------------------------------------
# 与其他页面共享数据时的兼容性处理
# ------------------------------------------------------------

snapshot = create_profile_snapshot(previous)

last_snapshot = st.session_state.get(
    "hg_profile_loaded_snapshot"
)

# 第一次访问或其他页面更新共享画像后，
# 在创建表单组件之前更新对应输入。

if last_snapshot != snapshot:

    st.session_state[
        "hg_profile_hours"
    ] = float(previous["hours"])

    st.session_state[
        "hg_profile_volume"
    ] = (
        previous["volume"]
        if previous["volume"] in VOLUME_OPTIONS
        else VOLUME_OPTIONS[0]
    )

    st.session_state[
        "hg_profile_environment"
    ] = (
        previous["environment"]
        if previous["environment"] in ENVIRONMENT_OPTIONS
        else ENVIRONMENT_OPTIONS[0]
    )

    st.session_state[
        "hg_profile_breaks"
    ] = (
        previous["breaks"]
        if previous["breaks"] in BREAK_OPTIONS
        else BREAK_OPTIONS[0]
    )

    st.session_state[
        "hg_extra_enabled"
    ] = bool(
        previous["extra_enabled"]
    )

    st.session_state[
        "hg_headphone_type"
    ] = (
        previous["headphone_type"]
        if previous["headphone_type"] in HEADPHONE_OPTIONS
        else HEADPHONE_OPTIONS[0]
    )

    st.session_state[
        "hg_sound_mode"
    ] = (
        previous["sound_mode"]
        if previous["sound_mode"] in MODE_OPTIONS
        else MODE_OPTIONS[0]
    )

    st.session_state[
        "hg_discomfort"
    ] = (
        previous["discomfort"]
        if previous["discomfort"] in DISCOMFORT_OPTIONS
        else DISCOMFORT_OPTIONS[0]
    )

    st.session_state[
        "hg_discomfort_onset"
    ] = (
        previous["discomfort_onset"]
        if previous["discomfort_onset"] in ONSET_OPTIONS
        else ONSET_OPTIONS[0]
    )

    st.session_state[
        "hg_scenes"
    ] = [
        value
        for value in previous["campus_scenes"]
        if value in SCENE_OPTIONS
    ]

    st.session_state[
        "hg_remove"
    ] = [
        value
        for value in previous["remove_reasons"]
        if value in REMOVE_OPTIONS
    ]

    st.session_state[
        "hg_profile_loaded_snapshot"
    ] = snapshot


# ============================================================
# 10 页面主视觉
# ============================================================

hero_html = (
    '<div class="hg-profile-hero">'

    '<div class="hg-profile-hero-title">'
    '🎧 我的听音画像'
    '</div>'

    '<div class="hg-profile-hero-description">'
    '从四项核心聆听习惯出发，生成可解释的行为画像。'
    '<br>'
    '你也可以补充耳机佩戴方式、校园使用场景和个人体验，'
    '让反馈更贴近日常生活。'
    '</div>'

    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)

st.caption(
    "HEARGUARD CAMPUS · PERSONAL LISTENING PROFILE"
)

st.info(
    "本模块用于安全聆听健康教育。"
    "教育性行为评分不是听力损失概率，"
    "也不是医学诊断。"
    "自报音量不能直接换算为dBA。"
)

st.divider()


# ============================================================
# 11 四项基础聆听习惯
# ============================================================

section_label(
    "01",
    "BASIC LISTENING HABITS",
)

st.header("① 基础聆听习惯 · 4项必填")

col1, col2 = st.columns(2)

with col1:

    hours = st.slider(
        "你每天使用耳机大约多长时间？",
        min_value=0.0,
        max_value=10.0,
        step=0.5,
        key="hg_profile_hours",
    )

    volume = st.selectbox(
        "你通常使用的音量水平？（主观感受）",
        VOLUME_OPTIONS,
        key="hg_profile_volume",
    )

with col2:

    environment = st.selectbox(
        "你最常在哪种环境中使用耳机？",
        ENVIRONMENT_OPTIONS,
        key="hg_profile_environment",
    )

    breaks = st.selectbox(
        "你是否会定期暂停使用耳机，让耳朵休息？",
        BREAK_OPTIONS,
        key="hg_profile_breaks",
    )

st.caption(
    "请根据自己的实际习惯选择。"
    "这些输入用于教育性行为分析，"
    "不是专业声级测量结果。"
)

st.divider()


# ============================================================
# 12 深度画像
# ============================================================

section_label(
    "02",
    "DEEP LISTENING PROFILE",
)

st.header("② 深度画像 · 5项可选")

extra_enabled = st.checkbox(
    "补充佩戴方式与校园场景，获取更细致的反馈",
    key="hg_extra_enabled",
)

headphone_type = None
sound_mode = None

campus_scenes = []
remove_reasons = []

discomfort = None
discomfort_onset = None


if extra_enabled:

    with st.container(border=True):

        ec1, ec2 = st.columns(2)

        with ec1:

            headphone_type = st.selectbox(
                "常用耳机类型",
                HEADPHONE_OPTIONS,
                key="hg_headphone_type",
            )

            campus_scenes = st.multiselect(
                "你经常在哪些校园场景使用耳机？（多选）",
                SCENE_OPTIONS,
                key="hg_scenes",
            )

        with ec2:

            sound_mode = st.selectbox(
                "最常使用的声音模式",
                MODE_OPTIONS,
                key="hg_sound_mode",
            )

            remove_reasons = st.multiselect(
                "你通常因为什么摘下耳机？（多选）",
                REMOVE_OPTIONS,
                key="hg_remove",
            )

        discomfort = st.selectbox(
            "你是否曾在使用耳机时感到耳部不适或听觉疲劳？",
            DISCOMFORT_OPTIONS,
            key="hg_discomfort",
        )

        if discomfort in [
            "偶尔出现",
            "经常出现",
        ]:

            discomfort_onset = st.selectbox(
                "如果出现过，通常在连续使用多久后？",
                ONSET_OPTIONS,
                key="hg_discomfort_onset",
            )

    st.caption(
        "补充信息用于生成校园场景反馈，"
        "不参与现有100分评分。"
        "佩戴体验不用于判断是否患病。"
    )

else:

    st.info(
        "只填写上方四项，"
        "也可以生成完整的基础行为画像。"
    )


# ============================================================
# 13 整理当前画像
# ============================================================

current_profile = {
    "hours": float(hours),

    "volume": volume,
    "environment": environment,
    "breaks": breaks,

    "extra_enabled": bool(extra_enabled),

    "headphone_type": headphone_type,
    "sound_mode": sound_mode,

    "campus_scenes": list(campus_scenes),
    "remove_reasons": list(remove_reasons),

    "discomfort": discomfort,
    "discomfort_onset": discomfort_onset,
}


# ============================================================
# 14 生成画像
# ============================================================

if st.button(
    "🎧 生成我的听音画像",
    type="primary",
    use_container_width=True,
    key="hg_profile_generate",
):

    # 保存完整画像

    st.session_state[
        PROFILE_KEY
    ] = current_profile.copy()

    # 保存100分模型结果

    st.session_state[
        PROFILE_RESULT_KEY
    ] = calculate_profile(
        current_profile
    )

    # 同步快照，避免下次重运行时
    # 覆盖用户刚刚填写的内容。

    st.session_state[
        "hg_profile_loaded_snapshot"
    ] = create_profile_snapshot(
        current_profile
    )

    st.success(
        "听音画像已生成，并保存在当前会话中。"
        "可以继续进入个性化建议页面。"
    )


# ============================================================
# 15 读取画像结果
# ============================================================

result = st.session_state.get(
    PROFILE_RESULT_KEY
)

required_keys = (
    "profile",
    "scores",
    "maximums",
    "percentages",
    "total_score",
    "risk_level",
    "risk_message",
)

if (
    not isinstance(result, dict)
    or not all(
        key in result
        for key in required_keys
    )
):

    st.info(
        "请填写信息后，"
        "点击上方按钮生成你的听音画像。"
    )

    st.stop()


if current_profile != result["profile"]:

    st.warning(
        "你已经修改了部分输入。"
        "下方仍是上一次生成的画像，"
        "请再次点击生成按钮更新。"
    )


profile = result["profile"]

scores = result["scores"]

maximums = result["maximums"]

percentages = result["percentages"]

level = result["risk_level"]


# ============================================================
# 16 核心画像结果
# ============================================================

st.divider()

section_label(
    "03",
    "PROFILE OVERVIEW",
)

st.header("③ 你的聆听行为画像")

a, b, c = st.columns(3)

a.metric(
    "每日耳机使用",
    f"{profile['hours']:.1f} 小时",
)

b.metric(
    "常用音量（主观）",
    profile["volume"],
)

c.metric(
    "教育性行为评分",
    f"{result['total_score']} / 100",
)

st.progress(
    min(
        result["total_score"] / 100,
        1.0,
    )
)

notice = (
    f"行为关注等级：{level}。"
    f"{result['risk_message']}"
)

if level == "较低":

    st.success(notice)

elif level == "一般":

    st.info(notice)

elif level == "需要关注":

    st.warning(notice)

else:

    st.warning(notice)

st.caption(
    "分数是项目内部的教育性行为关注指数。"
    "高分不等于临床疾病概率，"
    "低分也不能排除健康问题。"
)


# ============================================================
# 17 四维行为雷达图
# ============================================================

st.divider()

section_label(
    "04",
    "LISTENING RADAR",
)

st.header("④ 四维行为雷达图")

labels = list(percentages)

values = [
    percentages[key]
    for key in labels
]

radar = go.Figure()

radar.add_trace(
    go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",

        line=dict(
            color=COLORS["cyan_light"],
            width=3,
        ),

        fillcolor="rgba(71,199,243,0.24)",

        marker=dict(
            color=COLORS["cyan_light"],
            size=8,
        ),

        name="行为画像",

        hovertemplate=(
            "%{theta}<br>"
            "相对维度得分：%{r:.0f}%"
            "<extra></extra>"
        ),
    )
)

radar = style_plotly(
    radar,
    height=460,
)

radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickvals=[
                0,
                25,
                50,
                75,
                100,
            ],
        ),

        bgcolor="rgba(0,0,0,0)",
    ),

    showlegend=False,

    margin=dict(
        l=55,
        r=55,
        t=45,
        b=45,
    ),
)

st.plotly_chart(
    radar,
    use_container_width=True,
)

st.caption(
    "各轴显示该维度得分占其满分的百分比。"
    "越靠外表示在本项目规则下"
    "该维度越值得关注。"
)


# ============================================================
# 18 行为评分构成
# ============================================================

st.divider()

section_label(
    "05",
    "SCORE COMPOSITION",
)

st.header("⑤ 行为评分构成")

score_df = pd.DataFrame({
    "行为维度": list(scores),

    "当前得分": list(scores.values()),

    "维度满分": [
        maximums[key]
        for key in scores
    ],

    "相对占比（%）": [
        percentages[key]
        for key in scores
    ],
})

bar = go.Figure()

bar.add_trace(
    go.Bar(
        x=score_df["行为维度"],

        y=score_df["相对占比（%）"],

        text=[
            f"{value:.0f}%"
            for value in score_df["相对占比（%）"]
        ],

        textposition="outside",

        marker_color=COLORS["cyan_light"],

        hovertemplate=(
            "%{x}<br>"
            "相对维度得分：%{y:.0f}%"
            "<extra></extra>"
        ),
    )
)

bar = style_plotly(
    bar,
    height=385,
)

bar.update_layout(
    showlegend=False,

    yaxis=dict(
        title="相对维度得分（%）",
        range=[0, 110],
    ),

    margin=dict(
        l=35,
        r=35,
        t=50,
        b=45,
    ),
)

st.plotly_chart(
    bar,
    use_container_width=True,
)

with st.expander("📊 查看四维评分明细"):

    st.dataframe(
        score_df,
        hide_index=True,
        use_container_width=True,
    )


# ============================================================
# 19 深度画像结果
# ============================================================

if profile.get("extra_enabled"):

    st.divider()

    section_label(
        "06",
        "CAMPUS LISTENING CONTEXT",
    )

    st.header("⑥ 我的校园聆听情境")

    ex1, ex2 = st.columns(2)

    with ex1:

        with st.container(border=True):

            st.subheader("🎧 佩戴与声音模式")

            st.write(
                "耳机类型："
                + (
                    profile.get("headphone_type")
                    or "未填写"
                )
            )

            st.write(
                "常用模式："
                + (
                    profile.get("sound_mode")
                    or "未填写"
                )
            )

            st.write(
                "不适体验："
                + (
                    profile.get("discomfort")
                    or "未填写"
                )
            )

            if profile.get("discomfort_onset"):

                st.write(
                    "出现不适的时间："
                    + profile["discomfort_onset"]
                )

    with ex2:

        with st.container(border=True):

            st.subheader("🏫 校园场景与摘机习惯")

            scenes = profile.get(
                "campus_scenes"
            ) or []

            reasons = profile.get(
                "remove_reasons"
            ) or []

            st.write(
                "常用场景："
                + (
                    "、".join(scenes)
                    or "未选择"
                )
            )

            st.write(
                "摘机原因："
                + (
                    "、".join(reasons)
                    or "未选择"
                )
            )


# ============================================================
# 20 需要关注的行为因素
# ============================================================

st.divider()

section_label(
    "07",
    "BEHAVIOR FACTORS",
)

st.header("⑦ 需要关注的行为因素与建议")

risks = []

if percentages["使用时长"] >= 75:

    risks.append(
        "每日耳机使用时间较长"
    )

if percentages["音量习惯"] >= 65:

    risks.append(
        "日常耳机音量偏高（主观报告）"
    )

if percentages["环境暴露"] >= 65:

    risks.append(
        "较常在嘈杂环境中使用耳机"
    )

if percentages["休息习惯"] >= 65:

    risks.append(
        "缺乏规律的耳机使用休息"
    )


if risks:

    st.warning(
        "；".join(risks)
    )

else:

    st.success(
        "按照本项目内部评分规则，"
        "目前没有特别突出的高分维度。"
    )


# ============================================================
# 21 生成个性化建议
# ============================================================

suggestions = []

# ------------------------------------------------------------
# 基础建议
# ------------------------------------------------------------

if percentages["使用时长"] >= 50:

    suggestions.append((
        "安排主动休息",
        "减少长时间连续佩戴，"
        "学习或观看视频时主动安排无耳机休息。",
    ))

if percentages["音量习惯"] >= 50:

    suggestions.append((
        "关注实际音量",
        "避免为追求清晰度长期维持较高音量；"
        "设备上的音量百分比不能直接代表声压级。",
    ))

if percentages["环境暴露"] >= 50:

    suggestions.append((
        "避免背景噪声补偿",
        "嘈杂环境中留意自己是否会不自觉调高音量，"
        "可以暂停播放或选择更安静的环境。",
    ))

if percentages["休息习惯"] >= 50:

    suggestions.append((
        "提前安排休息",
        "不要等到不适才摘下耳机，"
        "尝试在连续使用过程中主动暂停。",
    ))


# ------------------------------------------------------------
# 深度画像建议
# ------------------------------------------------------------

if profile.get("extra_enabled"):

    scenes = profile.get(
        "campus_scenes"
    ) or []

    reasons = profile.get(
        "remove_reasons"
    ) or []

    # 食堂场景

    if "食堂" in scenes:

        suggestions.append((
            "食堂使用情境",
            "食堂人声可能较多，"
            "留意是否为了盖过背景声"
            "而持续提高耳机音量。",
        ))

    # 校园道路与公共交通

    if (
        "校园道路" in scenes
        or "公共交通" in scenes
    ):

        suggestions.append((
            "出行安全",
            "在道路和乘车情境中，"
            "优先保持对车辆、广播和警示声的感知，"
            "必要时暂停音频。",
        ))

    # 主动降噪

    if profile.get(
        "sound_mode"
    ) == "主动降噪（ANC）":

        suggestions.append((
            "降噪不等于零暴露",
            "主动降噪可能减少背景声干扰，"
            "但实际聆听声级和使用时间仍需关注。",
        ))

    # 主动休息

    if (
        "通常很少主动摘下耳机" in reasons
        or "感到耳部不适或听觉疲劳" in reasons
    ):

        suggestions.append((
            "从被动摘机转向主动暂停",
            "可以尝试提前安排休息提醒，"
            "而不是等到佩戴不适后才暂停。",
        ))

    # 不适体验

    if profile.get("discomfort") in [
        "偶尔出现",
        "经常出现",
    ]:

        suggestions.append((
            "关注不适体验",
            "出现不适时停止使用并休息。"
            "如不适持续或反复出现，"
            "或伴随听力变化，建议咨询专业人员。",
        ))

    # 耳机类型

    if profile.get("headphone_type") in [
        "入耳式",
        "半入耳式",
        "耳夹式",
        "骨传导",
        "头戴式",
    ]:

        suggestions.append((
            "关注佩戴舒适度",
            "选择合适的佩戴方式并注意舒适度。"
            "耳机类型本身不能推断个人听力风险。",
        ))


# ------------------------------------------------------------
# 默认建议
# ------------------------------------------------------------

if not suggestions:

    suggestions.append((
        "保持并观察",
        "继续留意音量、使用时长、"
        "环境和主动休息习惯。",
    ))


# ============================================================
# 22 展示建议卡片
# ============================================================

st.subheader("个性化行为建议")

for heading, detail in suggestions:

    with st.container(border=True):

        st.markdown(
            f"**{heading}**"
        )

        st.write(detail)


# ============================================================
# 23 页面跳转
# ============================================================

st.divider()

section_label(
    "08",
    "NEXT STEPS",
)

st.header("⑧ 下一步")

st.write(
    "当前画像已保存到本次会话，"
    "可以进入个性化建议与七天行动计划。"
    "深度画像信息也会共享给后续页面。"
)

next1, next2 = st.columns(2)

with next1:

    if st.button(
        "💡 进入个性化建议 →",
        type="primary",
        use_container_width=True,
        key="hg_profile_to_advice",
    ):

        st.switch_page(
            "pages/4_个性化建议.py"
        )

with next2:

    if st.button(
        "🔊 进入声音暴露模拟器 →",
        use_container_width=True,
        key="hg_profile_to_simulator",
    ):

        st.switch_page(
            "pages/3_声音暴露模拟器.py"
        )


# ============================================================
# 24 模型说明
# ============================================================

st.divider()

with st.expander(
    "📖 查看行为评分模型与数据说明"
):

    st.markdown(
        """
### 一、教育性行为评分

本页面采用以下四维规则：

- 使用时长：最高40分
- 音量习惯：最高30分
- 环境暴露：最高15分
- 休息习惯：最高15分

**总分最高100分。**

各维度得分经过标准化后，
用于生成四维雷达图。

### 二、深度画像

额外收集五项可选信息：

1. 耳机类型
2. 常用声音模式
3. 校园使用场景
4. 摘下耳机的原因
5. 佩戴不适体验

这些信息不会加入100分评分，
主要用于生成个性化场景建议。

### 三、评分解释

本模型是HearGuard Campus原型阶段
使用的教育性行为可视化指标。

该模型尚未经过临床有效性验证。

高分不等于疾病发生概率，
低分也不能保证没有健康风险。

### 四、声音水平说明

主观音量感受和设备音量百分比
不能直接换算成固定dBA。

实际耳机输出声级会受到设备、
耳机、音频内容和佩戴条件等因素影响。

### 五、数据保存

本页面使用Streamlit会话状态
与其他功能页面共享个人画像。

当前没有实现长期账户数据库。

浏览器会话结束、服务重启或连接中断后，
数据不保证保留。

### 六、医学边界

本页面仅用于安全聆听健康教育。

不能替代专业听力检查，
不用于听力损失诊断或疾病概率预测。
        """
    )


# ============================================================
# 25 页脚
# ============================================================

st.caption(
    "HearGuard Campus · 我的听音画像"
)

st.caption(
    "For educational and research communication purposes only."
)