"""
健壮的 JSON 解析器
处理 LLM 返回的 JSON 常见问题
"""
import json
import re
from typing import Any, Dict, Optional, Tuple


def extract_json_block(text: str) -> Optional[str]:
    """
    从文本中提取 ```json ... ``` 代码块
    
    Args:
        text: LLM 返回的原始文本
        
    Returns:
        提取出的 JSON 字符串，或 None
    """
    # 尝试匹配 ```json ... ```
    pattern = r'```json\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 尝试匹配 ``` ... ``` (不带 json 标记)
    pattern = r'```\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return None


def fix_common_json_issues(json_str: str) -> str:
    """
    修复 JSON 常见问题
    
    Args:
        json_str: 可能有问题的 JSON 字符串
        
    Returns:
        修复后的 JSON 字符串
    """
    result = json_str
    
    # 1. 替换中文引号为英文引号
    result = result.replace('"', '"').replace('"', '"')
    result = result.replace(''', "'").replace(''', "'")
    
    # 2. 移除行尾注释 (// ...)
    result = re.sub(r'//.*$', '', result, flags=re.MULTILINE)
    
    # 3. 移除块注释 (/* ... */)
    result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
    
    # 4. 修复尾部多余逗号
    # 在对象中
    result = re.sub(r',\s*([}\]])', r'\1', result)
    # 在数组中
    result = re.sub(r',\s*([}\]])', r'\1', result)
    
    # 5. 尝试截取第一个 { 到最后一个 }
    if '{' in result and '}' in result:
        start = result.find('{')
        end = result.rfind('}') + 1
        result = result[start:end]
    
    return result


def parse_json_safely(text: str, max_retries: int = 3) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    安全解析 JSON，包含修复和重试机制
    
    Args:
        text: LLM 返回的原始文本
        max_retries: 最大重试次数
        
    Returns:
        (解析后的字典, 错误信息)
        成功时错误信息为 None
        失败时字典为 None
    """
    current_text = text
    
    for attempt in range(max_retries):
        # Step 1: 提取 JSON 块
        json_str = extract_json_block(current_text)
        if json_str is None:
            # 如果没有代码块，假设整个文本就是 JSON
            json_str = current_text
        
        # Step 2: 修复常见问题
        fixed_json = fix_common_json_issues(json_str)
        
        # Step 3: 尝试解析
        try:
            result = json.loads(fixed_json)
            return result, None
        except json.JSONDecodeError as e:
            error_msg = f"解析失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
            
            if attempt < max_retries - 1:
                # 不是最后一次尝试，准备重新生成的 prompt
                current_text = f"""
之前返回的 JSON 格式有错误：
{fixed_json}

错误信息：{str(e)}

请重新生成正确的 JSON，只输出 JSON，不要添加其他文字。
"""
            else:
                return None, error_msg
    
    return None, "达到最大重试次数"


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    简单的 JSON Schema 验证
    
    Args:
        data: 要验证的数据
        schema:  Schema 定义
        
    Returns:
        (是否有效, 错误信息)
    """
    # 检查必需字段
    if 'required' in schema:
        for field in schema['required']:
            if field not in data:
                return False, f"缺少必需字段: {field}"
    
    # 检查字段类型
    if 'properties' in schema:
        for field, field_schema in schema['properties'].items():
            if field in data:
                expected_type = field_schema.get('type')
                actual_type = type(data[field]).__name__
                
                # 简单的类型映射
                type_mapping = {
                    'string': ['str'],
                    'number': ['int', 'float'],
                    'integer': ['int'],
                    'boolean': ['bool'],
                    'array': ['list'],
                    'object': ['dict']
                }
                
                if expected_type in type_mapping:
                    if actual_type not in type_mapping[expected_type]:
                        return False, f"字段 {field} 类型错误，期望 {expected_type}，实际 {actual_type}"
    
    return True, None
