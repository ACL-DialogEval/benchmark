import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer
import jieba

# ================= 配置区 =================
FILE_PATH = '/Users/iris/Desktop/coding汇总/gemini 2.0 flash_FIAC_combined_data.xlsx'
OUTPUT_FILENAME = 'Confusion_Matrix_FIAC_gemini.pdf'

COL_MAP = {
    'Text': ['课堂对话'],
    'True_Label': ['FIAC-1', 'True_Label'],
    'Pred_Label': ['FIAC_AI_Result_j1', 'FIAC_AI_Result_j2', 'FIAC_AI_Result_j3', 'FIAC_CoT_Result',
                   'FIAC_AI_j1', 'FIAC_AI_j2', 'FIAC_AI_j3',
                   'FIAC_j1', 'FIAC_j2', 'FIAC_j3', 'Pred_Label']
}
# ==========================================

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'PingFang HK', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False


def map_to_fiac_cluster(label):
    """单独定义的映射函数，不要在里面引用 df"""
    label_str = str(label).strip().split('.')[0]
    import re
    match = re.search(r'\d+', label_str)
    if not match:
        return 'Unknown'
    num = match.group()
    mapping = {
        '1': '1-AcceptFeelings', '2': '2-Praise', '3': '3-AcceptIdeas',
        '4': '4-AskQuestions', '5': '5-Lecturing', '6': '6-GiveDirections',
        '7': '7-Criticize', '8': '8-StudentResponse', '9': '9-StudentInitiation',
        '10': '10-Silence'
    }
    return mapping.get(num, 'Unknown')


def analyze_fiac():
    print(f"🚀 正在启动 FIAC 分析流: {FILE_PATH} ...")
    df = pd.read_excel(FILE_PATH) if FILE_PATH.endswith('.xlsx') else pd.read_csv(FILE_PATH)

    rename_dict = {}
    for target, candidates in COL_MAP.items():
        if target in df.columns: continue
        for c in candidates:
            if c in df.columns:
                rename_dict[c] = target
                break
    df = df.rename(columns=rename_dict).dropna(subset=['True_Label', 'Pred_Label'])

    df['True_Label'] = df['True_Label'].astype(str).str.strip()
    df['Pred_Label'] = df['Pred_Label'].astype(str).str.strip()

    print("🛠 正在应用 FIAC 标准分类规则...")
    # 执行转换
    df['True_Coarse'] = df['True_Label'].apply(map_to_fiac_cluster)
    df['Pred_Coarse'] = df['Pred_Label'].apply(map_to_fiac_cluster)

    # --- 诊断代码放在这里（转换完成后） ---
    print("📋 [数据诊断] 原始标签前5行:", df['True_Label'].head().tolist())
    print("📋 [数据诊断] 转换后标签前5行:", df['True_Coarse'].head().tolist())

    labels = [
        '1-AcceptFeelings', '2-Praise', '3-AcceptIdeas', '4-AskQuestions',
        '5-Lecturing', '6-GiveDirections', '7-Criticize',
        '8-StudentResponse', '9-StudentInitiation', '10-Silence'
    ]

    # 过滤掉 Unknown 数据
    df_clean = df[df['True_Coarse'].isin(labels) & df['Pred_Coarse'].isin(labels)].copy()

    # 2. 绘制混淆矩阵
    if len(df_clean) == 0:
        print("❌ 错误：过滤后样本量为 0，请检查 Excel 中的原始标签是否包含 1-10 的数字。")
        return

    print(f"🎨 正在绘制矩阵，样本量: {len(df_clean)}")
    y_true, y_pred = df_clean['True_Coarse'], df_clean['Pred_Coarse']
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_norm = np.nan_to_num(cm.astype('float') / cm.sum(axis=1)[:, np.newaxis])

    plt.figure(figsize=(12, 10))
    # cmap='Blues' 实现了蓝白配色
    # linewidths=.5 增加了格子间的细微白线，更清爽
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=labels, yticklabels=labels,
                linewidths=.5, cbar_kws={'label': 'Proportion'})

    plt.title('Confusion Matrix: Gemini-2.0-flash (FIAC Standard)', fontsize=15, pad=20)
    plt.xlabel('Predicted FIAC Category', fontsize=12, labelpad=10)
    plt.ylabel('True FIAC Category', fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig(OUTPUT_FILENAME, dpi=300)
    print(f"🎉 FIAC 混淆矩阵已保存至: {OUTPUT_FILENAME}")

    # 3. 关键词分析
    print("\n🔍 正在分析特征词...")
    np.fill_diagonal(cm_norm, 0)
    flattened = cm_norm.flatten()
    indices = np.argsort(flattened)[::-1]
    STOP_WORDS = set(
        ['的', '了', '在', '是', '我', '你', '他', '我们', '这个', '那个', '嗯', '啊', '吗', '吧', '老师', '同学'])

    for i in range(3):
        idx = indices[i]
        row, col = idx // len(labels), idx % len(labels)
        if cm_norm[row, col] < 0.05: continue

        true_l, pred_l = labels[row], labels[col]
        print(f"\n🔴 [误判分析] 真:【{true_l}】 -> 误判为:【{pred_l}】 (占比: {cm_norm[row, col]:.1%})")

        err_txt = df_clean[(df_clean['True_Coarse'] == true_l) & (df_clean['Pred_Coarse'] == pred_l)]['Text']
        corr_txt = df_clean[(df_clean['True_Coarse'] == true_l) & (df_clean['Pred_Coarse'] == true_l)]['Text']

        if len(err_txt) < 3: continue

        def get_words(ts):
            return [" ".join([w for w in jieba.cut(str(t)) if w not in STOP_WORDS and len(w) > 1]) for t in ts]

        try:
            vectorizer = CountVectorizer(max_features=300)
            X = vectorizer.fit_transform(get_words(err_txt) + get_words(corr_txt))
            names = vectorizer.get_feature_names_out()
            f_err = np.array(X[:len(err_txt)].sum(axis=0)).flatten() / len(err_txt)
            f_corr = np.array(X[len(err_txt):].sum(axis=0)).flatten() / len(corr_txt) + 1e-6
            ratios = f_err / f_corr
            for widx in np.argsort(ratios)[::-1][:5]:
                if ratios[widx] > 1.5: print(f"   诱饵词: {names[widx]:<10} | 风险倍数: {ratios[widx]:.1f}x")
        except:
            continue


if __name__ == '__main__':
    analyze_fiac()