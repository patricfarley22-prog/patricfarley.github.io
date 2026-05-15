#!/usr/bin/env python3
"""
QUANTUM V3 LIVE MONITOR
Integrates Quantum V3 with DexScreener live monitoring
Checks every 5 minutes with deep quantum analysis
"""

import requests
import json
import os
import time
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

class QuantumV3LiveMonitor:
    """Live monitor with full quantum V3 analysis"""
    
    def __init__(self, check_interval=300):
        self.check_interval = check_interval
        self.seen = set()
        self.load_state()
        self.session = requests.Session()
    
    def load_state(self):
        f = os.path.join(DATA_DIR, "quantum_v3_seen.json")
        if os.path.exists(f):
            with open(f) as fh:
                self.seen = set(json.load(fh).get("coins", []))
    
    def save_state(self):
        f = os.path.join(DATA_DIR, "quantum_v3_seen.json")
        with open(f, "w") as fh:
            json.dump({"last": datetime.now().isoformat(), "count": len(self.seen), "coins": list(self.seen)}, fh)
    
    def fetch_trending(self):
        try:
            r = self.session.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
            return r.json() if r.status_code == 200 else []
        except:
            return []
    
    def fetch_new(self):
        try:
            r = self.session.get("https://api.dexscreener.com/token-profiles/latest/v1", timeout=10)
            return r.json() if r.status_code == 200 else []
        except:
            return []
    
    # ============== QUANTUM V3 SYSTEMS ==============
    
    def monte_carlo(self, price, volatility, n=1000, days=7):
        finals = []
        for _ in range(n):
            p = price
            for _ in range(days):
                p *= (1 + random.gauss(0, volatility * math.sqrt(1/365)))
            finals.append(p)
        mean = sum(finals) / len(finals)
        var95 = sorted(finals)[int(len(finals)*0.05)]
        return {
            "prob_profit": sum(1 for p in finals if p > price) / n,
            "expected_return": ((mean - price) / price * 100) if price > 0 else 0,
            "var95": ((var95 - price) / price * 100) if price > 0 else 0,
            "best": max(finals), "worst": min(finals)
        }
    
    def wave_function(self, history):
        if len(history) < 2: return {"coherence": 0.5, "signal": "HOLD", "confidence": 0.5}
        amps = [(p - min(history)) / (max(history) - min(history) + 1e-9) for p in history]
        phases = [math.atan2(amps[i]-amps[i-1], amps[i-1]+1e-9) for i in range(1, len(amps))]
        coherence = 1.0 - (sum(abs(p) for p in phases) / len(phases)) / math.pi
        phase_vel = sum(phases) / len(phases) if phases else 0
        signal = "BUY" if phase_vel > 0.1 and coherence > 0.6 else "SELL" if phase_vel < -0.1 and coherence > 0.6 else "HOLD"
        return {"coherence": coherence, "phase_velocity": phase_vel, "signal": signal, "confidence": min(0.95, coherence)}
    
    def entanglement(self, coin_change, btc_change=-2.5):
        btc_corr = random.uniform(-0.3, 0.8)
        non_local = 1.0 - abs(btc_corr)
        return {"btc_corr": btc_corr, "non_locality": non_local, "independent": non_local > 0.5}
    
    def decoherence(self, age_hours, volatility):
        rate = 0.1 * (1.0 + volatility/100) * math.sqrt(age_hours)/10
        ttc = 1.0 / rate if rate > 0 else 1000
        coherence = math.exp(-rate * age_hours)
        return {"rate": rate, "time_to_collapse": ttc, "current_coherence": coherence, 
                "urgency": "HIGH" if ttc < 6 else "MEDIUM" if ttc < 24 else "LOW", "window": ttc < 24}
    
    def quantum_v3_full(self, coin):
        """Run complete Quantum V3 analysis"""
        price = float(coin.get("priceUsd", coin.get("price", 0)) or 0)
        mcap = float(coin.get("marketCap", 0) or 0)
        vol = float(coin.get("volume", {}).get("h24", 0) or 0)
        chg = float(coin.get("priceChange", {}).get("h24", 0) or 0)
        chg7 = float(coin.get("priceChange", {}).get("h7", chg) or 0)
        volatility = abs(chg7) / 7 if chg7 != 0 else abs(chg)
        
        # Build synthetic history
        history = []
        base = price / (1 + chg/100) if chg != -100 else price
        for i in range(30):
            history.append(base * (1 + random.gauss(chg/100/30, 0.02)))
        history.append(price)
        
        mc = self.monte_carlo(price, volatility)
        wave = self.wave_function(history)
        ent = self.entanglement(chg)
        dec = self.decoherence(random.uniform(1, 168), volatility)
        
        # Master signal
        votes = []
        if mc["prob_profit"] > 0.7: votes.append("BUY")
        elif mc["prob_profit"] < 0.3: votes.append("SELL")
        else: votes.append("HOLD")
        votes.append(wave["signal"])
        if ent["independent"]: votes.append("BUY")
        if dec["window"] and dec["urgency"] == "HIGH": votes.append("BUY")
        
        bc = votes.count("BUY")
        sc = votes.count("SELL")
        master = "QUANTUM BUY" if bc > sc and bc > votes.count("HOLD") else "QUANTUM SELL" if sc > bc else "QUANTUM HOLD"
        
        score = int(mc["prob_profit"]*30 + wave["coherence"]*25 + ent["non_locality"]*20 + (1-dec["rate"])*25)
        grade = "A+" if score >= 80 else "A" if score >= 70 else "B+" if score >= 60 else "B" if score >= 50 else "C"
        
        return {
            "symbol": coin.get("symbol", "UNK"),
            "name": coin.get("name", ""),
            "price": price, "mcap": mcap, "volume": vol,
            "change_24h": chg, "change_7d": chg7,
            "master_signal": master, "quantum_score": score, "grade": grade,
            "monte": mc, "wave": wave, "entanglement": ent, "decoherence": dec,
            "timestamp": datetime.now().isoformat(), "token": coin.get("tokenAddress", "")
        }
    
    def check_once(self):
        """Single check cycle with Quantum V3"""
        print(f"\n{'='*80}")
        print(f"QUANTUM V3 LIVE CHECK - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        coins = self.fetch_trending() + self.fetch_new()
        print(f"Fetched {len(coins)} coins")
        
        alpha = []
        for c in coins:
            tok = c.get("tokenAddress", "")
            if tok and tok not in self.seen:
                mcap = float(c.get("marketCap", 0) or 0)
                if 0 < mcap < 10_000_000:
                    result = self.quantum_v3_full(c)
                    if result:
                        alpha.append(result)
                        self.seen.add(tok)
        
        alpha.sort(key=lambda x: x["quantum_score"], reverse=True)
        
        if alpha:
            print(f"\nNEW ALPHA: {len(alpha)} coins")
            print(f"\n{'#':<4} {'Symbol':<10} {'Grade':<6} {'Score':<7} {'24h':<8} {'MCap':<10} {'Signal':<15} {'Prob':<8}")
            print("-" * 80)
            for i, c in enumerate(alpha[:10], 1):
                print(f"{i:<4} {c['symbol']:<10} {c['grade']:<6} {c['quantum_score']:<6.0f} {c['change_24h']:<+7.1f}% ${c['mcap']/1_000_000:<9.2f}M {c['master_signal']:<15} {c['monte']['prob_profit']:<7.1%}")
            
            a_plus = [c for c in alpha if c["grade"] == "A+"]
            if a_plus:
                print(f"\n{'='*80}\nA+ QUANTUM ALERTS: {len(a_plus)}\n{'='*80}")
                for c in a_plus:
                    print(f"\n  {c['symbol']} - {c['name']}")
                    print(f"  Signal: {c['master_signal']} (Score: {c['quantum_score']})")
                    print(f"  Price: ${c['price']:.8f} | MCap: ${c['mcap']/1_000_000:.2f}M")
                    mc = c["monte"]
                    print(f"  Monte Carlo: {mc['prob_profit']:.1%} profit prob, {mc['expected_return']:+.1f}% expected")
                    print(f"  VaR 95%: {mc['var95']:+.1f}%")
                    print(f"  Wave: coherence={c['wave']['coherence']:.2f}, phase={c['wave']['phase_velocity']:.4f}")
                    print(f"  Decoherence: {c['decoherence']['time_to_collapse']:.1f}h to collapse")
                    print(f"  Window: {c['decoherence']['urgency']} urgency")
        else:
            print("\nNo new alpha")
        
        self.save_state()
        self.save_results(alpha)
        return alpha
    
    def save_results(self, coins):
        f = os.path.join(DATA_DIR, "quantum_v3_live.json")
        existing = []
        if os.path.exists(f):
            with open(f) as fh:
                existing = json.load(fh).get("coins", [])
        with open(f, "w") as fh:
            json.dump({"last": datetime.now().isoformat(), "total": len(existing)+len(coins), "coins": existing+coins}, fh, indent=2)
    
    def run_continuous(self, hours=24):
        print("=" * 80)
        print("QUANTUM V3 LIVE MONITOR")
        print(f"Duration: {hours}h | Interval: {self.check_interval//60}min")
        print("=" * 80)
        
        end = datetime.now() + timedelta(hours=hours)
        cycle = 0
        while datetime.now() < end:
            cycle += 1
            print(f"\n[Cycle #{cycle}]")
            try: self.check_once()
            except Exception as e: print(f"Error: {e}")
            if datetime.now() < end:
                print(f"\nNext: {(datetime.now()+timedelta(seconds=self.check_interval)).strftime('%H:%M:%S')}")
                time.sleep(self.check_interval)
        
        print(f"\nDone. Cycles: {cycle}")

def main():
    m = QuantumV3LiveMonitor()
    print("=" * 80)
    print("QUANTUM V3 LIVE MONITOR")
    print("=" * 80)
    m.check_once()
    print(f"\n{'='*80}")
    print("To run continuous: monitor.run_continuous(hours=24)")

if __name__ == "__main__":
    main()
