# score.py
def calc_risk(text):
    # 利益诱惑词
    reward_words = ["中奖", "大奖", "打款", "返利", "佣金", "高额回报", "红包", "福利", "免费领取"]
    # 紧急压力词
    urgent_words = ["马上", "立刻", "限时", "冻结", "通缉", "抓捕", "后果自负", "过期失效"]
    # 诱导操作词
    action_words = ["提供身份证", "提供密码", "银行卡号", "转账", "扫码", "点击链接"]

    text = text.lower()
    hit_reward = [w for w in reward_words if w in text]
    hit_urgent = [w for w in urgent_words if w in text]
    hit_action = [w for w in action_words if w in text]

    score = len(hit_reward)*3 + len(hit_urgent)*4 + len(hit_action)*5
    if score >= 15:
        level = "高风险"
    elif score >= 6:
        level = "中风险"
    else:
        level = "低风险"
    return {
        "score": score,
        "level": level,
        "利益诱惑关键词": hit_reward,
        "紧急压力关键词": hit_urgent,
        "诱导操作关键词": hit_action
    }
