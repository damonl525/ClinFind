"""
搜索精度控制器 (Ported from V2.1)
提供多级精度设置和内容质量过滤
"""

import re
import string
from typing import List, Dict, Tuple, Optional
from enum import Enum

class PrecisionLevel(str, Enum):
    """搜索精度级别"""
    EXACT = "exact"           # 精确匹配
    HIGH = "high"             # 高精度
    MEDIUM = "medium"         # 中等精度
    LOOSE = "loose"           # 宽松匹配
    VERY_LOOSE = "very_loose" # 低精度

class SearchPrecisionController:
    """搜索精度控制器"""
    
    def __init__(self):
        # 精度级别对应的阈值 (for reference, mostly used in fuzzy matching)
        self.precision_thresholds = {
            PrecisionLevel.EXACT: 90,
            PrecisionLevel.HIGH: 80,
            PrecisionLevel.MEDIUM: 70,
            PrecisionLevel.LOOSE: 60,
            PrecisionLevel.VERY_LOOSE: 50
        }
        
        # 内容质量过滤规则
        self.quality_filters = {
            'min_length': 2,           # 最小长度
            'max_special_char_ratio': 0.4,  # 特殊字符比例上限
            'min_alpha_ratio': 0.4,    # 字母/汉字比例下限
            'blacklist_patterns': [    # 黑名单模式
                r'^[^\w\u4e00-\u9fff]+$',  # 只包含特殊符号
                r'^[0-9\s\.\-_]+$',        # 只包含数字和基本符号
                r'^[a-zA-Z]{1,2}$',        # 单个或两个字母 (too short)
                r'^\W{1,3}$',              # 1-3个非单词字符
                r'^[^\w\u4e00-\u9fff\s]{1,5}$',  # 1-5个非字母数字汉字字符
                r'^[a-zA-Z]\W*$',          # 单个字母后跟特殊字符
                r'^\W*[a-zA-Z]\W*$',       # 被特殊字符包围的单个字母
            ]
        }
    
    def get_threshold(self, precision_level: PrecisionLevel) -> int:
        """获取精度级别对应的阈值"""
        return self.precision_thresholds.get(precision_level, 70)
    
    def is_content_quality_acceptable(self, content: str) -> bool:
        """
        检查内容质量是否可接受
        
        Args:
            content: 要检查的内容
            
        Returns:
            是否通过质量检查
        """
        if not content or not content.strip():
            return False
        
        content = content.strip()
        
        # 长度检查
        if len(content) < self.quality_filters['min_length']:
            return False
        
        # 专门检查"u("这样的模式
        if re.match(r'^[a-zA-Z]\W+$', content):  # 单个字母后跟特殊字符
            return False
        
        # 检查是否主要由特殊字符组成（如"u(", "a)", "x!"等）
        if len(content) <= 3:
            alpha_count = sum(1 for c in content if c.isalpha())
            special_count = sum(1 for c in content if c in string.punctuation)
            if alpha_count <= 1 and special_count >= 1:
                return False
        
        # 黑名单模式检查
        for pattern in self.quality_filters['blacklist_patterns']:
            if re.match(pattern, content):
                return False
                
        return True
