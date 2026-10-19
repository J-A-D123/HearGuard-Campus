
import sys
from pathlib import Path

import streamlit as st


# ============================================================
# 01 项目路径与公共主题
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.theme import apply_theme


# ============================================================
# 02 页面配置
# ============================================================

st.set_page_config(
    page_title="HearGuard Campus | 声护校园",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()


# ============================================================
# 03 页面路径
# ============================================================

PAGE_DASHBOARD = "pages/1_校园数据大屏.py"
PAGE_PROFILE = "pages/2_我的听音画像.py"
PAGE_SIMULATOR = "pages/3_声音暴露模拟器.py"
PAGE_ADVICE = "pages/4_个性化建议.py"
PAGE_SOURCES = "pages/5_方法与数据来源.py"
PAGE_COMPARE = "pages/6_聆听行为改善对比.py"
PAGE_ATLAS = "pages/7_声音暴露图谱.py"


# ============================================================
# 04 视觉样式
# ============================================================

st.markdown(
    """
<style>

/* 页面宽度 */

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* 主视觉区域 */

.hg-home-hero {
    background:
        radial-gradient(
            circle at 82% 18%,
            rgba(71,199,243,0.16),
            transparent 35%
        ),
        linear-gradient(
            125deg,
            #081729 0%,
            #102b49 55%,
            #123d58 100%
        );

    border: 1px solid rgba(71,199,243,0.28);
    border-radius: 22px;

    padding: 46px 44px;
    margin-bottom: 24px;
}

.hg-eyebrow {
    color: #68d4ea;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 17px;
}

.hg-hero-title {
    font-size: clamp(34px,4.5vw,58px);
    font-weight: 800;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 12px;
}

.hg-hero-subtitle {
    color: #b9e8f3;
    font-size: clamp(19px,2.4vw,27px);
    font-weight: 600;
    margin-bottom: 22px;
}

.hg-hero-description {
    color: #d0e1ef;
    font-size: 15px;
    line-height: 1.9;
    max-width: 760px;
}

.hg-hero-footer {
    margin-top: 28px;
    padding-top: 18px;
    border-top: 1px solid rgba(113,213,236,0.20);

    font-size: 12px;
    color: #8bc7dc;
    letter-spacing: 1.2px;
}

/* 章节标签 */

.hg-section-label {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.7px;
    color: #43bad7;
    margin-bottom: 9px;
}

/* 核心入口卡片 */

.hg-feature-card {
    min-height: 245px;
    border-radius: 17px;
    padding: 23px 21px;

    background: rgba(19,47,73,0.62);
    border: 1px solid rgba(96,199,230,0.22);
}

.hg-feature-number {
    color: #43bad7;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 1.5px;
    margin-bottom: 15px;
}

.hg-feature-title {
    color: #f2f9ff;
    font-size: 22px;
    font-weight: 750;
    margin-bottom: 12px;
}

.hg-feature-description {
    color: #b8d2e5;
    font-size: 14px;
    line-height: 1.85;
}

/* 调查数字 */

.hg-data-card {
    background: rgba(19,47,73,0.46);
    border: 1px solid rgba(96,199,230,0.18);
    border-radius: 15px;

    padding: 21px 16px;
    min-height: 145px;
}

.hg-data-value {
    font-size: clamp(25px,3vw,35px);
    font-weight: 800;
    color: #47c7f3;
    margin-bottom: 9px;
}

.hg-data-title {
    color: #e1eff7;
    font-size: 13px;
    font-weight: 650;
    line-height: 1.7;
}

.hg-data-note {
    color: #91b6cc;
    font-size: 12px;
    margin-top: 7px;
}

/* 小提示文字 */

.hg-small-text {
    color: #a5c7d9;
    font-size: 13px;
    line-height: 1.85;
}

/* 页脚 */

.hg-home-footer {
    color: #7d9aad;
    font-size: 12px;
    text-align: center;
    line-height: 1.9;
    padding-top: 12px;
}

/* 手机适配 */

@media (max-width: 768px) {

    .hg-home-hero {
        padding: 30px 24px;
        border-radius: 16px;
    }

    .hg-feature-card {
        min-height: 0;
    }

    .hg-data-card {
        min-height: 0;
    }

    .block-container {
        padding-top: 1rem;
    }
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 05 通用函数
# ============================================================

def navigate(page_path):
    """
    跳转到现有页面。
    """

    target = PROJECT_ROOT / page_path

    if target.is_file():
        st.switch_page(page_path)

    else:
        st.error(
            f"找不到页面：{page_path}"
        )


def section_header(number, english, title, description=None):

    st.markdown(
        (
            '<div class="hg-section-label">'
            f'{number} / {english}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    st.header(title)

    if description:
        st.write(description)


def core_card(number, title, description):
    """
    仅绘制展示卡片。
    按钮在卡片外统一排列。
    """

    html = (
        '<div class="hg-feature-card">'
        '<div class="hg-feature-number">'
        f'{number}'
        '</div>'
        '<div class="hg-feature-title">'
        f'{title}'
        '</div>'
        '<div class="hg-feature-description">'
        f'{description}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def data_card(value, title, note):

    html = (
        '<div class="hg-data-card">'
        '<div class="hg-data-value">'
        f'{value}'
        '</div>'
        '<div class="hg-data-title">'
        f'{title}'
        '</div>'
        '<div class="hg-data-note">'
        f'{note}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# 06 首页主视觉
# ============================================================

hero_html = (
    '<div class="hg-home-hero">'

    '<div class="hg-eyebrow">'
    'HEARGUARD CAMPUS'
    '</div>'

    '<div class="hg-hero-title">'
    'HearGuard Campus'
    '</div>'

    '<div class="hg-hero-subtitle">'
    '声护校园 · 让聆听更有依据'
    '</div>'

    '<div class="hg-hero-description">'
    '从认识自己的聆听习惯开始，'
    '通过交互式声音暴露可视化，'
    '理解声级与时间的关系，'
    '并获得可实践的安全聆听行为建议。'
    '<br><br>'
    '基于校园问卷调查与公开科学参考，'
    '让听力健康教育更加直观、个性化和易于参与。'
    '</div>'

    '<div class="hg-hero-footer">'
    'UNDERSTAND YOUR HABITS · EXPLORE SOUND · TAKE ACTION'
    '</div>'

    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)

st.caption(
    "校园安全聆听健康教育与交互式数据可视化原型"
    "｜不提供医学诊断或听力损失概率预测"
)


# ============================================================
# 07 核心体验入口
# ============================================================

st.write("")

section_header(
    "01",
    "START EXPLORING",
    "选择你的体验方向",
    (
        "从认识自己，到理解声音，"
        "再到尝试改变聆听习惯。"
    ),
)

col1, col2, col3 = st.columns(
    3,
    gap="medium",
)

with col1:

    core_card(
        "STEP 01",
        "🎧 认识自己",
        (
            "填写四项核心聆听习惯，"
            "生成教育性行为画像。"
            "<br><br>"
            "了解哪些日常行为值得优先关注。"
        ),
    )

    if st.button(
        "开始听音画像 →",
        type="primary",
        use_container_width=True,
        key="home_start_profile",
    ):
        navigate(PAGE_PROFILE)


with col2:

    core_card(
        "STEP 02",
        "🌊 理解声音",
        (
            "调整假设声级与累计时间，"
            "通过声音暴露模拟和交互图谱"
            "理解声音能量的变化。"
        ),
    )

    if st.button(
        "探索声音暴露 →",
        use_container_width=True,
        key="home_start_sound",
    ):
        navigate(PAGE_SIMULATOR)


with col3:

    core_card(
        "STEP 03",
        "💡 改善行为",
        (
            "根据听音画像获取个性化建议，"
            "尝试七天行动计划，"
            "并比较不同聆听习惯的变化。"
        ),
    )

    if st.button(
        "查看个性化建议 →",
        use_container_width=True,
        key="home_start_advice",
    ):
        navigate(PAGE_ADVICE)


st.caption(
    "首次使用建议从「认识自己」开始。"
    "生成画像后，可以直接进入个性化建议页面。"
)

st.divider()


# ============================================================
# 08 校园调查依据
# ============================================================

section_header(
    "02",
    "CAMPUS RESEARCH",
    "从校园调查发现问题",
    (
        "我们以126份校园问卷记录为起点，"
        "观察参与者的耳机使用习惯、"
        "自报听觉体验与健康教育接触情况。"
    ),
)

data_cols = st.columns(4)

with data_cols[0]:

    data_card(
        "54.8%",
        "每日耳机使用不少于2小时",
        "69 / 126 人",
    )

with data_cols[1]:

    data_card(
        "30.2%",
        "嘈杂环境高频调高音量",
        "38 / 126 人",
    )

with data_cols[2]:

    data_card(
        "65.9%",
        "自报至少一种相关不适",
        "83 / 126 人",
    )

with data_cols[3]:

    data_card(
        "61.9%",
        "未接受校内听力健康教育",
        "78 / 126 人",
    )

st.caption(
    "数据为当前项目问卷的既有统计结果。"
    "最终提交前需与原始Excel及有效回答口径再次核对。"
    "便利样本不能代表全国大学生总体；"
    "自报不适不等于医学诊断。"
)

if st.button(
    "📊 查看完整调查数据 →",
    use_container_width=True,
    key="home_open_data",
):
    navigate(PAGE_DASHBOARD)

st.divider()


# ============================================================
# 09 作品工作流程
# ============================================================

section_header(
    "03",
    "HOW IT WORKS",
    "从数据认知到行为反馈",
    (
        "HearGuard Campus将调查数据、"
        "教育性行为分析和交互可视化"
        "连接成连续的使用体验。"
    ),
)

with st.container(border=True):

    st.markdown(
        """
**01 · 建立画像**

填写使用时长、主观音量、常用环境与休息习惯。

**02 · 理解结果**

通过教育性评分与可视化，识别需要关注的行为因素。

**03 · 获取建议**

根据不同输入生成场景化建议和七天行动计划。

**04 · 比较变化**

记录或模拟不同时点的聆听习惯，查看行为指标变化。
        """
    )

    st.caption(
        "行为比较用于教育性反馈，"
        "不代表已经证实听力健康获得改善。"
    )


# ============================================================
# 10 更多功能入口
# ============================================================

st.write("")

with st.expander(
    "🔎 探索更多功能与研究依据",
    expanded=False,
):

    st.write(
        "以下是系统已实现的扩展功能。"
        "首次体验时无需全部使用。"
    )

    extra1, extra2 = st.columns(2)

    with extra1:

        if st.button(
            "🌊 声音暴露图谱",
            use_container_width=True,
            key="home_more_atlas",
        ):
            navigate(PAGE_ATLAS)

        if st.button(
            "📈 聆听行为改善对比",
            use_container_width=True,
            key="home_more_compare",
        ):
            navigate(PAGE_COMPARE)

    with extra2:

        if st.button(
            "📚 方法与数据来源",
            use_container_width=True,
            key="home_more_sources",
        ):
            navigate(PAGE_SOURCES)

        if st.button(
            "🔊 声音暴露模拟器",
            use_container_width=True,
            key="home_more_sim",
        ):
            navigate(PAGE_SIMULATOR)


# ============================================================
# 11 科学依据与项目边界
# ============================================================

st.divider()

section_header(
    "04",
    "SCIENTIFIC FOUNDATION",
    "有研究依据，也有明确边界",
)

st.write(
    "作品结合三个层次的信息："
    "校园问卷用于描述参与者的聆听行为；"
    "公开学术研究提供背景；"
    "WHO–ITU参考框架用于解释"
    "假设声级与累计暴露时间的关系。"
)

with st.expander(
    "📖 查看科学方法和适用限制",
    expanded=False,
):

    st.markdown(
        """
**校园问卷**

当前使用126份问卷的既有统计数据。
问卷为自报信息，不能替代临床检查。

**个人听音画像**

100分评分由项目内部规则计算，
属于教育性行为关注指数，
不是疾病发生概率。

**声音暴露模拟**

成人参考点为80 dBA、40小时/周；
较保守参考点为75 dBA、40小时/周。

使用近似3 dB交换规则。
输入值是假设声级，不是设备实际测量结果。

**行为改善对比**

可比较不同输入下的教育性行为指标，
但不能据此断定真实听力状况得到改善。

**数据代表性**

校园问卷采用非概率便利抽样。
统计结果不能直接推广到全国大学生。

**研究和医疗边界**

HearGuard Campus用于健康教育、
交互可视化和研究沟通，
不是医疗器械，不提供医学诊断。
        """
    )

    if st.button(
        "查看完整方法与参考文献 →",
        use_container_width=True,
        key="home_method_detail",
    ):
        navigate(PAGE_SOURCES)


# ============================================================
# 12 页面底部
# ============================================================

st.write("")

st.markdown(
    (
        '<div class="hg-home-footer">'
        'HEARGUARD CAMPUS · 声护校园'
        '<br>'
        '<br>'
        'FOR EDUCATIONAL AND RESEARCH COMMUNICATION ONLY'
        '</div>'
    ),
    unsafe_allow_html=True,
)