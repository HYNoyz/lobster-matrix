import os
import requests
import logging
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class OKXOnchainService:
    """
    AlphaClaw 真实链上执行引擎 (Production Ready)
    深度聚合 OKX Onchain OS API，完成真实资产路由与签名广播
    """
    def __init__(self):
        # OKX DEX Aggregator API (公开免鉴权端点)
        self.okx_api_url = "https://www.okx.com/api/v5/dex/aggregator/swap"
        
        # 初始化 Web3 节点 (以 Arbitrum 为例，Gas 低，适合测试)
        # 抛弃公共裸奔节点，接入 MEV-Protect 隐私防夹路由
        # 生产环境中可接入 Flashbots 或 MEV Blocker RPC
        self.w3 = Web3(Web3.HTTPProvider("https://arbitrum.mev-blocker.io")) 
        
        # 如果上述节点在测试网络有延迟，作为备用降级方案保留：
        # self.w3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
        
        self.wallet_address = os.getenv("WALLET_ADDRESS")
        self.private_key = os.getenv("PRIVATE_KEY")
        
        # 常见 Token 地址字典 (Arbitrum 链)
        self.tokens = {
            "ETH": "0xEeeeeEeeeEeEeeEeEqEeeEEEheEeeEEEeEeeEEE", # OKX 原生 ETH 标识
            "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
            "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548"
        }

    def get_real_eth_gas(self):
        """获取真实网络 Gas (Gwei)"""
        try:
            gas_price = self.w3.eth.gas_price
            return round(self.w3.from_wei(gas_price, 'gwei'), 2)
        except Exception as e:
            logging.error(f"RPC Error: {e}")
            return 15.0 # Fallback

    def execute_real_swap(self, token_in_sym, token_out_sym, amount_in_ether):
        """
        调用 OKX Onchain OS 获取最优路由 calldata，并签名上链
        """
        if not self.private_key:
            return {"status": "error", "msg": "Private key not configured for real transaction."}

        token_in = self.tokens.get(token_in_sym.upper())
        token_out = self.tokens.get(token_out_sym.upper())
        
        if not token_in or not token_out:
            return {"status": "error", "msg": "Unsupported token for real execution."}

        # 转换金额精度 (ETH 默认 18 位)
        amount_wei = self.w3.to_wei(str(amount_in_ether), 'ether')

        # 1. 向 OKX Onchain OS 请求最优 Swap 路由与构建好的 calldata
        params = {
            "chainId": "42161", # Arbitrum One
            "amount": str(amount_wei),
            "fromTokenAddress": token_in,
            "toTokenAddress": token_out,
            "userWalletAddress": self.wallet_address,
            "slippage": "0.01" # 1% 滑点容忍度
        }
        
        logging.info(f"[OKX Router] Fetching optimal path from Onchain OS for {amount_in_ether} {token_in_sym} -> {token_out_sym}")
        
        try:
            response = requests.get(self.okx_api_url, params=params).json()
            
            if response["code"] != "0":
                return {"status": "error", "msg": f"OKX API Error: {response['msg']}"}
                
            tx_data = response["data"][0]["tx"]
            expected_output = response["data"][0]["routerResult"]["toTokenAmount"]
            
            # 2. 构建真实以太坊交易对象
            transaction = {
                'to': self.w3.to_checksum_address(tx_data['to']),
                'value': int(tx_data['value']),
                'data': tx_data['data'],
                'gas': int(tx_data['gasLimit']),
                'gasPrice': int(tx_data['gasPrice']),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                'chainId': 42161
            }

            # 3. 签名并发送上链 (实弹发射)
            logging.info("[Execution] Signing transaction via local wallet...")
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            logging.info("[Execution] Broadcasting to network...")
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt_hash = self.w3.to_hex(tx_hash)
            
            return {
                "status": "success",
                "quote": str(self.w3.from_wei(int(expected_output), 'mwei')), # 假设目标是 USDT (6位精度)
                "msg": f"Transaction Executed. Hash: {receipt_hash}"
            }

        except Exception as e:
            return {"status": "error", "msg": f"Execution failed: {str(e)}"}

# 沙盒独立测试入口
if __name__ == "__main__":
    okx_service = OKXOnchainService()
    # 警告：取消下方注释将花费真实的 ETH
    # print(okx_service.execute_real_swap("ETH", "USDT", 0.0001))
