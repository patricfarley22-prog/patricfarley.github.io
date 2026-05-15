# Meme Coin Analyzer

A Python tool to analyze meme coins with market cap under $1B USD.

## Features

- Fetches top coins from CoinGecko API
- Identifies meme coins using keyword matching + volume heuristics
- Filters for market cap < $1B
- Pulls historical daily price data (1-2 years)
- Calculates metrics:
  - Price changes (1D, 7D, 30D)
  - Volatility (daily standard deviation)
  - Volume averages (7D, 30D)
  - All-time high vs current price

## Installation

```bash
pip install requests
```

## Usage

### List meme coins under $1B
```bash
python meme-coin-analyzer.py
```

### Deep analysis on specific coin
```bash
python meme-coin-analyzer.py --deep <coin_id> [days]
```

Example:
```bash
python meme-coin-analyzer.py --deep bonk 90
```

## Current Results (Top 15 Meme Coins Under $1B)

| # | Symbol | Name | Price | Market Cap | 24h Volume | 24h Change |
|---|--------|------|-------|-----------|------------|-----------|
| 1 | BCAP | Blockchain Capital | $105.87 | $964.7M | $0 | 0.00% |
| 2 | ARB | Arbitrum | $0.12 | $758.7M | $67.5M | -7.49% |
| 3 | JUP | Jupiter | $0.21 | $695.8M | $31.4M | -7.50% |
| 4 | BONK | Bonk | $0.000006 | $571.7M | $52.9M | -6.88% |
| 5 | BILL | Billions Network | $0.20 | $480.8M | $2.2B | +0.12% |
| 6 | FDUSD | First Digital USD | $0.998 | $393.7M | $206.3M | -0.02% |
| 7 | MON | Monad | $0.028 | $335.5M | $109.9M | -6.05% |
| 8 | FLOKI | FLOKI | $0.000033 | $316.5M | $39.0M | -6.39% |
| 9 | LAB | LAB | $3.98 | $305.0M | $205.0M | -26.57% |
| 10 | APEPE | Ape and Pepe | $0.000001 | $250.2M | $26.5M | -3.97% |
| 11 | RUSD | Royal Dollar | $1.00 | $249.9M | $133.0M | -0.01% |
| 12 | WIF | dogwifhat | $0.20 | $202.7M | $59.1M | -8.83% |
| 13 | FARTCOIN | Fartcoin | $0.20 | $197.1M | $43.0M | -9.60% |
| 14 | SFP | SafePal | $0.29 | $146.6M | $1.9M | -5.68% |
| 15 | IRYS | Irys | $0.064 | $129.5M | $83.9M | +20.70% |

## Notable Findings

### Top Movers (7D)
- BILL: +137.89% (Billions Network)
- IRYS: +73.29% (Irys)

### Biggest Drops (7D)
- APEPE: -20.89%
- FARTCOIN: -18.63%
- MON: -13.24%

### High Volume
- BILL: $2.17B (massive volume for its size)
- FDUSD: $206.3M
- LAB: $205.0M

## API Notes

- Uses CoinGecko free tier
- Rate limit: 10-30 calls/minute
- Some coins may return 404 (not in CoinGecko database)
- For Solana meme coins, use DexScreener for better coverage

## Next Steps

1. Add Solana-specific meme coins via DexScreener
2. Integrate with quantum analyzer for signal generation
3. Add social sentiment tracking
4. Build backtesting engine
5. Create alert system for price moves
