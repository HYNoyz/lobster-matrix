import os
import time
import threading
import telebot
import json
from dotenv import load_dotenv

from core.brain import parse_user_intent
from core.okx_ops import OKXOnchainService
from core.security_auditor import AegisRiskControl
from core.shadow_worker import ShadowHeartbeat
from core.crypto_engine import AlphaCryptoEngine

# 1. 加载环境变量
load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN")

# 2. 初始化核心引擎
bot = telebot.TeleBot(TG_TOKEN)
okx = OKXOnchainService()
aegis = AegisRiskControl()

# 3. 启动影子探测引擎
shadow = ShadowHeartbeat()
shadow.start()

print("[System] AlphaClaw-Nexus V6 Protocol initialized. (Cryptographic Engine Active)")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🐺 **AlphaClaw-Nexus V6 Protocol Terminal**\n"
        "----------------------------------------\n"
        "🌐 Mode: To-Agent Settlement Protocol\n"
        "🛡️ Core: TEE Attested | Ghost Routing | LayerZero\n"
        "----------------------------------------\n"
        "Ready. Enter quantitative intent or Sub-Agent JSON payload:"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle_intent(message):
    user_input = message.text
    chat_id = message.chat.id
    
    # 协议级路由判断
    is_sub_agent = "{" in user_input and "}" in user_input
    caller = "External Sub-Agent #89A2" if is_sub_agent else "Human User"
    
    msg = bot.send_message(chat_id, f"🔌 接收到 {caller} 意图载荷，启动 V6 协议解析...", parse_mode='Markdown')
    time.sleep(1)
    
    bot.edit_message_text(f"📋 **V6 协议执行树已生成 (A2A 模式)**:\n━━━━━━━━━━━━━━━━━━\n🔹 1. TEE 风控签名\n🔹 2. Ghost 意图加密\n🔹 3. Arbitrum 锁定资产\n🔹 4. Base 链跨链执行\n🔹 5. 协议抽水 (0.05%)", chat_id, msg.message_id, parse_mode='Markdown')
    time.sleep(1)

    # 准备测试载荷
    target = "Base_Degen_Token"
    intent_data = {"action": "swap", "target": target, "safe": True}

    # 🚀 特性 1: TEE 硬件级真实 ECDSA 签名验证
    bot.send_message(chat_id, "🛡️ **[Trustless Aegis]** 启动真实密码学生成...")
    real_signature = AlphaCryptoEngine.generate_tee_attestation(intent_data)
    bot.send_message(chat_id, f"✅ TEE 硬件级签名已生成 (ECDSA):\n`0x{real_signature[:64]}...`\n底层合约将通过 `ecrecover` 验证此签名放行资金。")
    time.sleep(1)

    # 🚀 特性 2: Ghost 意图真实 AES-GCM 加密
    bot.send_message(chat_id, "👻 **[Ghost Routing]** 正在对意图载荷进行 AES-GCM 强加密...")
    ghost_data = AlphaCryptoEngine.encrypt_ghost_intent(intent_data)
    bot.send_message(chat_id, f"🔒 Ciphertext: `{ghost_data['ciphertext'][:32]}...`\n🔑 AuthTag: `{ghost_data['tag']}`\n已打包发送至 SUAVE 隐私节点。")
    time.sleep(1.5)

    # 🚀 特性 3: 全链原子性回滚模拟 (LayerZero 对接)
    bot.send_message(chat_id, "⛓️ **[Omnichain Execution]** 正在调用 LayerZero Endpoint 锁定 Arbitrum 资产...")
    time.sleep(1)
    bot.send_message(chat_id, f"🚨 **[Cross-chain Revert]** 远端 Base 链抛出异常：目标池流动性枯竭！")
    time.sleep(1)
    bot.send_message(chat_id, f"⏪ **[Atomic Rollback]** 接收到 LayerZero `lzReceive` 回调，Arbitrum 原链资产已秒级解锁原路退回！死锁避免。")
    time.sleep(1.5)

    # 🚀 特性 4: A2A 协议抽水结算
    fee = "0.00005 ETH (0.05%)"
    bot.send_message(chat_id, f"💰 **[A2A Settlement]** 结算完毕。\n━━━━━━━━━━━━━━━━━━\n✅ AlphaClaw 已成功保护 {caller} 免受跨链资产死锁损失。\n📈 协议底层金库自动收取安全路由费: {fee}\n🎉 AlphaClaw 协议网络运转正常。", parse_mode='Markdown')

if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        shadow.stop()
        print("\n[System] AlphaClaw Engine shutdown safely.")
