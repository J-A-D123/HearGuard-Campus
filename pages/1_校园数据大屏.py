"""HearGuard Campus · 公开数据大屏（完整模块版）
公开版仅使用126份校园问卷整体汇总，不包含个体级数据。
保留原版三层内容：校园调查、国际研究、WHO–ITU交互参考。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from utils.theme import apply_theme, style_plotly
st.set_page_config(page_title="校园安全聆听数据大屏", page_icon="📊", layout="wide")
apply_theme()
DATA_FILE = ROOT / "data" / "hearguard_public_summary.json"
if not DATA_FILE.exists():
    st.error("缺少公开汇总数据文件：data/hearguard_public_summary.json")
    st.stop()
with DATA_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)
n = int(data["sample_size"])
metrics = data["metrics"]
dists = data["distributions"]

SOURCE_WHO = (
    "https://www.who.int/publications/i/item/9789241515276"
)

SOURCE_ITU = (
    "https://www.itu.int/epublications/"
    "publication/itu-t-h-870-v2-2022-03-"
    "guidelines-for-safe-listening-devices-systems"
)

SOURCE_BMJ = (
    "https://gh.bmj.com/content/7/11/e010501"
)

SOURCE_CNNIC = (
    "https://cnnic.cn/NMediaFile/2025/0730/"
    "MAIN1753846666507QEK67ZS9DH.pdf"
)

SOURCE_VENUES = (
    "https://iris.who.int/bitstream/handle/"
    "10665/352277/9789240043114-eng.pdf"
)

SOURCE_GAMING = (
    "https://www.itu.int/dms_pub/itu-t/opb/joint/"
    "T-JOINT-WHO-2025-1-PDF-E.pdf"
)



st.markdown(
    """
<style>

.stApp {
    background: linear-gradient(
        145deg,
        #07111f 0%,
        #0b1829 52%,
        #0d2034 100%
    );
    color: #eef7ff;
}

[data-testid="stSidebar"] {
    background: #081423;
    border-right: 1px solid rgba(102,214,255,0.16);
}

.hero {
    padding: 1.35rem 1.5rem;
    border: 1px solid rgba(94,211,255,0.22);
    border-radius: 18px;

    background: linear-gradient(
        135deg,
        rgba(18,49,78,0.92),
        rgba(9,27,47,0.92)
    );

    margin-bottom: 1rem;
    box-shadow: 0 14px 40px rgba(0,0,0,0.22);
}

.hero h1 {
    margin: 0 0 0.35rem 0;
    font-size: 2rem;
    color: #f6fbff;
}

.hero p {
    margin: 0;
    color: #b9d3e8;
}

.evidence-card {
    min-height: 155px;
    padding: 1rem 1.1rem;
    border-radius: 15px;
    border: 1px solid rgba(117,220,255,0.18);
    background: rgba(13,36,59,0.86);
}

.evidence-card .label {
    color: #8cb7d5;
    font-size: 0.86rem;
    margin-bottom: 0.35rem;
}

.evidence-card .number {
    color: #47c7f3;
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.15;
}

.evidence-card .note {
    color: #d1e5f3;
    font-size: 0.86rem;
    margin-top: 0.5rem;
}

div[data-testid="stMetric"] {
    background: rgba(13,36,59,0.88);
    border: 1px solid rgba(105,218,255,0.18);
    padding: 0.9rem 1rem;
    border-radius: 15px;
}

div[data-testid="stMetricValue"] {
    color: #47c7f3;
}

.small-note {
    color: #8fb0c7;
    font-size: 0.84rem;
}

a {
    color: #6ddcff !important;
}

</style>
    """,
    unsafe_allow_html=True,
)



st.markdown(
    '<div class="hero"><h1>📊 校园安全聆听数据大屏</h1>'
    '<p>本地校园问卷 × 大样本研究 × WHO–ITU 国际参考</p></div>',
    unsafe_allow_html=True,
)
st.caption(
    "本页面用于校园安全聆听健康教育和群体行为观察。"
    "问卷采用便利抽样，不能外推全国大学生；"
    "自报症状并非医学诊断。"
)
st.info("公开版仅展示126份问卷整体汇总，不公开个体记录、学校、年级或性别交叉筛选。")

def percent(k):
    count = int(metrics[k])
    return f"{count/n:.1%}", f"{count}/{n}份"
cols = st.columns(5)
cols[0].metric("问卷记录", f"{n}份")
for col, key, label in zip(cols[1:], ["daily_2h_plus", "noise_often", "any_symptom", "no_education"], ["每日使用≥2小时", "嘈杂环境高频调音量", "至少一种自报不适", "未接受校内听力教育"]):
    value, note = percent(key)
    col.metric(label, value, note, delta_color="off")
st.caption("自报不适是问卷回答，并非专业听力检查或医学诊断。部分记录存在需核验的年级或互斥回答，详见研究方法说明。")

def plot_distribution(key, title, color="#47C7F3", multi=False, orientation="v"):
    records = dists.get(key, [])
    frame = pd.DataFrame(records)
    if frame.empty:
        st.info("本项暂无数据")
        return
    frame["比例"] = frame["count"] / n
    frame["显示比例"] = frame["比例"].map(lambda v: f"{v:.1%}")
    if orientation == "h":
        frame = frame.sort_values("count", ascending=True)
        fig = px.bar(frame, x="count", y="label", orientation="h", text="显示比例", color_discrete_sequence=[color])
        fig.update_xaxes(title="回答人数")
        fig.update_yaxes(title=None)
    else:
        fig = px.bar(frame, x="label", y="count", text="显示比例", color_discrete_sequence=[color])
        fig.update_xaxes(title=None)
        fig.update_yaxes(title="回答人数")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(title=title, showlegend=False, margin=dict(l=20, r=20, t=65, b=25))
    fig = style_plotly(fig, height=400)
    st.plotly_chart(fig, use_container_width=True)
    if multi:
        st.caption("多选题：同一受访者可以选择多个选项，各选项比例不要求合计100%。")


tab_local, tab_research, tab_standard = st.tabs(
    ["本地校园样本", "大样本研究对照", "国际安全聆听标准"]
)
with tab_local:
    local_tab1, local_tab2 = st.tabs(["使用习惯", "体验与教育"])
    with local_tab1:
        st.subheader("耳机使用时间")
        c1, c2 = st.columns(2)
        with c1: plot_distribution("daily", "平均每天使用时长")
        with c2: plot_distribution("continuous", "单次连续使用时长", "#38BFA6")
        st.subheader("校园聆听情景")
        c1, c2 = st.columns(2)
        with c1: plot_distribution("noise", "嘈杂环境调高音量频率", "#36C4D5")
        with c2: plot_distribution("purpose", "耳机使用用途（多选）", "#F3B35E", multi=True, orientation="h")
        with st.expander("查看更多耳机类型分布"):
            plot_distribution("headphone", "耳机类型", orientation="h")
    with local_tab2:
        st.subheader("听觉相关自报体验")
        plot_distribution("symptoms", "使用耳机后的自报不适（多选）", "#E77979", multi=True, orientation="h")
        st.warning("问卷自报不适不等于听力损失诊断；部分回答中出现‘从未出现’与具体不适同时勾选，现有指标按照具体选项优先的规则统计。")
        st.subheader("健康教育与行动意愿")
        c1, c2 = st.columns(2)
        with c1: plot_distribution("education", "是否接受过学校听力健康教育", "#47C7F3")
        with c2: plot_distribution("reminder", "是否愿意使用音量提醒", "#38BFA6")
        with st.expander("查看免费筛查参与意愿"):
            plot_distribution("screening", "免费筛查参与意愿", "#F3B35E")

with tab_research:

    st.subheader(
        "公开研究与中国数字音频背景"
    )

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (
            c1,
            "系统综述样本",
            "19,046人",
            "33项研究，覆盖20个国家",
        ),
        (
            c2,
            "个人聆听设备不安全暴露",
            "23.81%",
            "95% CI：18.99%–29.42%",
        ),
        (
            c3,
            "全球潜在风险人数",
            "6.7–13.5亿",
            "12–34岁青少年和青年估计",
        ),
        (
            c4,
            "中国网络音乐用户",
            "约7.24亿",
            "CNNIC：截至2025年6月，占网民64.5%",
        ),
    ]

    for column, label, number, note in cards:

        column.markdown(
            f"""
<div class="evidence-card">
    <div class="label">{label}</div>
    <div class="number">{number}</div>
    <div class="note">{note}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "不能把本地问卷中的“经常使用较高音量”"
        "直接与23.81%相减比较。"
        "公开研究使用声级与暴露时间定义，"
        "本地问卷则是主观频率回答，"
        "两者指标口径不同。"
    )

    st.markdown(
        f"""
**建议展示方式**

- 本地模块：展示本次126份问卷的行为、症状、教育和干预意愿。
- 研究模块：展示全球研究规模、研究结论和不确定性，不伪装成本地样本。
- 中国背景：CNNIC数据只用于说明数字音乐使用场景广泛，不代表耳机使用率或听力风险率。

**来源**

- [Dillard 等，BMJ Global Health，2022]({SOURCE_BMJ})
- [CNNIC 第56次《中国互联网络发展状况统计报告》]({SOURCE_CNNIC})
        """
    )


# ============================================================
# 15 WHO–ITU 国际安全聆听标准
# ============================================================

with tab_standard:

    st.subheader(
        "🌍 WHO–ITU 声音暴露参考"
    )

    st.write(
        "基于世界卫生组织（WHO）与国际电信联盟（ITU）"
        "提出的安全聆听参考框架，"
        "探索声音水平与每周参考暴露时间之间的关系。"
    )

    st.divider()

    # --------------------------------------------------------
    # 三张参考卡片
    # --------------------------------------------------------

    who_col1, who_col2, who_col3 = st.columns(
        3,
        gap="medium",
    )

    with who_col1:

        with st.container(border=True):

            st.markdown(
                "#### 👤 成人参考模式"
            )

            st.metric(
                label="参考声音水平",
                value="80 dBA",
            )

            st.markdown(
                "**每周参考时间：40 小时**"
            )

            st.caption(
                "WHO–ITU成人模式参考："
                "80 dBA × 40小时/周。"
            )

    with who_col2:

        with st.container(border=True):

            st.markdown(
                "#### 🛡️ 保守 / 儿童模式"
            )

            st.metric(
                label="参考声音水平",
                value="75 dBA",
            )

            st.markdown(
                "**每周参考时间：40 小时**"
            )

            st.caption(
                "WHO–ITU儿童模式参考："
                "75 dBA × 40小时/周。"
            )

    with who_col3:

        with st.container(border=True):

            st.markdown(
                "#### 📉 等能量交换率"
            )

            st.metric(
                label="声音水平增加",
                value="+3 dB",
            )

            st.markdown(
                "**参考暴露时间约减半**"
            )

            st.caption(
                "在等能量参考模型中，"
                "声音水平每增加约3 dB，"
                "参考暴露时间约减少一半。"
            )

    st.info(
        "这里的计算是教育性参考。"
        "实际声音暴露量还受到耳机型号、"
        "佩戴方式、设备校准、"
        "环境声音及个体差异等因素影响。"
    )

    st.divider()

    # --------------------------------------------------------
    # 交互模拟
    # --------------------------------------------------------

    st.subheader(
        "🔊 声音水平交互模拟"
    )

    st.write(
        "拖动滑块，可以观察不同声音水平下，"
        "成人模式和儿童模式对应的"
        "每周参考暴露时间。"
    )

    selected_db = st.slider(
        "声音水平（dBA）",
        min_value=75,
        max_value=107,
        value=80,
        step=1,
        key="who_standard_db",
    )

    adult_hours = (
        40 * (
            2 ** (
                (80 - selected_db) / 3
            )
        )
    )

    conservative_hours = (
        40 * (
            2 ** (
                (75 - selected_db) / 3
            )
        )
    )

    result_col1, result_col2 = st.columns(
        2,
        gap="medium",
    )

    with result_col1:

        with st.container(border=True):

            st.markdown(
                "#### 👤 成人参考模式"
            )

            st.metric(
                label="当前参考时间",
                value=f"{adult_hours:.2f}",
            )

            st.caption(
                "单位：小时 / 周"
            )

    with result_col2:

        with st.container(border=True):

            st.markdown(
                "#### 🛡️ 儿童参考模式"
            )

            st.metric(
                label="当前参考时间",
                value=f"{conservative_hours:.2f}",
            )

            st.caption(
                "单位：小时 / 周"
            )

    st.caption(
        "以上时间由等能量参考模型计算，"
        "并不代表低于该时间"
        "就一定不会发生听力损伤。"
    )

    st.divider()

    # --------------------------------------------------------
    # 参考时间曲线
    # --------------------------------------------------------

    st.subheader(
        "📉 声级与参考暴露时间的关系"
    )

    st.write(
        "曲线展示声音水平升高时，"
        "对应参考暴露时间的变化趋势。"
    )

    levels = list(
        range(75, 108)
    )

    standard_df = pd.DataFrame({
        "声音水平（dBA）": levels,

        "成人模式（小时/周）": [
            40 * (
                2 ** (
                    (80 - level) / 3
                )
            )
            for level in levels
        ],

        "儿童模式（小时/周）": [
            40 * (
                2 ** (
                    (75 - level) / 3
                )
            )
            for level in levels
        ],
    })

    fig_standard = go.Figure()

    fig_standard.add_trace(
        go.Scatter(
            x=standard_df[
                "声音水平（dBA）"
            ],

            y=standard_df[
                "成人模式（小时/周）"
            ],

            mode="lines",

            name="成人参考模式",

            line=dict(
                color="#47C7F3",
                width=3,
            ),
        )
    )

    fig_standard.add_trace(
        go.Scatter(
            x=standard_df[
                "声音水平（dBA）"
            ],

            y=standard_df[
                "儿童模式（小时/周）"
            ],

            mode="lines",

            name="儿童参考模式",

            line=dict(
                color="#36C4D5",
                width=3,
            ),
        )
    )

    fig_standard.add_trace(
        go.Scatter(
            x=[selected_db],

            y=[adult_hours],

            mode="markers",

            name="当前成人参考",

            marker=dict(
                color="#F2C14E",
                size=12,

                line=dict(
                    color="#FFFFFF",
                    width=2,
                ),
            ),

            hovertemplate=(
                "当前声音水平：%{x} dBA"
                "<br>"
                "成人参考时间：%{y:.2f} 小时/周"
                "<extra></extra>"
            ),
        )
    )

    # 公共主题
    fig_standard = style_plotly(
        fig_standard,
        height=500,
    )

    fig_standard.update_layout(
        title=dict(
            text="声级越高，参考暴露时间越短",
            x=0.02,
            xanchor="left",
            font=dict(size=19),
        ),

        height=500,

        margin=dict(
            l=70,
            r=35,
            t=120,
            b=75,
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#E5E7EB",
            size=13,
        ),

        legend=dict(
            orientation="h",
            x=0,
            xanchor="left",
            y=1.08,
            yanchor="bottom",
            font=dict(size=12),
        ),

        xaxis=dict(
            title="声音水平（dBA）",
            showgrid=True,
            gridcolor="rgba(148,163,184,0.12)",
            zeroline=False,
        ),

        yaxis=dict(
            title="参考时间（小时/周）",
            type="log",
            showgrid=True,
            gridcolor="rgba(148,163,184,0.12)",
            zeroline=False,
        ),

        hovermode="x unified",
    )

    st.plotly_chart(
        fig_standard,
        use_container_width=True,
        key="who_standard_chart",
    )

    st.caption(
        "纵轴使用对数刻度，"
        "便于同时展示较高和较低声级"
        "对应的参考时间。"
    )

    st.divider()

    # --------------------------------------------------------
    # 参考时间表
    # --------------------------------------------------------

    st.subheader(
        "📋 成人模式参考时间表"
    )

    reference_levels = [
        80,
        83,
        86,
        89,
        92,
        95,
    ]

    reference_table = pd.DataFrame({
        "声音水平（dBA）": reference_levels,

        "成人参考时间（小时/周）": [
            40 * (
                2 ** (
                    (80 - level) / 3
                )
            )
            for level in reference_levels
        ],
    })

    reference_table[
        "成人参考时间（小时/周）"
    ] = reference_table[
        "成人参考时间（小时/周）"
    ].round(2)

    st.dataframe(
        reference_table,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "成人模式以80 dBA、40小时/周为参考，"
        "声音水平每升高约3 dB，"
        "对应的参考时间约减半。"
    )

    st.divider()

    # --------------------------------------------------------
    # 文献说明
    # --------------------------------------------------------

    st.subheader(
        "📚 国际参考与应用边界"
    )

    with st.expander(
        "查看 WHO–ITU 参考标准与使用说明",
        expanded=False,
    ):

        st.markdown(
            f"""
**个人音频设备**

参考 [WHO–ITU 安全聆听设备标准]({SOURCE_WHO})
与 [ITU-T H.870 V2]({SOURCE_ITU})。

**校园演出和音乐活动**

参考 [WHO 安全聆听场所与活动标准]({SOURCE_VENUES})。

**游戏与电竞场景**

可进一步参考
[WHO–ITU 游戏与电竞安全聆听标准]({SOURCE_GAMING})。

**模型局限**

- 本模块使用等能量参考模型。
- 手机音量百分比不能直接换算为固定dBA。
- 未进行设备校准的输入只能用于情景模拟。
- 实际声音暴露量受设备、环境及个体差异影响。
- 参考时间不是个体绝对安全时间。
- 本系统不用于医学诊断或听力损伤预测。
            """
        )

    st.success(
        "WHO–ITU声音暴露参考模块已加载。"
    )



with st.expander("📚 查看公开数据来源及研究限制"):
    st.subheader("资料来源与统计口径")
    st.markdown("**调查数据**：HearGuard Campus 团队收集的126份校园安全聆听问卷；此页面仅使用各问题的整体汇总计数，不包含个体回答。")
    st.markdown("**抽样限制**：非概率便利抽样，部分学校或年级填写需要人工核验，调查结果不能直接推广到全国大学生。")
    st.markdown("**统计说明**：多选题比例以126份问卷为分母；自报体验不能用于临床判断；类别计数为实际问卷统计，不是虚拟样本。")
    st.markdown("**WHO–ITU 参考模型**：安全聆听成人模式参考 80 dBA、40小时/周及近似3 dB交换规则。该模型只用于教育性情景模拟，不代表受访者实测声级。")
    st.markdown("- [WHO–ITU 安全聆听参考](https://www.who.int/publications/i/item/9789241515276)\n- [BMJ Global Health 系统综述](https://gh.bmj.com/content/7/11/e010501)")
    st.caption(data.get("privacy", ""))
    st.caption("全样本整体汇总数据没有学校、年级、性别等子组筛选功能；本地原始问卷仍保留在研究团队设备中。")

with st.expander("📥 下载公开汇总统计（无个体信息）"):
    report = pd.DataFrame([{"统计指标":label,"人数":int(metrics[key]),"问卷记录":n,"比例（%）":round(100*int(metrics[key])/n,1)} for key,label in [("daily_2h_plus","每日使用≥2小时"),("noise_often","嘈杂环境高频调音量"),("any_symptom","至少一种自报不适"),("no_education","未接受校内听力教育")]])
    st.dataframe(report, hide_index=True, use_container_width=True)
    st.download_button("下载CSV", data=("\ufeff"+report.to_csv(index=False)).encode("utf-8"), file_name="HearGuard_public_summary.csv", mime="text/csv")
st.caption("HearGuard Campus · 声护校园 | 校园安全聆听健康教育与交互式数据可视化")
