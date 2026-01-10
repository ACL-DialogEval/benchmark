import requests
import pandas as pd
from tqdm import tqdm
import os
import time
from datetime import datetime, timedelta
import re
import urllib3

# 忽略 OpenSSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 1. 配置 =================
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
API_URL = "https://api-inference.modelscope.cn/v1/chat/completions"

API_KEYS = [
    "ms-7148a665-6b00-47a9-95dd-b67f5e79eb1b", "ms-e51527b2-e7b5-47de-a3f2-626c64fe88c7",
    "ms-ce7c8de6-b943-4dc7-b6e7-021836b3d95e", "ms-d1cc2822-40ea-4345-b07e-0f535d509bcd",
    "ms-ad571778-c500-430e-ad43-d8013a1dc944", "ms-84e750fa-4b82-4811-800f-313ba78edb70",
    "ms-2283f63b-cc72-492f-8931-ec1b20863606", "ms-b03680a8-0ba2-4523-80fc-00fc568a9f52",
    "ms-40129b5f-ee31-4efa-b32e-6ef6e058ffd1", "ms-d2dceccd-c9e7-4ee6-8d56-181f88f80917",
    "ms-ab783910-d3af-42e9-8ad8-7bac5a8ad809", "ms-08590663-79e4-4842-ba09-5f3f272703b2",
    "ms-f37af108-111d-48d7-bd4a-66498e626d96", "ms-d6f27b13-b089-4d39-9e88-a113866eb179",
    "ms-dfd8a9a7-bbb7-497b-9750-ad9613b9ebbf", "ms-ea2b5da2-ac58-4d9a-91ce-ddc014c863d8",
    "ms-43686d74-c9ea-4865-87af-c43428f4f3be", "ms-d2817253-7476-4204-9f07-330a9bf0c8de",
    "ms-c22ac9fa-e5d6-4c50-993b-9ec6b340ae3b", "ms-8b3c151a-da6d-4935-a9e2-3e8aad6e3d8a"
]
KEY_STATUS = {key: {"status": "ACTIVE", "retry_after": datetime.now()} for key in API_KEYS}


# ================= 2. 专家手册 (IRF版) =================
def get_irf_framework():
    """返回最详尽的 IRF 编码手册，用于 CoT 分析"""
    return """
    【IRF 编码定义】：
    1. I (Initiation) - 发起：
       - 场景：教师开启互动，如提问、引导、开启新话题或针对性点名。
       - 示例：“大家看这幅画，有什么感觉？”
    2. R (Response) - 回应：
       - 场景：学生对教师的回应或回答，包括直接回答、主动质疑或猜测。
       - 示例：“我觉得很明亮。”
    3. F (Feedback) - 反馈：
       - 场景：教师对学生回答的评价、肯定、总结性评价或纠正性反馈。
       - 示例：“说得好！”、“你抓住了构图的核心。”
    4. F+I (Mixed Behavior) - 混合行为：
       - 场景：教师先对前一句学生回答做反馈(F)，紧接着立刻提出新问题(I)。
       - 示例：“非常好(F)，那如果换成红色会怎样(I)？”
    5. None - 过滤项：
       - 场景：教师独自讲授背景、朗读课文、管理纪律或日常寒暄，无师生互动交换。
       - 示例：“同学们，这节课我们要讲的是...”
    """


# ================= 3. 核心：适配 DeepSeek R1 的调用逻辑 =================
def get_best_key():
    now = datetime.now()
    for key in API_KEYS:
        if KEY_STATUS[key]["status"] == "ACTIVE": return key
    for key in API_KEYS:
        if KEY_STATUS[key]["status"] == "COOLDOWN" and now >= KEY_STATUS[key]["retry_after"]:
            KEY_STATUS[key]["status"] = "ACTIVE"
            return key
    return None


def call_model_api_with_rotation(prompt):
    while True:
        active_key = get_best_key()
        if not active_key:
            print("\n[!!!] 所有令牌均已耗尽或失效。")
            return "ALL_DEAD", "DEAD_POOL"

        headers = {"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "max_tokens": 4096
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=180, verify=False)

            if response.status_code == 200:
                raw_content = response.json()["choices"][0]["message"]["content"]
                analysis = "未检测到思维链"
                result_text = raw_content

                think_match = re.search(r'<think>(.*?)</think>', raw_content, re.DOTALL)
                if think_match:
                    analysis = think_match.group(1).strip()
                    result_text = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()

                code_match = re.search(r'\b([IRF](\+[IRF])?|None)\b', result_text, re.IGNORECASE)
                code = code_match.group(1).upper() if code_match else "None"
                if code == "F+I": code = "F+I"

                return analysis, code

            elif response.status_code == 400:
                # 400 错误通常意味着模型名称不对或参数不支持
                print(f"\n[Error 400] 请求无效 (可能是模型ID不支持): {active_key[:10]}...")
                # 既然是请求无效，换个 Key 也没用，直接报错返回，避免死循环
                return "Error_400", "None"

            elif response.status_code == 401:
                print(f"\n[令牌失效] 401，剔除 Key: {active_key[:10]}...")
                KEY_STATUS[active_key]["status"] = "DEAD"
                continue

            elif response.status_code in [429, 403, 503]:
                KEY_STATUS[active_key]["status"] = "COOLDOWN"
                KEY_STATUS[active_key]["retry_after"] = datetime.now() + timedelta(seconds=60)
                continue
            else:
                print(f"\n[Error {response.status_code}] Key: {active_key[:10]}...")
                return f"HTTP_{response.status_code}", "None"

        except Exception as e:
            print(f"\n[请求异常] {str(e)[:50]}...")
            KEY_STATUS[active_key]["status"] = "COOLDOWN"
            KEY_STATUS[active_key]["retry_after"] = datetime.now() + timedelta(seconds=30)
            continue


# ================= 4. Prompt 构建 =================
def create_irf_prompt(df, index, text_column, framework_text):
    def get_line(idx):
        if idx < 0 or idx >= len(df): return None
        s_col = '角色' if '角色' in df.columns else ('发言人' if '发言人' in df.columns else df.columns[0])
        return f"{df.iloc[idx][s_col]}：{df.iloc[idx][text_column]}"

    pre = "\n".join([f"前文: {get_line(idx)}" for idx in range(index - 2, index) if get_line(idx)])
    target = get_line(index)
    post = "\n".join([f"后文: {get_line(idx)}" for idx in range(index + 1, index + 3) if get_line(idx)])

    return f"""你是一个课堂话语分析专家。请基于以下 IRF 框架对 <target> 标记的话语进行编码。

【框架定义】：
{framework_text}

【语境】：
{pre if pre else "(无前文)"}
目标 -> <target>{target}</target>
{post if post else "(无后文)"}

【要求】：
1. 充分思考说话人的角色、意图以及与前后文的关系。
2. 即使是混合行为（如 F+I），也请准确识别。
3. 思考结束后，请在最后一行仅输出编码结果（I, R, F, F+I 或 None）。"""


# ================= 5. 单文件处理逻辑 =================
def process_cot_file(input_file, text_col, output_folder):
    base_name = os.path.basename(input_file).split('.')[0]
    final_path = os.path.join(output_folder, f"Result_IRF_R1_{base_name}.xlsx")

    # ★★★ 修复 2：临时文件名必须以 .xlsx 结尾 ★★★
    temp_path = os.path.join(output_folder, f"Temp_Result_IRF_R1_{base_name}.xlsx")

    if os.path.exists(final_path):
        print(f"  [跳过] {base_name} 已完成。")
        return "CONTINUE"

    # 支持断点续传
    if os.path.exists(temp_path):
        print(f"  [恢复] 从临时文件恢复: {base_name}")
        df = pd.read_excel(temp_path)
    else:
        df = pd.read_excel(input_file)
        df["IRF_R1_Think"] = ""
        df["IRF_R1_Result"] = ""

    actual_col = text_col if text_col in df.columns else (df.columns[1] if len(df.columns) > 1 else df.columns[0])
    framework = get_irf_framework()

    print(f"\n🚀 DeepSeek-R1 分析中: {base_name}")

    temp_save_step = 20

    for i in tqdm(range(len(df))):
        # 如果已经有结果，跳过
        if str(df.at[i, "IRF_R1_Result"]) not in ["", "nan", "None", "Error_400"]:
            continue

        prompt = create_irf_prompt(df, i, actual_col, framework)
        analysis, code = call_model_api_with_rotation(prompt)

        if code == "DEAD_POOL": return "BREAK"

        df.at[i, "IRF_R1_Think"] = analysis
        df.at[i, "IRF_R1_Result"] = code

        # 实时保存临时文件
        if i % temp_save_step == 0:
            # ★★★ 修复：保存为正常的 .xlsx 文件 ★★★
            df.to_excel(temp_path, index=False)

    df.to_excel(final_path, index=False)
    # 删除临时文件
    if os.path.exists(temp_path): os.remove(temp_path)

    print(f"✅ 已保存: {final_path}")
    return "CONTINUE"


# ================= 6. 执行入口 =================
if __name__ == "__main__":
    DATA_DIR = '../data/'
    OUTPUT_DIR = 'output_irf_r1/'
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    stop_flag = False
    import glob

    files = sorted(glob.glob(os.path.join(DATA_DIR, "精-*.xlsx")))

    if not files:
        print("未找到数据文件，请检查 DATA_DIR 路径")

    for fpath in files:
        if stop_flag: break
        # 跳过临时文件
        if "Temp_" in fpath: continue

        status = process_cot_file(fpath, "内容", OUTPUT_DIR)
        if status == "BREAK":
            print("所有 Key 已耗尽，程序停止。")
            break

    print("\n>>> 任务结束 <<<")
