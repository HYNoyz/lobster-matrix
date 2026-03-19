// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title LobsterMatrixEscrow
 * @dev 专门为 OKX Onchain OS AI Hackathon 设计的 A2A 生息托管合约
 */
contract LobsterMatrixEscrow {
    address public owner;
    
    struct EscrowSession {
        address sender;
        address receiver;
        uint256 amount;
        bool isReleased;
        uint256 timestamp;
    }
    
    mapping(bytes32 => EscrowSession) public sessions;

    event Deposited(bytes32 indexed sessionId, address sender, uint256 amount);
    event Released(bytes32 indexed sessionId, address receiver, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    // AI 代理调用此函数锁定资金
    function deposit(bytes32 _sessionId, address _receiver) external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        require(sessions[_sessionId].sender == address(0), "Session already exists");

        sessions[_sessionId] = EscrowSession({
            sender: msg.sender,
            receiver: _receiver,
            amount: msg.value,
            isReleased: false,
            timestamp: block.timestamp
        });

        emit Deposited(_sessionId, msg.sender, msg.value);
    }

    // 当 AI 意图确认满足条件时释放资金
    function release(bytes32 _sessionId) external {
        EscrowSession storage session = sessions[_sessionId];
        require(!session.isReleased, "Already released");
        require(msg.sender == owner || msg.sender == session.sender, "Unauthorized");

        session.isReleased = true;
        payable(session.receiver).transfer(session.amount);

        emit Released(_sessionId, session.receiver, session.amount);
    }

    // 模拟 AAVE/Compound 生息逻辑的查询接口（用于 README 展示）
    function getEstimatedYield(bytes32 _sessionId) external view returns (uint256) {
        EscrowSession storage session = sessions[_sessionId];
        if (session.isReleased) return 0;
        uint256 duration = block.timestamp - session.timestamp;
        // 模拟 5% 年化收益
        return (session.amount * 5 * duration) / (365 days * 100);
    }

    receive() external payable {}
}
