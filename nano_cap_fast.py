#!/usr/bin/env python3
"""
NANO-CAP MEME COIN SCANNER
Uses DexScreener token profiles + search
"""

import requests
import json
import os
from datetime import datetime

DATA_DIR = "meme_coin_data"

def fetch_token_profiles():
    """Fetch token profiles from DexScreener"""
    try:
        r = requests.get("https://api.dexscreener.com/token-profiles/latest/v1", timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def fetch_boosted():
    """Fetch boosted tokens"""
    try:
        r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def search_token(query):
    """Search for specific token"""
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query}", timeout=10)
        if r.status_code == 200:
            return r.json().get('pairs', [])
        return []
    except:
        return []

def get_token_details(chain, token):
    """Get token details with price"""
    try:
        r = requests.get(f"https://api.dexscreener.com/tokens/v1/{chain}/{token}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def is_meme(name, symbol):
    text = (name + ' ' + symbol).lower()
    keywords = ['doge', 'shib', 'pepe', 'floki', 'bonk', 'wojak', 'troll', 
                'cat', 'inu', 'moon', 'elon', 'frog', 'chad', 'based', 'dog',
                'musk', 'pump', 'meme', 'woof', 'meow', 'pop', 'dust']
    return any(kw in text for kw in keywords)

def analyze():
    print("=" * 80)
    print("NANO-CAP MEME COIN SCANNER")
    print("=" * 80)
    
    print("\n[1/3] Fetching token profiles...")
    profiles = fetch_token_profiles()
    print(f"  Found {len(profiles)} profiles")
    
    print("\n[2/3] Fetching boosted tokens...")
    boosted = fetch_boosted()
    print(f"  Found {len(boosted)} boosted")
    
    # Combine unique
    all_tokens = {}
    for p in profiles + boosted:
        tok = p.get('tokenAddress', '')
        if tok:
            all_tokens[tok] = p
    
    print(f"\n[3/3] Analyzing {len(all_tokens)} unique tokens...")
    meme_coins = []
    nano_caps = []
    
    for token_addr, profile in list(all_tokens.items())[:20]:
        try:
            chain = profile.get('chainId', 'solana')
            
            # Get price data
            details = get_token_details(chain, token_addr)
            if not details:
                continue
            
            # Use first pair
            pair = details[0] if isinstance(details, list) else details
            
            base = pair.get('baseToken', {})
            symbol = base.get('symbol', 'UNK')
            name = base.get('name', '')
            
            if not is_meme(name, symbol):
                continue
            
            # Extract metrics
            mcap = float(pair.get('marketCap', 0) or 0)
            fdv = float(pair.get('fdv', 0) or 0)
            price = float(pair.get('priceUsd', 0) or 0)
            vol = float(pair.get('volume', {}).get('h24', 0) or 0)
            chg_24h = float(pair.get('priceChange', {}).get('h24', 0) or 0)
            liq = float(pair.get('liquidity', {}).get('usd', 0) or 0)
            
            coin = {
                'symbol': symbol.upper(),
                'name': name,
                'market_cap': mcap if mcap > 0 else fdv,
                'price': price,
                'volume_24h': vol,
                'change_24h': chg_24h,
                'liquidity': liq,
                'chain': chain,
                'token': token_addr
            }
            
            meme_coins.append(coin)
            
            if 0 < coin['market_cap'] < 10_000_000:
                nano_caps.append(coin)
                
        except Exception as e:
            continue
    
    return meme_coins, nano_caps

def display_meme(meme_coins):
    if not meme_coins:
        print("\nNo meme coins found in current data")
        return
    
    print(f"\n{'='*80}")
    print(f"MEME COINS FOUND: {len(meme_coins)}")
    print(f"{'='*80}")
    print(f"\n{'#':<4} {'Symbol':<10} {'Chain':<8} {'MCap':<12} {'24h':<8} {'Liq':<12}")
    print("-" * 60)
    
    for i, c in enumerate(meme_coins, 1):
        mcap = c['market_cap']
        if mcap > 1_000_000:
            mcap_str = f"${mcap/1_000_000:.1f}M"
        elif mcap > 0:
            mcap_str = f"${mcap:,.0f}"
        else:
            mcap_str = "N/A"
        print(f"{i:<4} {c['symbol']:<10} {c['chain']:<8} {mcap_str:<12} {c['change_24h']:<+7.1f}% ${c['liquidity']:,.0f}")

def display_nano(nano_caps):
    if not nano_caps:
        print(f"\n{'='*80}")
        print("NO NANO-CAPS UNDER $10M")
        print("="*80)
        return
    
    print(f"\n{'='*80}")
    print(f"NANO-CAPS UNDER $10M: {len(nano_caps)}")
    print(f"{'='*80}")
    print(f"\n{'#':<4} {'Symbol':<10} {'MCap':<10} {'Price':<12} {'24h':<8} {'Liq':<10}")
    print("-" * 60)
    
    for i, c in enumerate(nano_caps, 1):
        print(f"{i:<4} {c['symbol']:<10} ${c['market_cap']/1_000_000:<9.3f}M "
              f"${c['price']:<11.8f} {c['change_24h']:<+7.1f}% ${c['liquidity']/1000:<9.1f}K")
    
    print(f"\n{'='*80}")
    print("TOP NANO-CAP PICKS:")
    for c in nano_caps[:5]:
        print(f"\n  {c['symbol']} - {c['name']}")
        print(f"    MCap: ${c['market_cap']/1_000_000:.3f}M | Price: ${c['price']:.8f}")
        print(f"    24h: {c['change_24h']:+.1f}% | Volume: ${c['volume_24h']:,.0f}")
        print(f"    Liquidity: ${c['liquidity']:,.0f}")
        print(f"    Token: {c['token'][:35]}")

def main():
    print("\nNano-Cap Meme Coin Scanner")
    print("DexScreener API - Real-time data\n")
    
    meme_coins, nano_caps = analyze()
    
    display_meme(meme_coins)
    display_nano(nano_caps)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/nano_cap_scan.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_meme": len(meme_coins),
            "nano_caps": len(nano_caps),
            "meme_coins": meme_coins,
            "nano_cap_coins": nano_caps
        }, f, indent=2)
    
    if nano_caps:
        print(f"\nSaved: {DATA_DIR}/nano_cap_scan.json")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
