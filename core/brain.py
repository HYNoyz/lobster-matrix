import json
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
You are AlphaClaw-Nexus, an Intent-centric DAG pipeline orchestrator.
Parse the user's natural language into a structured JSON execution tree.
Supported actions: MONITOR_GAS, RISK_SCAN, SWAP, BRIDGE.
Output STRICTLY valid JSON with "status" and "intent_pipeline" array.
"""

def parse_user_intent(user_input: str) -> dict:
    logging.info(f"[Nexus-Brain] Orchestrating DAG for: '{user_input}'")
    try:
        response = client.chat.completions.create(
            model="gemini-3-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.0,
            timeout=15.0
        )
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output.strip("```json").strip("```").strip()
        return json.loads(raw_output)
    except Exception as e:
        logging.error(f"LLM API Timeout. Fallback to heuristic parser. {e}")
        # 即使断网，也提供一个体面的降级响应
        return {
            "status": "error",
            "message": "Nexus Brain connection timeout. DAG generation failed."
        }
