import streamlit as st
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from score import calc_total_score, identity_type, purpose_type
from explain import detect_techniques

st.set_page_config(page_title="诈识图谱 v2 检测", layout="wide")

tab1, tab2 = st.tabs(["🔍单条案件检测", "📊批量案例评测(60条数据集)"])

with tab1:
    st.title("诈识图谱｜诈骗文本检测（对齐标注规范V2）")
    st.markdown("""
    > 说明：输入完整案件对话，多条消息**换行分隔**。
    > 根据v2标注规范：无类型判据输出【待定】，不强行归类，支持查看候选类型人工核对。
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
            explain_res = detect_techniques(case_messages)

        total_score = res["total_score"]
        fraud_type = res["fraud_type"]
        candidate_list = res["candidate_list"]
        trigger = res["trigger"]
        difficulty = res["difficulty"]

        st.divider()
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("风险总分", value=f"{total_score:.1f}")

        with col2:
            if fraud_type == "待定":
                st.metric("骗局类型", value="待定")
                st.caption("⚠️ 无类型判据，建议人工复核")
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
        st.subheader("人工核对‑候选匹配骗局类型")
        if len(candidate_list) > 0:
            st.write(f"候选列表：{' ｜ '.join(candidate_list)}")
        else:
            st.write("无匹配的骗局类型候选")

        all_type_list = list(identity_type.keys()) + list(purpose_type.keys())
        manual_choose = st.selectbox("人工复核修正骗局类型", ["自动识别结果"] + all_type_list)
        if manual_choose != "自动识别结果":
            st.info(f"人工复核判定结果：{manual_choose}")

        st.divider()
        st.subheader("🔍 诈骗手法识别（建模组可解释输出）")
        if len(explain_res["technique_list"]) > 0:
            st.write(f"检测到诈骗手法：{' ｜ '.join(explain_res['technique_list'])}")
            st.markdown("**高亮命中句子：**")
            for sent in explain_res["highlight_sentences"]:
                tech_names = explain_res["sentence_technique_map"][sent]
                st.markdown(f":red[{sent}]")
                st.caption(f"命中手法：{', '.join(tech_names)}")

            st.markdown("**手法说明卡片：**")
            for tech_name, desc in explain_res["technique_info"].items():
                st.info(f"【{tech_name}】{desc}")
        else:
            st.write("未识别到诈骗手法")

        st.divider()
        st.subheader("推理提示（v2规范要点）")
        hints = []
        if fraud_type == "待定":
            hints.append("• 按标注规范：整案无类型判据输出待定，禁止强行分配骗局类别")
        if difficulty == "难":
            hints.append("• 难度为难：文本伪装接近官方通知，仅靠文本难以区分，建议人工介入")
        hints.append("• 判断以完整案件上下文为准，不可单独拿某一行消息下结论")
        for h in hints:
            st.markdown(h)

    elif run_btn:
        st.warning("请输入案件对话内容")

    st.sidebar.header("关于本系统")
    st.sidebar.markdown("""
    - 对齐文档：**诈识图谱_标注规范v2**
    - 判定单元：完整案件（多条对话）
    - 词典：3份txt特征词典（不修改原txt）
    - 约束：D5‑D6封存测试集禁止用于调参，仅用于最终评估
    """)


with tab2:
    st.title("📊批量案例评测（60条测试集）")
    st.markdown("""
    **Excel字段要求：**
    - `case_id`：案例编号
    - `case_text`：案件文本
    - `true_fraud_type`：真实骗局类型
    - `true_is_fraud`：1=诈骗样本，0=非诈骗（似诈非诈负样本）
    """)
    uploaded_file = st.file_uploader("上传60条测试集Excel(.xlsx)", type="xlsx")
    if uploaded_file is not None:
        df_raw = pd.read_excel(uploaded_file)
        st.info(f"读取样本数量：{len(df_raw)}条")
        if not all(x in df_raw.columns for x in ["case_id","case_text","true_fraud_type","true_is_fraud"]):
            st.error("Excel字段不全！必须包含 case_id,case_text,true_fraud_type,true_is_fraud")
        else:
            run_batch = st.button("🚀执行批量推理&计算准确度")
            if run_batch:
                out_rows = []
                with st.spinner("正在批量推理，请勿关闭页面..."):
                    for idx,row in df_raw.iterrows():
                        case_id = row["case_id"]
                        text = str(row["case_text"])
                        true_ft = row["true_fraud_type"]
                        true_is_fraud = int(row["true_is_fraud"])
                        msg_list = [line.strip() for line in text.splitlines() if line.strip()]
                        res = calc_total_score(msg_list)

                        pred_fraud_type = res["fraud_type"]
                        pred_total_score = res["total_score"]
                        pred_candidate = "｜".join(res["candidate_list"])
                        pred_diff = res["difficulty"]
                        trigger = res["trigger"]
                        # 简单映射：非待定则视为预测为诈骗1，待定视为0
                        pred_is_fraud = 0 if pred_fraud_type == "待定" else 1
                        match_type = "正确" if (str(pred_fraud_type)==str(true_ft)) else "错误"
                        match_is_fraud = "正确" if (pred_is_fraud == true_is_fraud) else "错误"

                        out_rows.append({
                            "case_id":case_id,
                            "true_fraud_type":true_ft,
                            "pred_fraud_type":pred_fraud_type,
                            "true_is_fraud":true_is_fraud,
                            "pred_is_fraud":pred_is_fraud,
                            "match_type":match_type,
                            "match_is_fraud":match_is_fraud,
                            "pred_total_score":round(pred_total_score,1),
                            "pred_candidate_list":pred_candidate,
                            "difficulty":pred_diff,
                            "urgent":trigger["紧急压力"],
                            "profit":trigger["利益诱惑"],
                            "operate":trigger["诱导操作"]
                        })
                df_out = pd.DataFrame(out_rows)
                st.divider()
                st.subheader("二分类（是否诈骗）评估指标")
                y_true = df_out["true_is_fraud"].tolist()
                y_pred = df_out["pred_is_fraud"].tolist()
                cm = confusion_matrix(y_true,y_pred)
                cr = classification_report(y_true,y_pred,target_names=["非诈骗","诈骗"],output_dict=True)
                st.write("混淆矩阵（行=真实，列=预测）")
                st.dataframe(cm)
                acc = cr["accuracy"]
                prec = cr["诈骗"]["precision"]
                recall = cr["诈骗"]["recall"]
                f1 = cr["诈骗"]["诈骗"]["f1-score"] if "诈骗" in cr else 0
                col_a,col_b,col_c,col_d = st.columns(4)
                col_a.metric("准确率Accuracy",f"{acc:.4f}")
                col_b.metric("精确率Precision",f"{prec:.4f}")
                col_c.metric("召回率Recall",f"{recall:.4f}")
                col_d.metric("F1‑Score",f"{f1:.4f}")

                st.divider()
                st.subheader("逐案比对详情")
                st.dataframe(df_out,use_container_width=True)

                # 下载结果Excel
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_out.to_excel(writer, index=False)
                st.download_button(
                    label="📥下载评测结果Excel",
                    data=buffer.getvalue(),
                    file_name="诈识图谱_60条评测输出.xlsx"
                )
