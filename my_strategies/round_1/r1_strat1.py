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
                POSITION_LIMIT = 20 # Please modify according to the actual system limits
                
                # --- 1. Buy Logic (Long) ---
                # Sort sell orders by price in ascending order (buy the cheapest first)
                sorted_sell_orders = sorted(order_depth.sell_orders.items())
                
                for ask_price, ask_amount in sorted_sell_orders:
                    if ask_price < acceptable_price:
                        # Calculate price deviation
                        price_diff = acceptable_price - ask_price
                        
                        # [Core Improvement]: Set target position based on deviation
                        if price_diff >= 5:
                            target_pos = POSITION_LIMIT       # Huge deviation: Full position
                        elif price_diff >= 3:
                            target_pos = POSITION_LIMIT // 2  # Moderate deviation: Half position
                        else:
                            target_pos = POSITION_LIMIT // 4  # Small deviation: Light position (e.g., 5 lots)
                            
                        # Calculate how much more we can buy to reach the target position
                        max_we_can_buy = target_pos - current_position
                        
                        if max_we_can_buy > 0:
                            # Actual buy volume = min(volume we want to buy, volume sold in the market)
                            # Note: ask_amount is negative, so use -ask_amount to make it positive
                            buy_volume = min(max_we_can_buy, -ask_amount)
                            print(f"BUY {product}: Price={ask_price}, Target Pos={target_pos}, Vol={buy_volume}")
                            
                            orders.append(Order(product, ask_price, buy_volume))
                            current_position += buy_volume # Update local position status
                            
                            # If the absolute position limit is reached, break the loop and stop buying
                            if current_position >= POSITION_LIMIT:
                                break
                
                # --- 2. Sell Logic (Short) ---
                # Sort buy orders by price in descending order (sell to the highest bidder first)
                # reverse=True means descending order
                sorted_buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
                
                for bid_price, bid_amount in sorted_buy_orders:
                    if bid_price > acceptable_price:
                        # Calculate price deviation
                        price_diff = bid_price - acceptable_price
                        
                        # Set target short position based on deviation (represented by a negative number)
                        if price_diff >= 5:
                            target_pos = -POSITION_LIMIT
                        elif price_diff >= 3:
                            target_pos = -(POSITION_LIMIT // 2)
                        else:
                            target_pos = -(POSITION_LIMIT // 4)
                            
                        # Calculate how much more we can sell to reach the target short position (result is negative)
                        max_we_can_sell = target_pos - current_position
                        
                        if max_we_can_sell < 0:
                            # Actual sell volume = max(volume we want to sell, buy order volume in the market)
                            # Note: bid_amount is positive, but we are placing sell orders, so convert to negative for comparison
                            sell_volume = max(max_we_can_sell, -bid_amount)
                            print(f"SELL {product}: Price={bid_price}, Target Pos={target_pos}, Vol={sell_volume}")
                            
                            orders.append(Order(product, bid_price, sell_volume))
                            current_position += sell_volume # Update local position status
                            
                            # If the absolute short limit is reached, break the loop and stop selling
                            if current_position <= -POSITION_LIMIT:
                                break

            # Temporarily do not trade INTARIAN_PEPPER_ROOT
            elif product == "INTARIAN_PEPPER_ROOT":
                pass 
            
            result[product] = orders
    
        traderData = "SAMPLE_DATA" 
        conversions = 0
        
        return result, conversions, traderData