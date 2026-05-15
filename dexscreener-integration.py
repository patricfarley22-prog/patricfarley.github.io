#!/usr/bin/env python3
"""
DEXSCREENER INTEGRATION FOR SOLANA MEME COINS
Fetches real-time data without CoinGecko rate limits
"""

import requests
import json
import os
from datetime import datetime

class DexScreenerIntegration:
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
        self.data_dir = 'meme_coin_data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_token_data(self, contract_address):
        """Fetch real-time data for a Solana token"""
        url = f"{self.base_url}/tokens/{contract_address}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pairs = data.get('pairs', [])
            if not pairs:
                return None
            
            # Get the pair with highest liquidity
            best_pair = max(pairs, key=lambda x: x.get('liquidity', {}).get('usd', 0))
            
            return {
                'symbol': best_pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                'name': best_pair.get('baseToken', {}).get('name', 'Unknown'),
                'contract_address': contract_address,
                'price': float(best_pair.get('priceUsd', 0)),
                'market_cap': float(best_pair.get('marketCap', 0)),
                'liquidity': float(best_pair.get('liquidity', {}).get('usd', 0)),
                'volume_24h': float(best_pair.get('volume', {}).get('h24', 0)),
                'volume_1h': float(best_pair.get('volume', {}).get('h1', 0)),
                'price_change_1h': float(best_pair.get('priceChange', {}).get('h1', 0)),
                'price_change_24h': float(best_pair.get('priceChange', {}).get('h24', 0)),
                'price_change_7d': float(best_pair.get('priceChange', {}).get('h7', 0)),
                'buys_24h': int(best_pair.get('txns', {}).get('h24', {}).get('buys', 0)),
                'sells_24h': int(best_pair.get('txns', {}).get('h24', {}).get('sells', 0)),
                'dex': best_pair.get('dexId', 'Unknown'),
                'pair_address': best_pair.get('pairAddress', ''),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching {contract_address}: {e}")
            return None
    
    def fetch_multiple_tokens(self, contract_addresses):
        """Fetch data for multiple tokens"""
        results = []
        
        for ca in contract_addresses:
            print(f"Fetching {ca[:8]}...", end=" ")
            
            data = self.fetch_token_data(ca)
            if data:
                print(f"OK - ${data['price']:.8f}")
                results.append(data)
            else:
                print("FAILED")
            
            # Rate limiting (DexScreener allows 60 req/min)
            import time
            time.sleep(1)
        
        return results
    
    def search_solana_meme_coins(self, query="solana"):
        """Search for Solana meme coins"""
        url = f"{self.base_url}/search"
        params = {'q': query}
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            pairs = data.get('pairs', [])
            
            # Filter for Solana pairs with reasonable liquidity
            solana_pairs = [
                p for p in pairs
                if p.get('chainId') == 'solana'
                and p.get('liquidity', {}).get('usd', 0) > 10000  # Min $10K liquidity
            ]
            
            return solana_pairs
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def identify_meme_coins(self, pairs):
        """Identify meme coins from pairs"""
        meme_keywords = [
            'bonk', 'wif', 'dogwifhat', 'pepe', 'floki', 'shib', 'doge',
            'fartcoin', 'mog', 'giga', 'popcat', 'michi', 'boden', 'tremp',
            'retardio', 'zerebro', 'ai16z', 'fwog', 'pnut', 'sloth',
            'bome', 'pengo', 'tokabu', 'omegax', 'hachi', 'troll',
            'dust', 'blue', 'chip', 'royal', 'lab', 'apepe'
        ]
        
        meme_coins = []
        seen = set()
        
        for pair in pairs:
            symbol = (pair.get('baseToken', {}).get('symbol') or '').lower()
            name = (pair.get('baseToken', {}).get('name') or '').lower()
            ca = pair.get('baseToken', {}).get('address', '')
            
            if not ca or ca in seen:
                continue
            
            is_meme = any(kw in symbol or kw in name for kw in meme_keywords)
            
            mcap = pair.get('marketCap', 0) or 0
            
            if is_meme and 0 < mcap < 1_000_000_000:
                seen.add(ca)
                meme_coins.append({
                    'symbol': pair['baseToken']['symbol'].upper(),
                    'name': pair['baseToken']['name'],
                    'contract_address': ca,
                    'price': float(pair.get('priceUsd', 0)),
                    'market_cap': mcap,
                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                    'dex': pair.get('dexId', 'Unknown')
                })
        
        # Sort by market cap
        meme_coins.sort(key=lambda x: x['market_cap'], reverse=True)
        return meme_coins
    
    def save_data(self, data, filename):
        """Save data to file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return filepath
    
    def display_meme_coins(self, coins):
        """Display meme coins in table format"""
        print("\n" + "=" * 100)
        print("SOLANA MEME COINS (From DexScreener)")
        print("=" * 100)
        print()
        
        print(f"{'#':<4} {'Symbol':<8} {'Price':<14} {'Market Cap':<12} {'Liquidity':<12} {'24h Vol':<12} {'24h':<8} {'DEX':<10}")
        print("-" * 100)
        
        for i, coin in enumerate(coins[:20], 1):
            print(
                f"{i:<4} {coin['symbol']:<8} "
                f"${coin['price']:<13.8f} "
                f"${coin['market_cap']/1_000_000:<11.1f}M "
                f"${coin['liquidity']/1_000:<11.1f}K "
                f"${coin['volume_24h']/1_000_000:<11.1f}M "
                f"{coin['price_change_24h']:>+6.1f}% "
                f"{coin['dex']:<10}"
            )
        
        print("\n" + "=" * 100)
        print(f"Showing top 20 of {len(coins)} meme coins")
        print("=" * 100)


def main():
    print("=" * 80)
    print("DEXSCREENER SOLANA MEME COIN FINDER")
    print("=" * 80)
    print()
    
    dex = DexScreenerIntegration()
    
    # Search for Solana meme coins
    print("Searching for Solana meme coins...")
    pairs = dex.search_solana_meme_coins("solana")
    print(f"Found {len(pairs)} Solana pairs")
    
    # Identify meme coins
    meme_coins = dex.identify_meme_coins(pairs)
    print(f"Identified {len(meme_coins)} meme coins under $1B")
    
    # Display
    dex.display_meme_coins(meme_coins)
    
    # Save
    filepath = dex.save_data(meme_coins, 'dexscreener-meme-coins.json')
    print(f"\nData saved to: {filepath}")
    
    # Test fetching specific tokens
    print("\n" + "=" * 80)
    print("FETCHING SPECIFIC TOKENS")
    print("=" * 80)
    
    test_tokens = [
        '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2',  # TROLL
        'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump',  # DOWGE
    ]
    
    results = dex.fetch_multiple_tokens(test_tokens)
    
    for r in results:
        print(f"\n{r['symbol']}:")
        print(f"  Price: ${r['price']:.10f}")
        print(f"  Market Cap: ${r['market_cap']:,.0f}")
        print(f"  24h Change: {r['price_change_24h']:+.2f}%")
        print(f"  Liquidity: ${r['liquidity']:,.0f}")
        print(f"  Volume 24h: ${r['volume_24h']:,.0f}")


if __name__ == "__main__":
    main()
