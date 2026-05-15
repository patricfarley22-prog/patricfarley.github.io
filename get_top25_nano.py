#!/usr/bin/env python3
"""Fetch top 25 meme coins under $10M market cap from CoinGecko"""

import requests
import json
import time

print("Fetching from CoinGecko API...")
print("Getting coins with market cap data...")

# Fetch more pages to find coins with actual market cap
all_coins = []
for page in range(1, 5):  # Pages 1-4
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_asc',
        'per_page': 250,
        'page': page,
        'price_change_percentage': '24h,7d,30d'
    }
    
    response = requests.get(url, params=params, timeout=15)
    if response.status_code == 429:
        print("Rate limited, waiting...")
        time.sleep(60)
        continue
    
    data = response.json()
    print(f"Page {page}: Got {len(data)} coins")
    
    for coin in data:
        mcap = coin.get('market_cap') or 0
        if mcap > 0:
            all_coins.append(coin)
    
    if len(data) < 250:
        break

print(f"\nTotal coins with market cap data: {len(all_coins)}")

# Now filter for meme coins under $10M
meme_keywords = ['doge', 'shib', 'pepe', 'meme', 'wojak', 'bonk', 'floki', 'cat', 'dog', 'frog', 'inu', 'elon', 'moon', 'chad', 'giga', 'turbo', 'ponke', 'mog', 'popcat', 'snek', 'wif', 'harry', 'potter', 'obama', 'sonic', 'trump', 'maga', 'based', 'degen', 'ape', 'pump', 'cum', 'cumrocket', 'safe', 'mars', 'rocket', 'shib', 'inu', 'doge', 'pepe', 'wojak', 'bonk', 'floki', 'cat', 'dog', 'frog']

meme_coins = []
for coin in all_coins:
    mcap = coin.get('market_cap') or 0
    if mcap > 0 and mcap < 10000000:
        coin_id = coin.get('id', '').lower()
        symbol = coin.get('symbol', '').lower()
        name = coin.get('name', '').lower()
        
        # Check if meme coin
        is_meme = any(kw in coin_id or kw in symbol or kw in name for kw in meme_keywords)
        
        if is_meme:
            meme_coins.append({
                'symbol': coin['symbol'].upper(),
                'name': coin['name'],
                'price': coin.get('current_price', 0),
                'mcap': mcap,
                'volume': coin.get('total_volume', 0) or 0,
                'change_24h': coin.get('price_change_percentage_24h', 0) or 0,
                'change_7d': coin.get('price_change_percentage_7d_in_currency', 0) or 0,
                'change_30d': coin.get('price_change_percentage_30d_in_currency', 0) or 0,
                'ath_change': coin.get('ath_change_percentage', 0) or 0
            })

# Sort by market cap descending
meme_coins.sort(key=lambda x: x['mcap'], reverse=True)

# Display
if meme_coins:
    print('\n' + '='*80)
    print(f'TOP {min(25, len(meme_coins))} MEME COINS UNDER $10M MARKET CAP')
    print('Source: CoinGecko API | Sorted by Market Cap Descending')
    print('='*80)
    print()
    print('Rank Symbol     Name                  Price          MCap      24h     7d      30d    ')
    print('-'*80)
    
    for i, coin in enumerate(meme_coins[:25], 1):
        print(f"{i:4d} {coin['symbol']:10s} {coin['name'][:21]:22s} ${coin['price']:13.8f} ${coin['mcap']/1000000:9.2f}M {coin['change_24h']:+7.1f}% {coin['change_7d']:+7.1f}% {coin['change_30d']:+7.1f}%")
    
    print()
    print(f"Total meme coins under $10M found: {len(meme_coins)}")
    print(f"Smallest: ${min(c['mcap'] for c in meme_coins)/1000:.1f}K | Largest: ${max(c['mcap'] for c in meme_coins)/1000000:.2f}M")
    
    # Save
    import os
    os.makedirs('meme_coin_data', exist_ok=True)
    with open('meme_coin_data/top25_nano_caps.json', 'w') as f:
        json.dump({'count': len(meme_coins), 'coins': meme_coins}, f, indent=2)
    
    print(f"\nSaved to: meme_coin_data/top25_nano_caps.json")
else:
    print("\nNo meme coins found under $10M")
    print("This could mean:")
    print("1. CoinGecko doesn't track many sub-$10M meme coins")
    print("2. Need to use DexScreener for real-time nano-caps")
    print("3. Most meme coins start on DEXs, not tracked by CoinGecko")
