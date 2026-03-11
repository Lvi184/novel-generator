"""
简单版本的章节生成器
直接使用 OpenAI SDK
"""
import json
import os
from openai import OpenAI


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("使用 LLM 生成古龙风格第一章")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    output_dir = config["filepath"]
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建 OpenAI 客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 古龙风格提示词
    new_story = config["new_story"]
    
    prompt = f"""请写一部都市重生小说的第一章，约4000字，严格按照古龙风格写作。

## 基本设定
- 主角：林风，28岁程序员
- 重生时间：2010年5月20日
- 地点：深圳
- 金手指：手机里保存了2010-2035年的所有知识（股市行情、创业机会、未来科技等）

## 古龙风格写作要求（必须严格遵守）
1. **短句为主**：句子要短，一行一句，不要长句复杂句
2. **对话占比高**：对话要占60%以上，用对话推动情节
3. **章末悬念**：章节结尾必须有强烈的悬念，让读者想看下一章
4. **哲理思考**：适当穿插一些有哲理的思考和金句
5. **机智对白**：人物对话要有机智、有深度、有张力
6. **心理描写**：注重心理战，不只是动作描写
7. **场景切换快**：短场景，快速切换，不要拖沓
8. **神秘氛围**：人物出场要神秘，不要一下子全说清楚

## 情节建议
- 开头：林风在2010年醒来，发现自己重生
- 发现手机里的未来知识
- 遇到初恋苏晴
- 听到同学李磊要创业的消息（李磊后来会成为亿万富翁）
- 接到一个神秘电话，约他晚上在咖啡厅见面
- 章末悬念：这个神秘电话是谁打来的？会发生什么？

现在开始写第一章："""
    
    print("\n正在生成第一章（可能需要几分钟）...")
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": "你是一个擅长写古龙风格小说的作家。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=config.get("max_tokens", 4096),
        temperature=config.get("temperature", 0.7)
    )
    
    chapter_content = response.choices[0].message.content
    
    # 保存章节
    chapter_path = os.path.join(output_dir, "chapter_1.txt")
    with open(chapter_path, 'w', encoding='utf-8') as f:
        f.write(chapter_content)
    
    print("\n" + "=" * 60)
    print("第一章生成完成！")
    print("=" * 60)
    print(f"\n文件位置：{chapter_path}")
    print("\n" + "-" * 60)
    print("第一章预览：")
    print("-" * 60)
    preview = chapter_content[:1000] + "..." if len(chapter_content) > 1000 else chapter_content
    print(preview)


if __name__ == "__main__":
    main()
