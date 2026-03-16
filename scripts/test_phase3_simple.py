"""
简化版 Phase 3 测试 - 针对《我在精神病院学斩神》
直接生成新风格的章节
"""
import json
import os
from openai import OpenAI


def main():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    print("=" * 60)
    print("Phase 3 - 简化版逐章生成测试")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "xue_zhong_han_dao_xing", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试生成第1章
    chapter_num = 1
    chapter_title = "第一章 黑缎缠目"
    
    print(f"\n正在生成第 {chapter_num} 章：{chapter_title}")
    
    prompt = f"""请以《我在精神病院学斩神》的叙事风格，写一部都市奇幻小说的第一章。

小说设定：
- 主角：陈明，17岁高中生，外表冷漠内心善良
- 背景：百年浩劫后，东海市是唯一净土的现代都市
- 风格：紧张悬疑，带点神秘超自然元素

要求：
1. 第一章主角登场，形象要特别（类似原作黑缎缠目的设定）
2. 要有日常场景，但暗藏神秘伏笔
3. 字数：3000-4000字
4. 章末要有悬念

现在开始写第一章：
"""
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": "你是一位优秀的都市奇幻小说作家，擅长营造悬疑氛围和神秘设定。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=4000
    )
    
    chapter_content = response.choices[0].message.content
    
    # 保存章节
    output_file = os.path.join(output_dir, f"chapter_{chapter_num:02d}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(chapter_content)
    
    print(f"\n第 {chapter_num} 章生成完成！")
    print(f"保存位置：{output_file}")
    print(f"\n章节预览（前500字）：")
    print("-" * 60)
    print(chapter_content[:500])
    print("-" * 60)
    print(f"\n完整章节已保存到文件中")
    
    print("\n" + "=" * 60)
    print("Phase 3 简化版测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
