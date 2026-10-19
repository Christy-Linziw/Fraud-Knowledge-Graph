def calc_risk(text):
    # 加载词典
    with open("特征词典_v1_利益诱惑.txt","r",encoding="utf-8") as f:
        benefit_words = f.read().splitlines()
    with open("特征词典_v1_紧急压力.txt","r",encoding="utf-8") as f:
        rush_words = f.read().splitlines()
    with open("特征词典_v1_诱导操作.txt","r",encoding="utf-8") as f:
        operate_words = f.read().splitlines()

    # 统计命中词
    hit_benefit = [w for w in benefit_words if w in text]
    hit_rush = [w for w in rush_words if w in text]
    hit_operate = [w for w in operate_words if w in text]

    total_score = len(hit_benefit) + len(hit_rush) + len(hit_operate)

    # 判断风险等级
    if total_score >=3:
        risk_level = "高风险"
    elif total_score >0:
        risk_level = "中风险"
    else:
        risk_level = "低风险"

    result = {
        "total_score": total_score,
        "risk_level": risk_level,
        "feature":{
            "利益诱惑关键词":hit_benefit,
            "紧急压力关键词":hit_rush,
            "诱导操作关键词":hit_operate
        }
    }
    return result
