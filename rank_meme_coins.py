#!/usr/bin/env python3
"""
RANK MEME COINS
Risk-adjusted ranking system for low-cap meme coins
"""

import json
import os
import math
from datetime import datetime

class MemeCoinRanker:
    def __init__(self, data_dir="meme_coin_data"):
        self.data_dir = data_dir
        self.coins = []
        
    def load_coin_list(self):
        """Load the coin list"""
        filepath = os.path.join(self.data_dir, "low_cap_meme_coins.json")
        with open(filepath, "r") as f:
            data = json.load(f)
        return data["coins"]
    
    def load_history(self, coin_id):
        """Load historical data if available"""
        filepath = os.path.join(self.data_dir, f"{coin_id.upper().replace('-', '_')}_history.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return None
    
    def calculate_risk_score(self, coin):
        """Calculate risk score (0-100, higher = riskier)"""
        score = 0
        
        # Market cap risk (smaller = riskier)
        mcap = coin.get("market_cap", 0)
        if mcap < 20_000_000:
            score += 40
        elif mcap < 50_000_000:
            score += 25
        elif mcap < 100_000_000:
            score += 10
        
        # Volatility from 24h/7d/30d changes
        changes = [
            abs(coin.get("price_change_percentage_24h", 0) or 0),
            abs(coin.get("price_change_percentage_7d_in_currency", 0) or 0) / 7,
            abs(coin.get("price_change_percentage_30d_in_currency", 0) or 0) / 30
        ]
        avg_daily_volatility = sum(changes) / len(changes)
        if avg_daily_volatility > 15:
            score += 30
        elif avg_daily_volatility > 8:
            score += 20
        elif avg_daily_volatility > 4:
            score += 10
        
        # Distance from ATH (further = riskier)
        ath_change = abs(coin.get("ath_change_percentage", 0) or 0)
        if ath_change > 90:
            score += 20
        elif ath_change > 70:
            score += 15
        elif ath_change > 50:
            score += 10
        
        # Volume risk (low volume = harder to exit)
        volume = coin.get("total_volume", 0)
        mcap = coin.get("market_cap", 1)
        volume_ratio = volume / mcap if mcap > 0 else 0
        if volume_ratio < 0.01:
            score += 10
        elif volume_ratio < 0.05:
            score += 5
        
        return min(100, score)
    
    def calculate_momentum_score(self, coin):
        """Calculate momentum score (0-100, higher = better momentum)"""
        score = 0
        
        # 24h change
        change_24h = coin.get("price_change_percentage_24h", 0) or 0
        if change_24h > 10:
            score += 25
        elif change_24h > 5:
            score += 15
        elif change_24h > 0:
            score += 5
        
        # 7d change
        change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0
        if change_7d > 50:
            score += 25
        elif change_7d > 20:
            score += 15
        elif change_7d > 0:
            score += 5
        
        # 30d change
        change_30d = coin.get("price_change_percentage_30d_in_currency", 0) or 0
        if change_30d > 100:
            score += 25
        elif change_30d > 50:
            score += 15
        elif change_30d > 20:
            score += 5
        
        # Volume trend (if volume increasing)
        volume = coin.get("total_volume", 0)
        mcap = coin.get("market_cap", 1)
        vol_ratio = volume / mcap if mcap > 0 else 0
        if vol_ratio > 0.2:
            score += 15
        elif vol_ratio > 0.1:
            score += 10
        elif vol_ratio > 0.05:
            score += 5
        
        # Nearness to ATH (closer = better momentum)
        ath_change = abs(coin.get("ath_change_percentage", 0) or 0)
        if ath_change < 20:
            score += 10
        elif ath_change < 50:
            score += 5
        
        return min(100, score)
    
    def calculate_value_score(self, coin):
        """Calculate value score (0-100, higher = more undervalued)"""
        score = 0
        
        # Distance from ATH (bigger drop = more potential upside)
        ath_change = abs(coin.get("ath_change_percentage", 0) or 0)
        if ath_change > 95:
            score += 40
        elif ath_change > 85:
            score += 30
        elif ath_change > 70:
            score += 20
        elif ath_change > 50:
            score += 10
        
        # Market cap vs volume (high volume relative to mcap = interest)
        volume = coin.get("total_volume", 0)
        mcap = coin.get("market_cap", 1)
        vol_ratio = volume / mcap if mcap > 0 else 0
        if vol_ratio > 0.3:
            score += 20
        elif vol_ratio > 0.15:
            score += 15
        elif vol_ratio > 0.05:
            score += 10
        
        # Small market cap (more room to grow)
        if mcap < 20_000_000:
            score += 20
        elif mcap < 40_000_000:
            score += 15
        elif mcap < 60_000_000:
            score += 10
        
        # Recent performance (if down, might be oversold)
        change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0
        if change_7d < -20:
            score += 20  # Oversold
        elif change_7d < -10:
            score += 10
        
        return min(100, score)
    
    def calculate_sharpe_proxy(self, coin):
        """Calculate proxy Sharpe ratio (return/volatility)"""
        # Use 30d annualized return / daily volatility proxy
        change_30d = coin.get("price_change_percentage_30d_in_currency", 0) or 0
        change_24h = coin.get("price_change_percentage_24h", 0) or 0
        
        # Annualize 30d return
        annual_return = ((1 + change_30d/100) ** 12 - 1) * 100
        
        # Volatility proxy (using 24h as daily vol, annualized)
        volatility = abs(change_24h) * math.sqrt(365)
        
        if volatility > 0:
            sharpe = annual_return / volatility
        else:
            sharpe = 0
        
        return round(sharpe, 2)
    
    def calculate_composite_score(self, coin):
        """Calculate composite score (0-100)"""
        risk = self.calculate_risk_score(coin)
        momentum = self.calculate_momentum_score(coin)
        value = self.calculate_value_score(coin)
        sharpe = self.calculate_sharpe_proxy(coin)
        
        # Sharpe score (normalize to 0-100)
        sharpe_score = min(100, max(0, (sharpe + 2) * 25))
        
        # Weights: 25% momentum, 25% value, 25% sharpe, 25% (100-risk)
        composite = (
            momentum * 0.25 +
            value * 0.25 +
            sharpe_score * 0.25 +
            (100 - risk) * 0.25
        )
        
        return {
            "composite": round(composite, 1),
            "risk": risk,
            "momentum": momentum,
            "value": value,
            "sharpe": sharpe,
            "sharpe_score": round(sharpe_score, 1)
        }
    
    def rank_all(self):
        """Rank all coins"""
        print("=" * 80)
        print("MEME COIN RANKING SYSTEM")
        print("=" * 80)
        
        coins = self.load_coin_list()
        print(f"Analyzing {len(coins)} coins...")
        
        ranked = []
        for coin in coins:
            scores = self.calculate_composite_score(coin)
            
            ranked.append({
                **coin,
                **scores,
                "risk_label": "LOW" if scores["risk"] < 30 else "MED" if scores["risk"] < 60 else "HIGH",
                "momentum_label": "WEAK" if scores["momentum"] < 30 else "MODERATE" if scores["momentum"] < 60 else "STRONG",
                "value_label": "OVERVALUED" if scores["value"] < 30 else "FAIR" if scores["value"] < 60 else "UNDERVALUED"
            })
        
        # Sort by composite score
        ranked.sort(key=lambda x: x["composite"], reverse=True)
        
        return ranked
    
    def display_rankings(self, ranked, limit=25):
        """Display ranked coins"""
        print(f"\n{'='*80}")
        print(f"TOP {limit} RANKED MEME COINS")
        print(f"{'='*80}")
        print(f"\n{'#':<4} {'Symbol':<8} {'Composite':<10} {'Risk':<6} {'Momentum':<10} {'Value':<12} {'Sharpe':<8} {'Price':<10} {'MCap':<10}")
        print("-" * 80)
        
        for i, coin in enumerate(ranked[:limit], 1):
            print(
                f"{i:<4} "
                f"{coin['symbol']:<8} "
                f"{coin['composite']:<9.1f} "
                f"{coin['risk_label']:<6} "
                f"{coin['momentum_label']:<10} "
                f"{coin['value_label']:<12} "
                f"{coin['sharpe']:<+7.2f} "
                f"${coin['current_price']:<9.6f} "
                f"${coin['market_cap']/1_000_000:<9.1f}M"
            )
        
        # Categories
        print(f"\n{'='*80}")
        print("BY CATEGORY")
        print(f"{'='*80}")
        
        # Best risk/reward
        best_risk_reward = sorted(ranked, key=lambda x: x["composite"], reverse=True)[:5]
        print("\nBest Risk/Reward (Composite Score):")
        for i, coin in enumerate(best_risk_reward, 1):
            print(f"  {i}. {coin['symbol']}: {coin['composite']:.1f} (Risk: {coin['risk_label']}, Sharpe: {coin['sharpe']:+.2f})")
        
        # Lowest risk
        lowest_risk = sorted(ranked, key=lambda x: x["risk"])[:5]
        print("\nLowest Risk:")
        for i, coin in enumerate(lowest_risk, 1):
            print(f"  {i}. {coin['symbol']}: {coin['risk']}/100 (MCap: ${coin['market_cap']/1_000_000:.1f}M)")
        
        # Highest momentum
        highest_momentum = sorted(ranked, key=lambda x: x["momentum"], reverse=True)[:5]
        print("\nHighest Momentum:")
        for i, coin in enumerate(highest_momentum, 1):
            print(f"  {i}. {coin['symbol']}: {coin['momentum']}/100 (30d: {coin['price_change_percentage_30d_in_currency'] or 0:+.1f}%)")
        
        # Most undervalued
        most_value = sorted(ranked, key=lambda x: x["value"], reverse=True)[:5]
        print("\nMost Undervalued:")
        for i, coin in enumerate(most_value, 1):
            print(f"  {i}. {coin['symbol']}: {coin['value']}/100 (ATH drop: {coin['ath_change_percentage']:.1f}%)")
    
    def save_rankings(self, ranked):
        """Save rankings to JSON"""
        filepath = os.path.join(self.data_dir, "meme_coin_rankings.json")
        data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(ranked),
            "rankings": [
                {
                    "rank": i + 1,
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "composite": coin["composite"],
                    "risk": coin["risk"],
                    "risk_label": coin["risk_label"],
                    "momentum": coin["momentum"],
                    "momentum_label": coin["momentum_label"],
                    "value": coin["value"],
                    "value_label": coin["value_label"],
                    "sharpe": coin["sharpe"],
                    "market_cap": coin["market_cap"],
                    "current_price": coin["current_price"],
                    "price_change_24h": coin.get("price_change_percentage_24h", 0),
                    "price_change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                    "price_change_30d": coin.get("price_change_percentage_30d_in_currency", 0),
                    "ath_change": coin.get("ath_change_percentage", 0)
                }
                for i, coin in enumerate(ranked)
            ]
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\nSaved rankings to: {filepath}")


def main():
    ranker = MemeCoinRanker()
    
    # Rank all coins
    ranked = ranker.rank_all()
    
    # Display
    ranker.display_rankings(ranked)
    
    # Save
    ranker.save_rankings(ranked)
    
    print(f"\n{'='*80}")
    print("RANKING COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
