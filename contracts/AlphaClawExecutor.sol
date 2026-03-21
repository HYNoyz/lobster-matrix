// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract AlphaClawExecutor {
    address public immutable aegisSignerNode;
    mapping(address => uint256) public userNonces;

    event IntentExecuted(address indexed user, bytes[] results);
    event AegisInterception(address indexed user, string reason);

    constructor(address _aegisSignerNode) {
        require(_aegisSignerNode != address(0), "Invalid Node");
        aegisSignerNode = _aegisSignerNode;
    }

    // 核心升级：引入原子性批量执行 (Atomic Multicall)
    function executeAtomicDAG(
        bytes[] calldata executionPayloads,
        uint256 deadline,
        bytes memory aegisSignature
    ) external payable {
        require(block.timestamp <= deadline, "AlphaClaw: Intent expired");

        // 1. 防篡改验证：校验整个 DAG Payload 数组的哈希
        bytes32 payloadHash = keccak256(abi.encode(executionPayloads));
        bytes32 messageHash = keccak256(
            abi.encodePacked(msg.sender, payloadHash, userNonces[msg.sender], deadline)
        );
        bytes32 ethSignedMessageHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );

        require(recoverSigner(ethSignedMessageHash, aegisSignature) == aegisSignerNode, "AlphaClaw: Aegis Clearance Failed");
        userNonces[msg.sender] += 1;

        // 2. 原子性执行：任何一个 payload 失败，整个交易 Revert
        bytes[] memory results = new bytes[](executionPayloads.length);
        for (uint256 i = 0; i < executionPayloads.length; i++) {
            (bool success, bytes memory result) = address(this).delegatecall(executionPayloads[i]);
            require(success, "AlphaClaw: DAG execution failed, rolling back entire state");
            results[i] = result;
        }

        emit IntentExecuted(msg.sender, results);
    }

    // ECDSA 恢复逻辑保持不变
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
