"""
HearGuard Campus · 声护校园
方法与数据来源 V1.3

功能：
1. 三层研究证据体系
2. 本地校园调查数据说明
3. 国际大样本研究背景
4. WHO–ITU 安全聆听参考
5. 等能量模型及参考时间表
6. 交互式声音暴露计算
7. 项目研究方法闭环
8. 研究局限性与参考文献
9. HearGuard Campus V1.3 统一主题

科学边界：
本项目用于校园听力健康教育。
不进行医学诊断或听力损失概率预测。
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
    page_title="方法与数据来源 | HearGuard Campus",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()


# ============================================================
# 03 页面专属样式
# ============================================================

st.markdown(
    """
<style>

.hg-method-hero {
    background:
        radial-gradient(
            circle at 85% 20%,
            rgba(71,199,243,0.18),
            transparent 35%
        ),
        linear-gradient(
            125deg,
            #081729,
            #102b49 55%,
            #123d58
        );

    border: 1px solid rgba(71,199,243,0.26);
    border-radius: 20px;
    padding: 34px 36px;
    margin-bottom: 20px;
}

.hg-method-title {
    font-size: clamp(27px,3.5vw,38px);
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 14px;
}

.hg-method-description {
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

.hg-evidence-note {
    background: rgba(32,167,187,0.08);
    border: 1px solid rgba(71,199,243,0.22);
    border-radius: 14px;
    padding: 18px 22px;
    margin-top: 14px;
    margin-bottom: 18px;
}

.hg-evidence-note-title {
    color: #43bad7;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 8px;
}

.hg-evidence-note-text {
    font-size: 14px;
    line-height: 1.9;
    opacity: 0.9;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 04 通用函数
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


def section_line():

    st.divider()


def evidence_card(
    number,
    title,
    description,
    question,
):

    with st.container(border=True):

        st.caption(
            f"EVIDENCE LAYER {number}"
        )

        st.subheader(title)

        st.write(description)

        st.markdown(
            f"**核心问题：** {question}"
        )


def flow_card(
    number,
    title,
    description,
):

    with st.container(border=True):

        st.caption(
            f"STEP {number}"
        )

        st.subheader(title)

        st.write(description)


# ============================================================
# 05 WHO–ITU 参考模型
# ============================================================

def reference_hours(
    level_db,
    reference_db=80,
):
    """
    WHO–ITU 等能量参考模型。

    成人模式：
        80 dBA，40小时/周

    较保守模式：
        75 dBA，40小时/周

    近似3 dB交换规则。
    """

    hours = (
        40
        * (
            2 ** (
                (reference_db - level_db) / 3
            )
        )
    )

    return float(hours)


def format_hours(hours):

    if float(hours).is_integer():
        return str(int(hours))

    return (
        f"{hours:.2f}"
        .rstrip("0")
        .rstrip(".")
    )


# ============================================================
# 06 页面主视觉
# ============================================================

hero_html = (
    '<div class="hg-method-hero">'
    '<div class="hg-method-title">'
    '📚 方法与数据来源'
    '</div>'
    '<div class="hg-method-description">'
    'HearGuard Campus 将校园调查、'
    '公开研究证据与 WHO–ITU 声音暴露参考框架结合，'
    '用于大学生安全聆听教育、'
    '声音暴露知识传播与行为建议。'
    '</div>'
    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)

st.caption(
    "EVIDENCE-BASED FRAMEWORK · CAMPUS HEARING HEALTH"
)

st.info(
    "本页面集中展示项目的数据来源、"
    "研究方法、教育性计算模型和科学适用边界。"
)

section_line()


# ============================================================
# 07 三层证据体系
# ============================================================

section_label(
    "01",
    "THREE-LAYER EVIDENCE",
)

st.header("三层证据体系")

st.write(
    "系统通过三个层次建立研究与设计基础："
    "本地调查反映参与者的自报情况，"
    "公开研究提供外部背景，"
    "国际参考框架支持教育性声音暴露计算。"
)

col1, col2, col3 = st.columns(3)

with col1:

    evidence_card(
        "01",
        "🏫 本地校园样本",
        (
            "通过校园问卷观察学生耳机使用时间、"
            "使用环境、音量习惯、自报听觉体验"
            "以及听力健康教育经历。"
        ),
        "参与调查的学生如何使用个人音频设备？",
    )

with col2:

    evidence_card(
        "02",
        "📊 大样本研究",
        (
            "参考系统综述和Meta分析等公开研究，"
            "理解不安全聆听行为在更广泛"
            "年轻群体中的研究背景。"
        ),
        "本地观察结果有哪些外部研究背景？",
    )

with col3:

    evidence_card(
        "03",
        "🌍 WHO–ITU 参考",
        (
            "使用WHO–ITU安全聆听参考框架，"
            "将假设声音水平和累计时间"
            "转换为相对参考暴露指标。"
        ),
        "怎样解释声级与时间之间的关系？",
    )

section_line()


# ============================================================
# 08 本地校园调查
# ============================================================

section_label(
    "02",
    "LOCAL CAMPUS SURVEY",
)

st.header("① 本地校园调查")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "有效问卷记录",
    "126 人",
)

m2.metric(
    "每日使用 ≥2小时",
    "54.8%",
)

m3.metric(
    "嘈杂环境高频调高音量",
    "30.2%",
)

m4.metric(
    "至少一种自报症状",
    "65.9%",
)

st.caption(
    "对应人数：每日使用≥2小时为69/126；"
    "嘈杂环境高频调高音量为38/126；"
    "至少一种自报症状为83/126。"
)

with st.container(border=True):

    st.subheader("📋 本地问卷观察内容")

    st.write(
        "本地校园调查主要围绕以下方面展开："
    )

    st.markdown(
        """
1. **使用时间：** 每日使用耳机或个人音频设备的时间。
2. **音量习惯：** 是否经常使用较高音量。
3. **使用环境：** 公共交通、校园及其他环境中的使用情况。
4. **自报体验：** 耳鸣、耳闷、听觉疲劳等主观体验。
5. **健康教育：** 是否接受过相关听力健康教育。
        """
    )

    st.caption(
        "研究用途：描述参与调查学生的聆听行为模式，"
        "为校园健康教育设计提供参考。"
    )

st.warning(
    "本地调查属于非概率便利抽样。"
    "结果主要描述参与调查者，"
    "不能直接外推到全国大学生群体。"
)

st.info(
    "问卷中的自报症状不等于"
    "听力损失或听觉疾病诊断。"
    "本项目没有通过临床听力检查"
    "确定疾病发生情况。"
)

section_line()


# ============================================================
# 09 大样本研究背景
# ============================================================

section_label(
    "03",
    "EXTERNAL RESEARCH",
)

st.header("② 大样本研究背景")

r1, r2, r3 = st.columns(3)

r1.metric(
    "研究参与者",
    "19,046",
)

r2.metric(
    "纳入研究",
    "33 项",
)

r3.metric(
    "涉及国家",
    "20 个",
)

with st.container(border=True):

    st.subheader(
        "📖 为什么需要大样本研究？"
    )

    st.write(
        "单次校园调查能够帮助我们"
        "了解参与调查学生的情况，"
        "但样本规模、地区覆盖和抽样方式"
        "限制了结果的推广范围。"
    )

    st.write(
        "因此，HearGuard Campus引入"
        "国际同行评议研究作为外部背景，"
        "帮助理解年轻群体中的"
        "安全聆听相关问题。"
    )

    st.markdown(
        "**研究比较的主要限制**"
    )

    st.markdown(
        """
- 不同研究的参与者年龄可能不同。
- 问卷设计与指标定义可能不同。
- 声音暴露测量方法可能不同。
- 地区、设备及研究环境可能不同。
- 统计方法和研究目的可能不同。
        """
    )

st.info(
    "本地问卷比例与国际研究中的比例"
    "不能直接进行严格的一一比较。"
    "国际数据用于补充研究背景，"
    "不能代替校园调查结果。"
)

section_line()


# ============================================================
# 10 WHO–ITU 声音暴露参考
# ============================================================

section_label(
    "04",
    "WHO–ITU REFERENCE",
)

st.header("③ WHO–ITU 声音暴露参考")

w1, w2 = st.columns(2)

with w1:

    with st.container(border=True):

        st.caption(
            "WHO–ITU · MODE 1"
        )

        st.subheader(
            "👤 成人参考模式"
        )

        st.metric(
            "参考声级",
            "80 dBA",
        )

        st.metric(
            "每周参考暴露时间",
            "40 小时",
        )

        st.caption(
            "用于个人音频设备"
            "成人模式的声音暴露参考。"
        )

with w2:

    with st.container(border=True):

        st.caption(
            "WHO–ITU · MODE 2"
        )

        st.subheader(
            "🛡️ 较保守参考模式"
        )

        st.metric(
            "参考声级",
            "75 dBA",
        )

        st.metric(
            "每周参考暴露时间",
            "40 小时",
        )

        st.caption(
            "对应WHO–ITU儿童模式"
            "采用的较保守参考设置。"
        )


# ============================================================
# 11 等能量计算模型
# ============================================================

st.subheader("等能量原则")

st.write(
    "WHO–ITU参考框架使用"
    "声音水平与暴露时间相结合的方式"
    "进行声音能量暴露估计。"
)

with st.container(border=True):

    st.markdown(
        "#### WHO–ITU 等能量参考模型"
    )

    st.latex(
        r"T_{\mathrm{ref}}"
        r"=40\times"
        r"2^{\frac{L_{\mathrm{ref}}-L}{3}}"
    )

    st.markdown(
        r"""
其中：

- $T_{\mathrm{ref}}$：当前声音水平下的参考暴露时间，单位为小时/周。
- $L_{\mathrm{ref}}$：所选模式的参考声级，单位为dBA。
- $L$：当前假设声音水平，单位为dBA。

在该近似等能量模型下，
声音水平每升高约 **3 dB**，
对应的参考暴露时间约减少一半。
        """
    )

st.caption(
    "这是一种教育性等能量换算，"
    "并不表示低于模型参考时间"
    "就能保证个体没有听觉健康风险。"
)


# ============================================================
# 12 成人模式参考时间表
# ============================================================

st.subheader("成人模式参考暴露时间")

levels = np.array(
    [80, 83, 86, 89, 92, 95],
    dtype=float,
)

hours = [
    reference_hours(level, 80)
    for level in levels
]

table_data = pd.DataFrame({
    "声音水平（dBA）": [
        int(level)
        for level in levels
    ],
    "参考时间（小时/周）": [
        reference_hours(level, 80)
        for level in levels
    ],
})

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "声音水平（dBA）":
            st.column_config.NumberColumn(
                "声音水平（dBA）",
                format="%d",
            ),

        "参考时间（小时/周）":
            st.column_config.NumberColumn(
                "参考时间（小时/周）",
                format="%.2f",
            ),
    },
)

st.caption(
    "以上数据采用80 dBA、40小时/周"
    "及约3 dB交换规则计算，"
    "属于参考模型结果。"
)


# ============================================================
# 13 参考时间曲线
# ============================================================

st.subheader("📉 声级与参考时间的关系")

chart_levels = np.arange(
    75,
    101,
    1,
)

chart_hours = [
    reference_hours(level, 80)
    for level in chart_levels
]

chart = go.Figure()

chart.add_trace(
    go.Scatter(
        x=chart_levels,
        y=chart_hours,
        mode="lines",
        name="成人参考时间",

        line=dict(
            color=COLORS["cyan_light"],
            width=3,
        ),

        fill="tozeroy",
        fillcolor="rgba(71,199,243,0.10)",

        hovertemplate=(
            "声音水平：%{x} dBA"
            "<br>参考时间：%{y:.2f}小时/周"
            "<extra></extra>"
        ),
    )
)

chart = style_plotly(
    chart,
    height=430,
)

chart.update_layout(
    xaxis_title="声音水平（dBA）",
    yaxis_title="参考时间（小时/周）",

    showlegend=False,

    margin=dict(
        l=45,
        r=35,
        t=50,
        b=50,
    ),
)

st.plotly_chart(
    chart,
    use_container_width=True,
)

st.caption(
    "随着声音水平提高，"
    "在相同声音能量参考假设下，"
    "对应的参考暴露时间迅速下降。"
)


# ============================================================
# 14 交互式暴露计算
# ============================================================

st.subheader("🔬 互动暴露模型")

st.write(
    "调整假设声音水平与本周累计使用时间，"
    "观察相对于WHO–ITU参考模型的"
    "声音暴露比例。"
)

s1, s2, s3 = st.columns(3)

with s1:

    mode = st.selectbox(
        "参考模式",
        [
            "成人模式（80 dBA）",
            "较保守模式（75 dBA）",
        ],
        key="hg_method_mode",
    )

with s2:

    demo_db = st.slider(
        "假设声音水平（dBA）",
        min_value=70,
        max_value=100,
        value=80,
        step=1,
        key="hg_method_db",
    )

with s3:

    demo_hours = st.slider(
        "本周累计暴露时间（小时）",
        min_value=0.0,
        max_value=50.0,
        value=20.0,
        step=0.5,
        key="hg_method_hours",
    )

if mode.startswith("成人"):

    reference_db = 80

else:

    reference_db = 75

allowed_hours = reference_hours(
    demo_db,
    reference_db,
)

exposure_percent = (
    demo_hours / allowed_hours * 100
)

a1, a2, a3 = st.columns(3)

a1.metric(
    "当前假设声音水平",
    f"{demo_db} dBA",
)

a2.metric(
    "模型参考时间",
    f"{allowed_hours:.1f} 小时",
)

a3.metric(
    "相对参考暴露量",
    f"{exposure_percent:.1f}%",
)

progress = min(
    exposure_percent / 100,
    1.0,
)

st.progress(float(progress))

if exposure_percent < 50:

    st.info(
        "当前模拟暴露量低于所选模型"
        "参考暴露量的50%。"
    )

elif exposure_percent < 100:

    st.info(
        "当前模拟暴露量介于所选模型"
        "参考暴露量的50%与100%之间。"
    )

elif exposure_percent < 200:

    st.warning(
        "当前模拟暴露量达到或超过"
        "所选模式的一周参考暴露量。"
    )

else:

    st.warning(
        "当前模拟暴露量明显高于"
        "所选模式的一周参考暴露量。"
    )

st.caption(
    "进度条以100%为显示上限，"
    "实际比例可能超过100%，"
    "请以右侧显示的百分比为准。"
)

st.caption(
    "这个模型仅用于健康教育和风险沟通。"
    "输入声级是假设值，不是实际测量结果，"
    "也不能直接用手机音量百分比替代。"
)

section_line()


# ============================================================
# 15 项目方法闭环
# ============================================================

section_label(
    "05",
    "METHODOLOGY WORKFLOW",
)

st.header("HearGuard Campus 方法闭环")

st.write(
    "项目采用从问卷调查"
    "到个性化行为建议的四阶段流程。"
)

f1, f2, f3, f4 = st.columns(4)

with f1:

    flow_card(
        "01",
        "📋 数据",
        "收集参与调查学生的聆听行为与自报体验。",
    )

with f2:

    flow_card(
        "02",
        "🔍 识别",
        "通过描述性统计识别值得关注的行为模式。",
    )

with f3:

    flow_card(
        "03",
        "📊 解释",
        "结合公开研究与国际参考框架进行教育性解释。",
    )

with f4:

    flow_card(
        "04",
        "🎯 建议",
        "生成更容易执行的个性化安全聆听建议。",
    )

st.caption(
    "当前系统属于健康教育原型，"
    "没有通过随机对照试验证明行为干预效果。"
)

section_line()


# ============================================================
# 16 研究与系统局限性
# ============================================================

section_label(
    "06",
    "RESEARCH LIMITATIONS",
)

st.header("研究与系统局限性")

with st.expander(
    "查看完整方法学局限",
    expanded=True,
):

    st.markdown(
        """
### 1. 便利抽样与代表性限制

本地调查属于非概率便利抽样。

参与者来自不同学校，
但不能据此认定样本具有全国代表性。

### 2. 自报偏倚

耳机使用时间、音量和听觉体验
主要依赖参与者的自我报告，
可能受到记忆误差及主观判断影响。

### 3. 音量百分比不等于固定声级

不同耳机、手机、佩戴方式
和音频内容的实际声音输出不同。

因此不能将设备音量百分比
直接转换为固定dBA。

### 4. 横断面研究不能证明因果关系

聆听行为和自报症状之间
即使出现统计关联，
也不能据此直接推断因果关系。

### 5. 参考模型存在不确定性

实际暴露量受到设备校准、
使用环境、佩戴方式和个人差异影响。

本项目使用的假设声级和累计时间
不等于实际测量结果。

### 6. 系统未进行临床验证

HearGuard Campus属于校园健康教育
和风险沟通工具。

教育性行为评分不等于临床风险等级，
也不是听力损失发生概率。

系统不能替代专业听力检查。
        """
    )

section_line()


# ============================================================
# 17 参考文献与数据来源
# ============================================================

section_label(
    "07",
    "REFERENCES & SOURCES",
)

st.header("主要资料来源")


# ------------------------------------------------------------
# WHO–ITU
# ------------------------------------------------------------

with st.expander(
    "🌍 WHO–ITU 安全聆听标准",
    expanded=True,
):

    st.markdown(
        "**Safe listening devices and systems: "
        "a WHO–ITU standard**"
    )

    st.write(
        "World Health Organization & "
        "International Telecommunication Union"
    )

    st.link_button(
        "打开WHO官方资料",
        "https://www.who.int/publications/i/item/9789241515276",
    )


# ------------------------------------------------------------
# BMJ Global Health
# ------------------------------------------------------------

with st.expander(
    "📖 Dillard et al. — BMJ Global Health",
    expanded=False,
):

    st.markdown(
        "**Prevalence and global estimates of "
        "unsafe listening practices in adolescents "
        "and young adults: a systematic review "
        "and meta-analysis**"
    )

    st.write(
        "BMJ Global Health, 2022"
    )

    st.link_button(
        "打开研究论文",
        "https://gh.bmj.com/content/7/11/e010501",
    )


# ------------------------------------------------------------
# CNNIC
# ------------------------------------------------------------

with st.expander(
    "🇨🇳 CNNIC — 中国互联网发展统计报告",
    expanded=False,
):

    st.markdown(
        "**Statistical Report on Internet "
        "Development in China**"
    )

    st.write(
        "China Internet Network Information Center"
    )

    st.link_button(
        "打开CNNIC官方网站",
        "https://www.cnnic.net.cn/",
    )


# ------------------------------------------------------------
# 本地数据
# ------------------------------------------------------------

with st.expander(
    "🏫 本地校园问卷数据",
    expanded=False,
):

    st.write(
        "数据来源：HearGuard Campus项目"
        "开展的校园安全聆听问卷调查。"
    )

    st.write(
        "当前研究记录数：126份。"
    )

    st.write(
        "研究方式：横断面、非概率便利抽样。"
    )

    st.write(
        "问卷内容：耳机使用时长、"
        "主观音量习惯、校园使用环境、"
        "自报症状和健康教育经历。"
    )

    st.caption(
        "原始问卷包含学校等信息，"
        "不在公开页面直接展示个人记录。"
        "如需核验统计结果，应使用"
        "项目内部保存的原始数据和数据字典。"
    )

section_line()


# ============================================================
# 18 项目定位
# ============================================================

section_label(
    "08",
    "PROJECT POSITIONING",
)

st.header("HearGuard Campus 的定位")

with st.container(border=True):

    st.subheader(
        "🎯 从研究证据到健康行为"
    )

    st.write(
        "HearGuard Campus将校园问卷调查、"
        "公开研究证据与国际声音暴露参考结合，"
        "帮助大学生了解个人音频设备使用行为，"
        "并通过可执行的日常建议"
        "提升安全聆听意识。"
    )

    st.markdown(
        "**研究定位：** "
        "校园听力健康教育、"
        "声音暴露知识传播与"
        "个性化行为建议。"
    )

st.caption(
    "HearGuard Campus · 方法与数据来源"
)

st.caption(
    "For educational and research communication purposes only. "
    "This project does not provide medical diagnosis "
    "or replace professional audiological assessment."
)