"""
HearGuard Campus
全站统一视觉主题 V1.3

主要功能：
1. 统一字体与页面间距
2. 统一按钮颜色
3. 统一卡片风格
4. 统一标题颜色
5. 适配深色与浅色界面
6. 提供 Plotly 图表主题

不影响数据计算、评分模型和页面跳转。
"""

import streamlit as st


# ============================================================
# 01 主题颜色
# ============================================================

COLORS = {
    "navy": "#081729",
    "navy_light": "#102B49",
    "cyan": "#20A7BB",
    "cyan_light": "#47C7F3",
    "teal": "#36C4D5",
    "blue": "#167B9A",
    "orange": "#F3B35E",
    "green": "#38BFA6",
    "red": "#E77979",
    "white": "#FFFFFF",
    "muted": "#8FA9BD",
}


# ============================================================
# 02 全站样式
# ============================================================

def apply_theme():
    """
    在每个Streamlit页面调用一次即可。

    注意：
    必须在 st.set_page_config() 之后调用。
    """

    st.markdown(
        """
<style>

/* ========================================
   全局字体
======================================== */

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "PingFang SC",
        "Microsoft YaHei",
        "Segoe UI",
        sans-serif;
}


/* ========================================
   页面宽度与间距
======================================== */

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ========================================
   一级标题
======================================== */

h1 {
    font-weight: 800 !important;
    letter-spacing: 0.3px;
}


/* ========================================
   二级标题
======================================== */

h2 {
    font-weight: 700 !important;
    letter-spacing: 0.2px;
}


/* ========================================
   三级标题
======================================== */

h3 {
    font-weight: 650 !important;
}


/* ========================================
   通用按钮
======================================== */

div.stButton > button[kind="primary"] {
    background: linear-gradient(
        120deg,
        #167B9A,
        #20A7BB
    ) !important;

    color: #FFFFFF !important;

    border: 1px solid #36C4D5 !important;

    border-radius: 10px !important;

    min-height: 44px !important;

    font-weight: 650 !important;

    box-shadow: none !important;
}

div.stButton > button[kind="primary"]:hover {
    background: #258CA8 !important;
    border-color: #66D6E8 !important;
    color: #FFFFFF !important;
}


/* ========================================
   次要按钮
======================================== */

div.stButton > button[kind="secondary"] {
    border-radius: 10px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
}


/* ========================================
   下载按钮
======================================== */

div.stDownloadButton > button {
    border-radius: 10px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
}


/* ========================================
   输入框与选择框
======================================== */

div[data-baseweb="select"] > div {
    border-radius: 10px;
}

div[data-baseweb="input"] > div {
    border-radius: 10px;
}


/* ========================================
   提示框
======================================== */

div[data-testid="stAlert"] {
    border-radius: 12px;
}


/* ========================================
   图表
======================================== */

div[data-testid="stPlotlyChart"] {
    border-radius: 14px;
}


/* ========================================
   分隔线
======================================== */

hr {
    opacity: 0.35;
}


/* ========================================
   移动端适配
======================================== */

@media (max-width: 768px) {

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-size: 1.9rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

}

</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 03 Plotly图表统一配置
# ============================================================

def style_plotly(fig, height=430):
    """
    对Plotly图表应用统一视觉风格。

    示例：
        fig = style_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

    不修改图表的数据。
    """

    fig.update_layout(
        height=height,
        font=dict(
            family="Arial, PingFang SC, sans-serif",
            size=13,
        ),
        colorway=[
            COLORS["cyan_light"],
            COLORS["orange"],
            COLORS["green"],
            COLORS["blue"],
            COLORS["red"],
        ],
        margin=dict(
            l=30,
            r=30,
            t=55,
            b=40,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            y=1.08,
            x=0,
        ),
    )

    return fig