# explain.py
def get_technique_mapping():
    # 图片里的7种诈骗手法映射表
    mapping = [
        {
            "name": "限时施压",
            "trigger_words": ["2小时", "限时", "尽快", "马上处理", "截止", "再不操作", "限期"],
            "desc": "对方在用时间压力让你来不及想。真正的机构办事不会只给你2小时。"
        },
        {
            "name": "后果恐吓",
            "trigger_words": ["冻结", "涉案", "起诉", "征信", "停用", "拘捕", "通缉", "账户异常"],
            "desc": "用'账户冻结''涉案'这类词制造恐惧，是诈骗最常用的一招。真有涉案，公安会当面找你，不会发短信。"
        },
        {
            "name": "权威冒充",
            "trigger_words": ["我是客服", "我是公安", "我是教务处", "我是领导", "辅导员", "警官"],
            "desc": "身份是自称的，不是证明的。挂了电话用官方号码回拨，两分钟就能验真。"
        },
        {
            "name": "信任前置",
            "trigger_words": ["首单返现", "小额提现", "试做一单", "先给佣金"],
            "desc": "先给你一点小钱，是为了让你相信后面的大钱。这是刷单骗局的固定套路。"
        },
        {
            "name": "稀缺竞争",
            "trigger_words": ["名额有限", "仅剩", "限前", "名额"],
            "desc": "稀缺感是催你快点决定的工具。真有好机会，不怕你多想一想。"
        },
        {
            "name": "通道逃逸",
            "trigger_words": ["加QQ", "加微信", "换到别的平台", "平台不方便", "私下聊"],
            "desc": "要求换到别的平台聊，是为了让原来的平台留不下证据、也拦不住你。"
        },
        {
            "name": "伪装亲密",
            "trigger_words": ["手机丢了", "这是新号", "猜猜我是谁", "换号了"],
            "desc": "熟人借钱，先打个电话听声音。骗子最怕你打电话。"
        }
    ]
    return mapping


def split_sentences(text: str):
    """分句：简单按换行、句号、问号、感叹号切分，保留原文句子用于高亮"""
    import re
    raw_sentences = re.split(r'([。！？\n])', text)
    sentences = []
    buf = ""
    for seg in raw_sentences:
        buf += seg
        if seg in ["。", "！", "？", "\n"] and buf.strip():
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())
    return sentences


def detect_techniques(case_messages: list[str]):
    """
    输入：case_messages 同score.py，是每行对话组成的列表
    返回结果：
        highlight_sentences: 需要高亮的句子列表
        sentence_technique_map: {句子: [命中手法]}
        technique_summary: 全部命中的手法集合
        technique_info: 每个手法配套说明文字
    """
    full_text = "\n".join(case_messages)
    all_sentences = split_sentences(full_text)
    tech_map = get_technique_mapping()

    sentence_technique_map = {}
    all_hit_tech = set()

    for sent in all_sentences:
        hit_techs = []
        for tech in tech_map:
            for kw in tech["trigger_words"]:
                if kw in sent:
                    hit_techs.append(tech["name"])
                    break
        if hit_techs:
            sentence_technique_map[sent] = hit_techs
            for t in hit_techs:
                all_hit_tech.add(t)

    # 组装手法配套描述
    technique_info = {}
    for tech in tech_map:
        if tech["name"] in all_hit_tech:
            technique_info[tech["name"]] = tech["desc"]

    return {
        "highlight_sentences": list(sentence_technique_map.keys()),
        "sentence_technique_map": sentence_technique_map,
        "technique_list": list(all_hit_tech),
        "technique_info": technique_info
    }