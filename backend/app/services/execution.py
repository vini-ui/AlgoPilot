"""
Execution Layer - Handles order placement and risk management
"""
from typing import Dict, Optional
from app.models import Order


class ExecutionLayer:
    """
    Receives trade intents, applies risk checks, and executes orders.
    Supports paper_mode for simulation.
    """
    def __init__(self, paper_mode: bool = True):
        self.paper_mode = paper_mode

    async def execute_order(
        self,
        app_id: int,
        strategy_id: Optional[int],
        symbol: str,
        qty: int,
        price: float,
        order_type: str = "MARKET"
    ) -> Dict:
        """
        Execute an order through SmartAPI or simulate in paper mode.
        """
        if self.paper_mode:
            # Simulate order execution
            order_result = {
                "order_id": f"PAPER_{app_id}_{strategy_id}_{symbol}",
                "status": "filled",
                "filled_qty": qty,
                "filled_price": price
            }
        else:
            # TODO: Call SmartAPI order placement
            order_result = {
                "order_id": None,
                "status": "pending"
            }
        
        # TODO: Store order in database
        return order_result

    def set_paper_mode(self, enabled: bool):
        self.paper_mode = enabled

