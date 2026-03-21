# 🐺 AlphaClaw-Nexus: The Intent-Centric Onchain OS

**PRODUCTION READY INFRASTRUCTURE** | **ARBITRUM MAINNET VERIFIED**

AlphaClaw-Nexus 并非一个简单的对话 Bot，而是基于 **OKX Onchain OS** 构建的【全链攻防一体化意图引擎】。我们将大语言模型从“翻译官”升级为“DAG 调度器”，在底层融合了前置启发式安全沙盒与 OKX DEX 聚合路由。

## ⛓️ 主网实弹执行记录 (Live Mainnet Execution Proof)
本项目已完全脱离 Mock 阶段，具备真实的底层链上交互与 ECDSA 签名分发能力。
- **执行动作:** NLP 意图编译 -> Aegis 审计通过 -> 私钥签名 -> 智能合约底层交互
- **Mainnet TxHash:** `0x665a2ff1ce30d62d986c245a1a0387f960d4ca4558a80a1dbdcf24cf46349e98`
- **网络环境:** Arbitrum One Mainnet
- **状态:** 结算成功 (Settled)

## 🧠 核心架构解析 (Architecture)


系统在处理极度复杂的链上交互时，严格遵循以下三层隔离架构：
1. **Nexus Brain (意图编译层):** 接入 LLM，将用户的模糊战略指令（如“查 SCAM，安全就买”）动态编译为多维 JSON 执行树 (Intent-Pipeline)。
2. **Lobster Aegis (风控沙盒层):** 在触碰任何资产前，强制对目标代币进行静态代码特征分析。面对貔貅盘 (Honeypot) 等高危漏洞，直接触发“红色熔断”。
3. **Onchain OS (全链调度层):** 安全审计放行后，底层无缝衔接 OKX DEX Aggregator，自动穿透全网锁定最优流动性深度，并完成物理层的签名上链。

## 📂 主网级工程结构 (Directory Structure)
```text
AlphaClaw-Nexus/
├── core/
│   ├── brain.py            # DAG 意图流水线生成器
│   ├── okx_ops.py          # OKX 聚合器 API 与主网实弹发射模块
│   └── security_auditor.py # Aegis 预执行静态风控沙盒
├── bot.py                  # 异步多线程终端状态机
├── .gitignore
└── README.md
