"""
改进版：避免习惯性表述问题
"""
import json
import os
import time
from openai import OpenAI


def generate_chapter(client, config, chapter_num, previous_chapters):
    """生成单章"""
    
    new_story = config["new_story"]
    
    # 准备前文摘要（非常简洁）
    previous_summary = ""
    if previous_chapters:
        previous_summary = "前情提要：\n"
        for i, chap in enumerate(previous_chapters[-1:], max(1, chapter_num-1)):
            previous_summary += f"\n第{chapter_num-1}章结尾：{chap[-300:]}\n"
    
    prompt = f"""请写都市重生小说的第{chapter_num}章，约4000字，古龙风格。

## 基本设定
- 主角：林风，28岁程序员
- 重生时间：2010年5月20日
- 地点：深圳
- 金手指：iPhone 15 Pro Max里有未来知识
- 人物：苏晴（女友）、李磊（兄弟）、小古（神秘AI）

{previous_summary}

## 写作风格要求（古龙风格）
1. 短句为主，一行一句
2. 对话占比60%以上
3. 章末必有强烈悬念
4. 适当哲理思考
5. 机智对白
6. 注重心理描写
7. 场景切换快
8. 保持神秘氛围

## ❌ 绝对避免的表述（重要！）
- 不要用"不是...不是..."这种否定排比
- 不要用"像2035年..."这种比喻
- 不要用"比...还..."这种重复比较
- 不要过度重复相同词汇
- 不要用QQ农场等过时网络梗

## ✅ 推荐的表达方式
- 直接描述，少用否定
- 用2010年时代背景的事物做比喻
- 多样化的句式结构
- 自然的语言流动

## 第{chapter_num}章情节
- 承接上一章悬念
- 推进剧情，引入新元素
- 揭开部分谜团，留下更多悬念
- 章末强悬念

现在开始写第{chapter_num}章："""
    
    print(f"正在生成第{chapter_num}章...")
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": "你是古龙风格小说作家，语言精炼，避免重复和习惯性表述。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=config.get("max_tokens", 4096),
        temperature=0.9,
        presence_penalty=0.4,
        frequency_penalty=0.4
    )
    
    return response.choices[0].message.content


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("生成第16-20章（改进版 - 避免习惯性表述）")
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
    
    for i in range(1, 16):
        chapter_path = os.path.join(output_dir, f"chapter_{i}.txt")
        if os.path.exists(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8') as f:
                previous_chapters.append(f.read())
            print(f"已加载第{i}章")
    
    # 生成第16-20章
    for chapter_num in range(16, 21):
        chapter_content = generate_chapter(client, config, chapter_num, previous_chapters)
        
        # 保存章节
        chapter_path = os.path.join(output_dir, f"chapter_{chapter_num}.txt")
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
        
        print(f"[OK] 第{chapter_num}章已保存：{chapter_path}")
        
        # 添加到前文列表
        previous_chapters.append(chapter_content)
        
        # 避免太快请求
        if chapter_num < 20:
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print("第16-20章生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
