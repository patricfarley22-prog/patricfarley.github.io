#!/usr/bin/env python3
"""
PAPER TRADING MODE - ASCII Version (no emojis)
Simulates trades without real money
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

class PaperTrader:
    """Paper trading simulator"""
    
    def __init__(self, initial_balance=1000.0):
        self.balance = initial_balance
        self.positions = {}
        self.trades = []
        self.load_state()
    
    def load_state(self):
        filepath = os.path.join(DATA_DIR, "paper_trading_state.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.balance = data.get("balance", 1000.0)
                self.positions = data.get("positions", {})
                self.trades = data.get("trades", [])
    
    def save_state(self):
        filepath = os.path.join(DATA_DIR, "paper_trading_state.json")
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "balance": self.balance,
                "positions": self.positions,
                "trades": self.trades,
                "total_trades": len(self.trades),
                "open_positions": len(self.positions)
            }, f, indent=2)
    
    def buy(self, symbol: str, price: float, amount: float = None, 
            target: float = None, stop_loss: float = None) -> Dict:
        """Simulate buy"""
        if amount is None:
            amount = self.balance * 0.1
        
        if amount > self.balance:
            return {"error": "Insufficient balance"}
        
        shares = amount / price
        self.balance -= amount
        
        position = {
            "symbol": symbol,
            "entry_price": price,
            "shares": shares,
            "cost": amount,
            "target": target or price * 2,
            "stop_loss": stop_loss or price * 0.8,
            "opened_at": datetime.now().isoformat(),
            "highest_price": price,
            "status": "OPEN"
        }
        
        self.positions[symbol] = position
        self.save_state()
        
        return {
            "action": "BUY",
            "symbol": symbol,
            "price": price,
            "shares": shares,
            "cost": amount,
            "balance_remaining": self.balance,
            "target": position["target"],
            "stop_loss": position["stop_loss"]
        }
    
    def sell(self, symbol: str, price: float, reason: str = "manual") -> Dict:
        """Simulate sell"""
        if symbol not in self.positions:
            return {"error": "No position found"}
        
        position = self.positions[symbol]
        shares = position["shares"]
        proceeds = shares * price
        pnl = proceeds - position["cost"]
        pnl_pct = (pnl / position["cost"]) * 100
        
        self.balance += proceeds
        
        trade = {
            "symbol": symbol,
            "entry_price": position["entry_price"],
            "exit_price": price,
            "shares": shares,
            "cost": position["cost"],
            "proceeds": proceeds,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "opened_at": position["opened_at"],
            "closed_at": datetime.now().isoformat(),
            "reason": reason,
            "target_hit": price >= position["target"],
            "stop_hit": price <= position["stop_loss"],
            "holding_hours": self._holding_hours(position["opened_at"])
        }
        
        self.trades.append(trade)
        del self.positions[symbol]
        self.save_state()
        
        return {
            "action": "SELL",
            "symbol": symbol,
            "price": price,
            "proceeds": proceeds,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "reason": reason,
            "balance": self.balance
        }
    
    def check_stop_losses(self, current_prices: Dict[str, float]):
        """Check and execute stop losses"""
        triggered = []
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                if current_price > position["highest_price"]:
                    position["highest_price"] = current_price
                
                if current_price <= position["stop_loss"]:
                    result = self.sell(symbol, current_price, "stop_loss")
                    triggered.append(result)
                elif current_price >= position["target"]:
                    result = self.sell(symbol, current_price, "target_hit")
                    triggered.append(result)
        
        return triggered
    
    def get_stats(self) -> Dict:
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0,
                "best_trade": None,
                "worst_trade": None,
                "balance": self.balance,
                "equity": self.balance,
                "roi_pct": 0
            }
        
        wins = [t for t in self.trades if t["pnl"] > 0]
        losses = [t for t in self.trades if t["pnl"] <= 0]
        
        total_pnl = sum(t["pnl"] for t in self.trades)
        avg_pnl = total_pnl / len(self.trades)
        win_rate = (len(wins) / len(self.trades)) * 100
        
        best = max(self.trades, key=lambda x: x["pnl_pct"])
        worst = min(self.trades, key=lambda x: x["pnl_pct"])
        
        equity = self.balance
        for symbol, position in self.positions.items():
            equity += position["cost"]
        
        return {
            "total_trades": len(self.trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(avg_pnl, 2),
            "avg_win": round(sum(t["pnl"] for t in wins) / len(wins), 2) if wins else 0,
            "avg_loss": round(sum(t["pnl"] for t in losses) / len(losses), 2) if losses else 0,
            "best_trade": {
                "symbol": best["symbol"],
                "pnl_pct": best["pnl_pct"]
            },
            "worst_trade": {
                "symbol": worst["symbol"],
                "pnl_pct": worst["pnl_pct"]
            },
            "balance": round(self.balance, 2),
            "equity": round(equity, 2),
            "open_positions": len(self.positions),
            "roi_pct": round((equity - 1000) / 1000 * 100, 2) if equity else 0
        }
    
    def display_portfolio(self):
        print("=" * 80)
        print("PAPER TRADING PORTFOLIO")
        print("=" * 80)
        
        stats = self.get_stats()
        
        print(f"\nBalance: ${stats['balance']:.2f}")
        print(f"Equity: ${stats['equity']:.2f}")
        print(f"ROI: {stats['roi_pct']:+.2f}%")
        print(f"\nTrades: {stats['total_trades']} (Wins: {stats['wins']}, Losses: {stats['losses']})")
        print(f"Win Rate: {stats['win_rate']}%")
        print(f"Total PnL: ${stats['total_pnl']:+.2f}")
        print(f"Avg PnL: ${stats['avg_pnl']:+.2f}")
        
        if stats['best_trade']:
            print(f"Best: {stats['best_trade']['symbol']} ({stats['best_trade']['pnl_pct']:+.1f}%)")
        if stats['worst_trade']:
            print(f"Worst: {stats['worst_trade']['symbol']} ({stats['worst_trade']['pnl_pct']:+.1f}%)")
        
        if self.positions:
            print(f"\nOpen Positions ({len(self.positions)}):")
            for symbol, pos in self.positions.items():
                print(f"  {symbol}: {pos['shares']:.0f} shares @ ${pos['entry_price']:.8f}")
                print(f"    Target: ${pos['target']:.8f} | Stop: ${pos['stop_loss']:.8f}")
        
        if self.trades:
            print(f"\nRecent Trades:")
            for trade in self.trades[-5:]:
                status = "WIN" if trade["pnl"] > 0 else "LOSS"
                print(f"  {status}: {trade['symbol']} {trade['pnl_pct']:+.1f}% ({trade['reason']})")
    
    def _holding_hours(self, opened_at: str) -> float:
        opened = datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
        return (datetime.now() - opened).total_seconds() / 3600

def main():
    trader = PaperTrader(initial_balance=1000.0)
    
    print("=" * 80)
    print("PAPER TRADING MODE")
    print("=" * 80)
    print("\nSimulates trading with $1000 fake money")
    print("Tracks performance without risk")
    print("=" * 80)
    
    print("\nAdding demo trades...")
    
    trader.buy("BONK", 0.00001, amount=100, target=0.00003, stop_loss=0.000008)
    trader.sell("BONK", 0.000025, "target_hit")
    
    trader.buy("WIF", 0.15, amount=100, target=0.30, stop_loss=0.12)
    trader.sell("WIF", 0.20, "partial_profit")
    
    trader.buy("RUG", 0.001, amount=100, target=0.003, stop_loss=0.0008)
    trader.sell("RUG", 0.0001, "stop_loss")
    
    trader.display_portfolio()
    
    print(f"\n{'='*80}")
    print("COMMANDS:")
    print(f"{'='*80}")
    print("  trader.buy('SYMBOL', price, amount=100)")
    print("  trader.sell('SYMBOL', price, reason='manual')")
    print("  trader.check_stop_losses({'SYMBOL': current_price})")
    print("  trader.get_stats()")
    print("  trader.display_portfolio()")

if __name__ == "__main__":
    main()
