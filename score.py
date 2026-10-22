def load_lexicon(file_path):
    words = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
    return words

# 加载三份txt词典
lex_urgent = load_lexicon("特征词典_v1_紧急压力.txt")
lex_profit = load_lexicon("特征词典_v1_利益诱惑.txt")
lex_operate = load_lexicon("特征词典_v1_诱导操作.txt")

# ========== v2新增：骗局类型词典（写在score.py，不用新建txt）==========
identity_type = {
    "冒充公检法": ["公安", "检察院", "法院", "警官", "民警", "洗钱", "通缉", "拘捕", "涉案", "安全账户"],
    "ETC认证": ["ETC", "高速", "通行", "OBU"],
    "注销校园贷": ["校园贷", "助学贷", "学生账户", "注销账户", "国家政策", "征信"],
    "冒充快递理赔": ["快递", "包裹", "物流", "丢件", "破损", "理赔"],
    "冒充客服退款": ["客服", "退款", "订单", "备用金", "商家失误", "多打了"],
    "冒充银行": ["银行", "信用卡", "储蓄卡", "积分兑换", "逾期", "征信", "冻结"],
    "冒充老师收费": ["老师", "辅导员", "班主任", "教材费", "资料费", "班费", "家长群"],
    "冒充领导": ["领导", "老总", "局长", "我是你老板", "在开会", "项目款"],
    "冒充熟人": ["新号", "换号", "手机丢了", "小号", "号码被注销"]
}

purpose_type = {
    "刷单返利": ["任务", "垫付", "垫资", "返利", "佣金", "联单", "卡单", "信誉分", "返购"],
    "虚假投资": ["投资", "理财", "内幕", "带单", "导师", "收益", "平台充值", "股票", "期货"],
    "虚假贷款": ["额度", "放款", "无抵押", "秒批", "授信", "免息", "贷款"],
    "虚假购物（门票）": ["门票", "演唱会", "景区", "代抢"],
    "虚假购物（二手）": ["二手", "转让", "闲鱼", "低价出"],
    "游戏账号交易": ["游戏", "账号", "装备", "皮肤", "代练"],
    "兼职引流": ["打字员", "日结", "在家做", "时间自由"]
}

# step词典 + step4叙述黑名单（v2新增）
step_keyword = {
    "step1引流": ["名额有限","赶紧行动"],
    "step2建立接触": ["请回电","请登录查看"],
    "step3做准备": ["扫码","进群","下载","上传证件","绑卡"],
    "step4付出资金": ["转账","汇款","垫付","预存","充值","代付"],
    "step5加码索取": ["卡单","再补","保证金","解冻","信誉分不足"],
    "step6收尾断联": ["不要再联系","不要报警"]
}
step4_narrate_black = ["被骗", "我转了", "已经转了", "当初转账"]

# ========== v2业务函数 ==========
def has_claim_identity(case_messages:list[str]) -> bool:
    """判断案件是否存在骗子第一人称自称"""
    full_text = "\n".join(case_messages)
    claim_patterns = ["我是", "这边是", "【"]
    for p in claim_patterns:
        if p in full_text:
            return True
    return False

def has_rebate_closed_loop(text:str)->bool:
    cond1 = any(k in text for k in ["垫付", "垫资", "预存"])
    cond2 = any(k in text for k in ["返利", "佣金", "返购"])
    cond3 = any(k in text for k in ["提现", "到账"])
    hit = sum([cond1,cond2,cond3])
    return hit >=2

def conflict_resolve(hit_list, text):
    if "冒充银行" in hit_list and "虚假贷款" in hit_list:
        if any(x in text for x in ["逾期","冻结","账户出事"]):
            return "冒充银行"
        elif any(x in text for x in ["额度","放款"]):
            return "虚假贷款"
    if "ETC认证" in hit_list:
        return "ETC认证"
    if "冒充快递理赔" in hit_list and "冒充客服退款" in hit_list:
        if any(x in text for x in ["丢件","破损","包裹"]):
            return "冒充快递理赔"
        else:
            return "冒充客服退款"
    return hit_list[0]

def predict_fraud_type(case_messages:list[str]):
    full_text = "\n".join(case_messages)
    if has_claim_identity(case_messages):
        hit_list = []
        for name,kwds in identity_type.items():
            if any(k in full_text for k in kwds):
                hit_list.append(name)
        if len(hit_list)>0:
            return conflict_resolve(hit_list, full_text)
    # 无自称，走目的类
    hit_purpose = []
    for name,kwds in purpose_type.items():
        if any(k in full_text for k in kwds):
            hit_purpose.append(name)
    if "刷单返利" in hit_purpose and not has_rebate_closed_loop(full_text):
        hit_purpose.remove("刷单返利")
    if len(hit_purpose)>0:
        return hit_purpose[0]
    return "待定"

def predict_step(msg:str):
    # step4：区分指令 vs 回忆叙述
    demand_pay = any(k in msg for k in step_keyword["step4付出资金"])
    is_narrate = any(b in msg for b in step4_narrate_black)
    if demand_pay and not is_narrate:
        return 4
    if any(k in msg for k in step_keyword["step3做准备"]):
        return 3
    if any(k in msg for k in step_keyword["step5加码索取"]):
        return5
    if any(k in msg for k in step_keyword["step6收尾断联"]):
        return6
    return 1

def calc_trigger(text):
    return {
        "紧急压力":any(w in text for w in lex_urgent),
        "利益诱惑":any(w in text for w in lex_profit),
        "诱导操作":any(w in text for w in lex_operate)
    }

def predict_difficulty(case_messages, trigger_res):
    full_text = "\n".join(case_messages)
    sig1 = has_claim_identity(case_messages)
    sig2 = any(k in full_text for k in ["转账","验证码","屏幕共享","下载App"])
    sig3 = trigger_res["紧急压力"] or trigger_res["利益诱惑"]
    cnt = sum([sig1,sig2,sig3])
    if cnt ==3:
        base = "易"
    elif cnt ==2:
        base = "中"
    else:
        base = "难"
    is_look_official = False
    if is_look_official:
        if base == "中":
            base = "难"
    return base

def calc_total_score(case_messages:list[str]):
    """总风险打分主函数，app.py调用这个"""
    full_text = "\n".join(case_messages)
    trigger = calc_trigger(full_text)
    fraud_type = predict_fraud_type(case_messages)
    # 统计触发维度数量作为基础分
    base_score = sum([trigger["紧急压力"], trigger["利益诱惑"], trigger["诱导操作"]]) * 30
    difficulty = predict_difficulty(case_messages, trigger)
    if difficulty == "易":
        base_score += 10
    elif difficulty == "中":
        base_score +=5
    # 待定扣分
    if fraud_type == "待定":
        base_score = base_score * 0.6
    return {
        "total_score": base_score,
        "fraud_type": fraud_type,
        "trigger": trigger,
        "difficulty": difficulty
    }
