def calc_risk(text):
    # 诈骗关键词库
    keywords = {
        "利益诱惑": ["中奖", "抽奖", "恭喜您", "号码选中", "免费领取", "补贴", "返利", "红包"],
        "紧急压力": ["马上", "立刻", "限时", "过期作废", "不要告诉别人"],
        "诱导操作": ["转账", "汇款", "保证金", "押金", "解冻", "验证码", "银行卡"]
    }

    hit_result = {
        "利益诱惑": {"hits": {}, "count": 0},
        "紧急压力": {"hits": {}, "count": 0},
        "诱导操作": {"hits": {}, "count": 0}
    }
    total = 0

    for category, words in keywords.items():
        cnt = 0
        for w in words:
            if w in text:
                hit_result[category]["hits"][w] = 1
                cnt += 1
        hit_result[category]["count"] = cnt
        total += cnt * 30

    # 上限控制最高200分
    if total > 200:
        total = 200

    if total >= 80:
        level = "高"
    elif total >= 30:
        level = "中"
    else:
        level = "低"

    return total, level, hit_result