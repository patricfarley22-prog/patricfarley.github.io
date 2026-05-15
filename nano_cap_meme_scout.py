#!/usr/bin/env python3
"""
NANO-CAP MEME COIN SCOUT (Production Ready)
Targets meme coins under $10M market cap
Uses CoinGecko API with pagination to find ultra low-cap gems
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)


class NanoCapScout:
    """Scout for ultra low-cap meme coins (under $10M)"""
    
    def __init__(self, max_mcap: float = 10_000_000):
        self.max_mcap = max_mcap
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "NanoCapScout/1.0"
        })
        self._last_request_time = 0
        self._min_delay = 2.0
    
    def _rate_limit(self):
        """Respect CoinGecko free tier rate limits"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited GET request"""
        self._rate_limit()
        url = f"{COINGECKO_BASE}/{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=15)
            if response.status_code == 429:
                print(f"  Rate limited. Waiting 60s...")
                time.sleep(60)
                return self._get(endpoint, params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            return None
    
    def fetch_all_coins(self, max_pages: int = 15) -> List[Dict]:
        """Fetch coins sorted by market cap ascending (smallest first)"""
        all_coins = []
        
        for page in range(1, max_pages + 1):
            print(f"\nFetching page {page} (sorted ascending)...")
            
            params = {
                "vs_currency": "usd",
                "order": "market_cap_asc",
                "per_page": 250,
                "page": page,
                "sparkline": "false",
                "price_change_percentage": "24h,7d,30d"
            }
            
            data = self._get("coins/markets", params)
            if not data:
                break
            
            for coin in data:
                mcap = coin.get("market_cap") or 0
                if mcap > 0 and mcap < self.max_mcap:
                    all_coins.append(coin)
                elif mcap >= self.max_mcap and mcap > 0:
                    print(f"  Found coin at ${mcap/1_000_000:.2f}M - stopping")
                    return all_coins
            
            if len(data) < 250:
                break
        
        return all_coins
    
    def filter_meme_coins(self, coins: List[Dict]) -> List[Dict]:
        """Filter for meme coins"""
        meme_keywords = [
            "doge", "shib", "pepe", "meme", "wojak", "bonk", "floki",
            "cat", "dog", "frog", "bird", "elon", "moon", "rocket",
            "based", "degen", "ape", "pump", "dump", "inu", "chad",
            "giga", "turbo", "ponke", "mog", "popcat", "snek", "wif",
            "harry", "potter", "obama", "sonic", "trump", "maga"
        ]
        
        known_meme_ids = {
            "dogecoin", "shiba-inu", "pepe", "bonk", "floki",
            "dogwifhat", "memecoin", "book-of-meme", "brett",
            "mog-coin", "popcat", "spx6900", "gigachad-2",
            "turbo", "wojak", "dejitaru-tsuka",
            "harrypotterobamasonic10in"
        }
        
        meme_coins = []
        for coin in coins:
            coin_id = coin.get("id", "").lower()
            symbol = coin.get("symbol", "").lower()
            name = coin.get("name", "").lower()
            
            is_meme = (
                coin_id in known_meme_ids or
                symbol in known_meme_ids or
                any(kw in coin_id for kw in meme_keywords) or
                any(kw in symbol for kw in meme_keywords) or
                any(kw in name for kw in meme_keywords)
            )
            
            if is_meme:
                meme_coins.append({
                    "id": coin["id"],
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "current_price": coin.get("current_price", 0),
                    "market_cap": coin.get("market_cap", 0),
                    "total_volume": coin.get("total_volume", 0),
                    "price_change_24h": coin.get("price_change_24h", 0),
                    "price_change_percentage_24h": coin.get("price_change_percentage_24h", 0),
                    "price_change_percentage_7d_in_currency": coin.get("price_change_percentage_7d_in_currency", 0),
                    "price_change_percentage_30d_in_currency": coin.get("price_change_percentage_30d_in_currency", 0),
                    "ath": coin.get("ath", 0),
                    "ath_change_percentage": coin.get("ath_change_percentage", 0),
                    "ath_date": coin.get("ath_date", ""),
                    "last_updated": coin.get("last_updated", "")
                })
        
        meme_coins.sort(key=lambda x: x["market_cap"], reverse=True)
        return meme_coins
    
    def display_coins(self, coins: List[Dict]):
        """Display nano-cap coins"""
        print(f"\n{'='*80}")
        print(f"NANO-CAP MEME COINS (Under ${self.max_mcap/1_000_000:.0f}M)")
        print(f"{'='*80}")
        print(f"Found: {len(coins)} coins")
        print(f"{'='*80}")
        
        if not coins:
            print("No coins found.")
            return
        
        print(f"\n{'#':<4} {'Symbol':<10} {'Name':<22} {'Price':<14} {'MCap':<10} {'24h':<8} {'7d':<8} {'30d':<8}")
        print("-" * 80)
        
        for i, coin in enumerate(coins, 1):
            print(
                f"{i:<4} "
                f"{coin['symbol']:<10} "
                f"{coin['name'][:21]:<22} "
                f"${coin['current_price']:<13.8f} "
                f"${coin['market_cap']/1_000_000:<9.2f}M "
                f"{coin['price_change_percentage_24h'] or 0:<+7.1f}% "
                f"{coin['price_change_percentage_7d_in_currency'] or 0:<+7.1f}% "
                f"{coin['price_change_percentage_30d_in_currency'] or 0:<+7.1f}%"
            )
        
        if coins:
            avg_mcap = sum(c["market_cap"] for c in coins) / len(coins)
            print(f"\n{'='*80}")
            print(f"Avg Market Cap: ${avg_mcap/1_000_000:.2f}M | Avg 24h: {sum((c['price_change_percentage_24h'] or 0) for c in coins)/len(coins):+.1f}%")
            print(f"Smallest: ${min(c['market_cap'] for c in coins)/1_000:.0f}K | Largest: ${max(c['market_cap'] for c in coins)/1_000_000:.2f}M")
    
    def fetch_historical_data(self, coin_id: str, days: int = 365) -> Optional[Dict]:
        """Fetch historical data for a coin"""
        print(f"\nFetching {days}-day history for {coin_id}...")
        
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily"
        }
        
        data = self._get(f"coins/{coin_id}/market_chart", params)
        if not data:
            return None
        
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        market_caps = data.get("market_caps", [])
        
        history = []
        for i in range(len(prices)):
            timestamp = prices[i][0]
            history.append({
                "date": datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d"),
                "price": prices[i][1],
                "volume": volumes[i][1] if i < len(volumes) else 0,
                "market_cap": market_caps[i][1] if i < len(market_caps) else 0
            })
        
        # Calculate metrics
        prices_list = [h["price"] for h in history]
        volumes_list = [h["volume"] for h in history]
        
        import statistics
        daily_returns = []
        for i in range(1, len(prices_list)):
            if prices_list[i-1] > 0:
                daily_returns.append((prices_list[i] - prices_list[i-1]) / prices_list[i-1])
        
        volatility = 0
        if daily_returns and len(daily_returns) > 1:
            volatility = statistics.stdev(daily_returns) * (365 ** 0.5) * 100
        
        metrics = {
            "total_return_pct": round(((prices_list[-1] - prices_list[0]) / prices_list[0] * 100) if prices_list[0] > 0 else 0, 2),
            "volatility_annualized_pct": round(volatility, 2),
            "avg_daily_volume": round(sum(volumes_list) / len(volumes_list) if volumes_list else 0, 2),
            "max_price": round(max(prices_list), 10),
            "min_price": round(min(prices_list), 10),
            "ath_from_history": round(max(prices_list), 10),
            "data_points": len(history)
        }
        
        return {
            "coin_id": coin_id,
            "days": len(history),
            "history": history,
            "metrics": metrics
        }
    
    def save_coin_list(self, coins: List[Dict]):
        """Save coin list"""
        filepath = os.path.join(DATA_DIR, "nano_cap_meme_coins.json")
        with open(filepath, "w") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "max_market_cap": self.max_mcap,
                "count": len(coins),
                "coins": coins
            }, f, indent=2)
        print(f"\nSaved to: {filepath}")
    
    def save_history(self, coin_id: str, data: Dict):
        """Save history"""
        symbol = coin_id.upper().replace("-", "_")
        filepath = os.path.join(DATA_DIR, f"{symbol}_history.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved: {filepath}")


def main():
    scout = NanoCapScout(max_mcap=10_000_000)
    
    print("=" * 80)
    print("NANO-CAP MEME COIN SCOUT")
    print("Finding ultra low-cap gems under $10M market cap")
    print("=" * 80)
    
    # Fetch coins
    print("\n[Step 1] Fetching from CoinGecko (ascending order)...")
    all_coins = scout.fetch_all_coins(max_pages=15)
    
    if all_coins:
        print(f"\nFound {len(all_coins)} coins under $10M")
        
        # Filter for meme coins
        print("\n[Step 2] Filtering for meme coins...")
        meme_coins = scout.filter_meme_coins(all_coins)
        
        # Display
        scout.display_coins(meme_coins)
        
        # Save
        scout.save_coin_list(meme_coins)
        
        # Fetch history for top 3
        if meme_coins:
            print(f"\n{'='*80}")
            print("[Step 3] Fetching 365-day history for top 3 movers...")
            print(f"{'='*80}")
            
            sorted_by_30d = sorted(
                meme_coins,
                key=lambda x: abs(x["price_change_percentage_30d_in_currency"] or 0),
                reverse=True
            )
            
            for coin in sorted_by_30d[:3]:
                history = scout.fetch_historical_data(coin["id"], days=365)
                if history:
                    scout.save_history(coin["id"], history)
                    print(f"\n  {coin['symbol']}: {history['days']} days")
                    for key, val in history["metrics"].items():
                        print(f"    {key}: {val}")
    else:
        print("\nNo coins found. CoinGecko API may be slow/rate-limited.")
        print("Try again later or use the existing $100M scan data.")
    
    print(f"\n{'='*80}")
    print("SCAN COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
