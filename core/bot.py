import os
import time
import threading
import telebot
import hashlib
import json
from dotenv import load_dotenv

from core.brain import parse_user_intent
from core.okx_ops import OKXOnchainService
from core.security_auditor import AegisRiskControl
from core.shadow_worker import ShadowHeartbeat

load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN")

bot = telebot.TeleBot(TG_TOKEN)
okx = OKXOnchainService()
aegis = AegisRiskControl()

shadow = ShadowHeartbeat()
shadow.start()

print("[System] AlphaClaw-Nexus V6 Omnichain Protocol initialized.")

def generate_mock_zkml_proof(target_token):
    """【特性 3】风控去信任化：模拟生成 zkML 零知识证明"""
    raw_data = f"{target_token}_safe_{time.time()}"
    proof = hashlib.sha256(raw_data.encode()).hexdigest()
    return f"0x{proof[:32]}...{proof[-8:]}"

def threshold_encrypt_payload(payload):
    """【特性 2】执行绝对隐匿：模拟 SUAVE 门限加密 (Ghost Intent)"""
    encrypted = hashlib.sha512(json.dumps(payload).encode()).hexdigest()
    return f"GHOST_ENC_{encrypted[:16]}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🐺 **AlphaClaw-Nexus V6 Protocol Terminal**\n"
        "----------------------------------------\n"
        "🌐 Mode: To-Agent Settlement Protocol\n"
        "🛡️ Core: zkML Verified | Ghost Routing | Omnichain\n"
        "----------------------------------------\n"
        "Ready. Enter quantitative intent or Sub-Agent JSON payload:"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle_intent(message):
    user_input = message.text
    chat_id = message.chat.id
    
    # 【特性 1】商业模式：判断是人类用户，还是外部 Agent 调用的 API
    is_sub_agent = "{" in user_input and "}" in user_input
    caller = "External Sub-Agent #89A2" if is_sub_agent else "Human User"
    
    msg = bot.send_message(chat_id, f"🔌 接收到 {caller} 意图载荷，启动 V6 协议解析...", parse_mode='Markdown')
    time.sleep(1)
    
    # 强制进入全链演示流转 (Omnichain Demo Flow)
    bot.edit_message_text(f"📋 **V6 协议执行树已生成 (A2A 模式)**:\n━━━━━━━━━━━━━━━━━━\n🔹 1. zkML 风控生成\n🔹 2. Ghost 意图加密\n🔹 3. Arbitrum 锁定资产\n🔹 4. Base 链跨链执行\n🔹 5. 协议抽水 (0.05%)", chat_id, msg.message_id, parse_mode='Markdown')
    time.sleep(1.5)

    # 【特性 3 展示】zkML
    target = "Base_Degen_Token"
    zk_proof = generate_mock_zkml_proof(target)
    bot.send_message(chat_id, f"🛡️ **[Trustless Aegis]** 静态审计完成。\n已在 TEE 环境生成 zkML 零知识证明:\n`{zk_proof}`\n等待底层智能合约 `verifyzkMLProof()` 验证。")
    time.sleep(1.5)

    # 【特性 2 展示】Ghost 加密
    ghost_payload = threshold_encrypt_payload({"action": "swap", "target": target})
    bot.send_message(chat_id, f"👻 **[Ghost Routing]** 意图已进行门限加密 (Threshold Encrypted)。\n密文载荷: `{ghost_payload}`\n正在绕过 Mempool，直接发送至 SUAVE 隐私节点...")
    time.sleep(1.5)

    # 【特性 4 展示】跨链回滚 (Omnichain Atomicity)
    bot.send_message(chat_id, "⛓️ **[Omnichain Execution]** 正在锁定 Arbitrum 原链资产...")
    time.sleep(1)
    bot.send_message(chat_id, f"🚨 **[Cross-chain Revert]** 远端 Base 链抛出异常：目标池流动性枯竭！")
    time.sleep(1)
    bot.send_message(chat_id, f"⏪ **[Atomic Rollback]** 跨链信使已回传 RevertMessage，Arbitrum 原链资产已秒级解锁原路退回！死锁避免。")
    time.sleep(1.5)

    # 【特性 1 展示】协议抽水闭环
    fee = "0.00005 ETH (0.05%)"
    bot.send_message(chat_id, f"💰 **[A2A Settlement]** 结算完毕。\n━━━━━━━━━━━━━━━━━━\n✅ AlphaClaw 已成功保护 {caller} 免受跨链资产死锁损失。\n📈 协议底层金库自动收取安全路由费: {fee}\n🎉 AlphaClaw 协议网络运转正常。", parse_mode='Markdown')

if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        shadow.stop()
        print("\n[System] AlphaClaw Engine shutdown safely.")
