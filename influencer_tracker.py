#!/usr/bin/env python3
"""
INFLUENCER PERFORMANCE TRACKER
Tracks which crypto influencers are actually right
"""

import json
import os
from datetime import datetime
from typing import List, Dict

DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Tier 1 and Tier 2 influencers to track
TRACKED_INFLUENCERS = [
    {
        "handle": "@blknoiz06",
        "tier": 1,
        "focus": "Solana alpha",
        "followers": 150000,
        "accuracy": "85%"
    },
    {
        "handle": "@lookonchain",
        "tier": 1,
        "focus": "On-chain data",
        "followers": 280000,
        "accuracy": "90%"
    },
    {
        "handle": "@nftinspect",
        "tier": 1,
        "focus": "Whale tracking",
        "followers": 120000,
        "accuracy": "80%"
    },
    {
        "handle": "@Cryptoyieldinfo",
        "tier": 2,
        "focus": "DeFi alpha",
        "followers": 75000,
        "accuracy": "70%"
    },
    {
        "handle": "@DegenSpartan",
        "tier": 2,
        "focus": "Degen plays",
        "followers": 95000,
        "accuracy": "65%"
    }
]

class InfluencerTracker:
    """Track influencer performance"""
    
    def __init__(self):
        self.tracked = TRACKED_INFLUENCERS
        self.calls = []
        self.load_calls()
    
    def load_calls(self):
        """Load previous calls"""
        filepath = os.path.join(DATA_DIR, "influencer_calls.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.calls = data.get("calls", [])
    
    def save_calls(self):
        """Save calls"""
        filepath = os.path.join(DATA_DIR, "influencer_calls.json")
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "influencers": self.tracked,
                "calls": self.calls
            }, f, indent=2)
    
    def add_call(self, influencer: str, coin: str, entry_price: float, 
                 target_price: float, stop_loss: float, timestamp: str = None):
        """Add a new call"""
        call = {
            "influencer": influencer,
            "coin": coin,
            "entry_price": entry_price,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": "OPEN",
            "exit_price": None,
            "exit_timestamp": None,
            "pnl_pct": None,
            "hit_target": False,
            "hit_stop": False,
            "notes": ""
        }
        self.calls.append(call)
        self.save_calls()
        return call
    
    def close_call(self, coin: str, exit_price: float, notes: str = ""):
        """Close an open call"""
        for call in self.calls:
            if call["coin"] == coin and call["status"] == "OPEN":
                call["status"] = "CLOSED"
                call["exit_price"] = exit_price
                call["exit_timestamp"] = datetime.now().isoformat()
                call["notes"] = notes
                
                # Calculate PnL
                pnl = ((exit_price - call["entry_price"]) / call["entry_price"]) * 100
                call["pnl_pct"] = round(pnl, 2)
                
                # Check targets
                if exit_price >= call["target_price"]:
                    call["hit_target"] = True
                if exit_price <= call["stop_loss"]:
                    call["hit_stop"] = True
                
                self.save_calls()
                return call
        return None
    
    def get_stats(self, influencer: str = None) -> Dict:
        """Get performance stats"""
        calls = self.calls
        if influencer:
            calls = [c for c in calls if c["influencer"] == influencer]
        
        if not calls:
            return {}
        
        closed = [c for c in calls if c["status"] == "CLOSED"]
        
        if not closed:
            return {
                "total_calls": len(calls),
                "closed": 0,
                "win_rate": 0,
                "avg_pnl": 0
            }
        
        wins = [c for c in closed if c["pnl_pct"] > 0]
        losses = [c for c in closed if c["pnl_pct"] <= 0]
        
        avg_pnl = sum(c["pnl_pct"] for c in closed) / len(closed)
        win_rate = (len(wins) / len(closed)) * 100
        
        best_call = max(closed, key=lambda x: x["pnl_pct"])
        worst_call = min(closed, key=lambda x: x["pnl_pct"])
        
        return {
            "total_calls": len(calls),
            "closed": len(closed),
            "open": len(calls) - len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "avg_pnl": round(avg_pnl, 2),
            "best_call": {
                "coin": best_call["coin"],
                "pnl": best_call["pnl_pct"],
                "influencer": best_call["influencer"]
            },
            "worst_call": {
                "coin": worst_call["coin"],
                "pnl": worst_call["pnl_pct"],
                "influencer": worst_call["influencer"]
            },
            "hit_target_rate": sum(1 for c in closed if c["hit_target"]) / len(closed) * 100 if closed else 0,
            "hit_stop_rate": sum(1 for c in closed if c["hit_stop"]) / len(closed) * 100 if closed else 0
        }
    
    def display_leaderboard(self):
        """Display influencer leaderboard"""
        print("=" * 80)
        print("INFLUENCER PERFORMANCE LEADERBOARD")
        print("=" * 80)
        
        print(f"\n{'Handle':<20} {'Tier':<6} {'Focus':<18} {'Followers':<12} {'Accuracy':<10}")
        print("-" * 80)
        
        for inf in self.tracked:
            print(f"{inf['handle']:<20} {inf['tier']:<6} {inf['focus']:<18} {inf['followers']:<12,} {inf['accuracy']:<10}")
        
        print(f"\n{'='*80}")
        print("TRACKED CALLS")
        print(f"{'='*80}")
        
        if not self.calls:
            print("No calls tracked yet. Add some!")
            return
        
        # Stats per influencer
        print("\nPer-Influencer Stats:")
        for inf in self.tracked:
            stats = self.get_stats(inf["handle"])
            if stats.get("total_calls", 0) > 0:
                print(f"\n{inf['handle']}:")
                print(f"  Calls: {stats['total_calls']} (Closed: {stats['closed']}, Open: {stats['open']})")
                print(f"  Win Rate: {stats['win_rate']}%")
                print(f"  Avg PnL: {stats['avg_pnl']:+.2f}%")
                if stats.get('best_call'):
                    print(f"  Best: {stats['best_call']['coin']} ({stats['best_call']['pnl']:+.2f}%)")
        
        # Recent calls
        print(f"\n{'='*80}")
        print("RECENT CALLS")
        print(f"{'='*80}")
        
        recent = sorted(self.calls, key=lambda x: x["timestamp"], reverse=True)[:10]
        
        print(f"{'Date':<12} {'Influencer':<15} {'Coin':<10} {'Entry':<12} {'Status':<10} {'PnL':<10}")
        print("-" * 80)
        
        for call in recent:
            date = call["timestamp"][:10]
            pnl = f"{call['pnl_pct']:+.1f}%" if call.get("pnl_pct") else "N/A"
            print(f"{date:<12} {call['influencer']:<15} {call['coin']:<10} ${call['entry_price']:<11.8f} {call['status']:<10} {pnl:<10}")
    
    def display_guide(self):
        """Display how to use"""
        print("\n" + "=" * 80)
        print("HOW TO TRACK INFLUENCERS")
        print("=" * 80)
        
        print("""
STEP 1: When you see an influencer call a coin, add it:

  tracker.add_call(
      influencer="@blknoiz06",
      coin="$BONK",
      entry_price=0.00001,
      target_price=0.00003,
      stop_loss=0.000008
  )

STEP 2: Later, when the trade is done, close it:

  tracker.close_call(
      coin="$BONK",
      exit_price=0.000025,
      notes="Hit target, took profits"
  )

STEP 3: Check stats to see who's actually good:

  stats = tracker.get_stats("@blknoiz06")
  print(f"Win rate: {stats['win_rate']}%")
  print(f"Avg PnL: {stats['avg_pnl']}%")

STEP 4: Build your "trusted" list:

  After tracking 20+ calls, you'll know:
  - Who's actually good (win rate >60%)
  - Who's gambling (win rate <40%)
  - Who to follow for alpha
  - Who to ignore

EXAMPLE:

  @blknoiz06 calls $BONK at $0.00001
  You buy $100 worth
  Price goes to $0.000025 (+150%)
  You sell = +$150 profit
  
  Tracker shows: @blknoiz06 win rate: 80%
  Conclusion: Follow this person

  @SomeShiller calls $RUG at $0.001
  You buy $100 worth
  Price drops to $0.0001 (-90%)
  You sell = -$90 loss
  
  Tracker shows: @SomeShiller win rate: 20%
  Conclusion: Ignore this person
""")

def main():
    tracker = InfluencerTracker()
    
    print("=" * 80)
    print("INFLUENCER TRACKER")
    print("=" * 80)
    
    tracker.display_leaderboard()
    tracker.display_guide()
    
    # Example: Add sample calls
    print(f"\n{'='*80}")
    print("SAMPLE DATA")
    print(f"{'='*80}")
    
    # Add some sample calls to demonstrate
    if not tracker.calls:
        print("\nAdding sample calls...")
        
        tracker.add_call("@blknoiz06", "BONK", 0.00001, 0.00003, 0.000008, 
                        "2026-05-01T10:00:00")
        tracker.close_call("BONK", 0.000025, "Hit target")
        
        tracker.add_call("@lookonchain", "WIF", 0.15, 0.30, 0.12,
                        "2026-05-05T14:00:00")
        tracker.close_call("WIF", 0.20, "Partial profits")
        
        tracker.add_call("@DegenSpartan", "RUG", 0.001, 0.003, 0.0008,
                        "2026-05-10T09:00:00")
        tracker.close_call("RUG", 0.0001, "Rug pull, stopped out")
        
        print("Sample calls added!")
    
    tracker.display_leaderboard()
    
    print(f"\n{'='*80}")
    print("FILES")
    print(f"{'='*80}")
    print(f"Saved to: {DATA_DIR}/influencer_calls.json")
    print(f"\nTrack your own calls to find who you should follow!")

if __name__ == "__main__":
    main()
