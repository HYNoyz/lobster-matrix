// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AlphaClaw Executor & Aegis Verifier
 * @dev 配合 AlphaClaw-Nexus 链下 Agent 的链上执行网关
 * 强制要求所有交易必须携带 Lobster Aegis 节点的 ECDSA 安全签名
 */
contract AlphaClawExecutor {
    // Lobster Aegis 风控节点的官方公钥地址
    address public immutable aegisSignerNode;
    
    // 防重放攻击的 Nonce 记录
    mapping(address => uint256) public userNonces;

    event IntentExecuted(address indexed user, address tokenIn, address tokenOut, uint256 amount);
    event AegisInterception(address indexed user, address targetToken, string reason);

    constructor(address _aegisSignerNode) {
        require(_aegisSignerNode != address(0), "Invalid Aegis Node");
        aegisSignerNode = _aegisSignerNode;
    }

    /**
     * @notice 核心意图执行函数
     * @param tokenIn 输入代币地址
     * @param tokenOut 目标代币地址 (经过 Aegis 扫描的地址)
     * @param amount 交易数量
     * @param deadline 时间锁
     * @param aegisSignature Aegis 节点在链下生成的安全放行签名
     */
    function executeIntent(
        address tokenIn,
        address tokenOut,
        uint256 amount,
        uint256 deadline,
        bytes memory aegisSignature
    ) external {
        require(block.timestamp <= deadline, "AlphaClaw: Intent expired");

        // 1. 构建 EIP-191 签名哈希
        bytes32 messageHash = keccak256(
            abi.encodePacked(msg.sender, tokenIn, tokenOut, amount, userNonces[msg.sender], deadline)
        );
        bytes32 ethSignedMessageHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );

        // 2. TEE 级密码学验签 (验证指令是否真的通过了 Lobster Aegis 的安全审计)
        address recoveredSigner = recoverSigner(ethSignedMessageHash, aegisSignature);
        require(recoveredSigner == aegisSignerNode, "AlphaClaw: Aegis Security Clearance Failed or Forged");

        // 3. 递增 Nonce 防止重放
        userNonces[msg.sender] += 1;

        // 4. 调用 OKX Onchain OS Router 执行最终交易 (Demo 预留接口)
        // _callOKXRouter(tokenIn, tokenOut, amount);

        emit IntentExecuted(msg.sender, tokenIn, tokenOut, amount);
    }

    // --- ECDSA 签名恢复工具函数 ---
    function recoverSigner(bytes32 _ethSignedMessageHash, bytes memory _signature) internal pure returns (address) {
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(_signature);
        return ecrecover(_ethSignedMessageHash, v, r, s);
    }

    function splitSignature(bytes memory sig) internal pure returns (bytes32 r, bytes32 s, uint8 v) {
        require(sig.length == 65, "Invalid signature length");
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
    }
}
