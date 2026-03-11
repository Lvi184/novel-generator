# 网络小说叙事技法仿写系统 - Case1

> 基于 AI_NovelGenerator 框架 + 古龙风格分析
> 
> **目标**：分析《多情剑客无情剑》的叙事技法，创作都市重生故事

---

## 📋 项目说明

本项目能够：
1. **分析目标小说**（如《多情剑客无情剑》）的叙事技法
2. **迁移到新题材**（如都市重生）
3. **每天自动生成一章**（定时任务）

---

## 🚀 快速开始

### 1. 配置 API Key

编辑 `config.json`，填入你的 Claude API Key：

```json
{
  "api_key": "sk-YOUR-CLAUDE-API-KEY",
  "base_url": "https://api.anthropic.com/v1",
  "model_name": "claude-sonnet-4-20250514"
}
```

### 2. 运行初始化脚本

```powershell
# 以管理员身份运行 PowerShell
cd D:\openclaw\workspace\case1
.\init-scheduler.ps1
```

这会：
- ✅ 检查配置文件
- ✅ 检查目标小说
- ✅ 创建 Windows 定时任务（每天上午 9 点执行）

### 3. 测试运行

```powershell
# 立即运行一次测试
.\create-novel.ps1

# 或者通过任务计划运行
schtasks /run /tn "NovelGenerator_GuLong"
```

---

## 📁 项目结构

```
case1/
├── config.json              # 配置文件（填入 API Key）
├── create-novel.ps1         # 定时任务脚本
├── init-scheduler.ps1       # 初始化脚本
├── README.md                # 本文件
│
├── src/                     # 新增模块（待开发）
│   ├── style_analyzer.py    # 叙事技法分析
│   └── narrative_migrator.py # 叙事技法迁移
│
└── data/
    └── output/
        ├── narrative_profile.json   # 叙事技法档案（自动生成）
        ├── Novel_setting.txt        # 新故事设定（自动生成）
        ├── Novel_directory.txt      # 章节目录（自动生成）
        └── chapter_X.txt            # 生成的章节（自动生成）
```

---

## 📖 配置说明

### config.json 关键配置

```json
{
  // 目标小说路径
  "target_novel_path": "D:\\openclaw\\workspace\\.ai\\case1\\多情剑客无情剑.txt",
  
  // 新故事设定
  "new_story": {
    "genre": "都市重生",
    "core_idea": "现代程序员重生 2010 年，用未来 AI 系统逆袭",
    "protagonist": {
      "name": "林风",
      "occupation": "程序员"
    }
  },
  
  // 分析参数
  "analysis": {
    "chunk_size": 5000,
    "analyze_dialogue": true,
    "analyze_hooks": true
  },
  
  // 迁移参数
  "migration": {
    "similarity": 0.85,  // 相似度 0-1
    "keep_guolong_style": true  // 保持古龙风格
  }
}
```

---

## ⏰ 定时任务管理

### 查看任务状态
```powershell
schtasks /query /tn "NovelGenerator_GuLong"
```

### 立即运行一次
```powershell
schtasks /run /tn "NovelGenerator_GuLong"
```

### 修改执行时间（如改为每天晚上 8 点）
```powershell
schtasks /change /tn "NovelGenerator_GuLong" /st 20:00
```

### 删除任务
```powershell
schtasks /delete /tn "NovelGenerator_GuLong" /f
```

---

## 📊 工作流程

```
┌─────────────────────────────────────────────────────────┐
│              工作流程                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  【第一次运行】                                          │
│   1. 分析《多情剑客无情剑》→ narrative_profile.json    │
│   2. 迁移设定 → Novel_setting.txt                      │
│   3. 生成目录 → Novel_directory.txt                    │
│   4. 生成第 1 章 → chapter_1.txt                        │
│                                                         │
│  【之后每天运行】                                        │
│   1. 跳过分析（已有档案）                               │
│   2. 跳过迁移（已有设定）                               │
│   3. 生成下一章 → chapter_X.txt                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 测试用例

### 输入
- **目标小说**：《多情剑客无情剑》（古龙）
- **新故事**： "现代程序员重生 2010 年，用未来 AI 系统逆袭都市"

### 预期输出
| 文件 | 内容 | 检查点 |
|------|------|--------|
| narrative_profile.json | 古龙叙事技法 | 对话占比、悬念频率 |
| Novel_setting.txt | 都市重生设定 | 2010 年深圳、程序员主角 |
| Novel_directory.txt | 120 章目录 | 古龙式节奏 |
| chapter_1.txt | 第 1 章正文 | 古龙风格 + 都市背景 |

---

## 🛠️ 开发计划

- [x] RPD 文档
- [x] 定时任务脚本
- [x] 配置文件
- [ ] 叙事分析模块（style_analyzer.py）
- [ ] 叙事迁移模块（narrative_migrator.py）
- [ ] 完整测试

---

## 📝 日志查看

运行日志保存在：
```
D:\openclaw\workspace\case1\logs\YYYY-MM-DD.log
```

---

## ⚠️ 注意事项

1. **API Key 安全**：不要将 `config.json` 提交到公开仓库
2. **版权问题**：目标小说仅用于学习研究
3. **内容审核**：生成的内容请人工审核后再发布

---

## 📄 License

基于 AI_NovelGenerator 开发，遵守 MIT License

---

## 🎉 开始创作吧！

```powershell
# 初始化
.\init-scheduler.ps1

# 之后每天自动生成一章！
```
