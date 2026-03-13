"""
LLM 调用缓存系统
避免重复调用相同的 prompt，节省成本
"""
import json
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class LLMCache:
    """LLM 调用缓存"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计信息
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_calls': 0
        }
    
    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            prompt: 提示词
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            缓存键 (SHA256 哈希)
        """
        # 把所有参数排序后序列化
        params = {
            'prompt': prompt,
            'model': model,
            **kwargs
        }
        
        # 序列化，确保键顺序一致
        param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
        
        # 生成 SHA256 哈希
        hash_obj = hashlib.sha256(param_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        # 使用两级目录避免单个目录文件过多
        return self.cache_dir / cache_key[:2] / f"{cache_key}.json"
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        从缓存获取结果
        
        Args:
            prompt: 提示词
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            缓存的结果，或 None
        """
        cache_key = self._get_cache_key(prompt, model, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        self.stats['total_calls'] += 1
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # 检查是否过期（默认 7 天）
                max_age = kwargs.get('cache_max_age', 7 * 24 * 3600)
                if time.time() - cache_data.get('timestamp', 0) < max_age:
                    self.stats['hits'] += 1
                    return cache_data.get('result')
            except Exception:
                pass
        
        self.stats['misses'] += 1
        return None
    
    def set(self, prompt: str, model: str, result: Any, **kwargs) -> None:
        """
        缓存结果
        
        Args:
            prompt: 提示词
            model: 模型名称
            result: 要缓存的结果
            **kwargs: 其他参数
        """
        cache_key = self._get_cache_key(prompt, model, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        # 确保目录存在
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        cache_data = {
            'timestamp': time.time(),
            'prompt': prompt,
            'model': model,
            'kwargs': kwargs,
            'result': result
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 缓存写入失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        hit_rate = 0.0
        if self.stats['total_calls'] > 0:
            hit_rate = self.stats['hits'] / self.stats['total_calls'] * 100
        
        return {
            **self.stats,
            'hit_rate': f"{hit_rate:.1f}%"
        }
    
    def clear(self, older_than_days: Optional[int] = None) -> int:
        """
        清理缓存
        
        Args:
            older_than_days: 只清理指定天数之前的缓存，None 表示全部清理
            
        Returns:
            清理的文件数量
        """
        count = 0
        cutoff_time = time.time() - (older_than_days * 24 * 3600) if older_than_days else None
        
        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                if cutoff_time is None:
                    cache_file.unlink()
                    count += 1
                else:
                    stat = cache_file.stat()
                    if stat.st_mtime < cutoff_time:
                        cache_file.unlink()
                        count += 1
            except Exception:
                pass
        
        return count


# 全局缓存实例
_global_cache: Optional[LLMCache] = None


def get_cache() -> LLMCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = LLMCache()
    return _global_cache


def set_cache(cache: LLMCache) -> None:
    """设置全局缓存实例"""
    global _global_cache
    _global_cache = cache
