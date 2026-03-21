// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AlphaClaw Margin Vault (V5 Prototype)
 * @dev 解决无限授权黑洞：用户资金物理隔离，Agent 仅拥有受限交易权，无提现权。
 */
contract AlphaClawVault {
    address public immutable owner;          // 巨鲸/用户本人 (拥有唯一提现权)
    address public immutable agentExecutor;  // AlphaClaw 调度器 (只有交易权)

    mapping(address => uint256) public balances;

    event Deposited(address token, uint256 amount);
    event Withdrawn(address token, uint256 amount);
    event ExecutedByAgent(address target, uint256 value);

    modifier onlyOwner() {
        require(msg.sender == owner, "Vault: Only Owner");
        _;
    }

    modifier onlyAgent() {
        require(msg.sender == agentExecutor, "Vault: Only AlphaClaw Agent");
        _;
    }

    constructor(address _agentExecutor) {
        owner = msg.sender;
        agentExecutor = _agentExecutor;
    }

    // 巨鲸存入高频弹药
    function deposit() external payable {
        balances[address(0)] += msg.value;
        emit Deposited(address(0), msg.value);
    }

    // AlphaClaw Agent 发起交易 (例如调用 DEX Router)
    // 即使 Agent 逻辑被黑客挟持，也无法将钱转给自己，因为只允许 call 操作
    function executeTrade(address target, bytes calldata data, uint256 value) external onlyAgent {
        require(balances[address(0)] >= value, "Vault: Insufficient margin");
        balances[address(0)] -= value;
        
        (bool success, ) = target.call{value: value}(data);
        require(success, "Vault: Trade execution failed");
        
        emit ExecutedByAgent(target, value);
    }

    // 巨鲸随时一键抽离资金
    function emergencyWithdraw(uint256 amount) external onlyOwner {
        require(balances[address(0)] >= amount, "Vault: Insufficient balance");
        balances[address(0)] -= amount;
        payable(owner).transfer(amount);
        emit Withdrawn(address(0), amount);
    }
}
