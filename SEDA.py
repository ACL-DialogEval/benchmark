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
print(">>> SEDA 教育对话分析脚本已成功启动 <<<")
print(">>> 模式：支持多重编码 (如 P5+R1) | 5句滑动窗口 <<<")
print("=" * 30 + "\n")

# ================= 1. 多令牌池配置 (保持不变) =================
API_KEYS = [
    "ms-8b3c151a-da6d-4935-a9e2-3e8aad6e3d8a", "ms-b03680a8-0ba2-4523-80fc-00fc568a9f52",
    "ms-dfd8a9a7-bbb7-497b-9750-ad9613b9ebbf", "ms-ea2b5da2-ac58-4d9a-91ce-ddc014c863d8",
    "ms-43686d74-c9ea-4865-87af-c43428f4f3be", "ms-7148a665-6b00-47a9-95dd-b67f5e79eb1b",
    "ms-d2817253-7476-4204-9f07-330a9bf0c8de", "ms-e51527b2-e7b5-47de-a3f2-626c64fe88c7",
    "ms-40129b5f-ee31-4efa-b32e-6ef6e058ffd1", "ms-d2dceccd-c9e7-4ee6-8d56-181f88f80917",
    "ms-ab783910-d3af-42e9-8ad8-7bac5a8ad809", "ms-08590663-79e4-4842-ba09-5f3f272703b2",
    "ms-ad571778-c500-430e-ad43-d8013a1dc944", "ms-d1cc2822-40ea-4345-b07e-0f535d509bcd",
    "ms-ce7c8de6-b943-4dc7-b6e7-021836b3d95e", "ms-f37af108-111d-48d7-bd4a-66498e626d96",
    "ms-d6f27b13-b089-4d39-9e88-a113866eb179", "ms-84e750fa-4b82-4811-800f-313ba78edb70",
    "ms-2283f63b-cc72-492f-8931-ec1b20863606", "ms-c22ac9fa-e5d6-4c50-993b-9ec6b340ae3b"

]
KEY_STATUS = {key: {"status": "ACTIVE", "retry_after": datetime.now()} for key in API_KEYS}
API_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
MODEL_ID = "Qwen/Qwen2.5-72B-Instruct"


# ================= 2. 专家手册 (SEDA 框架分级版) =================
def get_seda_framework(j):
    """
    根据 j 级别返回 SEDA 编码手册，涵盖 8 个编码簇及 33 个子代码 [cite: 36]
    """
    # 基础子代码清单 (用于 j=1)
    seda_list = (
        "I1-要求解释/论证他人观点, I2-邀请评价他人贡献, I3-邀请基于他人贡献进行推测, "
        "I4-要求解释/论证(新问题), I5-邀请进行推测/预测, I6-要求阐述/澄清; "
        "R1-解释/论证他人贡献, R2-解释/论证自己贡献, R3-基于他人贡献进行推测, R4-进行推测/预测; "
        "B1-构建/澄清他人贡献, B2-澄清/阐述自己贡献; "
        "P1-综合观点, P2-评价替代性观点, P3-提出解决方案, P4-承认立场转变, P5-挑战观点, P6-陈述(不)同意; "
        "C1-回溯之前活动, C2-明确学习轨迹, C3-连接广泛背景, C4-邀请课外探究; "
        "G1-鼓励生生对话, G2-提议行动/探究, G3-引入权威视角, G4-提供反馈, G5-聚焦主题, G6-给予思考时间; "
        "RD1-谈论谈话本身, RD2-反思学习过程, RD3-邀请反思学习; "
        "E1-表达/邀请想法, E2-做出其他相关贡献。"
    )

    if j == 1:
        return f"【SEDA 任务等级 j=1】请根据以下 33 个子代码进行编码：\n{seda_list}"

    elif j == 2:
        return """
        【SEDA 任务等级 j=2】名称 + 定义版：
        - I (邀请阐述/推理): I1-要求他人解释[cite: 37]; I2-邀请评价他人[cite: 37]; I3-邀请基于他人推测[cite: 37]; I4-要求论证新问题[cite: 37]; I5-邀请预测[cite: 37]; I6-要求阐述 [cite: 37]。
        - R (明确推理): R1-解释他人贡献[cite: 37]; R2-解释自己贡献[cite: 37]; R3-基于他人推测[cite: 37]; R4-进行预测 [cite: 37]。
        - B (建立联系): B1-构建他人贡献[cite: 37]; B2-澄清自己贡献 [cite: 37]。
        - P (定位与协调): P1-综合观点[cite: 37]; P2-评价替代观点[cite: 37]; P3-提出方案[cite: 37]; P4-承认转变[cite: 37]; P5-挑战观点[cite: 39]; P6-表明立场 [cite: 39]。
        - C (连接): C1-回溯[cite: 39]; C2-明确轨迹[cite: 39]; C3-连接背景[cite: 39]; C4-课外探究 [cite: 39]。
        - G (引导方向): G1-生生对话[cite: 39]; G2-提议行动[cite: 39]; G3-权威视角[cite: 39]; G4-提供反馈[cite: 39]; G5-聚焦主题[cite: 39]; G6-思考时间 [cite: 39]。
        - RD (反思): RD1-谈论谈话[cite: 39]; RD2-反思过程[cite: 39]; RD3-邀请反思 [cite: 39]。
        - E (表达): E1-表达/邀请想法[cite: 39]; E2-其他相关贡献 [cite: 39]。
        """

    elif j == 3:
        return """
        【SEDA 任务等级 j=3】名称 + 定义 + 示例版 [cite: 37, 39, 61]：
        簇 I：邀请阐述或推理 (Invite elaboration or reasoning)
        - I1 (要求解释/论证他人观点): T:“小明说得很有趣,谁能帮他解释一下这种情况?”
        - I2 (邀请评价他人贡献): T:“对于小红刚才提到的这个观点,大家有想法吗?”
        - I3 (邀请基于他人贡献进行推测): T:“如果按照小强的假设,接下来可能会发生什么?”
        - I4 (要求解释或论证新问题): T:“为什么这一步要乘以 2 呢?”
        - I5 (邀请进行可能性思考/预测): T:“想象一下,如果此时温度升高,结果会怎样?”
        - I6 (要求阐述或澄清): T:“你能再详细说说“饱和”是什么意思吗?”

        簇 R：明确推理 (Make reasoning explicit)
        - R1 (解释/论证他人的贡献): S:“我觉得小李说得对,因为书上第三页说……”
        - R2 (解释/论证自己的贡献): S:“我之所以选择这个答案,是因为公式里……”
        - R3 (基于他人贡献进行推测): S:“如果像老师说的那样,那么我猜结果是酸性的。”
        - R4 (进行推测或预测): S:“如果不加催化剂的话,这个反应会变慢。”

        簇 B：建立联系 (Build on ideas)
        - B1 (构建或澄清他人的贡献): S:“我想接着小芳的话说,除了她提到的,我觉得还有一点很重要。”
        - B2 (澄清或阐述自己的贡献): S:“我刚才的意思其实是,这两个变量是正相关的。”

        簇 P：定位与协调 (Positioning and Coordination)
        - P1 (综合多个观点): T:“好,如果我们把刚才小明、小红和小强的观点合起来看,我们会发现……”
        - P2 (评价替代性观点): S:“虽然第二种方法也能算出答案,但我觉得第一种更简便。”
        - P3 (提出解决方案/建议): S:“既然我们意见不统一,不如我们通过实验来验证一下?”
        - P4 (承认自己立场的转变): S:“听了你的解释,我现在觉得你是对的。”
        - P5 (挑战某个观点): S:“但是我不同意这个说法,因为……”
        - P6 (陈述/表明立场): S:“我同意小张的看法。” / “我不同意。”

        簇 C：连接 (Connect)
        - C1 (回溯之前的贡献/活动): T:“大家还记得我们在上节课讨论过的电路图吗?”
        - C2 (明确学习轨迹): T:“我们现在的讨论是为了为下一步的实验做准备。”
        - C3 (连接到广泛背景): T:“这个物理原理在我们的日常生活中有哪些应用?”
        - C4 (邀请课外探究): T:“这个问题很有意思,大家课后可以去查查资料。”

        簇 G：引导方向 (Guide direction)
        - G1 (鼓励学生间对话): T:“你们两个可以先讨论一下,然后把结果告诉大家。”
        - G2 (提议行动/探究): T:“现在让我们来进行这个化学实验。”
        - G3 (引入权威性视角): T:“根据教科书的定义,名词是……”
        - G4 (提供信息性反馈): T:“你的答案是对的,而且你用那种简便算法非常棒。”
        - G5 (聚焦主题/任务): T:“让我们回到刚才的问题上来,不要跑偏了。”
        - G6 (给予思考时间): T:“这个问题有点难,大家先思考一分钟。”(配合停顿)

        簇 RD：反思对话或活动 (Reflect)
        - RD1 (谈论“谈话”本身): T:“我觉得我们刚才的讨论非常热烈,每个人都发表了见解。”
        - RD2 (反思学习过程/结果): S:“通过这次小组合作,我学会了如何更好地沟通。”
        - RD3 (邀请对学习过程进行反思): T:“谁能总结一下我们今天这节课学到了什么?”

        簇 E：表达或邀请想法 (Express or invite ideas)
        - E1 (表达/邀请想法-无推理): T:“你觉得这幅画怎么样?” / S: “我觉得很漂亮。”
        - E2 (做出其他贡献): S:“我这里有一支红色的笔。” (简单信息提供)

        【操作提示】：
        1. 判断原则：问自己“这句话是在处理谁的观点？”接着别人的茬标“1”，圆自己的话标“2” [cite: 111, 112]。
        2. 多重编码：若一句话同时具备多种功能（如挑战并给出理由），请用“+”连接，如 P5+R1 [cite: 113, 116]。
        """
    return ""


def call_model_api_with_rotation(prompt):
    while True:
        active_key = get_best_key()
        if not active_key:
            return "ALL_KEYS_DEAD"

        headers = {"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"}

        # 核心修改点 1：必须调高 max_tokens 供 DeepSeek-R1 进行思维推理
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1024  # 从 20 提高到 1024
        }

        try:
            # 核心修改点 2：timeout 必须拉长，推理模型响应较慢
            response = requests.post(API_URL, json=payload, headers=headers, timeout=60)

            if response.status_code == 200:
                full_content = response.json()["choices"][0]["message"]["content"].strip()
                # 核心修改点 3：过滤掉 <think> 标签内容，防止正则匹配到思考过程中的无关代码
                clean_content = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()

                # 匹配 SEDA 编码格式
                match = re.search(r'([A-Z]{1,2}\d(\+[A-Z]{1,2}\d)*)', clean_content)
                return match.group(1) if match else "Unknown"

            elif response.status_code == 401:
                print(f"Key {active_key[:10]} 无效(401)，已剔除")
                KEY_STATUS[active_key]["status"] = "DEAD"
                continue
            elif response.status_code == 403:
                print(f"Key {active_key[:10]} 无权访问该模型(403)，已剔除")
                KEY_STATUS[active_key]["status"] = "DEAD"
                continue
            elif response.status_code == 400:
                print(f"请求参数错误(400)。请确保 max_tokens 足够。")
                # 暂时将该 Key 设为冷却，排查参数
                KEY_STATUS[active_key]["status"] = "COOLDOWN"
                KEY_STATUS[active_key]["retry_after"] = datetime.now() + timedelta(seconds=60)
                return "Param_Error"
            else:
                return f"Error_{response.status_code}"
        except Exception as e:
            return f"Exception_{str(e)[:20]}"


def get_best_key():
    now = datetime.now()
    for key in API_KEYS:
        if KEY_STATUS[key]["status"] == "ACTIVE": return key
    for key in API_KEYS:
        if KEY_STATUS[key]["status"] == "COOLDOWN" and now >= KEY_STATUS[key]["retry_after"]:
            KEY_STATUS[key]["status"] = "ACTIVE"
            return key
    return None


# ================= 4. 处理逻辑 (切换为 SEDA) =================
def create_expert_prompt(df, index, text_column, framework_text):
    def get_line(idx):
        if idx < 0 or idx >= len(df): return None
        s_col = '发言人' if '发言人' in df.columns else df.columns[0]
        return f"{df.iloc[idx][s_col]}：{df.iloc[idx][text_column]}"

    target = get_line(index)
    pre = "\n".join([f"前文: {get_line(idx)}" for idx in range(max(0, index - 2), index) if get_line(idx)])
    post = "\n".join([f"后文: {get_line(idx)}" for idx in range(index + 1, min(len(df), index + 3)) if get_line(idx)])

    # 修复 4: 针对推理模型微调指令，明确要求把代码放在最后
    return f"""你是一位深耕教育对话分析的专家，请根据 SEDA 框架对目标句进行编码。

【编码手册】：
{framework_text}

【语境】：
{pre}
目标 -> <target>{target}</target>
{post}

请在经过逻辑思考后，在回复的最后一行仅输出最终的子代码（如 I4 或 P5+R1）："""


def is_file_completed(output_folder, base_name, j_level):
    pattern = os.path.join(output_folder, f"Result_{base_name}_SEDA_j{j_level}_*.xlsx")
    files = glob.glob(pattern)
    if not files: return False, None
    files.sort(key=os.path.getmtime, reverse=True)
    latest = files[0]
    try:
        df = pd.read_excel(latest)
        if 'SEDA_Result' not in df.columns: return False, latest
        # 只要没有 Unknown 或 Error 开头的就算完成
        invalid = df[df['SEDA_Result'].astype(str).str.contains("Unknown|Error", na=True)]
        return len(invalid) == 0, latest
    except:
        return False, None


def process_single_file(input_file, text_col, j_level, output_folder):
    base_name = os.path.basename(input_file).split('.')[0]
    done, latest = is_file_completed(output_folder, base_name, j_level)
    if done:
        print(f"  [跳过] {base_name} (SEDA j={j_level}) 已完成。")
        return "SKIP"

    df = pd.read_excel(latest) if latest else pd.read_excel(input_file)
    if 'SEDA_Result' not in df.columns: df['SEDA_Result'] = ""

    actual_col = text_col if text_col in df.columns else ("内容" if "内容" in df.columns else df.columns[1])
    framework = get_seda_framework(j_level)

    for i in tqdm(range(len(df)), desc=f"{base_name}_SEDA_j{j_level}"):
        # 跳过已有结果
        if pd.notna(df.at[i, 'SEDA_Result']) and df.at[i, 'SEDA_Result'] not in ["", "Unknown"] and "Error" not in str(
                df.at[i, 'SEDA_Result']):
            continue

        prompt = create_expert_prompt(df, i, actual_col, framework)
        result = call_model_api_with_rotation(prompt)
        if result == "ALL_KEYS_DEAD": return "BREAK"

        df.at[i, 'SEDA_Result'] = result
        if i % 10 == 0:
            df.to_excel(os.path.join(output_folder, f"Result_{base_name}_SEDA_j{j_level}_temp.xlsx"), index=False)
        time.sleep(0.5)

    final_path = os.path.join(output_folder,
                              f"Result_{base_name}_SEDA_j{j_level}_{datetime.now().strftime('%m%d_%H%M')}.xlsx")
    df.to_excel(final_path, index=False)
    return "CONTINUE"


# ================= 5. 执行入口 =================
if __name__ == "__main__":
    DATA_DIR = '../data/'
    OUTPUT_DIR = 'output_seda/'
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    stop_flag = False
    for sub in ['Art', 'Science']:
        if stop_flag: break

        # 如果是 Art 类别，直接跳过（因为已全部完成）
        if sub == 'Art':
            continue

        for i in range(1, 11):
            if stop_flag: break

            # 跳过 Science 1 到 Science 8（已完成）
            if sub == 'Science' and i < 9:
                continue

            fpath = os.path.join(DATA_DIR, f"精-{sub}{i}.xlsx")
            if os.path.exists(fpath):
                for j in range(1, 4):
                    # 【核心断点逻辑】：如果是 Science 9 且 j<3，则跳过
                    if sub == 'Science' and i == 9 and j < 3:
                        print(f"Skipping completed: {sub}{i} j={j}")
                        continue

                    print(f"Processing: {sub}{i} j={j}...")
                    status = process_single_file(fpath, "内容", j, OUTPUT_DIR)
                    if status == "BREAK":
                        stop_flag = True
                        break

    print("\n>>> SEDA 断点续传任务已结束。<<<")