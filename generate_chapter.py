"""
章节生成脚本
基于叙事技法档案生成古龙风格的章节
"""
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from novel_generator.llm_adapters import create_llm_adapter


def generate_chapter(config_path: str, chapter_num: int = 1):
    """生成指定章节"""
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 读取叙事技法档案
    profile_path = os.path.join(config["filepath"], "narrative_profile.json")
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    # 读取故事设定
    setting_path = os.path.join(config["filepath"], "Novel_setting.txt")
    with open(setting_path, 'r', encoding='utf-8') as f:
        setting = f.read()
    
    # 读取章节目录
    directory_path = os.path.join(config["filepath"], "Novel_directory.txt")
    with open(directory_path, 'r', encoding='utf-8') as f:
        directory = f.read()
    
    # 创建 LLM 适配器
    llm = create_llm_adapter(
        interface_format=config.get("interface_format", "OpenAI"),
        base_url=config["base_url"],
        model_name=config["model_name"],
        api_key=config["api_key"],
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
        timeout=config.get("timeout", 600)
    )
    
    profile_str = json.dumps(profile, ensure_ascii=False, indent=2)
    
    prompt = f"""请根据以下信息，生成小说的第{chapter_num}章，字数约{config.get('word_number', 4000)}字：

## 叙事技法档案（源自《多情剑客无情剑》）
{profile_str}

## 古龙风格写作要求（严格遵守）
1. **短句为主**：句子要短，不要长句复杂句
2. **对话占比高**：对话要占60%以上，用对话推动情节
3. **章末悬念**：章节结尾必须有强烈的悬念，让读者想看下一章
4. **哲理思考**：适当穿插一些有哲理的思考和金句
5. **机智对白**：人物对话要有机智、有深度、有张力
6. **心理描写**：注重心理战，不只是动作描写
7. **场景切换快**：短场景，快速切换，不要拖沓
8. **神秘氛围**：人物出场要神秘，不要一下子全说清楚

## 故事设定
{setting[:3000]}

## 章节目录
{directory[:3000]}

## 第{chapter_num}章特别要求
- 第1章必须是重生/穿越开场
- 主角林风，28岁程序员
- 重生到2010年深圳
- 金手指：手机里保存了2010-2035年的所有知识
- 章节结尾必须有悬念

现在开始写第{chapter_num}章："""
    
    print(f"正在生成第{chapter_num}章...")
    chapter_content = llm.invoke(prompt)
    
    # 保存章节
    output_path = os.path.join(config["filepath"], f"chapter_{chapter_num}.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(chapter_content)
    
    print(f"第{chapter_num}章已保存：{output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) &lt; 2:
        print("用法：python generate_chapter.py --config &lt;config_path&gt; [--chapter &lt;num&gt;]")
        sys.exit(1)
    
    config_path = None
    chapter_num = 1
    
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "--config" and i + 1 &lt; len(sys.argv):
            config_path = sys.argv[i + 1]
        elif sys.argv[i] == "--chapter" and i + 1 &lt; len(sys.argv):
            chapter_num = int(sys.argv[i + 1])
    
    if not config_path:
        print("错误：请指定配置文件 --config &lt;config_path&gt;")
        sys.exit(1)
    
    generate_chapter(config_path, chapter_num)
