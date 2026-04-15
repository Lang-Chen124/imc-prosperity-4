from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math

class Trader:
    
    def run(self, state: TradingState):
        result = {}
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # ==========================================
            # Strategy 1: ASH_COATED_OSMIUM (Stepped Mean Reversion)
            # ==========================================
            if product == "ASH_COATED_OSMIUM":
                acceptable_price = 10000
                current_position = state.position.get(product, 0)
                POSITION_LIMIT = 20 # [Needs Confirmation] System position limit for ASH_COATED_OSMIUM
                
                # --- Buy Logic (Long) ---
                sorted_sell_orders = sorted(order_depth.sell_orders.items())
                for ask_price, ask_amount in sorted_sell_orders:
                    if ask_price < acceptable_price:
                        price_diff = acceptable_price - ask_price
                        
                        # Set target position based on deviation
                        if price_diff >= 5: target_pos = POSITION_LIMIT
                        elif price_diff >= 3: target_pos = POSITION_LIMIT // 2
                        else: target_pos = POSITION_LIMIT // 4
                            
                        max_we_can_buy = target_pos - current_position
                        if max_we_can_buy > 0:
                            buy_volume = min(max_we_can_buy, -ask_amount)
                            orders.append(Order(product, ask_price, buy_volume))
                            current_position += buy_volume
                            if current_position >= POSITION_LIMIT: break
                
                # --- Sell Logic (Short) ---
                sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
                for bid_price, bid_amount in sorted_buy_orders:
                    if bid_price > acceptable_price:
                        price_diff = bid_price - acceptable_price
                        
                        # Set target short position based on deviation
                        if price_diff >= 5: target_pos = -POSITION_LIMIT
                        elif price_diff >= 3: target_pos = -(POSITION_LIMIT // 2)
                        else: target_pos = -(POSITION_LIMIT // 4)
                            
                        max_we_can_sell = target_pos - current_position
                        if max_we_can_sell < 0:
                            sell_volume = max(max_we_can_sell, -bid_amount)
                            orders.append(Order(product, bid_price, sell_volume))
                            current_position += sell_volume
                            if current_position <= -POSITION_LIMIT: break

            # ==========================================
            # Strategy 2: INTARIAN_PEPPER_ROOT (Order Book Micro-Momentum/Imbalance)
            # ==========================================
            elif product == "INTARIAN_PEPPER_ROOT":
                PEPPER_LIMIT = 20  # [Needs Confirmation] System position limit for INTARIAN_PEPPER_ROOT
                current_position = state.position.get(product, 0)
                
                # 1. Calculate the total order volume on both sides of the order book
                total_bid_vol = sum(order_depth.buy_orders.values())
                total_ask_vol = sum(abs(vol) for vol in order_depth.sell_orders.values())
                
                if total_bid_vol + total_ask_vol > 0:
                    # 2. Calculate Buy Imbalance
                    buy_imbalance = total_bid_vol / (total_bid_vol + total_ask_vol)
                    
                    # Get the best bid and ask prices
                    best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) > 0 else 0
                    best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) > 0 else 0
                    
                    # --- 3. Trend-following Buy Logic (Long) ---
                    # Threshold 0.7: Indicates buyers are absolutely dominant (over 70%), high probability of price increase
                    if buy_imbalance > 0.70 and best_ask > 0:
                        # Tentatively buy 5 lots with the trend each time
                        buy_volume = min(PEPPER_LIMIT - current_position, 5) 
                        if buy_volume > 0:
                            orders.append(Order(product, best_ask, buy_volume))
                            current_position += buy_volume
                            
                    # --- 4. Trend-following Sell Logic (Short) ---
                    # Threshold 0.3: Indicates buying power is weak (under 30%), meaning sellers dominate, high probability of price drop
                    elif buy_imbalance < 0.30 and best_bid > 0:
                        # Tentatively sell 5 lots with the trend each time (negative value)
                        sell_volume = max(-PEPPER_LIMIT - current_position, -5) 
                        if sell_volume < 0:
                            orders.append(Order(product, best_bid, sell_volume))
                            current_position += sell_volume
            
            result[product] = orders
    
        traderData = "SAMPLE_DATA" 
        conversions = 0
        return result, conversions, traderData