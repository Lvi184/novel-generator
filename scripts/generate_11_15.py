"""
生成第11-15章（改进版 - 减少重复）
"""
import json
import os
import time
from openai import OpenAI


def generate_chapter(client, config, chapter_num, previous_chapters, used_phrases):
    """生成单章"""
    
    new_story = config["new_story"]
    
    # 准备前文摘要（更简洁，避免重复）
    previous_summary = ""
    if previous_chapters:
        previous_summary = "前情提要（简要）：\n"
        for i, chap in enumerate(previous_chapters[-2:], max(1, chapter_num-2)):
            # 只取每章的前200字作为摘要
            chapter_idx = max(1, chapter_num-2 + i)
            previous_summary += f"\n第{chapter_idx}章：{chap[:200]}...\n"
    
    # 构建避免重复的提示
    avoid_repeat = ""
    if used_phrases:
        avoid_repeat = "\n## 避免重复（重要！）\n"
        avoid_repeat += "以下词语和表达已经在前文中过度使用，请尽量避免或用同义词替换：\n"
        for phrase in list(used_phrases)[:20]:
            avoid_repeat += f"- {phrase}\n"
    
    prompt = f"""请写都市重生小说的第{chapter_num}章，约4000字，严格按照古龙风格写作。

## 基本设定
- 主角：林风，28岁程序员
- 重生时间：2010年5月20日
- 地点：深圳
- 金手指：iPhone 15 Pro Max里保存了2010-2035年的所有知识
- 重要人物：苏晴（女朋友）、李磊（兄弟）、小古（神秘AI/女人）

{previous_summary}

## 古龙风格写作要求（必须严格遵守）
1. **短句为主**：句子要短，一行一句，不要长句复杂句
2. **对话占比高**：对话要占60%以上，用对话推动情节
3. **章末悬念**：章节结尾必须有强烈的悬念
4. **哲理思考**：适当穿插有哲理的思考和金句
5. **机智对白**：人物对话要有机智、有深度、有张力
6. **心理描写**：注重心理战
7. **场景切换快**：短场景，快速切换
8. **神秘氛围**：保持神秘氛围

{avoid_repeat}

## 第{chapter_num}章情节要求
- 承接上一章结尾的悬念
- 推进剧情发展，不要原地踏步
- 引入新的元素或冲突
- 揭开部分谜团，但留下更多悬念
- 章末要有强烈的悬念

## 语言多样性要求
- 尝试使用不同的比喻和表达方式
- 避免过度重复相同的词语
- 保持古龙风格的同时，让语言更丰富

现在开始写第{chapter_num}章："""
    
    print(f"正在生成第{chapter_num}章...")
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": "你是一个擅长写古龙风格小说的作家，擅长使用多样化的语言表达，避免重复。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=config.get("max_tokens", 4096),
        temperature=0.85,
        presence_penalty=0.3,
        frequency_penalty=0.3
    )
    
    return response.choices[0].message.content


def extract_used_phrases(chapters):
    """从已生成章节中提取频繁使用的短语"""
    import re
    
    all_text = "\n".join(chapters)
    
    phrases = []
    
    common_patterns = [
        r"网吧的吊扇",
        r"红双喜",
        r"华强北",
        r"歪歪扭扭",
        r"草莓",
        r"N97",
        r"蓝T恤",
        r"硬邦邦",
        r"凉冰冰",
        r"昏黄的灯光",
        r"二手烟",
        r"泡面"
    ]
    
    for pattern in common_patterns:
        count = len(re.findall(pattern, all_text))
        if count > 3:
            phrases.append(pattern)
    
    return set(phrases)


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("生成第11-15章（改进版 - 减少重复）")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    output_dir = config["filepath"]
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 读取已有的章节
    previous_chapters = []
    
    for i in range(1, 11):
        chapter_path = os.path.join(output_dir, f"chapter_{i}.txt")
        if os.path.exists(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8') as f:
                previous_chapters.append(f.read())
            print(f"已加载第{i}章")
    
    # 提取已使用的短语
    used_phrases = extract_used_phrases(previous_chapters)
    if used_phrases:
        print(f"\n检测到频繁使用的短语：{', '.join(used_phrases)}")
    
    # 生成第11-15章
    for chapter_num in range(11, 16):
        chapter_content = generate_chapter(client, config, chapter_num, previous_chapters, used_phrases)
        
        # 保存章节
        chapter_path = os.path.join(output_dir, f"chapter_{chapter_num}.txt")
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
        
        print(f"[OK] 第{chapter_num}章已保存：{chapter_path}")
        
        # 添加到前文列表
        previous_chapters.append(chapter_content)
        
        # 更新已使用的短语
        used_phrases = extract_used_phrases(previous_chapters[-5:])
        
        # 避免太快请求
        if chapter_num < 15:
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print("第11-15章生成完成！")
    print("=" * 60)
    print(f"\n输出文件位置：{output_dir}")


if __name__ == "__main__":
    main()
