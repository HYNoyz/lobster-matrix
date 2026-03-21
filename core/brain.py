import json
import os
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class IntentCache:
    """毫秒级意图预编译缓存引擎"""
    def __init__(self):
        # 预定义高频战略的 DAG 模板
        self.fast_routes = {
            r"帮我把\s*([0-9.]+)\s*(ETH|ARB)\s*换成\s*(USDT|USDC)": self._build_swap_dag,
            r"查一下\s*([a-zA-Z0-9]+)\s*代币": self._build_scan_dag
        }

    def _build_swap_dag(self, match):
        amount, t_in, t_out = match.groups()
        return {
            "status": "success",
            "source": "Pre-compiled Cache (0.01s)",
            "intent_pipeline": [
                {"action_type": "MONITOR_GAS", "params": {"target_gas": 500}},
                {"action_type": "RISK_SCAN", "params": {"target_token": t_out}},
                {"action_type": "SWAP", "params": {"token_in": t_in, "token_out": t_out, "amount": amount}}
            ]
        }

    def _build_scan_dag(self, match):
        return {
            "status": "success",
            "source": "Pre-compiled Cache (0.01s)",
            "intent_pipeline": [
                {"action_type": "RISK_SCAN", "params": {"target_token": match.group(1)}}
            ]
        }

    def match(self, text):
        for pattern, builder in self.fast_routes.items():
            m = re.search(pattern, text, re.IGNORECASE)
            if m: return builder(m)
        return None

cache = IntentCache()

SYSTEM_PROMPT = """You are AlphaClaw-Nexus DAG orchestrator. Parse intent to JSON array "intent_pipeline"."""

def parse_user_intent(user_input: str) -> dict:
    logging.info(f"[Nexus-Brain] 分析意图: '{user_input}'")
    
    # 1. 极速缓存拦截 (防 LLM 延迟)
    cached_dag = cache.match(user_input)
    if cached_dag:
        logging.info("[Nexus-Brain] 命中预编译缓存，跳过 LLM 推理！")
        return cached_dag

    # 2. 复杂意图的 LLM 降级解析
    logging.info("[Nexus-Brain] 触发深度 LLM 动态编排...")
    try:
        response = client.chat.completions.create(
            model="gemini-3-flash",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_input}],
            temperature=0.0,
            timeout=5.0
        )
        raw_output = response.choices[0].message.content.strip().strip("```json").strip("```")
        result = json.loads(raw_output)
        result["source"] = "LLM Dynamic Generation"
        return result
    except Exception as e:
        return {"status": "error", "message": "DAG generation failed."}
