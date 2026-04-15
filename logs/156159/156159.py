from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math

class Trader:
    
    def run(self, state: TradingState):
        result = {}
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Safely get the current best_bid and best_ask
            best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) > 0 else 0
            best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) > 0 else 0
            
            # ==========================================
            # Strategy 1: ASH_COATED_OSMIUM (Enhanced Hybrid Market Making)
            # ==========================================
            if product == "ASH_COATED_OSMIUM":
                acceptable_price = 10000
                POSITION_LIMIT = 80
                current_position = state.position.get(product, 0)
                
                # Remaining tradable volume (considering current position)
                buy_vol_remaining = POSITION_LIMIT - current_position
                sell_vol_remaining = -POSITION_LIMIT - current_position
                
                # 1. Taker Section: Prioritize taking the most profitable orders (widest spread)
                if best_bid > 0 and best_ask > 0:
                    
                    # --- Taking Sell Orders (Buy): Sort from low to high, take cheapest first ---
                    sorted_asks = sorted(order_depth.sell_orders.items())  # [(price, vol), ...] vol is negative
                    
                    for ask_price, ask_amount in sorted_asks:
                        if ask_price < acceptable_price and buy_vol_remaining > 0:
                            price_diff = acceptable_price - ask_price
                            available_vol = -ask_amount  # positive number
                            
                            # Dynamically determine take volume based on price difference
                            if price_diff >= 15:
                                take_vol = min(buy_vol_remaining, available_vol)      # Very profitable -> aggressive full take
                            elif price_diff >= 9:
                                take_vol = min(buy_vol_remaining, available_vol * 2 // 3)  # Moderately profitable
                            elif price_diff >= 5:
                                take_vol = min(buy_vol_remaining, available_vol // 2)      # Slightly profitable
                            else:
                                take_vol = min(buy_vol_remaining, 8)                       # Very small spread -> conservative
                            
                            if take_vol > 0:
                                orders.append(Order(product, ask_price, take_vol))
                                buy_vol_remaining -= take_vol
                    
                    # --- Taking Buy Orders (Sell): Sort from high to low, take most expensive first ---
                    sorted_bids = sorted(order_depth.buy_orders.items(), reverse=True)
                    
                    for bid_price, bid_amount in sorted_bids:
                        if bid_price > acceptable_price and sell_vol_remaining < 0:
                            price_diff = bid_price - acceptable_price
                            available_vol = bid_amount  # positive number
                            
                            # Dynamically determine take volume based on price difference
                            if price_diff >= 15:
                                take_vol = min(-sell_vol_remaining, available_vol)
                            elif price_diff >= 9:
                                take_vol = min(-sell_vol_remaining, available_vol * 2 // 3)
                            elif price_diff >= 5:
                                take_vol = min(-sell_vol_remaining, available_vol // 2)
                            else:
                                take_vol = min(-sell_vol_remaining, 8)
                            
                            if take_vol > 0:
                                orders.append(Order(product, bid_price, -take_vol))  # Use negative volume for sell
                                sell_vol_remaining += take_vol   # sell_vol_remaining moves toward 0
                
                # 2. Maker Section: Quote remaining capacity (provide liquidity)
                if best_bid > 0 and best_ask > 0:
                    our_bid = min(acceptable_price - 1, best_bid + 1)
                    our_ask = max(acceptable_price + 1, best_ask - 1)
                    
                    if buy_vol_remaining > 0:
                        orders.append(Order(product, our_bid, buy_vol_remaining))
                    if sell_vol_remaining < 0:
                        orders.append(Order(product, our_ask, sell_vol_remaining))

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
                    
                    # --- Adjust quotes dynamically based on market imbalance ---
                    if imbalance > 0.60:          # Strongly bullish
                        our_bid = best_bid
                        our_ask = best_ask + 5    # Place ask high to avoid being filled
                    elif imbalance < 0.40:        # Strongly bearish
                        our_bid = best_bid - 5    # Place bid low to avoid being filled
                        our_ask = best_ask
                    else:                         # Sideways market, tight pennying
                        our_bid = best_bid + 1
                        our_ask = best_ask - 1
                        if our_bid >= our_ask:    # Prevent bid >= ask
                            our_bid = best_bid
                            our_ask = best_ask
                            
                    # Only place Maker orders, no active Taking
                    if buy_vol > 0:
                        orders.append(Order(product, int(our_bid), buy_vol))
                    if sell_vol < 0:
                        orders.append(Order(product, int(our_ask), sell_vol))
            
            # Add orders for this product to the results
            result[product] = orders
        
        traderData = "SAMPLE_DATA" 
        conversions = 0
        return result, conversions, traderData