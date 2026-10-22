import streamlit as st
from score import calc_total_score

st.set_page_config(page_title="诈识图谱 v2 检测", layout="wide")

st.title("诈识图谱｜诈骗文本检测（对齐标注规范V2）")
st.markdown("""
> 说明：输入完整案件对话，多条消息**换行分隔**。
> 模型按照【案件级】做判断，不是单句；输出待定代表文本不足以判定，建议人工复核。
""")

user_input = st.text_area(
    "请粘贴案件对话（多条消息换行）",
    height=220,
    placeholder="""你好，请问是林XX女士吗，我是某宝网XX店客服。这里看到您购买的商品...
由于工作人员失误多转了350元，需要返还，如不及时返还，支付宝将一直扣款。"""
)

run_btn = st.button("开始检测")

if run_btn and user_input.strip():
    case_messages = [line.strip() for line in user_input.splitlines() if line.strip()]

    with st.spinner("正在按照v2标注规范推理..."):
        res = calc_total_score(case_messages)

    total_score = res["total_score"]
    fraud_type = res["fraud_type"]
    trigger = res["trigger"]
    difficulty = res["difficulty"]

    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("风险总分", value=f"{total_score:.1f}")

    with col2:
        if fraud_type == "待定":
            st.metric("骗局类型", value="待定")
            st.caption("⚠️ 文本信息不足，建议人工复核")
        else:
            st.metric("骗局类型", value=fraud_type)

    with col3:
        st.metric("样本难度", value=difficulty)
        if difficulty == "易":
            st.markdown(":red[易] —— 特征明显")
        elif difficulty == "中":
            st.markdown(":orange[中] —— 部分伪装")
        else:
            st.markdown(":yellow[难] —— 和正规通知高度近似")

    with col4:
        st.subheader("触发维度")
        st.write(f"紧急压力：{trigger['紧急压力']}")
        st.write(f"利益诱惑：{trigger['利益诱惑']}")
        st.write(f"诱导操作：{trigger['诱导操作']}")

    st.divider()
    st.subheader("推理提示（v2规范要点）")
    hints = []
    if fraud_type == "待定":
        hints.append("• 整案没有匹配到判据，输出待定，不要强行判定诈骗")
    if difficulty == "难":
        hints.append("• 难度为难：文本伪装接近官方通知，文本手段很难区分，建议人工介入")
    hints.append("• 判断以完整案件上下文为准，不要单独拿某一行做结论")
    for h in hints:
        st.markdown(h)

elif run_btn:
    st.warning("请输入案件对话内容")

st.sidebar.header("关于本系统")
st.sidebar.markdown("""
- 对齐文档：**诈识图谱_标注规范v2**
- 判定单元：完整案件（多条对话）
- 词典：3份txt特征词典
- 约束：D5‑D6封存测试集禁止用于调参，仅用于最终评估
""")
