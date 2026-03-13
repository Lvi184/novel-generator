"""
测试基础设施模块
- Prompt 管理器
- 成本估算器
"""
import json
import os
import sys

# 导入模块
from prompts import get_prompt_manager
from cost_estimator import get_cost_estimator


def test_prompt_manager():
    """测试 Prompt 管理器"""
    print("\n" + "=" * 60)
    print("测试 Prompt 管理器")
    print("=" * 60)
    
    pm = get_prompt_manager()
    
    # 列出所有模板
    templates = pm.list_templates()
    print(f"\n可用模板 ({len(templates)} 个):")
    for i, name in enumerate(templates, 1):
        template = pm.get(name)
        print(f"  {i}. {name} - {template.description if template else ''}")
    
    # 测试格式化一个模板
    print("\n" + "-" * 60)
    print("测试模板格式化: chapter_summary")
    print("-" * 60)
    
    formatted = pm.format(
        "chapter_summary",
        title="第一章 测试",
        content="这是测试内容... " * 100
    )
    
    print(f"格式化后的模板长度: {len(formatted)} 字符")
    print(f"\n前300字符:\n{formatted[:300]}...")
    
    # 测试保存模板到文件
    print("\n" + "-" * 60)
    print("测试保存模板到文件")
    print("-" * 60)
    
    templates_dir = os.path.join(os.path.dirname(__file__), "prompts")
    os.makedirs(templates_dir, exist_ok=True)
    
    test_template = "chapter_generation"
    save_path = os.path.join(templates_dir, f"{test_template}.txt")
    pm.save_to_file(test_template, save_path)
    
    if os.path.exists(save_path):
        print(f"[OK] 模板已保存: {save_path}")
        print(f"  文件大小: {os.path.getsize(save_path)} 字节")
    
    print("\n[OK] Prompt 管理器测试完成！")


def test_cost_estimator():
    """测试成本估算器"""
    print("\n" + "=" * 60)
    print("测试成本估算器")
    print("=" * 60)
    
    # 读取配置
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    model_name = config.get("model_name", "doubao-seed-2.0-code")
    
    ce = get_cost_estimator(config)
    
    # 测试单次操作估算
    print("\n" + "-" * 60)
    print("测试单次操作估算")
    print("-" * 60)
    
    operations = [
        ("chapter_summary", 10000, 500),
        ("character_analysis", 5000, 1500),
        ("chapter_generation", 6000, 4000),
    ]
    
    for op_name, prompt_len, output_len in operations:
        estimate = ce.estimate_operation(
            model_name=model_name,
            operation=op_name,
            prompt_length=prompt_len,
            estimated_output_length=output_len
        )
        print(f"\n操作: {op_name}")
        print(f"  预估输入: {estimate.estimated_input_tokens:,} tokens")
        print(f"  预估输出: {estimate.estimated_output_tokens:,} tokens")
        print(f"  总成本: {estimate.total_estimated_cost:.4f} {estimate.currency}")
    
    # 测试 Phase 1/2/3 整体估算
    print("\n" + "-" * 60)
    print("测试 Phase 整体估算")
    print("-" * 60)
    
    # Phase 1
    print("\nPhase 1 估算 (100章):")
    phase1_est = ce.estimate_phase1(model_name, num_chapters=100)
    ce.print_estimate(phase1_est)
    
    # Phase 2
    print("\nPhase 2 估算:")
    phase2_est = ce.estimate_phase2(model_name)
    ce.print_estimate(phase2_est)
    
    # Phase 3
    print("\nPhase 3 估算 (20章):")
    phase3_est = ce.estimate_phase3(model_name, num_chapters=20)
    ce.print_estimate(phase3_est)
    
    # 总成本
    total = phase1_est.total_estimated_cost + phase2_est.total_estimated_cost + phase3_est.total_estimated_cost
    print(f"\n" + "=" * 60)
    print(f"预估总成本 (100章分析 + 20章生成): {total:.4f} {phase1_est.currency}")
    print("=" * 60)
    
    # 测试使用记录
    print("\n" + "-" * 60)
    print("测试使用记录")
    print("-" * 60)
    
    # 记录一些模拟使用
    ce.record_usage(
        model_name=model_name,
        input_tokens=7000,
        output_tokens=3500,
        operation="chapter_summary"
    )
    ce.record_usage(
        model_name=model_name,
        input_tokens=4200,
        output_tokens=840,
        operation="character_analysis"
    )
    ce.record_usage(
        model_name=model_name,
        input_tokens=4200,
        output_tokens=2800,
        operation="chapter_generation"
    )
    
    # 获取使用摘要
    summary = ce.get_usage_summary()
    print(f"\n总记录数: {summary['total_records']}")
    print(f"总输入 tokens: {summary['total_input_tokens']:,}")
    print(f"总输出 tokens: {summary['total_output_tokens']:,}")
    print(f"总成本: {summary['total_cost']:.4f}")
    
    print("\n按操作类型统计:")
    for op, data in summary['by_operation'].items():
        print(f"  {op}: {data['count']}次, {data['cost']:.4f}")
    
    print("\n✓ 成本估算器测试完成！")


def main():
    print("=" * 60)
    print("基础设施模块测试")
    print("=" * 60)
    
    # 测试 Prompt 管理器
    test_prompt_manager()
    
    # 测试成本估算器
    test_cost_estimator()
    
    print("\n" + "=" * 60)
    print("所有基础设施测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
