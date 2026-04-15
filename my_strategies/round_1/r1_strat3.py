from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math

class Trader:
    
    def run(self, state: TradingState):
        result = {}
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Safely get the current best_bid and best_ask (prevent the order book from being momentarily empty)
            best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) > 0 else 0
            best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) > 0 else 0
            
            # ==========================================
            # Strategy 1: ASH_COATED_OSMIUM (Hybrid Market Making Strategy)
            # ==========================================
            if product == "ASH_COATED_OSMIUM":
                acceptable_price = 10000
                current_position = state.position.get(product, 0)
                POSITION_LIMIT = 80 
                
                # Calculate how much more we can buy and sell
                buy_vol = POSITION_LIMIT - current_position
                sell_vol = -POSITION_LIMIT - current_position
                
                if best_bid > 0 and best_ask > 0:
                    # --- Maker Pricing Logic ---
                    # Bid quote: Maximum no more than 9999. If the market best bid is 9997, we quote 9998 to be first (Pennying)
                    our_bid = min(acceptable_price - 1, best_bid + 1)
                    # Ask quote: Minimum no less than 10001. If the market best ask is 10003, we quote 10002 to be first
                    our_ask = max(acceptable_price + 1, best_ask - 1)
                    
                    # 1. Try Taker (Taking liquidity): If there are foolish sell orders far below the fair price, take them directly!
                    for ask_price, ask_amount in list(order_depth.sell_orders.items()):
                        if ask_price < acceptable_price and buy_vol > 0:
                            vol = min(buy_vol, -ask_amount)
                            orders.append(Order(product, ask_price, vol))
                            buy_vol -= vol
                            
                    # 2. Try Maker (Providing liquidity): Use the remaining quota to place limit orders to make the market
                    if buy_vol > 0:
                        orders.append(Order(product, our_bid, buy_vol))
                        
                    # Handle the sell direction in the same way
                    for bid_price, bid_amount in list(order_depth.buy_orders.items()):
                        if bid_price > acceptable_price and sell_vol < 0:
                            vol = max(sell_vol, -bid_amount)
                            orders.append(Order(product, bid_price, vol))
                            sell_vol -= vol
                            
                    if sell_vol < 0:
                        orders.append(Order(product, our_ask, sell_vol))

            # ==========================================
            # Strategy 2: INTARIAN_PEPPER_ROOT (Momentum Skewed Market Making)
            # ==========================================
            elif product == "INTARIAN_PEPPER_ROOT":
                current_position = state.position.get(product, 0)
                PEPPER_LIMIT = 80
                
                total_bid_vol = sum(order_depth.buy_orders.values())
                total_ask_vol = sum(abs(vol) for vol in order_depth.sell_orders.values())
                
                buy_vol = PEPPER_LIMIT - current_position
                sell_vol = -PEPPER_LIMIT - current_position
                
                if total_bid_vol + total_ask_vol > 0 and best_bid > 0 and best_ask > 0:
                    imbalance = total_bid_vol / (total_bid_vol + total_ask_vol)
                    
                    # --- Maker Skewed Quoting Logic ---
                    # Adjust our order placement based on market momentum
                    if imbalance > 0.70:
                        # Strongly bullish: We really want to buy.
                        # We place the bid at best_bid (following the crowd); place the ask extremely high to prevent it from being easily bought.
                        our_bid = best_bid
                        our_ask = best_ask + 4 
                    elif imbalance < 0.30:
                        # Strongly bearish: We really want to sell.
                        # We place the ask at best_ask; place the bid extremely low.
                        our_bid = best_bid - 4
                        our_ask = best_ask
                    else:
                        # Range-bound market: Earn the spread on both sides (Pennying)
                        # We squeeze into the middle of the order book, trying to buy and sell simultaneously
                        our_bid = best_bid + 1
                        our_ask = best_ask - 1
                        # Risk control: Ensure our own bid price is not higher than our ask price
                        if our_bid >= our_ask:
                            our_bid = best_bid
                            our_ask = best_ask
                            
                    # Place limit orders (only provide liquidity, do not actively take orders)
                    if buy_vol > 0:
                        orders.append(Order(product, int(our_bid), buy_vol))
                    if sell_vol < 0:
                        orders.append(Order(product, int(our_ask), sell_vol))
            
            result[product] = orders
    
        traderData = "SAMPLE_DATA" 
        conversions = 0
        return result, conversions, traderData