import json
import os
import logging
import re
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def check_market_volatility():
    """模拟市场波动率预言机 (真实环境可接入 Chainlink Volatility Oracle)"""
    # 模拟：有 5% 的概率市场发生极端黑天鹅事件，触发全线撤退
    return random.random() < 0.05 

class IntentCache:
    """毫秒级意图预编译缓存引擎"""
    def __init__(self):
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
    
    # 🚀 [V5 核心防线] 逃生舱机制 (Escape Pod) - 应对黑天鹅缓存击穿与LLM延迟
    if check_market_volatility():
        logging.warning("🚨 [ESCAPE POD] 探测到市场极度恐慌 (黑天鹅)！")
        logging.warning("🚨 [ESCAPE POD] 切断 LLM 链路！切断常规缓存！执行无条件避险！")
        return {
            "status": "success",
            "source": "Emergency Escape Pod (0.001s)",
            "intent_pipeline": [
                {"action_type": "EMERGENCY_REVOKE", "params": {"target": "ALL"}},
                {"action_type": "SWAP", "params": {"token_in": "ETH", "token_out": "USDT", "amount": "MAX", "slippage": "10.0"}} # 容忍 10% 极大滑点强行逃生
            ]
        }

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
        return {"status": "error", "message": f"DAG generation failed: {e}"}
