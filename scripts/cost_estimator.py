"""
成本估算器
估算 LLM 调用的成本
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class ModelPricing:
    """模型定价"""
    model_name: str
    input_price_per_1k: float  # 输入价格，每1k tokens
    output_price_per_1k: float  # 输出价格，每1k tokens
    currency: str = "CNY"


# 预定义的模型定价
DEFAULT_PRICING = {
    # 火山引擎豆包系列
    "doubao-seed-2.0-code": ModelPricing(
        "doubao-seed-2.0-code",
        input_price_per_1k=0.004,
        output_price_per_1k=0.012
    ),
    "doubao-seed-2.0-pro": ModelPricing(
        "doubao-seed-2.0-pro",
        input_price_per_1k=0.008,
        output_price_per_1k=0.024
    ),
    "doubao-seed-2.0-lite": ModelPricing(
        "doubao-seed-2.0-lite",
        input_price_per_1k=0.002,
        output_price_per_1k=0.006
    ),
    
    # 其他常见模型
    "gpt-4o-mini": ModelPricing(
        "gpt-4o-mini",
        input_price_per_1k=0.00105,
        output_price_per_1k=0.0042
    ),
    "gpt-4o": ModelPricing(
        "gpt-4o",
        input_price_per_1k=0.021,
        output_price_per_1k=0.084
    ),
    "deepseek-chat": ModelPricing(
        "deepseek-chat",
        input_price_per_1k=0.0005,
        output_price_per_1k=0.002
    )
}


@dataclass
class CostEstimate:
    """成本估算结果"""
    model_name: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_input_cost: float
    estimated_output_cost: float
    total_estimated_cost: float
    currency: str = "CNY"
    notes: str = ""


@dataclass
class UsageRecord:
    """使用记录"""
    model_name: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: str
    operation: str  # "chapter_summary", "character_analysis", "chapter_generation", etc.


class CostEstimator:
    """成本估算器"""
    
    def __init__(self, config: dict = None, pricing_file: str = None):
        self.pricing: Dict[str, ModelPricing] = DEFAULT_PRICING.copy()
        self.usage_history: List[UsageRecord] = []
        self.usage_file = None
        
        # 加载配置
        if config:
            self.load_config(config)
        
        # 加载自定义定价
        if pricing_file and os.path.exists(pricing_file):
            self.load_pricing(pricing_file)
        
        # 设置使用记录文件
        if config:
            usage_dir = os.path.join(os.path.dirname(__file__), "data", "usage")
            os.makedirs(usage_dir, exist_ok=True)
            self.usage_file = os.path.join(usage_dir, "usage_history.json")
            self._load_usage_history()
    
    def load_config(self, config: dict):
        """从配置加载"""
        # 可以从配置中自定义定价
        pass
    
    def load_pricing(self, pricing_file: str):
        """从文件加载自定义定价"""
        with open(pricing_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for model_name, pricing_data in data.items():
            self.pricing[model_name] = ModelPricing(
                model_name=model_name,
                input_price_per_1k=pricing_data.get("input_price_per_1k", 0),
                output_price_per_1k=pricing_data.get("output_price_per_1k", 0),
                currency=pricing_data.get("currency", "CNY")
            )
    
    def _load_usage_history(self):
        """加载使用历史"""
        if self.usage_file and os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.usage_history = [
                    UsageRecord(**record)
                    for record in data.get("history", [])
                ]
            except Exception:
                pass
    
    def _save_usage_history(self):
        """保存使用历史"""
        if self.usage_file:
            data = {
                "history": [asdict(r) for r in self.usage_history],
                "total_cost": self.get_total_cost(),
                "last_updated": ""  # TODO: 添加时间戳
            }
            
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def estimate_operation(
        self,
        model_name: str,
        operation: str,
        prompt_length: int,
        estimated_output_length: int = None
    ) -> CostEstimate:
        """
        估算单次操作的成本
        
        Args:
            model_name: 模型名称
            operation: 操作类型
            prompt_length: 提示词长度（字符数，估算token）
            estimated_output_length: 预估输出长度（字符数）
            
        Returns:
            成本估算结果
        """
        # 简单估算：中文字符 ≈ 0.7 tokens
        estimated_input_tokens = int(prompt_length * 0.7)
        
        if estimated_output_length is None:
            # 根据操作类型预估输出长度
            operation_output_estimates = {
                "chapter_summary": 500,
                "character_analysis": 1500,
                "world_mapping": 800,
                "character_mapping": 1200,
                "beat_mapping": 1000,
                "chapter_outline": 2000,
                "chapter_generation": 4000,
                "quality_check": 500,
                "transition_optimize": 400
            }
            estimated_output_length = operation_output_estimates.get(operation, 1000)
        
        estimated_output_tokens = int(estimated_output_length * 0.7)
        
        # 获取定价
        pricing = self.pricing.get(model_name)
        if pricing is None:
            # 默认使用豆包的定价
            pricing = self.pricing.get("doubao-seed-2.0-code", 
                ModelPricing(model_name, 0.004, 0.012)
            )
        
        # 计算成本
        input_cost = (estimated_input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (estimated_output_tokens / 1000) * pricing.output_price_per_1k
        total_cost = input_cost + output_cost
        
        return CostEstimate(
            model_name=model_name,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            estimated_input_cost=input_cost,
            estimated_output_cost=output_cost,
            total_estimated_cost=total_cost,
            currency=pricing.currency,
            notes=f"操作类型: {operation}"
        )
    
    def estimate_phase1(self, model_name: str, num_chapters: int = 100) -> CostEstimate:
        """
        估算 Phase 1 的成本
        
        Args:
            model_name: 模型名称
            num_chapters: 章节数
            
        Returns:
            成本估算结果
        """
        total_input = 0
        total_output = 0
        
        # 逐章摘要
        total_input += num_chapters * 10000  # 每章约1万字
        total_output += num_chapters * 500
        
        # 递归摘要（假设每10章一组）
        num_groups = num_chapters // 10
        total_input += num_groups * 5000
        total_output += num_groups * 800
        
        # 全局分析
        total_input += 10000
        total_output += 3000
        
        # 估算成本
        pricing = self.pricing.get(model_name, 
            ModelPricing(model_name, 0.004, 0.012)
        )
        
        input_tokens = int(total_input * 0.7)
        output_tokens = int(total_output * 0.7)
        
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        total_cost = input_cost + output_cost
        
        return CostEstimate(
            model_name=model_name,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_input_cost=input_cost,
            estimated_output_cost=output_cost,
            total_estimated_cost=total_cost,
            currency=pricing.currency,
            notes=f"Phase 1 估算: {num_chapters} 章"
        )
    
    def estimate_phase2(self, model_name: str) -> CostEstimate:
        """
        估算 Phase 2 的成本
        
        Args:
            model_name: 模型名称
            
        Returns:
            成本估算结果
        """
        total_input = 0
        total_output = 0
        
        # 世界观映射
        total_input += 2000
        total_output += 800
        
        # 角色映射
        total_input += 3000
        total_output += 1200
        
        # 剧情节拍映射
        total_input += 3000
        total_output += 1000
        
        # 章节大纲展开（20章）
        total_input += 5000
        total_output += 3000
        
        # 估算成本
        pricing = self.pricing.get(model_name, 
            ModelPricing(model_name, 0.004, 0.012)
        )
        
        input_tokens = int(total_input * 0.7)
        output_tokens = int(total_output * 0.7)
        
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        total_cost = input_cost + output_cost
        
        return CostEstimate(
            model_name=model_name,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_input_cost=input_cost,
            estimated_output_cost=output_cost,
            total_estimated_cost=total_cost,
            currency=pricing.currency,
            notes="Phase 2 估算"
        )
    
    def estimate_phase3(self, model_name: str, num_chapters: int = 20) -> CostEstimate:
        """
        估算 Phase 3 的成本
        
        Args:
            model_name: 模型名称
            num_chapters: 章节数
            
        Returns:
            成本估算结果
        """
        total_input = 0
        total_output = 0
        
        # 每章生成 + 质量检查 + 重试
        per_chapter_input = 6000  # 提示词
        per_chapter_output = 4000  # 生成
        
        # 假设平均重试1次
        total_input += num_chapters * per_chapter_input * 1.5
        total_output += num_chapters * per_chapter_output * 1.5
        
        # 估算成本
        pricing = self.pricing.get(model_name, 
            ModelPricing(model_name, 0.004, 0.012)
        )
        
        input_tokens = int(total_input * 0.7)
        output_tokens = int(total_output * 0.7)
        
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        total_cost = input_cost + output_cost
        
        return CostEstimate(
            model_name=model_name,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_input_cost=input_cost,
            estimated_output_cost=output_cost,
            total_estimated_cost=total_cost,
            currency=pricing.currency,
            notes=f"Phase 3 估算: {num_chapters} 章"
        )
    
    def record_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        operation: str
    ):
        """
        记录使用情况
        
        Args:
            model_name: 模型名称
            input_tokens: 输入 tokens
            output_tokens: 输出 tokens
            operation: 操作类型
        """
        pricing = self.pricing.get(model_name, 
            ModelPricing(model_name, 0.004, 0.012)
        )
        
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        total_cost = input_cost + output_cost
        
        record = UsageRecord(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=total_cost,
            timestamp="",  # TODO: 添加时间戳
            operation=operation
        )
        
        self.usage_history.append(record)
        self._save_usage_history()
    
    def get_total_cost(self) -> float:
        """获取总成本"""
        return sum(r.cost for r in self.usage_history)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """获取使用摘要"""
        total_cost = self.get_total_cost()
        total_input_tokens = sum(r.input_tokens for r in self.usage_history)
        total_output_tokens = sum(r.output_tokens for r in self.usage_history)
        
        # 按操作类型统计
        by_operation = {}
        for record in self.usage_history:
            if record.operation not in by_operation:
                by_operation[record.operation] = {
                    "count": 0,
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            
            by_operation[record.operation]["count"] += 1
            by_operation[record.operation]["cost"] += record.cost
            by_operation[record.operation]["input_tokens"] += record.input_tokens
            by_operation[record.operation]["output_tokens"] += record.output_tokens
        
        return {
            "total_cost": total_cost,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_records": len(self.usage_history),
            "by_operation": by_operation
        }
    
    def print_estimate(self, estimate: CostEstimate):
        """打印估算结果"""
        print("\n" + "=" * 60)
        print("成本估算")
        print("=" * 60)
        print(f"模型: {estimate.model_name}")
        print(f"预估输入 tokens: {estimate.estimated_input_tokens:,}")
        print(f"预估输出 tokens: {estimate.estimated_output_tokens:,}")
        print(f"输入成本: {estimate.estimated_input_cost:.4f} {estimate.currency}")
        print(f"输出成本: {estimate.estimated_output_cost:.4f} {estimate.currency}")
        print(f"总成本: {estimate.total_estimated_cost:.4f} {estimate.currency}")
        if estimate.notes:
            print(f"备注: {estimate.notes}")
        print("=" * 60)


# 全局实例
_global_cost_estimator: Optional[CostEstimator] = None


def get_cost_estimator(config: dict = None) -> CostEstimator:
    """获取全局成本估算器"""
    global _global_cost_estimator
    if _global_cost_estimator is None:
        _global_cost_estimator = CostEstimator(config)
    return _global_cost_estimator


def set_cost_estimator(estimator: CostEstimator) -> None:
    """设置全局成本估算器"""
    global _global_cost_estimator
    _global_cost_estimator = estimator
