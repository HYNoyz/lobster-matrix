import { OKXOnchainOS } from '@okx/onchain-os-sdk';
import { readFileSync } from 'fs';

// 模拟读取 Claw 编译好的共识 JSON
const compiledOrder = JSON.parse(readFileSync('./output_schema.json', 'utf-8'));

async function executeMatrixEscrow(order) {
    const os = new OKXOnchainOS({ network: 'Mainnet' });
    console.log(`[Matrix Router] Initiating A2A Escrow for Order: ${order.order_id}`);

    const routePayload = {
        action: 'CREATE_YIELD_BEARING_ESCROW',
        from: order.participants.agent_a,
        token: order.escrow_details.asset,
        amount: order.escrow_details.amount,
        targetYieldProtocol: order.escrow_details.yield_strategy, 
        releaseCondition: order.execution_trigger
    };

    try {
        const tx = await os.executeRoute(routePayload);
        console.log(`[Matrix Router] Escrow Secured. Yield Routing Active. TX: ${tx.hash}`);
    } catch (e) {
        console.error(`[Matrix Router] Execution Blocked. Reason: ${e.message}`);
    }
}

executeMatrixEscrow(compiledOrder);
