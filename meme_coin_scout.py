#!/usr/bin/env python3
"""
MEME COIN SCOUT - Low Cap Analyzer
Fetches meme coins from CoinGecko, filters for market cap under $100M,
pulls historical data, and calculates key metrics.
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# CoinGecko free tier: 10-30 calls/minute
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Known meme coin categories on CoinGecko
MEME_CATEGORIES = [
    "meme-token",
    "doge",
    "elon-musk-inspired",
    "solana-meme-coins"
]


class MemeCoinScout:
    """Scout for low-cap meme coins using CoinGecko"""
    
    def __init__(self, max_mcap: float = 100_000_000):
        """
        Args:
            max_mcap: Maximum market cap in USD (default $100M)
        """
        self.max_mcap = max_mcap
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "MemeCoinScout/1.0"
        })
        self._last_request_time = 0
        self._min_delay = 2.0  # seconds between requests (free tier safe)
    
    def _rate_limit(self):
        """Respect CoinGecko free tier rate limits"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a rate-limited GET request"""
        self._rate_limit()
        url = f"{COINGECKO_BASE}/{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=15)
            if response.status_code == 429:
                print(f"  Rate limited. Waiting 60s...")
                time.sleep(60)
                return self._get(endpoint, params)  # Retry once
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            return None
    
    def fetch_meme_coins(self, per_page: int = 100, page: int = 1) -> List[Dict]:
        """
        Fetch coins from the 'meme-token' category on CoinGecko.
        Returns list of coins with basic data.
        """
        print(f"\nFetching meme coins (page {page}, {per_page} per page)...")
        
        # Method 1: Search by category (if available)
        params = {
            "vs_currency": "usd",
            "category": "meme-token",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "24h,7d,30d"
        }
        
        data = self._get("coins/markets", params)
        if data:
            return data
        
        # Fallback: Get top coins and filter by known meme IDs
        print("  Category search failed, trying top coins fallback...")
        return self._fetch_top_coins_and_filter(per_page)
    
    def _fetch_top_coins_and_filter(self, limit: int = 250) -> List[Dict]:
        """Fallback: fetch top coins and filter known meme coins"""
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "price_change_percentage": "24h,7d,30d"
        }
        
        data = self._get("coins/markets", params)
        if not data:
            return []
        
        # Known meme coin IDs (verified on CoinGecko)
        meme_ids = {
            "bonk", "floki", "pepe", "shiba-inu", "dogecoin",
            "dogwifhat", "memecoin", "book-of-meme", "brett",
            "mog-coin", "popcat", "spx6900", "gigachad-2",
            "turbo", "harrypotterobamasonic10in", "wojak",
            "bobacoin", "fomo", "dejitaru-tsuka",
            "volt-inu", "catcoin", "monkey-pox"
        }
        
        filtered = []
        for coin in data:
            coin_id = coin.get("id", "").lower()
            symbol = coin.get("symbol", "").lower()
            name = coin.get("name", "").lower()
            
            # Check if it's a known meme coin
            is_meme = (
                coin_id in meme_ids or
                symbol in meme_ids or
                any(meme in name for meme in ["doge", "pepe", "shib", "meme", "cat", "wojak"])
            )
            
            if is_meme:
                filtered.append(coin)
        
        return filtered
    
    def filter_low_cap(self, coins: List[Dict]) -> List[Dict]:
        """Filter coins for market cap under threshold"""
        low_caps = []
        
        for coin in coins:
            mcap = coin.get("market_cap") or 0
            if 0 < mcap < self.max_mcap:
                low_caps.append({
                    "id": coin["id"],
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "current_price": coin.get("current_price", 0),
                    "market_cap": mcap,
                    "market_cap_rank": coin.get("market_cap_rank", 999999),
                    "total_volume": coin.get("total_volume", 0),
                    "price_change_24h": coin.get("price_change_24h", 0),
                    "price_change_percentage_24h": coin.get("price_change_percentage_24h", 0),
                    "price_change_percentage_7d_in_currency": coin.get("price_change_percentage_7d_in_currency", 0),
                    "price_change_percentage_30d_in_currency": coin.get("price_change_percentage_30d_in_currency", 0),
                    "circulating_supply": coin.get("circulating_supply", 0),
                    "total_supply": coin.get("total_supply", 0),
                    "ath": coin.get("ath", 0),
                    "ath_change_percentage": coin.get("ath_change_percentage", 0),
                    "ath_date": coin.get("ath_date", ""),
                    "image": coin.get("image", ""),
                    "last_updated": coin.get("last_updated", "")
                })
        
        # Sort by market cap descending
        low_caps.sort(key=lambda x: x["market_cap"], reverse=True)
        return low_caps
    
    def display_coins(self, coins: List[Dict], title: str = "Low-Cap Meme Coins"):
        """Pretty print coin list"""
        print(f"\n{'='*80}")
        print(f"{title}")
        print(f"{'='*80}")
        print(f"Filter: Market Cap < ${self.max_mcap/1_000_000:.0f}M")
        print(f"Found: {len(coins)} coins")
        print(f"{'='*80}")
        
        if not coins:
            print("No coins found matching criteria.")
            return
        
        # Header
        print(f"\n{'#':<4} {'Symbol':<8} {'Name':<20} {'Price':<14} {'MCap':<12} {'24h':<8} {'7d':<8} {'30d':<8}")
        print("-" * 80)
        
        for i, coin in enumerate(coins[:25], 1):  # Show top 25
            print(
                f"{i:<4} "
                f"{coin['symbol']:<8} "
                f"{coin['name'][:19]:<20} "
                f"${coin['current_price']:<13.8f} "
                f"${coin['market_cap']/1_000_000:<11.2f}M "
                f"{coin['price_change_percentage_24h'] or 0:<+7.1f}% "
                f"{coin['price_change_percentage_7d_in_currency'] or 0:<+7.1f}% "
                f"{coin['price_change_percentage_30d_in_currency'] or 0:<+7.1f}%"
            )
        
        if len(coins) > 25:
            print(f"\n... and {len(coins) - 25} more coins")
    
    def save_coin_list(self, coins: List[Dict], filename: str = "low_cap_meme_coins.json"):
        """Save coin list to JSON"""
        filepath = os.path.join(DATA_DIR, filename)
        data = {
            "generated_at": datetime.now().isoformat(),
            "max_market_cap": self.max_mcap,
            "count": len(coins),
            "coins": coins
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved to: {filepath}")
    
    def fetch_historical_data(self, coin_id: str, days: int = 365) -> Optional[Dict]:
        """
        Fetch historical OHLC data for a coin.
        CoinGecko free tier limits: max 365 days for daily data.
        """
        print(f"\nFetching {days}-day history for {coin_id}...")
        
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily"
        }
        
        data = self._get(f"coins/{coin_id}/market_chart", params)
        if not data:
            return None
        
        # Parse into clean format
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
        metrics = self._calculate_metrics(history)
        
        return {
            "coin_id": coin_id,
            "days": len(history),
            "history": history,
            "metrics": metrics
        }
    
    def _calculate_metrics(self, history: List[Dict]) -> Dict:
        """Calculate key metrics from price history"""
        if len(history) < 2:
            return {}
        
        prices = [h["price"] for h in history]
        volumes = [h["volume"] for h in history]
        
        # Basic stats
        latest = prices[-1]
        earliest = prices[0]
        
        # Returns
        total_return = ((latest - earliest) / earliest * 100) if earliest > 0 else 0
        
        # Volatility (daily returns std dev, annualized)
        daily_returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                daily_returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        volatility = 0
        if daily_returns:
            import statistics
            volatility = statistics.stdev(daily_returns) * (365 ** 0.5) * 100
        
        # Volume metrics
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        max_volume = max(volumes) if volumes else 0
        
        # Price extremes
        max_price = max(prices)
        min_price = min(prices)
        
        # Moving averages
        ma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else latest
        ma_30 = sum(prices[-30:]) / 30 if len(prices) >= 30 else latest
        
        return {
            "total_return_pct": round(total_return, 2),
            "volatility_annualized_pct": round(volatility, 2),
            "avg_daily_volume": round(avg_volume, 2),
            "max_daily_volume": round(max_volume, 2),
            "max_price": round(max_price, 8),
            "min_price": round(min_price, 8),
            "price_range_pct": round((max_price - min_price) / min_price * 100, 2) if min_price > 0 else 0,
            "ma_7": round(ma_7, 8),
            "ma_30": round(ma_30, 8),
            "price_vs_ma7_pct": round((latest - ma_7) / ma_7 * 100, 2) if ma_7 > 0 else 0,
            "price_vs_ma30_pct": round((latest - ma_30) / ma_30 * 100, 2) if ma_30 > 0 else 0,
            "data_points": len(history)
        }
    
    def save_history(self, coin_id: str, data: Dict):
        """Save historical data to JSON"""
        symbol = coin_id.upper().replace("-", "_")
        filepath = os.path.join(DATA_DIR, f"{symbol}_history.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved history: {filepath} ({data['days']} days)")


def main():
    """Demo: Fetch and display low-cap meme coins"""
    scout = MemeCoinScout(max_mcap=100_000_000)
    
    print("=" * 80)
    print("MEME COIN SCOUT - Finding Low-Cap Gems")
    print("=" * 80)
    print(f"Target: Coins under ${scout.max_mcap/1_000_000:.0f}M market cap")
    print("Source: CoinGecko API (free tier)")
    print("=" * 80)
    
    # Step 1: Fetch meme coins
    print("\n[Step 1] Fetching meme coin list...")
    coins = scout.fetch_meme_coins(per_page=100)
    
    if not coins:
        print("Failed to fetch coins. Check internet/Rate limits.")
        return
    
    print(f"  Found {len(coins)} total meme coins")
    
    # Step 2: Filter for low market cap
    print("\n[Step 2] Filtering for market cap < $100M...")
    low_caps = scout.filter_low_cap(coins)
    
    # Step 3: Display
    scout.display_coins(low_caps)
    
    # Step 4: Save list
    scout.save_coin_list(low_caps)
    
    # Step 5: Fetch history for top picks (optional - limited by rate limits)
    print(f"\n{'='*80}")
    print("[Step 3] Fetching historical data for top 3 coins...")
    print("Note: CoinGecko free tier = ~10-15 historical calls per minute")
    print(f"{'='*80}")
    
    for coin in low_caps[:3]:
        history = scout.fetch_historical_data(coin["id"], days=365)
        if history:
            scout.save_history(coin["id"], history)
            print(f"\n  Metrics for {coin['symbol']}:")
            for key, val in history["metrics"].items():
                print(f"    {key}: {val}")
        else:
            print(f"  Failed to fetch history for {coin['symbol']}")
    
    print(f"\n{'='*80}")
    print("SCAN COMPLETE")
    print(f"{'='*80}")
    print(f"Total coins found: {len(low_caps)}")
    print(f"Data saved to: {DATA_DIR}/")
    print(f"Next: Run with different filters or analyze specific coins")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
