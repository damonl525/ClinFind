import httpx
import logging
import json
import re

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, base_url: str, api_key: str, model: str = "gpt-3.5-turbo"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model

    async def _call_api(self, messages: list, temperature: float = 0.3, max_tokens: int = 200) -> str:
        """统一的 API 调用方法"""
        if not self.base_url or not self.api_key:
            raise ValueError("AI Configuration (Base URL or API Key) is missing.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        url = f"{self.base_url}/chat/completions"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"AI API Error: {response.text}")
                raise Exception(f"API 返回错误 {response.status_code}: {response.text[:200]}")
            
            data = response.json()
            
            # 尝试多种响应格式
            # 标准 OpenAI 格式
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                if 'message' in choice:
                    return choice['message'].get('content', '')
                elif 'text' in choice:
                    return choice['text']
            
            # 一些 API 直接返回 content
            if 'content' in data:
                return data['content']
            
            # 一些 API 返回 result
            if 'result' in data:
                return data['result']
            
            # 一些 API 返回 data.content
            if 'data' in data:
                if isinstance(data['data'], str):
                    return data['data']
                elif isinstance(data['data'], dict) and 'content' in data['data']:
                    return data['data']['content']
            
            # 如果都没有，记录完整响应并抛出错误
            logger.error(f"Unexpected API response format: {data}")
            raise Exception(f"API 响应格式不兼容。响应: {str(data)[:300]}")

    async def expand_query(self, query: str, custom_prompt: str = None) -> list[str]:
        """
        使用 AI 扩展搜索查询，生成相关词和同义词
        """
        # 使用自定义 prompt 或默认 prompt
        if custom_prompt:
            # 替换 {{query}} 占位符
            prompt = custom_prompt.replace("{{query}}", query)
        else:
            prompt = f"""你是一个专业的文档搜索助手。请为以下搜索关键词生成 3-5 个最相关的扩展词，帮助用户找到更多相关文档。

搜索词：{query}

扩展规则：
1. 优先生成该词在**专业领域**中的同义词（如医学、统计、法律、金融等）
2. 包含该词的**中英文对应词**
3. 包含该词的**常见缩写或全称**
4. 不要生成过于宽泛或偏离原意的词
5. 不要包含原始搜索词本身

示例：
- "样本" → ["sample", "样本量", "sample size", "受试者", "n值"]
- "随机" → ["randomization", "随机化", "random", "随机分配", "RCT"]
- "盲法" → ["blinding", "双盲", "单盲", "double-blind", "设盲"]

请只返回 JSON 数组格式，如 ["词1", "词2", "词3"]，不要其他解释。"""

        try:
            messages = [
                {"role": "system", "content": "你是专业的搜索关键词扩展助手。根据用户的搜索词，智能识别其所属领域，生成最相关的同义词和扩展词。只返回JSON数组。"},
                {"role": "user", "content": prompt}
            ]
            
            content = await self._call_api(messages, temperature=0.3, max_tokens=150)
            
            # 清理响应，提取 JSON 数组
            content = content.strip()
            # 移除 markdown 代码块标记
            content = re.sub(r'^```json?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            expanded_terms = json.loads(content)
            
            if isinstance(expanded_terms, list):
                # 过滤并限制数量
                expanded_terms = [str(t).strip() for t in expanded_terms if t]
                return expanded_terms[:5]
            
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"AI Query Expansion Failed: {e}")
            return []

    async def test_connection(self) -> dict:
        """测试 API 连接"""
        try:
            messages = [
                {"role": "user", "content": "回复'OK'"}
            ]
            await self._call_api(messages, max_tokens=10)
            return {"success": True, "message": "连接成功"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def explain_code(self, code_snippet: str, context: str = "") -> str:
        """
        Send code snippet to AI API for explanation.
        """
        if not self.base_url or not self.api_key:
            return "Error: AI Configuration (Base URL or API Key) is missing."

        prompt = f"请简要解释以下 {context} 代码的功能和逻辑：\n\n```\n{code_snippet}\n```"
        
        try:
            messages = [
                {"role": "system", "content": "You are a helpful coding assistant. Explain the code clearly in Chinese."},
                {"role": "user", "content": prompt}
            ]
            return await self._call_api(messages, max_tokens=500)
        except Exception as e:
            logger.error(f"AI Request Failed: {e}")
            return f"Error: Request failed - {str(e)}"

