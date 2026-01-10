import requests
import pandas as pd
from tqdm import tqdm
import os
import time
from datetime import datetime, timedelta
import glob
import re

# ================= 验证标志 =================
print("\n" + "=" * 30)
print(">>> FIAC 弗兰德斯诊断版脚本已成功启动 <<<")
print("=" * 30 + "\n")

# ================= 1. 多令牌池配置 =================
API_KEYS = [
    "ms-40129b5f-ee31-4efa-b32e-6ef6e058ffd1",
    "ms-d2dceccd-c9e7-4ee6-8d56-181f88f80917",
    "ms-ab783910-d3af-42e9-8ad8-7bac5a8ad809",
    "ms-08590663-79e4-4842-ba09-5f3f272703b2",
    "ms-ad571778-c500-430e-ad43-d8013a1dc944",
    "ms-d1cc2822-40ea-4345-b07e-0f535d509bcd",
    "ms-ce7c8de6-b943-4dc7-b6e7-021836b3d95e",
    "ms-f37af108-111d-48d7-bd4a-66498e626d96",
    "ms-d6f27b13-b089-4d39-9e88-a113866eb179",
    "ms-84e750fa-4b82-4811-800f-313ba78edb70",
    "ms-2283f63b-cc72-492f-8931-ec1b20863606",
    "ms-c22ac9fa-e5d6-4c50-993b-9ec6b340ae3b",
    "ms-8b3c151a-da6d-4935-a9e2-3e8aad6e3d8a",
    "ms-b03680a8-0ba2-4523-80fc-00fc568a9f52",
    "ms-dfd8a9a7-bbb7-497b-9750-ad9613b9ebbf",
    "ms-ea2b5da2-ac58-4d9a-91ce-ddc014c863d8",
    "ms-43686d74-c9ea-4865-87af-c43428f4f3be",
    "ms-7148a665-6b00-47a9-95dd-b67f5e79eb1b",
    "ms-d2817253-7476-4204-9f07-330a9bf0c8de",
    "ms-e51527b2-e7b5-47de-a3f2-626c64fe88c7"
]

KEY_STATUS = {key: {"status": "ACTIVE", "retry_after": datetime.now()} for key in API_KEYS}
API_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
MODEL_ID = "Qwen/Qwen2.5-32B-Instruct"


# ================= 2. 专家手册 (FIAC 弗兰德斯版) =================
def get_fiac_framework(j):
    """根据 j 级别返回最详尽的 FIAC 编码手册"""
    if j == 1:
        return "FIAC 编码类别：1-接纳情感, 2-表扬鼓励, 3-接受观点, 4-提问, 5-讲授, 6-指令, 7-批评维护权威, 8-学生被动回应, 9-学生主动发起, 10-沉默或混乱。"

    elif j == 2:
        return """
        【FIAC 编码定义简表】：
        - 教师语言 (间接影响): 1-接纳情感; 2-表扬或鼓励; 3-接受或使用学生观点; 4-提问。
        - 教师语言 (直接影响): 5-讲授; 6-给予指令; 7-批评或维护权威。
        - 学生语言: 8-学生被动回应; 9-学生主动发起。
        - 其他: 10-超过3秒的沉默或混乱。
        """

    elif j == 3:
        return """
        【弗兰德斯 (FIAC) 资深专家编码手册 - 深度案例版】：

        一、教师语言 (Teacher Talk) - 间接影响：
        1. 接纳情感：以非威胁方式接纳学生情感。示例：“我知道这道题让大家感到很沮丧。”
        2. 表扬或鼓励：表扬学生的行为或想法。示例：“非常好，你的思路很清晰。”
        3. 接受或使用学生观点：澄清、构建或拓展学生提出的观点。示例：“正如小明刚才提到的，光合作用需要光。”
        4. 提问：提出关于内容或程序的问题，并期望学生回答。示例：“谁能告诉我为什么会出现这种现象？”

        二、教师语言 (Teacher Talk) - 直接影响：
        5. 讲授：教师陈述事实、表达观点、解释内容或演示。示例：“牛顿第二定律的公式是 F=ma。”
        6. 给予指令：教师发出命令或指示。示例：“请大家翻到课本第 30 页。”
        7. 批评或维护权威：批评学生不可接受的行为，或维护教师权威。示例：“不要再说话了！”

        三、学生语言 (Student Talk)：
        8. 学生被动回应：学生对教师提问或指令做出的直接、可预测的回答。示例：T:“这叫什么？” -> S:“显微镜。”
        9. 学生主动发起：学生主动发言，或对提问进行超出预期的拓展。示例：S:“老师，我有一个新的想法……”

        四、其他 (Other)：
        10. 沉默或混乱：超过3秒的停顿、沉默，或多人同时说话导致的混乱状态。

        【操作提示】：如果一句话发生多种行为，记录占主导地位或持续时间最长的一个。
        """
    return ""

# ================= 3. 令牌轮换与数字提取逻辑 =================
def call_model_api_with_rotation(prompt):
    while True:
        active_key = get_best_key()
        if not active_key:
            cooldown_keys = [k for k in API_KEYS if KEY_STATUS[k]["status"] == "COOLDOWN"]
            if cooldown_keys:
                wait_sec = int((min([KEY_STATUS[k].get("retry_after", datetime.now()) for k in cooldown_keys]) - datetime.now()).total_seconds()) + 1
                time.sleep(max(1, wait_sec))
                continue
            return "ALL_KEYS_DEAD"

        headers = {"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"}
        payload = {"model": MODEL_ID, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 10}

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                # 提取数字 1-10
                match = re.search(r'\b(10|[1-9])\b', content)
                if match:
                    return int(match.group(1))
                return "Unknown"
            elif response.status_code == 429:
                KEY_STATUS[active_key]["status"] = "COOLDOWN"
                KEY_STATUS[active_key]["retry_after"] = datetime.now() + timedelta(seconds=45)
                continue
            elif response.status_code in [401, 403]:
                KEY_STATUS[active_key]["status"] = "DEAD"
                continue
            else: return f"Error_{response.status_code}"
        except Exception as e:
            time.sleep(1); continue

def get_best_key():
    now = datetime.now()
    for key in API_KEYS:
        if KEY_STATUS[key]["status"] == "ACTIVE": return key
    for key in API_KEYS:
        if KEY_STATUS[key]["status"] == "COOLDOWN" and now >= KEY_STATUS[key]["retry_after"]:
            KEY_STATUS[key]["status"] = "ACTIVE"
            return key
    return None

# ================= 4. 处理逻辑 (切换为 FIAC) =================
def create_expert_prompt(df, index, text_column, framework_text):
    def get_line(idx):
        if idx < 0 or idx >= len(df): return None
        s_col = '发言人' if '发言人' in df.columns else df.columns[0]
        return f"{df.iloc[idx][s_col]}：{df.iloc[idx][text_column]}"
    target = get_line(index)
    pre = "\n".join([f"前文: {get_line(idx)}" for idx in range(max(0, index - 2), index) if get_line(idx)])
    post = "\n".join([f"后文: {get_line(idx)}" for idx in range(index + 1, min(len(df), index + 3)) if get_line(idx)])
    # 核心：要求 AI 只输出数字编码
    return f"专家，请对目标句进行 FIAC 弗兰德斯编码：\n{framework_text}\n\n{pre}\n目标 -> <target>{target}</target>\n{post}\n请直接输出 1-10 之间的数字代码："

def is_file_completed(output_folder, base_name, j_level):
    pattern = os.path.join(output_folder, f"Result_{base_name}_j{j_level}_*.xlsx")
    files = glob.glob(pattern)
    if not files: return False, None
    files.sort(key=os.path.getmtime, reverse=True)
    latest = files[0]
    try:
        df = pd.read_excel(latest)
        # 结果列名统一改为 FIAC_Result
        if 'FIAC_Result' not in df.columns: return False, latest
        valid_codes = [float(i) for i in range(1, 11)] + [int(i) for i in range(1, 11)]
        invalid = df[~df['FIAC_Result'].isin(valid_codes)]
        return len(invalid) == 0, latest
    except: return False, None

def process_single_file(input_file, text_col, j_level, output_folder):
    base_name = os.path.basename(input_file).split('.')[0]
    done, latest = is_file_completed(output_folder, base_name, j_level)
    if done:
        print(f"  [跳过] {base_name} (j={j_level}) 已彻底完成。")
        return "SKIP"

    df = pd.read_excel(latest) if latest else pd.read_excel(input_file)
    if 'FIAC_Result' not in df.columns: df['FIAC_Result'] = ""

    actual_col = text_col if text_col in df.columns else ("内容" if "内容" in df.columns else df.columns[1])
    framework = get_fiac_framework(j_level)

    for i in tqdm(range(len(df)), desc=f"{base_name}_j{j_level}"):
        # 跳过已存在的有效数字
        try:
            val = float(df.at[i, 'FIAC_Result'])
            if 1 <= val <= 10: continue
        except: pass

        prompt = create_expert_prompt(df, i, actual_col, framework)
        result = call_model_api_with_rotation(prompt)
        if result == "ALL_KEYS_DEAD": return "BREAK"

        df.at[i, 'FIAC_Result'] = result
        if i % 10 == 0:
            df.to_excel(os.path.join(output_folder, f"Result_{base_name}_j{j_level}_temp.xlsx"), index=False)
        time.sleep(0.5)

    final_path = os.path.join(output_folder, f"Result_{base_name}_j{j_level}_{datetime.now().strftime('%m%d_%H%M')}.xlsx")
    df.to_excel(final_path, index=False)
    return "CONTINUE"

# ================= 5. 执行入口 =================
if __name__ == "__main__":
    DATA_DIR = '../data/'
    OUTPUT_DIR = 'output/'
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    stop_flag = False
    for sub in ['Art', 'Science']:
        if stop_flag: break
        for i in range(1, 11):
            if stop_flag: break
            fpath = os.path.join(DATA_DIR, f"精-{sub}{i}.xlsx")
            if os.path.exists(fpath):
                for j in range(1, 4):
                    status = process_single_file(fpath, "内容", j, OUTPUT_DIR)
                    if status == "BREAK":
                        stop_flag = True; break

    print("\n>>> 全量 FIAC 扫描任务已圆满结束。<<<")