"""
连续生成多章
"""
import json
import os
import time
from openai import OpenAI


def generate_chapter(client, config, chapter_num, previous_chapters):
    """生成单章"""
    
    new_story = config["new_story"]
    
    # 准备前文摘要
    previous_summary = ""
    if previous_chapters:
        previous_summary = "前情提要：\n"
        for i, chap in enumerate(previous_chapters[-3:], max(1, chapter_num-3)):
            previous_summary += f"\n第{i}章摘要：\n{chap[:500]}...\n"
    
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

## 第{chapter_num}章情节建议
- 承接上一章结尾的悬念
- 林风准备去星巴克见小古
- 可能遇到新的人物或事件
- 揭开部分谜团，但留下更多悬念
- 章末要有强烈的悬念

现在开始写第{chapter_num}章："""
    
    print(f"正在生成第{chapter_num}章...")
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": "你是一个擅长写古龙风格小说的作家。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=config.get("max_tokens", 4096),
        temperature=config.get("temperature", 0.7)
    )
    
    return response.choices[0].message.content


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("连续生成10章古龙风格小说")
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
    start_chapter = 2
    
    # 检查第一章是否存在
    chapter1_path = os.path.join(output_dir, "chapter_1.txt")
    if os.path.exists(chapter1_path):
        with open(chapter1_path, 'r', encoding='utf-8') as f:
            previous_chapters.append(f.read())
        print("已加载第1章")
    
    # 生成第2-10章
    for chapter_num in range(start_chapter, 11):
        chapter_content = generate_chapter(client, config, chapter_num, previous_chapters)
        
        # 保存章节
        chapter_path = os.path.join(output_dir, f"chapter_{chapter_num}.txt")
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
        
        print(f"[OK] 第{chapter_num}章已保存：{chapter_path}")
        
        # 添加到前文列表
        previous_chapters.append(chapter_content)
        
        # 避免太快请求
        if chapter_num < 10:
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("10章生成完成！")
    print("=" * 60)
    print(f"\n输出文件位置：{output_dir}")


if __name__ == "__main__":
    main()
