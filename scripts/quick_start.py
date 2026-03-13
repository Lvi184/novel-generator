"""
快速开始脚本
使用内置的古龙风格档案，快速生成第一章
"""
import os
import sys
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("网络小说叙事技法仿写系统 - 快速开始")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    output_dir = config["filepath"]
    os.makedirs(output_dir, exist_ok=True)
    
    # 步骤1：创建叙事技法档案（使用内置古龙风格）
    print("\n[步骤 1/4] 创建古龙叙事技法档案...")
    profile_path = os.path.join(output_dir, "narrative_profile.json")
    
    guolong_profile = {
        "pacing": {
            "avg_scene_length": "短",
            "tension_pattern": "突然爆发",
            "scene_switch_frequency": "高",
            "description": "短场景，快速切换，紧张感强"
        },
        "hooks": {
            "hook_frequency": 0.9,
            "hook_types": {
                "mystery": 0.4,
                "reveal": 0.3,
                "cliffhanger": 0.3
            },
            "avg_intensity": 8,
            "description": "90%章节有悬念，悬念强度高"
        },
        "dialogue_style": {
            "dialogue_ratio": 0.6,
            "sentence_style": "短句为主",
            "wit_exchange": True,
            "philosophical_ratio": 0.3,
            "description": "对话占比60%，短句为主，有机智对白和哲理思考"
        },
        "conflict_patterns": {
            "primary_type": "心理战",
            "escalation": "sudden",
            "psychological_warfare": "高",
            "sudden_twist": "高",
            "description": "高频率心理战，突然反转多"
        },
        "character_archetypes": {
            "lonely_hero": True,
            "mysterious_beauty": True,
            "complex_villain": True,
            "description": "孤独英雄、神秘美女、复杂反派"
        },
        "guolong_signatures": [
            "短句对话，语言精炼",
            "章末必有悬念",
            "哲理思考穿插",
            "心理战为主",
            "人物出场神秘",
            "突然反转频繁"
        ]
    }
    
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(guolong_profile, f, ensure_ascii=False, indent=2)
    print(f"[OK] 叙事技法档案已创建：{profile_path}")
    
    # 步骤2：创建故事设定
    print("\n[步骤 2/4] 创建故事设定...")
    new_story = config["new_story"]
    
    setting_content = f"""# 新故事设定

## 题材
{new_story['genre']}

## 核心想法
{new_story['core_idea']}

## 主角
- 姓名：{new_story['protagonist']['name']}
- 年龄：{new_story['protagonist']['age']}
- 职业：{new_story['protagonist']['occupation']}
- 特点：{new_story['protagonist']['trait']}

## 背景
- 时间：{new_story['setting']['time']}
- 地点：{new_story['setting']['location']}
- 时代背景：{new_story['setting']['background']}

## 叙事风格（源自《多情剑客无情剑》）
- 对话占比：60%
- 短句为主
- 90% 章末有悬念
- 有机智对白
- 有哲理金句

## 金手指设定
主角林风的手机里保存了2010-2035年的所有知识，包括：
- 未来科技趋势
- 股市行情
- 创业机会
- 重要事件

## 主要人物
- 林风：主角，28岁程序员，聪明低调重情义
- 神秘美女：身份不明，与主角有复杂关系
- 商业对手：复杂反派，有自己的原则

## 故事主线
林风重生2010年深圳，利用未来知识创业，在商业竞争中成长，同时揭开自己重生的秘密。
"""
    
    setting_path = os.path.join(output_dir, "Novel_setting.txt")
    with open(setting_path, 'w', encoding='utf-8') as f:
        f.write(setting_content)
    print(f"[OK] 故事设定已创建：{setting_path}")
    
    # 步骤3：创建章节目录
    print("\n[步骤 3/4] 创建章节目录...")
    directory_content = """# 章节目录（共 120 章）

## 第一章 归来
2025年的程序员林风，在一个雷雨天醒来，发现自己回到了2010年的深圳。手机里保存着未来25年的所有知识。

## 第二章 手机
林风发现手机里的未来知识：股市行情、创业机会、科技趋势。他意识到这是他逆袭的机会。

## 第三章 第一桶金
林风用仅有的几千块钱，根据未来记忆投资股市。一天之内，资金翻倍。

## 第四章 初见
在证券营业部，林风遇到了一个神秘的女人。她似乎对林风很感兴趣。

## 第五章 选择
林风面临选择：是继续炒股快速赚钱，还是用未来知识创业？

## 第六章 机会
林风想起2010年的一个重要创业机会。他决定行动。

## 第七章 阻力
有人不相信林风的想法。质疑、嘲笑、阻碍接踵而至。

## 第八章 赌约
林风与一个商业对手定下赌约。如果失败，他将失去一切。

## 第九章 神秘
那个神秘女人再次出现。她似乎知道很多事。

## 第十章 揭晓
第一章的悬念揭晓。但新的悬念又出现了。

## 第11-120章
（剩余110章的详细内容待生成）

### 后续章节概要
- 主角创业，逐步建立商业帝国
- 与神秘女人的关系逐渐复杂
- 商业对手不断升级挑战
- 逐步揭开重生的秘密
- 最终达到人生巅峰
"""
    
    directory_path = os.path.join(output_dir, "Novel_directory.txt")
    with open(directory_path, 'w', encoding='utf-8') as f:
        f.write(directory_content)
    print(f"[OK] 章节目录已创建：{directory_path}")
    
    # 步骤4：创建第一章示例
    print("\n[步骤 4/4] 创建第一章示例...")
    chapter_content = """# 第一章 归来

雨。

深圳的雨，总是来得突然。

林风睁开眼的时候，窗外正下着这样的雨。

他记得自己刚才还在2025年的办公室里，改着永远改不完的代码。窗外的霓虹灯闪烁，是深圳熟悉的夜景。

可是现在——

他看着墙上的日历。

2010年5月20日。

林风猛地坐起来，抓过床头柜上的手机。

手机很旧，是一部iPhone 4。

屏幕亮起，显示的时间确实是2010年5月20日。

他重生了。

回到了15年前。

林风的心开始狂跳。他不是在做梦。他捏了自己一把，疼得龇牙咧嘴。

然后他想到了一件事。

他立刻解锁手机，打开相册。

相册里有一个文件夹，名字叫"未来知识"。

文件夹里有无数个文档，按年份分类：2010、2011、2012……一直到2035。

林风的手在颤抖。

他打开2010年的文档，里面是：

- 2010年股市行情表
- 2010年比特币价格走势
- 2010年深圳房价数据
- 2010年创业机会分析
- ……

他真的有了未来25年的所有知识。

林风走到窗前，看着楼下的街道。

2010年的深圳，还没有那么多高楼大厦。但是他知道，这里即将发生什么。

腾讯即将崛起，阿里即将上市，比特币即将从几分钱涨到几万美元……

而他，林风，一个普通的程序员，现在站在了这一切的起点。

"林风？你醒了？"

门外传来一个女人的声音。

林风的心跳突然停了一拍。

这个声音……他太熟悉了。

是苏晴。

他的大学同学，他的初恋，也是他这辈子最大的遗憾。

林风深吸一口气，打开了门。

门外站着一个年轻的女孩，穿着简单的T恤和牛仔裤，长发披肩，眼睛明亮。

正是2010年的苏晴。

"你昨天淋了雨，发烧了，睡了一天。"苏晴把一碗粥放在桌上，"感觉怎么样？"

林风看着她，喉咙有些发紧。

他记得，就是在2010年，他错过了苏晴。因为他的懦弱，因为他的自卑。

但是现在，一切都不一样了。

"我没事。"林风说，声音有些沙哑。

"那就好。"苏晴笑了笑，"对了，我有个消息要告诉你。"

"什么消息？"

"我们班的李磊，他爸给了他一笔钱，他要创业了。"苏晴说，"做互联网，好像是做什么社交网站。"

林风的心猛地一跳。

李磊。

他当然记得李磊。

这个人后来创立了一家估值几十亿的公司。而他的起点，就是2010年的这次创业。

"哦。"林风淡淡地说。

"你好像一点都不惊讶？"苏晴奇怪地看着他。

"没什么好惊讶的。"林风说，"每个人都有自己的路。"

苏晴还想说什么，但就在这时，林风的手机响了。

是一个陌生的号码。

林风接起电话。

"是林风吗？"电话那头是一个陌生的男人声音，"我有个东西要给你。"

"什么东西？"

"你看了就知道。"男人说，"今天晚上八点，在'旧时光'咖啡厅。一个人来。"

电话挂了。

林风拿着手机，陷入了沉思。

这个电话，是什么意思？

他不记得2010年的今天，有接过这样一个电话。

难道是因为他的重生，事情发生了变化？

"谁的电话？"苏晴问。

"不知道。"林风说，"一个陌生人。"

"陌生人？"苏晴有些担心，"会不会是骗子？"

"也许吧。"林风说，"不过，我想去看看。"

"为什么？"

"因为，"林风看着窗外的雨，嘴角微微上扬，"我有种感觉，这通电话，会改变很多事情。"

雨还在下。

但是林风知道，他的人生，已经不一样了。

晚上八点，旧时光咖啡厅。

他会去。

不管等待着他的是什么。

（第一章 完）

（欲知后事如何，且听下回分解）
"""
    
    chapter_path = os.path.join(output_dir, "chapter_1.txt")
    with open(chapter_path, 'w', encoding='utf-8') as f:
        f.write(chapter_content)
    print(f"[OK] 第一章示例已创建：{chapter_path}")
    
    print("\n" + "=" * 60)
    print("所有文件创建完成！")
    print("=" * 60)
    print(f"\n输出文件位置：{output_dir}")
    print("\n生成的文件：")
    print("  - narrative_profile.json  (古龙叙事技法档案)")
    print("  - Novel_setting.txt       (故事设定)")
    print("  - Novel_directory.txt     (章节目录)")
    print("  - chapter_1.txt           (第一章示例)")
    print("\n下一步：")
    print("  1. 在 config.json 中配置你的 API Key")
    print("  2. 运行 python run_all.py 来生成真正的 AI 章节")


if __name__ == "__main__":
    main()
