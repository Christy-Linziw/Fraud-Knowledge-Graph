import re, jieba

LEX = {
    "紧急压力": {
        "时间词": ["立刻","马上","立即","尽快","2小时","24小时","今天","最后","仅剩","逾期","限时","倒计时"],
        "后果词": ["冻结","涉案","起诉","传票","立案","停用","注销","封禁","征信","黑名单","移交","拘留"],
        "命令式": ["别挂","不要告诉","按我说的","不准","必须","只能"],
    },
    "利益诱惑": {
        "收益承诺": ["日结","日入","稳赚","包赚","返利","返现","高额","内部","无风险","零风险","保本"],
        "稀缺性": ["仅剩","限前","名额有限","最后一天","抢"],
        "无门槛": ["零投入","不用垫","扫码即","免费领","无需经验"],
    },
    "诱导操作": {
        "高危动作": ["转账","汇款","打款","扫码","屏幕共享","共享屏幕","验证码","短信转发","礼品卡","充值"],
        "平台逃逸": ["加我QQ","加微信","加V","微信不方便","平台抽成","私聊"],
        "身份索要": ["身份证","银行卡号","密码","人脸","手持身份证"],
    },
}

def extract(text: str) -> dict:
    t = text.replace(" ", "")
    out = {}
    for dim, groups in LEX.items():
        hits = {}
        for gname, words in groups.items():
            found = [w for w in words if w in t]
            if found:
                hits[gname] = found
        out[dim] = {
            "hits": hits,
            "count": sum(len(v) for v in hits.values()),
        }
    out["感叹号"] = t.count("!") + t.count("！")
    out["金额"] = re.findall(r"\d+(?:\.\d+)?\s*(?:元|块|万)", t)
    out["长度"] = len(t)
    return out

def locate(text):
    sents = re.split(r"[。！？!?\n；;]", text)
    out = []
    for s in sents:
        if not s.strip():
            continue
        f = extract(s)
        c = sum(len(v) for d in f if d in LEX for v in f[d]["hits"].values())
        if c > 0:
            out.append({"句": s.strip(), "特征数": c})
    return sorted(out, key=lambda x: -x["特征数"])[:5]


if __name__ == "__main__":
    test_txt = "你必须马上转账，否则账户冻结拉入黑名单"
    res = extract(test_txt)
    print("特征提取结果：")
    print(res)
    print("\n命中句子定位：")
    print(locate(test_txt))