import streamlit as st
from score import calc_risk

st.title("诈骗文本风险检测")
text = st.text_area("请输入待检测文本：", value="你必须马上转账，否则账户冻结拉入黑名单")
if st.button("开始检测"):
    res = calc_risk(text)
    st.write(f"风险分数：{res['total_score']}")
    st.write(f"风险等级：{res['risk_level']}")
    st.json(res["feature"])