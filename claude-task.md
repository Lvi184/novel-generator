
# 任务：实现网络小说叙事技法仿写系统的完整功能

## 项目概述
基于 AI_NovelGenerator 框架，开发一个网络小说叙事技法仿写系统。

## 核心目标
1. 分析《多情剑客无情剑》的叙事技法（节奏、钩子、对话风格等）
2. 将这些技法迁移到都市重生题材
3. 每天自动生成一章小说

## 已有的文件
- ✅ `config.json` - 配置文件（已填好）
- ✅ `rpd.md` - 需求项目文档（在 `.ai\case1\` 目录）
- ✅ `src/style_analyzer.py` - 叙事分析模块（基础版）
- ✅ `src/narrative_migrator.py` - 叙事迁移模块（基础版）
- ✅ `src/prompts.yaml` - 提示词文件
- ✅ `novel_generator/` - AI_NovelGenerator 开源框架（已克隆）

## 需要完成的工作

### Phase 1: 完善叙事分析模块
1. 完善 `src/style_analyzer.py`，使其能够真正分析《多情剑客无情剑》
2. 分析维度包括：
   - 剧情节奏（紧张度曲线、场景长度）
   - 钩子设计（章末悬念类型、频率）
   - 对话风格（对话占比、句式特点、哲理对话比例）
   - 冲突模式（冲突类型、升级方式）
   - 人物弧线（主角成长、关系变化）
3. 输出完整的 `narrative_profile.json` 到 `data/output/`

### Phase 2: 完善叙事迁移模块
1. 完善 `src/narrative_migrator.py`
2. 根据叙事技法档案和配置文件中的新故事设定，生成：
   - `Novel_setting.txt` - 完整的故事设定
   - `Novel_directory.txt` - 120 章的章节目录（古龙式节奏）

### Phase 3: 集成 AI_NovelGenerator
1. 学习 AI_NovelGenerator 的使用方式
2. 修改或创建脚本，使其能够：
   - 读取我们的叙事技法档案
   - 生成保持古龙风格的章节
   - 对话占比高、短句为主、章末有悬念

### Phase 4: 生成第一章
1. 运行完整流程，生成第一章
2. 第一章内容应该：
   - 都市重生题材（2010 年深圳，程序员主角林风）
   - 完全古龙风格（短句对话、章末悬念、哲理思考）
   - 金手指：手机里保存 2010-2035 年的知识
   - 核心冲突：创业、爱情、商业竞争

## 目标小说位置
`D:\openclaw\workspace\.ai\case1\多情剑客无情剑.txt`

## 输出目录
`D:\openclaw\workspace\case1\data\output\`

## 执行要求
1. 严格按照 rpd.md 中的设计实现
2. 保持代码清晰、可维护
3. 生成的内容要真正有古龙风格
4. 所有输出文件都要保存到指定目录

现在开始实现！
