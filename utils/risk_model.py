# HearGuard Campus
# 声护校园
# 安全聆听行为风险模型
#
# 注意：
# 本模型用于健康教育、行为风险可视化和声音暴露参考，
# 不用于医学诊断，也不表示疾病发生概率。


# =========================================================
# 1. 行为风险模型
# =========================================================

def calculate_behavior_risk(
    hours,
    volume,
    environment,
    breaks
):
    """
    根据四个行为维度计算教育性行为风险指数。

    参数：
        hours       每日耳机使用时间（小时）
        volume      常用音量水平
        environment 使用环境
        breaks      休息习惯

    返回：
        total_score
        level
        scores
        percentages

    注意：
        该指数是项目内部的行为教育指标，
        不是医学风险概率。
    """

    # -------------------------
    # 使用时长：0-40
    # -------------------------

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

    # -------------------------
    # 音量：0-30
    # -------------------------

    volume_scores = {
        "较低": 5,
        "中等": 10,
        "较高": 20,
        "很高": 30
    }

    volume_score = volume_scores.get(
        volume,
        10
    )

    # -------------------------
    # 环境：0-15
    # -------------------------

    environment_scores = {
        "安静室内": 0,
        "宿舍": 5,
        "校园": 8,
        "公共交通": 15,
        "其他嘈杂环境": 15
    }

    environment_score = environment_scores.get(
        environment,
        5
    )

    # -------------------------
    # 休息习惯：0-15
    # -------------------------

    break_scores = {
        "经常": 0,
        "有时": 5,
        "很少": 10,
        "几乎没有": 15
    }

    break_score = break_scores.get(
        breaks,
        5
    )

    # -------------------------
    # 总分
    # -------------------------

    total_score = (
        duration_score
        + volume_score
        + environment_score
        + break_score
    )

    total_score = min(
        100,
        max(0, total_score)
    )

    # -------------------------
    # 行为关注等级
    # -------------------------

    if total_score < 30:
        level = "较低"
    elif total_score < 50:
        level = "一般"
    elif total_score < 70:
        level = "需要关注"
    else:
        level = "重点关注"

    # -------------------------
    # 各维度原始得分
    # -------------------------

    scores = {
        "使用时长": duration_score,
        "音量习惯": volume_score,
        "环境暴露": environment_score,
        "休息习惯": break_score
    }

    # -------------------------
    # 各维度标准化百分比
    # -------------------------

    percentages = {
        "使用时长": round(
            duration_score / 40 * 100,
            1
        ),
        "音量习惯": round(
            volume_score / 30 * 100,
            1
        ),
        "环境暴露": round(
            environment_score / 15 * 100,
            1
        ),
        "休息习惯": round(
            break_score / 15 * 100,
            1
        )
    }

    return {
        "total_score": round(total_score, 1),
        "level": level,
        "scores": scores,
        "percentages": percentages
    }


# =========================================================
# 2. WHO-ITU 声音暴露参考模型
# =========================================================

def calculate_sound_exposure(
    db,
    hours_per_day,
    days_per_week,
    mode="adult"
):
    """
    WHO-ITU 教育性声音暴露参考模型。

    成人模式：
        80 dBA × 40 小时/周

    儿童/敏感人群模式：
        75 dBA × 40 小时/周

    采用等能量原则：
        每增加约 3 dB，
        参考允许暴露时间约减半。

    注意：
        结果是“参考暴露比例”，
        不是医学诊断，也不应直接解释为
        “安全”或“危险”的疾病概率。
    """

    # -------------------------
    # 选择参考模式
    # -------------------------

    if mode == "child":
        reference_db = 75
        reference_hours = 40
        mode_name = "儿童/敏感人群参考模式"
    else:
        reference_db = 80
        reference_hours = 40
        mode_name = "成人参考模式"

    # -------------------------
    # 输入限制
    # -------------------------

    db = max(
        reference_db,
        min(110, float(db))
    )

    hours_per_day = max(
        0,
        float(hours_per_day)
    )

    days_per_week = max(
        0,
        min(7, float(days_per_week))
    )

    # -------------------------
    # 每周实际暴露时间
    # -------------------------

    weekly_hours = (
        hours_per_day
        * days_per_week
    )

    # -------------------------
    # 参考允许暴露时间
    #
    # 每增加约3 dB，时间减半
    # -------------------------

    allowed_weekly_hours = (
        reference_hours
        * 2 ** (
            (reference_db - db) / 3
        )
    )

    # -------------------------
    # 相对暴露比例
    # -------------------------

    exposure_percent = (
        weekly_hours
        / allowed_weekly_hours
        * 100
    )

    # -------------------------
    # 状态判断
    # -------------------------

    if exposure_percent < 50:
        level = "低于参考暴露水平"

    elif exposure_percent < 100:
        level = "接近参考上限"

    elif exposure_percent < 200:
        level = "超过参考暴露水平"

    else:
        level = "明显超过参考暴露水平"

    return {
        "db": round(db, 1),
        "weekly_hours": round(
            weekly_hours,
            2
        ),
        "allowed_weekly_hours": round(
            allowed_weekly_hours,
            2
        ),
        "exposure_percent": round(
            exposure_percent,
            1
        ),
        "level": level,
        "mode": mode_name,
        "reference_db": reference_db,
        "reference_hours": reference_hours
    }


# =========================================================
# 3. 根据 dB 计算参考周暴露时间
# =========================================================

def reference_weekly_time(
    db,
    mode="adult"
):
    """
    返回某一声音水平下的参考周暴露时间。

    示例：

        成人模式
        80 dBA -> 40小时
        83 dBA -> 20小时
        86 dBA -> 10小时
        89 dBA -> 5小时
        92 dBA -> 2.5小时

    返回单位：小时/周
    """

    if mode == "child":
        reference_db = 75
    else:
        reference_db = 80

    reference_hours = 40

    db = max(
        reference_db,
        min(110, float(db))
    )

    allowed_hours = (
        reference_hours
        * 2 ** (
            (reference_db - db) / 3
        )
    )

    return round(
        allowed_hours,
        2
    )


# =========================================================
# 4. 生成教育性解释
# =========================================================

def explain_sound_exposure(
    db,
    hours_per_day,
    days_per_week,
    mode="adult"
):
    """
    根据声音暴露结果生成简短解释。
    """

    result = calculate_sound_exposure(
        db=db,
        hours_per_day=hours_per_day,
        days_per_week=days_per_week,
        mode=mode
    )

    percent = result["exposure_percent"]

    if percent < 50:
        message = (
            "当前模拟暴露低于所选参考模式的周暴露水平，"
            "仍建议关注实际音量和连续使用时间。"
        )

    elif percent < 100:
        message = (
            "当前模拟暴露正在接近参考上限，"
            "建议降低音量或增加休息间隔。"
        )

    elif percent < 200:
        message = (
            "当前模拟暴露已经超过参考水平，"
            "建议优先降低音量并减少累计暴露时间。"
        )

    else:
        message = (
            "当前模拟暴露明显超过参考水平，"
            "建议优先减少音量、缩短使用时间并增加休息。"
        )

    return {
        "result": result,
        "message": message
    }