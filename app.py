import streamlit as st
import pandas as pd
from score import calc_total_score, identity
from explain import detect_techniques

# ===================== 原生指标计算（无sklearn）=====================
def calc_metrics(y_true, y_pred):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 0:
            tn += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 1 and p == 0:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    cm = [[tn, fp], [fn, tp]]
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": acc,
        "cm": cm
    }

# ===================== 页面配置 =====================
st.set_page_config(page_title="诈识图谱 v2 检测", layout="wide")
st.title("诈识图谱 — 诈骗文本风险检测")
tab1, tab2 = st.tabs(["单条检测", "批量评测（内部评估）"])

# ===================== Tab1 单条检测 =====================
with tab1:
    st.subheader("输入待检测文本")
    user_text = st.text_area("粘贴短信/聊天话术：", height=200)
    if st.button("开始检测"):
        if not user_text.strip():
            st.warning("请输入文本！")
        else:
            total_score, hit_words, hit_sentences, fraud_type = calc_total_score(user_text)
            st.divider()
            st.subheader("检测结果")
            st.metric("风险分数", f"{total_score}")
            st.write(f"判定类型：{fraud_type}")
            st.write("命中关键词：")
            st.write(hit_words)
            st.write("风险句子：")
            for s in hit_sentences:
                st.markdown(f"- :red[{s}]")
            st.write("识别诈骗手法：")
            tech_list = detect_techniques(user_text, hit_words)
            for t in tech_list:
                st.markdown(f"- {t}")

# ===================== Tab2 批量评测 =====================
with tab2:
    st.info("⚠️ 本页面仅用于内部模型评估，上传的表格需要包含两列：case_text, true_is_fraud（0/1）")
    upload_file = st.file_uploader("上传Excel数据集", type=["xlsx"])
    if upload_file is not None:
        df = pd.read_excel(upload_file)
        if "case_text" not in df.columns or "true_is_fraud" not in df.columns:
            st.error("表格必须有 case_text 和 true_is_fraud 列！")
        else:
            if st.button("批量推理并评估"):
                y_true = []
                y_pred = []
                score_list = []
                type_list = []
                hit_list = []
                progress_bar = st.progress(0)
                for idx, row in df.iterrows():
                    text = str(row["case_text"])
                    label = int(row["true_is_fraud"])
                    score, hit_words, _, ftype = calc_total_score(text)
                    pred_label = 1 if score >= 21 else 0
                    y_true.append(label)
                    y_pred.append(pred_label)
                    score_list.append(score)
                    type_list.append(ftype)
                    hit_list.append(str(hit_words))
                    progress_bar.progress((idx + 1) / len(df))

                # 计算指标
                metric_res = calc_metrics(y_true, y_pred)
                st.subheader("评估指标汇总")
                st.write(f"TP:{metric_res['tp']}, TN:{metric_res['tn']}, FP:{metric_res['fp']}, FN:{metric_res['fn']}")
                st.write(f"精确率 Precision：{metric_res['precision']:.3f}")
                st.write(f"召回率 Recall：{metric_res['recall']:.3f}")
                st.write(f"F1分数：{metric_res['f1']:.3f}")
                st.write(f"准确率 Accuracy：{metric_res['accuracy']:.3f}")

                # 混淆矩阵表格
                st.subheader("混淆矩阵")
                cm = metric_res["cm"]
                st.markdown(f"""
                |真实\预测 | 0(非诈骗) | 1(诈骗)|
                | ---- | ---- | ---- |
                |0(非诈骗)| {cm[0][0]} | {cm[0][1]} |
                |1(诈骗)| {cm[1][0]} | {cm[1][1]} |
                """)

                # 输出结果表
                out_df = df.copy()
                out_df["pred_is_fraud"] = y_pred
                out_df["risk_score"] = score_list
                out_df["pred_fraud_type"] = type_list
                out_df["hit_keywords"] = hit_list
                st.dataframe(out_df)

                # 下载
                csv_data = out_df.to_csv(index=False, enc
