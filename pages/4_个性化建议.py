"""
HearGuard Campus · 声护校园
个性化安全聆听建议 V1.3

功能：
1. 自动读取个人听音画像
2. 四维行为关注因素分析
3. 校园场景化聆听建议
4. 耳机类型与声音模式反馈
5. 佩戴舒适度及主动休息反馈
6. 个性化七天行动计划
7. 七天任务进度记录
8. 与其他页面共享会话数据
9. HearGuard Campus V1.3 统一主题

注意：
本模块仅用于健康教育和行为反馈。
不提供医学诊断或听力损失概率预测。
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
import sys


# ============================================================
# 01 项目路径与主题
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.theme import apply_theme, style_plotly, COLORS


# ============================================================
# 02 页面配置
# ============================================================

st.set_page_config(
    page_title="个性化建议 | HearGuard Campus",
    page_icon="💡",
    layout="wide",
)

apply_theme()


# ============================================================
# 03 页面专属样式
# ============================================================

st.markdown(
    """
<style>

.hg-section-label {
    color: #43bad7;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.6px;
    margin-bottom: 8px;
}

.hg-advice-intro {
    background: linear-gradient(
        120deg,
        #0b2037,
        #123b54
    );

    border: 1px solid rgba(71, 199, 243, 0.25);
    border-radius: 18px;

    padding: 28px 30px;
    margin-bottom: 20px;

    color: #ffffff;
}

.hg-advice-intro-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 12px;
}

.hg-advice-intro-text {
    color: #c5e2ee;
    font-size: 15px;
    line-height: 1.9;
}

.hg-day-label {
    color: #3fc5de;
    font-weight: 700;
    font-size: 13px;
}

.hg-progress-note {
    font-size: 13px;
    opacity: 0.75;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 04 共享数据配置
# ============================================================

PROFILE_KEY = "hearguard_shared_profile"

ADVICE_RESULT_KEY = "hearguard_advice_result"

PLAN_PROGRESS_KEY = "hearguard_plan_progress"

PLAN_VERSION_KEY = "hearguard_plan_version"


# ============================================================
# 05 基础选项
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


DEFAULT_PROFILE = {
    "hours": 2.0,
    "volume": "中等",
    "environment": "安静室内",
    "breaks": "有时",

    "extra_enabled": False,
    "headphone_type": None,
    "sound_mode": None,
    "campus_scenes": [],
    "remove_reasons": [],
    "discomfort": None,
    "discomfort_onset": None,
}


# ============================================================
# 06 通用组件
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


def get_saved_profile():
    """
    读取共享画像。

    保留全部深度画像字段，
    避免在建议页面修改基础信息时丢失补充内容。
    """

    saved = st.session_state.get(PROFILE_KEY)

    profile = DEFAULT_PROFILE.copy()

    if isinstance(saved, dict):

        for key in DEFAULT_PROFILE:

            if key in saved:
                profile[key] = saved[key]

    for key in [
        "campus_scenes",
        "remove_reasons",
    ]:

        value = profile.get(key)

        if isinstance(value, list):
            profile[key] = value.copy()
        else:
            profile[key] = []

    return profile


def save_profile(profile):
    """
    保存完整共享画像。
    """

    saved = profile.copy()

    for key in [
        "campus_scenes",
        "remove_reasons",
    ]:

        saved[key] = list(
            profile.get(key) or []
        )

    st.session_state[PROFILE_KEY] = saved


# ============================================================
# 07 四维行为因素计算
# ============================================================

def calculate_advice(profile):
    """
    使用原有的1～4分教育性行为排序规则。

    不改变画像页面的100分制。
    两套评分不能直接比较。
    """

    hours = float(profile["hours"])

    volume = profile["volume"]

    environment = profile["environment"]

    breaks = profile["breaks"]

    risks = []

    # --------------------------------------------------------
    # 使用时长
    # --------------------------------------------------------

    if hours >= 6:

        duration_score = 4
        duration_message = "每日耳机使用时间较长"

    elif hours >= 4:

        duration_score = 3
        duration_message = "每日耳机使用时间偏长"

    elif hours >= 2:

        duration_score = 2
        duration_message = "建议继续关注连续使用时间"

    else:

        duration_score = 1
        duration_message = "每日耳机使用时间相对较短"

    risks.append({
        "name": "使用时长",
        "score": duration_score,
        "message": duration_message,
    })

    # --------------------------------------------------------
    # 音量习惯
    # --------------------------------------------------------

    volume_scores = {
        "较低": 1,
        "中等": 2,
        "较高": 3,
        "很高": 4,
    }

    volume_messages = {
        "较低": "自报常用音量较低",
        "中等": "自报常用音量为中等",
        "较高": "自报常用音量偏高",
        "很高": "自报常用音量很高，需要优先关注",
    }

    risks.append({
        "name": "音量习惯",
        "score": volume_scores[volume],
        "message": volume_messages[volume],
    })

    # --------------------------------------------------------
    # 使用环境
    # --------------------------------------------------------

    environment_scores = {
        "安静室内": 1,
        "宿舍": 2,
        "校园": 2,
        "公共交通": 4,
        "其他嘈杂环境": 4,
    }

    environment_messages = {
        "安静室内": "主要在安静室内使用耳机",
        "宿舍": "宿舍是主要使用环境",
        "校园": "校园环境是主要使用场景",
        "公共交通": "经常在公共交通环境中使用耳机",
        "其他嘈杂环境": "经常在较嘈杂环境中使用耳机",
    }

    risks.append({
        "name": "环境暴露",
        "score": environment_scores[environment],
        "message": environment_messages[environment],
    })

    # --------------------------------------------------------
    # 主动休息
    # --------------------------------------------------------

    break_scores = {
        "经常": 1,
        "有时": 2,
        "很少": 3,
        "几乎没有": 4,
    }

    break_messages = {
        "经常": "已有主动暂停耳机使用的习惯",
        "有时": "偶尔会主动安排休息",
        "很少": "主动休息较少",
        "几乎没有": "几乎没有规律的休息习惯",
    }

    risks.append({
        "name": "休息习惯",
        "score": break_scores[breaks],
        "message": break_messages[breaks],
    })

    risks_sorted = sorted(
        risks,
        key=lambda item: item["score"],
        reverse=True,
    )

    total_score = sum(
        item["score"] for item in risks
    )

    # 保留原有教育性关注等级

    if total_score <= 6:
        overall_level = "较低"

    elif total_score <= 9:
        overall_level = "一般"

    elif total_score <= 12:
        overall_level = "需要关注"

    else:
        overall_level = "重点关注"

    attention_count = sum(
        1
        for item in risks
        if item["score"] >= 3
    )

    return {
        "profile": profile.copy(),
        "risks": risks,
        "risks_sorted": risks_sorted,
        "top_risk": risks_sorted[0],
        "total_score": total_score,
        "overall_level": overall_level,
        "attention_count": attention_count,
    }


# ============================================================
# 08 构建个性化建议
# ============================================================

def build_suggestions(profile):

    suggestions = []

    hours = float(profile["hours"])
    volume = profile["volume"]
    environment = profile["environment"]
    breaks = profile["breaks"]

    def add(title, category, priority, content):

        suggestions.append({
            "title": title,
            "category": category,
            "priority": priority,
            "content": content,
        })

    # --------------------------------------------------------
    # 基础建议
    # --------------------------------------------------------

    if hours >= 4:

        add(
            "合理安排聆听时间",
            "使用时长",
            "优先",
            (
                "你自报的每日耳机使用时间较长。"
                "建议减少长时间连续使用，"
                "在学习和娱乐过程中主动安排无耳机休息。"
            ),
        )

    elif hours >= 2:

        add(
            "留意连续使用时间",
            "使用时长",
            "常规",
            (
                "建议观察每次连续佩戴耳机的时间，"
                "避免因学习、游戏或观看视频而忽略休息。"
            ),
        )

    if volume in ["较高", "很高"]:

        add(
            "优先关注常用音量",
            "音量习惯",
            "优先",
            (
                "你选择的主观音量水平较高。"
                "建议尝试降低常用音量，"
                "并避免长时间保持较高声音水平。"
                "主观音量不能直接换算为实际dBA。"
            ),
        )

    if environment in [
        "公共交通",
        "其他嘈杂环境",
    ]:

        add(
            "避免背景噪声引起的音量补偿",
            "使用环境",
            "优先",
            (
                "在嘈杂环境中，人们可能为了听清内容"
                "而不自觉提高耳机音量。"
                "可以考虑暂停播放，"
                "或在更安静的环境中聆听。"
            ),
        )

    if breaks in [
        "很少",
        "几乎没有",
    ]:

        add(
            "建立主动休息习惯",
            "休息习惯",
            "优先",
            (
                "你目前较少主动暂停耳机使用。"
                "可以尝试在连续聆听过程中安排休息，"
                "不必等到感到不适才停止。"
            ),
        )

    # --------------------------------------------------------
    # 深度画像建议
    # --------------------------------------------------------

    if profile.get("extra_enabled"):

        scenes = profile.get(
            "campus_scenes"
        ) or []

        reasons = profile.get(
            "remove_reasons"
        ) or []

        headphone_type = profile.get(
            "headphone_type"
        )

        sound_mode = profile.get(
            "sound_mode"
        )

        discomfort = profile.get(
            "discomfort"
        )

        # 允许来自画像页的完整场景名称
        # 不要求与这里的字符串完全一致

        if any("食堂" in s for s in scenes):

            add(
                "食堂场景：关注背景人声",
                "校园场景",
                "场景",
                (
                    "食堂可能存在较多交谈声。"
                    "如果发现自己需要不断提高耳机音量，"
                    "可以暂停播放或选择更安静的环境。"
                ),
            )

        if any("校园道路" in s for s in scenes):

            add(
                "校园道路：保持环境感知",
                "校园场景",
                "场景",
                (
                    "在校园道路上应留意车辆、"
                    "行人和安全提示声。"
                    "必要时暂停播放或摘下耳机。"
                ),
            )

        if any("公共交通" in s for s in scenes):

            add(
                "公共交通：兼顾音量与提示信息",
                "校园场景",
                "场景",
                (
                    "乘坐公共交通时，"
                    "避免持续提高音量来掩盖背景噪声，"
                    "同时注意广播和安全提示。"
                ),
            )

        if any(
            "教室" in s or "图书馆" in s
            for s in scenes
        ):

            add(
                "学习场景：避免长时间连续聆听",
                "校园场景",
                "场景",
                (
                    "在自习或线上学习过程中，"
                    "留意连续佩戴耳机的时间，"
                    "在合适的学习间隙暂停音频。"
                ),
            )

        if any("宿舍" in s for s in scenes):

            add(
                "宿舍场景：建立舒适的聆听习惯",
                "校园场景",
                "场景",
                (
                    "宿舍是常见的学习和娱乐场景。"
                    "建议关注常用音量，"
                    "避免长时间连续播放。"
                ),
            )

        if any(
            "运动场" in s or "健身" in s
            for s in scenes
        ):

            add(
                "运动场景：注意周围环境",
                "校园场景",
                "场景",
                (
                    "运动时注意周围人员、"
                    "设备以及安全提示。"
                    "必要时降低音量或暂停播放。"
                ),
            )

        # ----------------------------------------------------
        # 声音模式
        # ----------------------------------------------------

        if sound_mode == "主动降噪（ANC）":

            add(
                "主动降噪：仍需关注声音水平",
                "耳机模式",
                "补充",
                (
                    "主动降噪可以减少部分环境噪声干扰，"
                    "但不代表声音暴露一定安全。"
                    "实际聆听声级和累计时间仍然重要。"
                ),
            )

        elif sound_mode == "通透模式":

            add(
                "通透模式：不等于完全感知环境",
                "耳机模式",
                "补充",
                (
                    "通透模式能够传入部分环境声音，"
                    "但效果与设备和使用条件有关。"
                    "在需要注意安全提示时，"
                    "不要完全依赖耳机模式。"
                ),
            )

        # ----------------------------------------------------
        # 摘下耳机的原因
        # ----------------------------------------------------

        if any(
            "很少主动" in r
            for r in reasons
        ):

            add(
                "尝试主动摘下耳机",
                "休息行为",
                "优先",
                (
                    "你选择了较少主动摘下耳机。"
                    "建议提前安排无耳机时段，"
                    "帮助建立主动休息习惯。"
                ),
            )

        if any(
            "不适" in r or "疲劳" in r
            for r in reasons
        ):

            add(
                "不要等到不适才暂停",
                "休息行为",
                "优先",
                (
                    "如果经常在感到不适后才摘下耳机，"
                    "可以尝试提前安排休息。"
                    "出现不适时应停止使用并休息。"
                ),
            )

        if any(
            "主动安排休息" in r
            for r in reasons
        ):

            add(
                "继续保持主动休息",
                "休息行为",
                "保持",
                (
                    "主动暂停耳机使用是值得保持的习惯。"
                    "可以继续结合日常学习和生活"
                    "安排合适的休息时间。"
                ),
            )

        # ----------------------------------------------------
        # 佩戴不适
        # ----------------------------------------------------

        if discomfort in [
            "偶尔出现",
            "经常出现",
        ]:

            add(
                "关注耳部不适体验",
                "佩戴体验",
                "优先",
                (
                    "你报告曾在使用耳机时出现不适。"
                    "出现不适时应停止使用并休息。"
                    "如果不适持续、反复出现，"
                    "或伴随听力变化，建议咨询专业人员。"
                ),
            )

        # ----------------------------------------------------
        # 耳机类型
        # ----------------------------------------------------

        if headphone_type:

            add(
                "结合耳机类型关注佩戴体验",
                "耳机类型",
                "补充",
                (
                    f"你常用的耳机类型为：{headphone_type}。"
                    "建议选择适合且舒适的佩戴方式。"
                    "不能仅凭耳机类型判断个人声音暴露风险。"
                ),
            )

    # --------------------------------------------------------
    # 默认建议
    # --------------------------------------------------------

    if not suggestions:

        add(
            "保持当前习惯",
            "日常习惯",
            "保持",
            (
                "根据当前填写的信息，"
                "暂无特别突出的高分行为因素。"
                "建议继续关注实际音量、"
                "使用时长、环境变化和主动休息。"
            ),
        )

    # --------------------------------------------------------
    # 建议去重
    # --------------------------------------------------------

    unique = []
    seen = set()

    for item in suggestions:

        if item["title"] not in seen:

            unique.append(item)
            seen.add(item["title"])

    return unique


# ============================================================
# 09 个性化七天行动计划
# ============================================================

def build_seven_day_plan(profile, result):

    top_factor = result["top_risk"]["name"]

    volume_high = profile["volume"] in [
        "较高",
        "很高",
    ]

    hours_long = float(profile["hours"]) >= 4

    breaks_low = profile["breaks"] in [
        "很少",
        "几乎没有",
    ]

    scenes = (
        profile.get("campus_scenes") or []
        if profile.get("extra_enabled")
        else []
    )

    plan = [
        {
            "day": 1,
            "title": "记录自己的聆听习惯",
            "task": (
                "观察当天耳机使用总时间、"
                "常用音量以及连续使用情况。"
            ),
            "goal": "建立自己的聆听习惯基线。",
        },
        {
            "day": 2,
            "title": "观察日常音量",
            "task": (
                "观察不同环境下"
                "是否会不自觉提高耳机音量。"
            ),
            "goal": "识别影响音量选择的情境。",
        },
        {
            "day": 3,
            "title": "尝试更合适的音量",
            "task": (
                "在日常聆听中尝试降低"
                "不必要的高音量，关注聆听体验。"
            ),
            "goal": "培养关注音量的习惯。",
        },
        {
            "day": 4,
            "title": "尝试主动暂停耳机使用",
            "task": (
                "在学习或娱乐过程中，"
                "安排一次主动的无耳机休息。"
            ),
            "goal": "减少不间断使用。",
        },
        {
            "day": 5,
            "title": "观察校园聆听场景",
            "task": (
                "选择一个日常校园场景，"
                "观察背景噪声是否影响自己的音量习惯。"
            ),
            "goal": "识别场景对聆听行为的影响。",
        },
        {
            "day": 6,
            "title": "建立可持续的使用习惯",
            "task": (
                "选择一个容易长期坚持的方式，"
                "例如主动休息或关注常用音量。"
            ),
            "goal": "形成适合自己的行为调整计划。",
        },
        {
            "day": 7,
            "title": "重新评估个人聆听习惯",
            "task": (
                "重新填写个人画像，"
                "比较使用时间、音量习惯、"
                "使用环境和休息习惯是否发生变化。"
            ),
            "goal": "观察自报行为变化，不作医学结论。",
        },
    ]

    # --------------------------------------------------------
    # 根据画像调整任务
    # --------------------------------------------------------

    if volume_high:

        plan[2]["task"] = (
            "你报告的常用音量偏高。"
            "今天重点观察常用音量，"
            "尝试降低不必要的高音量。"
        )

    if hours_long:

        plan[3]["task"] = (
            "你每日耳机使用时间较长。"
            "今天尝试减少一次长时间连续使用，"
            "并在中途主动休息。"
        )

    if breaks_low:

        plan[5]["task"] = (
            "你目前主动休息较少。"
            "今天为常见的聆听活动"
            "安排一个容易坚持的休息时段。"
        )

    if any("食堂" in s for s in scenes):

        plan[4]["task"] = (
            "今天重点观察食堂场景。"
            "留意是否会为了掩盖人声"
            "而不自觉提高音量。"
        )

    elif any("校园道路" in s for s in scenes):

        plan[4]["task"] = (
            "今天重点观察校园道路场景。"
            "确保自己能够留意车辆、"
            "行人和周围安全提示。"
        )

    elif any("宿舍" in s for s in scenes):

        plan[4]["task"] = (
            "今天观察宿舍内的耳机使用习惯，"
            "记录连续使用时间与主动休息情况。"
        )

    plan[0]["goal"] += (
        f" 当前建议重点关注：{top_factor}。"
    )

    return plan


# ============================================================
# 10 输入状态初始化
# ============================================================

saved_profile = get_saved_profile()

CORE_FIELDS = [
    "hours",
    "volume",
    "environment",
    "breaks",
]

WIDGET_KEYS = {
    "hours": "hg_advice_hours",
    "volume": "hg_advice_volume",
    "environment": "hg_advice_environment",
    "breaks": "hg_advice_breaks",
}

# 当共享画像数据发生变化时，
# 在创建输入组件之前更新页面输入。

core_snapshot = tuple(
    saved_profile[field]
    for field in CORE_FIELDS
)

last_snapshot = st.session_state.get(
    "hg_advice_loaded_snapshot"
)

if last_snapshot != core_snapshot:

    for field in CORE_FIELDS:

        st.session_state[
            WIDGET_KEYS[field]
        ] = saved_profile[field]

    st.session_state[
        "hg_advice_loaded_snapshot"
    ] = core_snapshot


# ============================================================
# 11 页面标题
# ============================================================

st.markdown(
    (
        '<div class="hg-advice-intro">'
        '<div class="hg-advice-intro-title">'
        '💡 个性化安全聆听建议'
        '</div>'
        '<div class="hg-advice-intro-text">'
        '根据日常聆听习惯与校园使用情境，'
        '生成可解释的行为反馈、'
        '个性化健康教育建议和七天行动计划。'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

st.caption(
    "HEARGUARD CAMPUS · PERSONALIZED LISTENING GUIDANCE"
)

st.info(
    "本模块使用规则驱动的教育性分析方法，"
    "不进行听力损失预测，也不提供医学诊断。"
)

if PROFILE_KEY in st.session_state:

    st.success(
        "已读取「我的听音画像」中保存的信息。"
        "你可以直接生成建议，也可以调整基础输入。"
    )

else:

    st.info(
        "目前还没有保存个人听音画像。"
        "你可以在本页填写四项基础信息，"
        "也可以先到画像页面完成深度画像。"
    )

st.divider()


# ============================================================
# 12 四项基础输入
# ============================================================

section_label(
    "01",
    "LISTENING HABITS",
)

st.header("① 确认你的日常聆听习惯")

col1, col2 = st.columns(2)

with col1:

    hours = st.slider(
        "每天使用耳机多长时间？",
        min_value=0.0,
        max_value=10.0,
        step=0.5,
        key="hg_advice_hours",
    )

    volume = st.selectbox(
        "常用音量水平（主观感受）",
        VOLUME_OPTIONS,
        key="hg_advice_volume",
    )

with col2:

    environment = st.selectbox(
        "最常使用耳机的环境",
        ENVIRONMENT_OPTIONS,
        key="hg_advice_environment",
    )

    breaks = st.selectbox(
        "主动暂停耳机使用的频率",
        BREAK_OPTIONS,
        key="hg_advice_breaks",
    )


# ============================================================
# 13 整理完整画像
# ============================================================

current_profile = get_saved_profile()

current_profile.update({
    "hours": float(hours),
    "volume": volume,
    "environment": environment,
    "breaks": breaks,
})


# ============================================================
# 14 深度画像摘要
# ============================================================

st.divider()

section_label(
    "02",
    "DEEP LISTENING PROFILE",
)

st.header("② 你的深度聆听画像")

if current_profile.get("extra_enabled"):

    e1, e2, e3 = st.columns(3)

    e1.metric(
        "常用耳机类型",
        current_profile.get("headphone_type") or "未填写",
    )

    e2.metric(
        "常用声音模式",
        current_profile.get("sound_mode") or "未填写",
    )

    e3.metric(
        "佩戴不适体验",
        current_profile.get("discomfort") or "未填写",
    )

    scenes = current_profile.get(
        "campus_scenes"
    ) or []

    reasons = current_profile.get(
        "remove_reasons"
    ) or []

    with st.container(border=True):

        st.markdown("**校园使用场景**")

        st.write(
            "、".join(scenes)
            if scenes
            else "暂无补充信息"
        )

        st.markdown("**摘下耳机的主要原因**")

        st.write(
            "、".join(reasons)
            if reasons
            else "暂无补充信息"
        )

    st.caption(
        "补充信息用于完善个性化建议，"
        "不直接参与四维行为评分。"
    )

else:

    st.info(
        "当前仅有四项基础信息。"
        "如果希望获得更详细的校园场景建议，"
        "可以先前往「我的听音画像」"
        "填写可选的深度画像。"
    )


# ============================================================
# 15 生成建议与重置计划
# ============================================================

st.divider()

if st.button(
    "💡 生成我的个性化建议",
    type="primary",
    use_container_width=True,
    key="hg_generate_advice",
):

    save_profile(current_profile)

    advice_result = calculate_advice(
        current_profile
    )

    advice_result["suggestions"] = build_suggestions(
        current_profile
    )

    advice_result["seven_day_plan"] = build_seven_day_plan(
        current_profile,
        advice_result,
    )

    st.session_state[
        ADVICE_RESULT_KEY
    ] = advice_result

    # --------------------------------------------------------
    # 重要修复：
    #
    # 每次重新生成计划，
    # 必须同时重置计划列表和复选框状态。
    #
    # 只重置列表会导致旧复选框状态残留。
    # --------------------------------------------------------

    st.session_state[
        PLAN_PROGRESS_KEY
    ] = [False] * 7

    # 计划版本递增。
    # 新版本使用新的一组复选框 key，
    # 不再读取旧计划的勾选状态。

    old_version = st.session_state.get(
        PLAN_VERSION_KEY,
        0,
    )

    st.session_state[
        PLAN_VERSION_KEY
    ] = old_version + 1

    st.success(
        "个性化建议生成成功！"
        "已更新建议内容，并重新开始七天行动计划。"
    )


# ============================================================
# 16 读取建议结果
# ============================================================

result = st.session_state.get(
    ADVICE_RESULT_KEY
)

if not isinstance(result, dict):

    st.info(
        "点击上方按钮生成你的个性化建议。"
    )

    st.stop()


required_keys = [
    "profile",
    "risks",
    "risks_sorted",
    "top_risk",
    "overall_level",
    "attention_count",
    "suggestions",
    "seven_day_plan",
]

if not all(
    key in result
    for key in required_keys
):

    st.warning(
        "检测到旧版本建议结果。"
        "请重新点击上方按钮生成新版建议。"
    )

    st.stop()


if current_profile != result["profile"]:

    st.warning(
        "你已修改部分输入。"
        "下方仍显示上一次生成的结果，"
        "请重新点击生成按钮更新。"
    )


profile = result["profile"]

risks = result["risks"]

risks_sorted = result["risks_sorted"]

top_risk = result["top_risk"]

overall_level = result["overall_level"]

attention_count = result["attention_count"]

suggestions = result["suggestions"]

plan = result["seven_day_plan"]


# ============================================================
# 17 行为关注概览
# ============================================================

st.divider()

section_label(
    "03",
    "BEHAVIOR OVERVIEW",
)

st.header("③ 你的行为关注概览")

c1, c2, c3 = st.columns(3)

c1.metric(
    "总体关注等级",
    overall_level,
)

c2.metric(
    "首要关注因素",
    top_risk["name"],
)

c3.metric(
    "优先关注维度",
    f"{attention_count} 项",
)


if overall_level == "较低":

    st.success(
        "当前整体行为关注程度较低，"
        "建议继续关注声音水平与使用时长。"
    )

elif overall_level == "一般":

    st.info(
        "当前部分聆听习惯值得继续关注。"
    )

elif overall_level == "需要关注":

    st.warning(
        "当前多个行为因素值得关注，"
        "可以优先调整排名靠前的因素。"
    )

else:

    st.warning(
        "当前多个聆听行为因素需要优先关注，"
        "建议从最容易调整的行为开始。"
    )


st.caption(
    "本页采用各维度1～4分的教育性行为排序规则，"
    "不同于画像页的100分制。"
    "两者不能直接进行数值比较，"
    "也不代表临床风险等级。"
)


# ============================================================
# 18 四维行为优先级图表
# ============================================================

st.divider()

section_label(
    "04",
    "BEHAVIOR PRIORITIES",
)

st.header("④ 四维行为因素优先级")

risk_df = pd.DataFrame(
    risks_sorted
)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=risk_df["score"],
        y=risk_df["name"],
        orientation="h",
        marker_color=COLORS["cyan_light"],
        text=[
            f"{score} / 4"
            for score in risk_df["score"]
        ],
        textposition="outside",
        hovertemplate=(
            "%{y}<br>"
            "教育性排序分数：%{x}/4"
            "<extra></extra>"
        ),
    )
)

fig = style_plotly(
    fig,
    height=350,
)

fig.update_layout(
    xaxis=dict(
        range=[0, 4.8],
        title="教育性行为排序分数",
    ),
    yaxis=dict(
        autorange="reversed",
    ),
    margin=dict(
        l=30,
        r=70,
        t=40,
        b=45,
    ),
    showlegend=False,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.caption(
    "图中数值仅用于确定教育性建议的关注顺序，"
    "不代表听力损失概率。"
)


# ============================================================
# 19 具体行为优先级
# ============================================================

for index, risk in enumerate(
    risks_sorted,
    start=1,
):

    score = risk["score"]

    with st.container(border=True):

        st.markdown(
            f"**{index}. {risk['name']}**"
        )

        st.write(
            risk["message"]
        )

        st.progress(
            score / 4
        )

        st.caption(
            f"教育性排序分数：{score} / 4"
        )


# ============================================================
# 20 个性化建议卡片
# ============================================================

st.divider()

section_label(
    "05",
    "PERSONALIZED GUIDANCE",
)

st.header("⑤ 为你生成的安全聆听建议")

st.write(
    f"系统根据当前画像生成了 "
    f"**{len(suggestions)} 条建议**。"
)

priority_order = {
    "优先": 0,
    "场景": 1,
    "常规": 2,
    "补充": 3,
    "保持": 4,
}

sorted_suggestions = sorted(
    suggestions,
    key=lambda item: priority_order.get(
        item["priority"],
        5,
    ),
)

for item in sorted_suggestions:

    with st.container(border=True):

        st.subheader(
            item["title"]
        )

        st.caption(
            f"分类：{item['category']}"
            f" ｜ 类型：{item['priority']}"
        )

        st.write(
            item["content"]
        )


# ============================================================
# 21 七天行动计划
# ============================================================

st.divider()

section_label(
    "06",
    "SEVEN-DAY ACTION PLAN",
)

st.header("⑥ 我的7天安全聆听行动计划")

st.write(
    "以下行动计划根据你的自报习惯生成，"
    "帮助你逐步观察和调整日常行为。"
)

st.caption(
    "计划属于健康教育任务，"
    "不是医学治疗或听力康复方案。"
)


# ============================================================
# 22 初始化任务进度
# ============================================================

progress = st.session_state.get(
    PLAN_PROGRESS_KEY
)

if (
    not isinstance(progress, list)
    or len(progress) != 7
):

    progress = [False] * 7

    st.session_state[
        PLAN_PROGRESS_KEY
    ] = progress


plan_version = st.session_state.get(
    PLAN_VERSION_KEY,
    0,
)

# ============================================================
# 23 七天任务卡片
# ============================================================

for index, day in enumerate(plan):

    with st.expander(
        f"Day {day['day']}｜{day['title']}",
        expanded=(index == 0),
    ):

        st.markdown("**今日任务**")

        st.write(
            day["task"]
        )

        st.markdown("**今日目标**")

        st.info(
            day["goal"]
        )

        # 使用计划版本管理复选框 key。
        # 重新生成计划后，自动获得全新的复选框。

        checkbox_key = (
            f"hg_plan_v{plan_version}_day_{index + 1}"
        )

        checked = st.checkbox(
            "我已完成今天的行动任务",
            value=progress[index],
            key=checkbox_key,
        )

        progress[index] = checked


st.session_state[
    PLAN_PROGRESS_KEY
] = progress


# ============================================================
# 24 行动计划进度
# ============================================================

completed = sum(progress)

st.subheader("📊 七天行动进度")

p1, p2 = st.columns(2)

p1.metric(
    "已完成任务",
    f"{completed} / 7",
)

p2.metric(
    "计划完成比例",
    f"{completed / 7 * 100:.0f}%",
)

st.progress(
    completed / 7
)

st.caption(
    "这里的完成率仅表示用户勾选的任务数量，"
    "不能说明听力健康已经改善。"
)


# ============================================================
# 25 本周重点行动目标
# ============================================================

st.divider()

section_label(
    "07",
    "WEEKLY GOALS",
)

st.header("⑦ 本周重点行动目标")

goals = []

if profile["hours"] >= 4:

    goals.append(
        "减少一次长时间连续使用耳机"
    )

if profile["volume"] in [
    "较高",
    "很高",
]:

    goals.append(
        "尝试降低不必要的高音量"
    )

if profile["breaks"] in [
    "很少",
    "几乎没有",
]:

    goals.append(
        "建立一个固定的主动休息时段"
    )

if profile["environment"] in [
    "公共交通",
    "其他嘈杂环境",
]:

    goals.append(
        "留意嘈杂环境中的音量补偿"
    )

if profile.get("extra_enabled"):

    scenes = profile.get(
        "campus_scenes"
    ) or []

    if any("校园道路" in s for s in scenes):

        goals.append(
            "校园出行时保持对安全提示的感知"
        )

    if any("食堂" in s for s in scenes):

        goals.append(
            "留意食堂背景噪声对音量选择的影响"
        )

if not goals:

    goals.append(
        "继续关注并保持当前聆听习惯"
    )

for goal in goals:

    st.write(
        f"✅ {goal}"
    )


# ============================================================
# 26 页面跳转
# ============================================================

st.divider()

section_label(
    "08",
    "CONTINUE EXPLORING",
)

st.header("⑧ 继续探索 HearGuard Campus")

st.write(
    "你可以进一步体验声音暴露模拟器，"
    "也可以比较不同聆听行为下的教育性指标变化。"
)

next1, next2 = st.columns(2)

with next1:

    if st.button(
        "🔊 声音暴露模拟器 →",
        use_container_width=True,
        key="hg_advice_simulator",
    ):

        st.switch_page(
            "pages/3_声音暴露模拟器.py"
        )

with next2:

    if st.button(
        "📈 聆听行为改善对比 →",
        type="primary",
        use_container_width=True,
        key="hg_advice_comparison",
    ):

        st.switch_page(
            "pages/6_聆听行为改善对比.py"
        )


# ============================================================
# 27 方法与科学边界
# ============================================================

st.divider()

with st.expander(
    "📖 查看个性化建议模型说明"
):

    st.markdown(
        """
### 1. 基础分析方法

系统依据四个维度生成行为关注排序：

1. 每日耳机使用时长
2. 主观音量习惯
3. 主要使用环境
4. 主动休息习惯

每个维度采用1～4分的教育性排序规则。

该规则与个人听音画像页面的100分制不同，
两套分数不能直接比较。

### 2. 深度画像

系统可读取五项补充信息：

- 常用耳机类型
- 常用声音模式
- 校园使用场景
- 摘下耳机的原因
- 佩戴不适体验

这些信息用于生成场景化反馈，
不会直接增加基础四维评分。

### 3. 七天行动计划

七天计划根据当前自报行为自动生成。

任务完成情况由用户自行勾选。

完成七天任务不代表已证明某种健康干预有效。

### 4. 数据保存

当前页面通过Streamlit会话状态
与个人画像等页面共享数据。

数据不会自动保存到长期数据库。

刷新、断开连接、关闭会话或服务重启后，
相关记录不保证保留。

### 5. 科学性限制

主观音量不能直接换算为真实dBA。

本系统不测量实际耳机输出声压级。

使用环境和耳机类型本身
不能直接确定个体声音暴露程度。

系统不生成听力损失发生概率，
也不能替代专业听力检查。
        """
    )


# ============================================================
# 28 页脚
# ============================================================

st.caption(
    "HearGuard Campus · 个性化安全聆听建议"
)

st.caption(
    "For educational and research communication purposes only."
)