from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        result = {}
        
        # Set product parameters
        POSITION_LIMIT = 20  # Assuming the position limit for AMETHYSTS is 20
        acceptable_price = 10000

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if product == 'AMETHYSTS':
                # 1. Get current position!
                # state.position is a dictionary. If a product hasn't been traded yet, 
                # it won't have a key, so we use .get(product, 0) to default to 0.
                current_position = state.position.get(product, 0)

                # ================= Buy Logic =================
                if len(order_depth.sell_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_amount = order_depth.sell_orders[best_ask]
                    
                    if best_ask < acceptable_price:
                        # Core protection logic: Calculate how much more you can buy
                        # For example: Limit is 20, current position is 15, so you can buy a maximum of 5 more
                        max_buy_capacity = POSITION_LIMIT - current_position
                        
                        # Market order volume (convert negative to positive)
                        available_volume = -best_ask_amount
                        
                        # Final order volume: Take the minimum of "maximum capacity to buy" and "available volume"
                        buy_volume = min(max_buy_capacity, available_volume)
                        
                        # Place order as long as the calculated volume is greater than 0
                        if buy_volume > 0:
                            print(f"BUY AMETHYSTS at {best_ask}, Volume: {buy_volume}, Current Pos: {current_position}")
                            orders.append(Order(product, best_ask, buy_volume))
                            
                            # Update the local position variable to prevent calculation errors in subsequent code within the same time step
                            current_position += buy_volume

                # ================= Sell Logic =================
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_amount = order_depth.buy_orders[best_bid]
                    
                    if best_bid > acceptable_price:
                        # Core protection logic: Calculate how much more you can sell
                        # We can short up to -20. So the amount you can sell = absolute limit + current position
                        # For example: current position 5, max you can sell is 20 + 5 = 25 (after selling it becomes -20)
                        # For example: current position -15, max you can sell is 20 + (-15) = 5 (after selling it becomes -20)
                        max_sell_capacity = POSITION_LIMIT + current_position
                        
                        # Market order volume (buy orders are already positive)
                        available_volume = best_bid_amount
                        
                        # Final order volume: Take the minimum of the two
                        sell_volume = min(max_sell_capacity, available_volume)
                        
                        # Place order as long as the calculated volume is greater than 0
                        if sell_volume > 0:
                            print(f"SELL AMETHYSTS at {best_bid}, Volume: {-sell_volume}, Current Pos: {current_position}")
                            # When sending a sell order, a negative sign must be added to convert it to a negative number!
                            orders.append(Order(product, best_bid, -sell_volume))
                            
                            # Update local variable
                            current_position -= sell_volume

            # Add the orders for this product to the result dictionary
            result[product] = orders
            
        conversions = 0
        traderData = "SAMPLE"
        return result, conversions, traderData