#!/usr/bin/env python3
"""
MEME COIN ANALYZER
Focused on meme coins with market cap under $1B USD
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os

class MemeCoinAnalyzer:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'CortexMemeAnalyzer/1.0'
        })
        self.data_dir = os.path.join(os.path.dirname(__file__), 'meme_coin_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def get_meme_coins(self, limit=250):
        """Fetch coins from CoinGecko"""
        print("Fetching coin list from CoinGecko...")
        
        url = f"{self.base_url}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h,7d,30d'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            coins = response.json()
            print(f"Got {len(coins)} coins")
            return coins
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coins: {e}")
            return []
    
    def identify_meme_coins(self, coins):
        """Identify meme coins from list"""
        meme_keywords = [
            'doge', 'shib', 'pepe', 'floki', 'bonk', 'wojak', 'meme', 
            'dog', 'cat', 'frog', 'elon', 'moon', 'safe', 'baby',
            'inu', 'shiba', 'akita', 'kishu', 'saitama', 'feg',
            'cumrocket', 'hokk', 'pit', 'wolf', 'poodl', 'banano',
            'garlic', 'mona', 'nyan', 'troll', 'turbo', 'bob',
            'ladys', 'arb', 'aidoge', 'mong', 'rfd', 'psyop',
            'ben', 'wagmi', 'gme', 'amc', 'corn', 'mog', 'bome',
            'wif', 'boden', 'tremp', 'michi', 'popcat', 'giga',
            'bome', 'sloth', 'pnut', 'ai16z', 'zerebro', 'luce',
            'fartcoin', 'buttcoin', 'retardio', 'mubarak'
        ]
        
        meme_coins = []
        
        for coin in coins:
            symbol = coin.get('symbol', '').lower()
            name = coin.get('name', '').lower()
            coin_id = coin.get('id', '').lower()
            
            is_meme = any(keyword in symbol or keyword in name or keyword in coin_id 
                         for keyword in meme_keywords)
            
            # Additional heuristic
            price = coin.get('current_price', 0) or 0
            volume = coin.get('total_volume', 0) or 0
            mcap = coin.get('market_cap', 0) or 0
            
            if mcap > 0 and volume / mcap > 0.5:
                is_meme = True
            
            if is_meme:
                meme_coins.append(coin)
        
        return meme_coins
    
    def filter_by_market_cap(self, coins, max_mcap=1_000_000_000):
        """Filter coins with market cap below threshold"""
        filtered = []
        
        for coin in coins:
            mcap = coin.get('market_cap') or 0
            
            if 0 < mcap < max_mcap:
                filtered.append({
                    'id': coin.get('id'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'current_price': coin.get('current_price', 0),
                    'market_cap': mcap,
                    'market_cap_formatted': self.format_mcap(mcap),
                    'total_volume_24h': coin.get('total_volume', 0),
                    'volume_formatted': self.format_volume(coin.get('total_volume', 0)),
                    'price_change_24h': coin.get('price_change_percentage_24h', 0),
                    'price_change_7d': coin.get('price_change_percentage_7d_in_currency', 0),
                    'price_change_30d': coin.get('price_change_percentage_30d_in_currency', 0),
                    'ath': coin.get('ath', 0),
                    'ath_change_percentage': coin.get('ath_change_percentage', 0),
                    'image': coin.get('image'),
                })
        
        filtered.sort(key=lambda x: x['market_cap'], reverse=True)
        return filtered
    
    def format_mcap(self, mcap):
        if mcap >= 1_000_000_000:
            return f"${mcap/1_000_000_000:.2f}B"
        elif mcap >= 1_000_000:
            return f"${mcap/1_000_000:.2f}M"
        elif mcap >= 1_000:
            return f"${mcap/1_000:.2f}K"
        else:
            return f"${mcap:.2f}"
    
    def format_volume(self, volume):
        if volume >= 1_000_000_000:
            return f"${volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"${volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"${volume/1_000:.2f}K"
        else:
            return f"${volume:.2f}"
    
    def get_historical_data(self, coin_id, days=365):
        """Fetch historical daily price data"""
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Build simple list of daily data
            prices = data.get('prices', [])
            market_caps = data.get('market_caps', [])
            volumes = data.get('total_volumes', [])
            
            history = []
            for i in range(len(prices)):
                ts = prices[i][0]
                date = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d')
                
                history.append({
                    'date': date,
                    'timestamp': ts,
                    'price': prices[i][1],
                    'market_cap': market_caps[i][1] if i < len(market_caps) else 0,
                    'volume': volumes[i][1] if i < len(volumes) else 0
                })
            
            return history
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data for {coin_id}: {e}")
            return None
    
    def calculate_metrics(self, history):
        """Calculate basic metrics from historical data"""
        if not history or len(history) < 2:
            return {}
        
        # Get latest and past prices
        latest = history[-1]
        price_1d = history[-2]['price'] if len(history) >= 2 else latest['price']
        price_7d = history[-8]['price'] if len(history) >= 8 else latest['price']
        price_30d = history[-31]['price'] if len(history) >= 31 else latest['price']
        
        # Calculate price changes
        price_changes = []
        for i in range(1, len(history)):
            change = (history[i]['price'] - history[i-1]['price']) / history[i-1]['price'] * 100
            price_changes.append(change)
        
        # Volatility (standard deviation of daily returns)
        volatility = 0
        if price_changes:
            mean = sum(price_changes) / len(price_changes)
            variance = sum((x - mean) ** 2 for x in price_changes) / len(price_changes)
            volatility = variance ** 0.5
        
        metrics = {
            'current_price': latest['price'],
            'current_mcap': latest['market_cap'],
            'current_volume': latest['volume'],
            'price_change_1d': (latest['price'] - price_1d) / price_1d * 100 if price_1d > 0 else 0,
            'price_change_7d': (latest['price'] - price_7d) / price_7d * 100 if price_7d > 0 else 0,
            'price_change_30d': (latest['price'] - price_30d) / price_30d * 100 if price_30d > 0 else 0,
            'volatility': volatility,
            'avg_volume_7d': sum(h['volume'] for h in history[-7:]) / min(7, len(history)),
            'avg_volume_30d': sum(h['volume'] for h in history[-30:]) / min(30, len(history)),
            'data_points': len(history),
            'date_range': f"{history[0]['date']} to {history[-1]['date']}"
        }
        
        return metrics
    
    def analyze_top_meme_coins(self, max_mcap=1_000_000_000, top_n=20):
        """Main analysis pipeline"""
        print("=" * 80)
        print("MEME COIN ANALYZER")
        print("Focus: Market Cap < $1B")
        print("=" * 80)
        print()
        
        # Step 1: Get all coins
        all_coins = self.get_meme_coins(limit=250)
        
        if not all_coins:
            print("Failed to fetch coins")
            return []
        
        # Step 2: Identify meme coins
        print("\nIdentifying meme coins...")
        meme_coins = self.identify_meme_coins(all_coins)
        print(f"Found {len(meme_coins)} potential meme coins")
        
        # Step 3: Filter by market cap
        print(f"\nFiltering for market cap < $1B...")
        filtered = self.filter_by_market_cap(meme_coins, max_mcap)
        print(f"Found {len(filtered)} meme coins under $1B")
        
        # Step 4: Display results
        print("\n" + "=" * 80)
        print("TOP MEME COINS (Under $1B Market Cap)")
        print("=" * 80)
        print()
        
        for i, coin in enumerate(filtered[:top_n], 1):
            print(f"{i}. ${coin['symbol']} - {coin['name']}")
            print(f"   Price: ${coin['current_price']:.6f}")
            print(f"   Market Cap: {coin['market_cap_formatted']}")
            print(f"   Volume 24h: {coin['volume_formatted']}")
            print(f"   24h Change: {coin['price_change_24h']:.2f}%")
            print(f"   7d Change: {coin['price_change_7d']:.2f}%")
            print(f"   30d Change: {coin.get('price_change_30d', 0) or 0:.2f}%")
            
            if coin.get('ath') and coin['ath'] > 0:
                print(f"   ATH: ${coin['ath']:.6f} ({coin['ath_change_percentage']:.1f}% from ATH)")
            
            print()
        
        return filtered[:top_n]
    
    def deep_analysis(self, coin_id, days=365):
        """Perform deep analysis on a single coin"""
        print(f"\nDeep Analysis: {coin_id}")
        print("=" * 80)
        
        # Fetch historical data
        print(f"Fetching {days} days of historical data...")
        history = self.get_historical_data(coin_id, days)
        
        if history:
            print(f"Got {len(history)} data points")
            
            # Calculate metrics
            metrics = self.calculate_metrics(history)
            
            print("\nMETRICS:")
            print(f"   Current Price: ${metrics['current_price']:.6f}")
            print(f"   Market Cap: ${metrics['current_mcap']:,.0f}")
            print(f"   Volume: ${metrics['current_volume']:,.0f}")
            print(f"\nPRICE CHANGES:")
            print(f"   1D: {metrics['price_change_1d']:.2f}%")
            print(f"   7D: {metrics['price_change_7d']:.2f}%")
            print(f"   30D: {metrics['price_change_30d']:.2f}%")
            print(f"\nVOLATILITY:")
            print(f"   Daily: {metrics['volatility']:.2f}%")
            print(f"\nVOLUME:")
            print(f"   7D Average: ${metrics['avg_volume_7d']:,.0f}")
            print(f"   30D Average: ${metrics['avg_volume_30d']:,.0f}")
            
            return metrics
        else:
            print("Failed to get historical data")
            return None


def main():
    analyzer = MemeCoinAnalyzer()
    
    # Get list of meme coins under $1B
    coins = analyzer.analyze_top_meme_coins(max_mcap=1_000_000_000, top_n=20)
    
    print("\n" + "=" * 80)
    print("Want deep analysis on any coin?")
    print("Run: python meme-coin-analyzer.py --deep <coin_id> [days]")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == '--deep':
        analyzer = MemeCoinAnalyzer()
        coin_id = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 365
        analyzer.deep_analysis(coin_id, days)
    else:
        main()
