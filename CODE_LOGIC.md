# 小说仿写系统 - 代码逻辑快速指南

## 🎯 核心流程

```
原著小说(TXT)
    ↓
[Phase 1] 深度解剖 → 原著骨架(JSON)
    ↓
[Phase 2] 骨架变形 → 新大纲(JSON)
    ↓
[Phase 3] 逐章生成 → 新小说(TXT)
```

---

## 📦 模块依赖关系

```
┌─────────────────────────────────────────────────────────┐
│                     基础设施层                            │
│  json_parser.py  llm_cache.py  state_tracker.py         │
│  prompts.py      cost_estimator.py  config_loader.py    │
└──────────────────┬──────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ↓              ↓              ↓
┌─────────┐   ┌─────────┐   ┌─────────┐
│ Phase 1 │   │ Phase 2 │   │ Phase 3 │
│ 深度解剖 │   │ 骨架变形 │   │ 逐章生成 │
└─────────┘   └─────────┘   └─────────┘
```

---

## 🔧 Phase 1 - 深度解剖逻辑

### 文件：`scripts/phase1_analyzer.py` 或 `src/analysis/`

```python
# 1. 分割小说
splitter = NovelSplitter()
chapters = splitter.split(novel_text)
# 输出: [ChapterInfo, ChapterInfo, ...]

# 2. 逐章摘要
summarizer = ChapterSummarizer(llm_adapter)
chapter_summaries = []
for chapter in chapters:
    summary = summarizer.summarize(chapter)
    chapter_summaries.append(summary)
# 输出: [ChapterSummary, ChapterSummary, ...]

# 3. 递归摘要（处理长篇）
recursive_summarizer = RecursiveSummarizer(llm_adapter)
recursive_summary = recursive_summarizer.summarize(chapter_summaries)
# 输出: {level1, level2, level3, full}

# 4. 全局分析
analyzer = GlobalAnalyzer(llm_adapter)
skeleton = analyzer.analyze(chapter_summaries, recursive_summary)
# 输出: NovelSkeleton {characters, relationships, structure, foreshadowing}

# 5. 保存
skeleton.save("data/analysis_full/novel_skeleton.json")
```

---

## 🔧 Phase 2 - 骨架变形逻辑

### 文件：`scripts/phase2_transformer.py` 或 `src/transformation/`

```python
# 1. 加载原著骨架
skeleton = NovelSkeleton.load("data/analysis_full/novel_skeleton.json")

# 2. 定义新世界设定
new_world_concept = {
    "genre": "都市重生",
    "setting": "2010年深圳",
    "protagonist": "林风，28岁程序员",
    "magic_element": "iPhone 15 Pro Max 里的未来知识"
}

# 3. 世界观映射
world_mapper = WorldMapper(llm_adapter)
world_mapping = world_mapper.map(skeleton.world, new_world_concept)
# 输出: {original_element -> new_element, ...}

# 4. 角色映射
character_mapper = CharacterMapper(llm_adapter)
character_mapping = character_mapper.map(skeleton.characters, world_mapping)
# 输出: {original_character -> new_character, ...}

# 5. 剧情节拍映射
beat_mapper = BeatMapper(llm_adapter)
beat_mapping = beat_mapper.map(skeleton.beats, character_mapping, world_mapping)
# 输出: {original_beat -> new_beat, ...}

# 6. 章节大纲展开
outline_expander = OutlineExpander(llm_adapter)
chapter_outlines = outline_expander.expand(beat_mapping, character_mapping)
# 输出: [ChapterOutline, ChapterOutline, ...]

# 7. 整合变形
transformer = SkeletonTransformer()
transformed_outline = transformer.transform(
    world_mapping,
    character_mapping,
    beat_mapping,
    chapter_outlines
)

# 8. 保存
transformed_outline.save("data/transformed/transformed_outline.json")
```

---

## 🔧 Phase 3 - 逐章生成逻辑

### 文件：`scripts/phase3_generator.py` 或 `src/generation/`

```python
# 1. 加载新大纲
outline = TransformedOutline.load("data/transformed/transformed_outline.json")

# 2. 初始化状态追踪器
state_tracker = StateTracker()
state_tracker.load("data/state/state.json")  # 可选

# 3. 初始化记忆检索器
memory_retriever = MemoryRetriever(state_tracker)

# 4. 初始化质量检查器
quality_checker = QualityChecker(llm_adapter)

# 5. 逐章生成
for chapter_num in range(1, total_chapters + 1):
    
    # 5.1 检索记忆
    memories = memory_retriever.retrieve(
        chapter_num=chapter_num,
        chapter_outline=outline.chapters[chapter_num]
    )
    # 输出: {character_states, foreshadowing, previous_chapters, relationships}
    
    # 5.2 组装Prompt
    prompt = assemble_prompt(
        world_view=outline.world_view,
        story_outline=outline.story_outline,
        character_cards=outline.character_cards,
        memories=memories,
        chapter_outline=outline.chapters[chapter_num],
        style_guide="古龙风格"
    )
    
    # 5.3 生成（带自动重试）
    generator = EnhancedChapterGenerator(llm_adapter, quality_checker)
    chapter_text, quality_report = generator.generate(
        prompt=prompt,
        chapter_num=chapter_num,
        max_retries=2
    )
    
    # 5.4 章节衔接优化
    if chapter_num > 1:
        optimizer = TransitionOptimizer(llm_adapter)
        chapter_text = optimizer.optimize(
            previous_chapter=previous_chapter_text,
            current_chapter=chapter_text
        )
    
    # 5.5 更新状态追踪器
    state_tracker.update_from_chapter(chapter_text, chapter_num)
    
    # 5.6 保存
    save_chapter(chapter_text, chapter_num)
    state_tracker.save(f"data/state/state_chapter_{chapter_num}.json")
    
    # 5.7 记录上一章
    previous_chapter_text = chapter_text
```

---

## 🧠 关键数据结构

### NovelSkeleton（原著骨架）
```python
{
  "metadata": {
    "title": "多情剑客无情剑",
    "author": "古龙",
    "genre": "武侠"
  },
  "characters": [
    {
      "name": "李寻欢",
      "role": "主角",
      "personality": "...",
      "background": "..."
    }
  ],
  "relationships": [
    {"from": "李寻欢", "to": "林诗音", "type": "恋人", "description": "..."}
  ],
  "structure": {
    "acts": [...],
    "beats": [...]
  },
  "foreshadowing": [...]
}
```

### TransformedOutline（新大纲）
```python
{
  "world_view": {...},
  "story_outline": {...},
  "character_cards": [...],
  "chapters": [
    {
      "chapter_num": 1,
      "title": "归来",
      "goal": "...",
      "key_events": [...],
      "characters": [...],
      "foreshadowing": [...]
    }
  ]
}
```

### StateTracker（状态追踪器）
```python
{
  "chapter": 5,
  "character_states": {
    "林风": {
      "location": "深圳",
      "emotion": "激动",
      "condition": "健康",
      "items": ["iPhone 15 Pro Max"]
    }
  },
  "relationships": {
    "林风->林薇": {"trust": 80, "affection": 60, "hostility": 0}
  },
  "foreshadowing": {
    "active": [...],
    "resolved": [...]
  },
  "timeline": [...],
  "known_info": {
    "林风": ["未来知识", "2010-2035年科技发展"]
  }
}
```

---

## 🔄 调用链示例

### 完整流程调用链

```
run_all.py
  ↓
test_phase1_full.py
  ↓
phase1_analyzer.py
  ├→ NovelSplitter.split()
  ├→ ChapterSummarizer.summarize() × N章
  ├→ RecursiveSummarizer.summarize()
  ├→ GlobalAnalyzer.analyze()
  └→ 保存 novel_skeleton.json
       ↓
test_phase2.py
  ↓
phase2_transformer.py
  ├→ WorldMapper.map()
  ├→ CharacterMapper.map()
  ├→ BeatMapper.map()
  ├→ OutlineExpander.expand()
  └→ 保存 transformed_outline.json
       ↓
test_phase3.py
  ↓
phase3_generator.py
  ├→ MemoryRetriever.retrieve()
  ├→ EnhancedChapterGenerator.generate()
  │   ├→ LLM调用
  │   ├→ QualityChecker.check()
  │   └→ [可选] 重试 × 2
  ├→ TransitionOptimizer.optimize()
  ├→ StateTracker.update_from_chapter()
  └→ 保存 chapter_*.txt + state.json
```

---

## 💡 关键设计模式

### 1. 分而治之（递归摘要）
```
问题：小说太长，上下文窗口不够
解决：分层摘要，每一层综合上一层的信息
```

### 2. 状态机（状态追踪器）
```
问题：需要记住之前发生了什么
解决：用状态机追踪所有变化，每章更新
```

### 3. 记忆检索（记忆系统）
```
问题：生成当前章需要知道相关历史
解决：根据当前章需求，从状态中检索相关记忆
```

### 4. 质量反馈（质量检查+重试）
```
问题：LLM输出质量不稳定
解决：生成后检查，不合格就重试，带上次问题
```

---

## 📝 快速开始

### 跑通完整流程（旧版）

```python
# 1. 配置API密钥
export DEEPSEEK_API_KEY="your-key"

# 2. 运行Phase1
python scripts/test_phase1_full.py

# 3. 运行Phase2
python scripts/test_phase2.py

# 4. 运行Phase3
python scripts/test_phase3.py

# 5. 或者一键运行所有
python scripts/run_all.py
```

### 生成单章

```python
from scripts.phase3_generator import EnhancedChapterGenerator
from src.core import create_llm_adapter, StateTracker

# 初始化
llm = create_llm_adapter()
state_tracker = StateTracker()

# 生成
generator = EnhancedChapterGenerator(llm)
chapter_text, report = generator.generate(chapter_num=1, outline=...)

# 保存
with open("chapter_1.txt", "w", encoding="utf-8") as f:
    f.write(chapter_text)
```

---

*文档创建：2026-03-13*
