"""
叙事技法迁移模块
将分析出的叙事技法应用到新故事
"""
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from novel_generator.llm_adapters import create_llm_adapter


class NarrativeMigrator:
    def __init__(self, config_path, narrative_profile):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.profile = narrative_profile
        
        # 创建 LLM 适配器
        self.llm = create_llm_adapter(
            interface_format=self.config.get("interface_format", "OpenAI"),
            base_url=self.config["base_url"],
            model_name=self.config["model_name"],
            api_key=self.config["api_key"],
            temperature=self.config.get("temperature", 0.7),
            max_tokens=self.config.get("max_tokens", 4096),
            timeout=self.config.get("timeout", 600)
        )
    
    def generate_setting(self):
        """生成新故事设定"""
        new_story = self.config['new_story']
        
        profile_str = json.dumps(self.profile, ensure_ascii=False, indent=2)
        
        prompt = f"""请根据以下信息，生成一份详细的小说故事设定：

## 叙事技法档案（源自《多情剑客无情剑》）
{profile_str}

## 新故事基本信息
- 题材：{new_story['genre']}
- 核心想法：{new_story['core_idea']}
- 主角姓名：{new_story['protagonist']['name']}
- 主角年龄：{new_story['protagonist']['age']}
- 主角职业：{new_story['protagonist']['occupation']}
- 主角特点：{new_story['protagonist']['trait']}
- 时间背景：{new_story['setting']['time']}
- 地点背景：{new_story['setting']['location']}
- 时代背景：{new_story['setting']['background']}

## 要求
1. 保持古龙的叙事风格：短句对话、高对话占比、章末悬念、哲理思考
2. 设定要详细，包括：
   - 完整的世界观设定
   - 主要人物介绍（主角、配角、反派）
   - 核心冲突设定
   - 金手指/特殊能力设定
   - 故事主线脉络
3. 适合都市重生题材

请输出完整的故事设定文档。"""
        
        try:
            setting = self.llm.invoke(prompt)
            return setting
        except Exception as e:
            print(f"生成设定时出错：{e}")
            # 返回备用设定
            return self._generate_backup_setting()
    
    def _generate_backup_setting(self) -&gt; str:
        """生成备用设定"""
        new_story = self.config['new_story']
        
        setting = f"""# 新故事设定

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
        return setting
    
    def generate_directory(self, num_chapters=120):
        """生成章节目录"""
        new_story = self.config['new_story']
        profile_str = json.dumps(self.profile, ensure_ascii=False, indent=2)
        
        prompt = f"""请根据以下信息，生成{num_chapters}章的小说章节目录：

## 叙事技法档案（源自《多情剑客无情剑》）
{profile_str}

## 新故事基本信息
- 题材：{new_story['genre']}
- 核心想法：{new_story['core_idea']}
- 主角：{new_story['protagonist']['name']}

## 古龙风格要求
1. 短场景，快速切换
2. 每章结尾都要有悬念
3. 对话占比高
4. 心理战和突然反转

## 要求
- 生成{num_chapters}章的完整目录
- 每章要有标题和简要内容描述
- 节奏要符合古龙风格：起承转合要快
- 第1章必须是重生/穿越开场
- 前10章要完成世界观铺垫和主要人物出场

请输出完整的章节目录。"""
        
        try:
            directory = self.llm.invoke(prompt)
            return directory
        except Exception as e:
            print(f"生成目录时出错：{e}")
            # 返回备用目录
            return self._generate_backup_directory(num_chapters)
    
    def _generate_backup_directory(self, num_chapters: int = 120) -&gt; str:
        """生成备用目录"""
        directory = f"# 章节目录（共 {num_chapters} 章）\n\n"
        
        # 前20章的详细目录
        chapters = [
            ("第一章 归来", "2025年的程序员林风，在一个雷雨天醒来，发现自己回到了2010年的深圳。手机里保存着未来25年的所有知识。"),
            ("第二章 手机", "林风发现手机里的未来知识：股市行情、创业机会、科技趋势。他意识到这是他逆袭的机会。"),
            ("第三章 第一桶金", "林风用仅有的几千块钱，根据未来记忆投资股市。一天之内，资金翻倍。"),
            ("第四章 初见", "在证券营业部，林风遇到了一个神秘的女人。她似乎对林风很感兴趣。"),
            ("第五章 选择", "林风面临选择：是继续炒股快速赚钱，还是用未来知识创业？"),
            ("第六章 机会", "林风想起2010年的一个重要创业机会。他决定行动。"),
            ("第七章 阻力", "有人不相信林风的想法。质疑、嘲笑、阻碍接踵而至。"),
            ("第八章 赌约", "林风与一个商业对手定下赌约。如果失败，他将失去一切。"),
            ("第九章 神秘", "那个神秘女人再次出现。她似乎知道很多事。"),
            ("第十章 揭晓", "第一章的悬念揭晓。但新的悬念又出现了。")
        ]
        
        for title, desc in chapters:
            directory += f"## {title}\n{desc}\n\n"
        
        if num_chapters &gt; 10:
            directory += f"## 第11-{num_chapters}章\n（剩余{num_chapters-10}章的详细内容待生成）\n\n"
            directory += "### 后续章节概要\n"
            directory += "- 主角创业，逐步建立商业帝国\n"
            directory += "- 与神秘女人的关系逐渐复杂\n"
            directory += "- 商业对手不断升级挑战\n"
            directory += "- 逐步揭开重生的秘密\n"
            directory += "- 最终达到人生巅峰\n"
        
        return directory
    
    def save_setting(self, setting, output_path):
        """保存设定"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(setting)
        print(f"故事设定已保存：{output_path}")
    
    def save_directory(self, directory, output_path):
        """保存目录"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(directory)
        print(f"章节目录已保存：{output_path}")


if __name__ == "__main__":
    if len(sys.argv) &lt; 3:
        print("用法：python narrative_migrator.py --config &lt;config_path&gt;")
        sys.exit(1)
    
    config_path = sys.argv[2]
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    profile_path = os.path.join(config["filepath"], "narrative_profile.json")
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    migrator = NarrativeMigrator(config_path, profile)
    
    setting_path = os.path.join(config["filepath"], "Novel_setting.txt")
    directory_path = os.path.join(config["filepath"], "Novel_directory.txt")
    
    setting = migrator.generate_setting()
    migrator.save_setting(setting, setting_path)
    
    directory = migrator.generate_directory(config.get("num_chapters", 120))
    migrator.save_directory(directory, directory_path)
