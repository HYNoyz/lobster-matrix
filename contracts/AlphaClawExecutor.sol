// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// 引入真实的 LayerZero 终端接口
interface ILayerZeroEndpoint {
    function send(uint16 _dstChainId, bytes calldata _destination, bytes calldata _payload, address payable _refundAddress, address _zroPaymentAddress, bytes calldata _adapterParams) external payable;
}

interface ILayerZeroReceiver {
    function lzReceive(uint16 _srcChainId, bytes calldata _srcAddress, uint64 _nonce, bytes calldata _payload) external;
}

contract AlphaClawOmniVault is ILayerZeroReceiver {
    ILayerZeroEndpoint public immutable lzEndpoint;
    address public immutable protocolFeeReceiver;
    
    // intentId => 是否已解决
    mapping(bytes32 => bool) public intentResolved;
    // intentId => 锁定的资产数量
    mapping(bytes32 => uint256) public lockedAssets;
    // intentId => 用户地址
    mapping(bytes32 => address) public intentOwners;

    event CrossChainIntentSent(bytes32 indexed intentId, uint16 dstChainId);
    event AtomicRollbackExecuted(bytes32 indexed intentId, address user, uint256 refundedAmount);

    constructor(address _lzEndpoint, address _feeReceiver) {
        lzEndpoint = ILayerZeroEndpoint(_lzEndpoint);
        protocolFeeReceiver = _feeReceiver;
    }

    // 1. 发起跨链意图 (锁定 Arbitrum 资产)
    function sendOmniIntent(uint16 _dstChainId, bytes calldata _dstAddress, bytes32 _intentId) external payable {
        require(!intentResolved[_intentId], "Intent active");
        
        // 锁定用户的资金作为跨链担保
        lockedAssets[_intentId] = msg.value;
        intentOwners[_intentId] = msg.sender;

        // 构建跨链执行载荷
        bytes memory payload = abi.encode(_intentId, "EXECUTE_SWAP");

        // 真实调用 LayerZero 跨链发送
        lzEndpoint.send{value: msg.value}(
            _dstChainId, 
            _dstAddress, 
            payload, 
            payable(msg.sender), 
            address(0), 
            bytes("")
        );

        emit CrossChainIntentSent(_intentId, _dstChainId);
    }

    // 2. 真正的跨链原子回滚接收端 (LayerZero 回调)
    // 如果远端 Base 链执行失败，会跨链调用这个函数
    function lzReceive(uint16 _srcChainId, bytes calldata _srcAddress, uint64 _nonce, bytes calldata _payload) external override {
        require(msg.sender == address(lzEndpoint), "Only LayerZero Endpoint");

        // 解码远端传回的消息: (intentId, 执行结果状态)
        (bytes32 intentId, bool executionSuccess) = abi.decode(_payload, (bytes32, bool));
        
        require(!intentResolved[intentId], "Already resolved");
        intentResolved[intentId] = true;

        if (!executionSuccess) {
            // 🚀 [V6 核心] 远端执行失败，触发原子性原路退款！
            uint256 refundAmount = lockedAssets[intentId];
            address user = intentOwners[intentId];
            
            lockedAssets[intentId] = 0;
            payable(user).transfer(refundAmount);
            
            emit AtomicRollbackExecuted(intentId, user, refundAmount);
        } else {
            // 执行成功，资金划转给协议与清算方
            payable(protocolFeeReceiver).transfer(lockedAssets[intentId]);
        }
    }
}
