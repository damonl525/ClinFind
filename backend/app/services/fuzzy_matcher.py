"""
模糊搜索引擎模块 (Ported from V2.1)
支持拼音搜索、容错搜索和智能匹配
"""

import re
from typing import List, Dict, Tuple, Any, Optional

try:
    import pypinyin
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False
    print("警告: pypinyin库未安装，拼音搜索功能将不可用")

class FuzzySearchEngine:
    """模糊搜索引擎，支持拼音搜索、容错搜索和智能匹配"""
    
    def __init__(self):
        self.common_errors = {
            # 常见的拼写错误映射
            'excel': ['execl', 'exel', 'exle'],
            'word': ['wrod', 'wrold', 'worrd'],
            'powerpoint': ['ppt', 'pptx', 'powerpiont'],
            'document': ['doc', 'docx', 'documnet'],
            'presentation': ['pres', 'presen', 'presn'],
            'spreadsheet': ['spread', 'spredsheet', 'sprd'],
            '文档': ['文件', '档案', '文本'],
            '表格': ['表单', '工作表', '电子表格'],
            '幻灯片': ['演示文稿', '演示', 'PPT'],
        }
        
        # 同义词映射
        self.synonyms = {
            'excel': ['表格', '工作表', 'xls', 'xlsx', '电子表格'],
            'word': ['文档', 'doc', 'docx', '文本'],
            'powerpoint': ['幻灯片', 'ppt', 'pptx', '演示文稿'],
            'document': ['文档', '文件', '档案'],
            'presentation': ['演示', '幻灯片', '讲演'],
            '文档': ['document', 'doc', 'docx', '文件'],
            '表格': ['excel', 'xls', 'xlsx', '电子表格'],
            '幻灯片': ['powerpoint', 'ppt', 'pptx', '演示文稿'],
        }
    
    def text_to_pinyin(self, text: str) -> str:
        """将中文文本转换为拼音"""
        if not PYPINYIN_AVAILABLE:
            return text
        
        try:
            # 转换为拼音，不带声调
            pinyin_list = pypinyin.lazy_pinyin(text, style=pypinyin.NORMAL)
            return ''.join(pinyin_list)
        except Exception as e:
            print(f"拼音转换错误: {str(e)}")
            return text
    
    def get_pinyin_variations(self, text: str) -> List[str]:
        """获取文本的拼音变体"""
        if not PYPINYIN_AVAILABLE:
            return [text]
        
        variations = [text]
        
        # 如果文本包含中文字符，添加拼音变体
        if re.search(r'[\u4e00-\u9fff]', text):
            pinyin = self.text_to_pinyin(text)
            if pinyin != text:
                variations.append(pinyin)
                
                # 添加首字母缩写
                initials = ''.join([p[0] if p else '' for p in pypinyin.lazy_pinyin(text, style=pypinyin.NORMAL)])
                if initials:
                    variations.append(initials)
        
        return variations
    
    def expand_query(self, query: str) -> List[str]:
        """扩展查询词：包括同义词、拼音变体等"""
        query = query.lower().strip()
        expanded_terms = {query}
        
        # 1. 常见错误纠正
        for correct, errors in self.common_errors.items():
            if query in errors:
                expanded_terms.add(correct)
        
        # 2. 同义词扩展
        # 先检查原始查询
        if query in self.synonyms:
            expanded_terms.update(self.synonyms[query])
        
        # 再检查纠正后的词
        current_terms = list(expanded_terms)
        for term in current_terms:
            if term in self.synonyms:
                expanded_terms.update(self.synonyms[term])
                
        # 3. 拼音扩展 (仅当查询包含中文时)
        if re.search(r'[\u4e00-\u9fff]', query):
            variations = self.get_pinyin_variations(query)
            expanded_terms.update(variations)
            
        return list(expanded_terms)
