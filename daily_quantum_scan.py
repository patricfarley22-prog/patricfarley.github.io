#!/usr/bin/env python3
"""
DAILY QUANTUM SCANNER
Runs every morning at 6 AM
Sends results to Telegram
"""

import json
import subprocess
import os
from datetime import datetime

DATA_DIR = "meme_coin_data"

def run_quantum_scan():
    """Run the quantum scanner"""
    print(f"[{datetime.now().strftime('%H:%M')}] Running quantum scan...")
    
    result = subprocess.run(
        ["python", "quantum_full_comparison.py"],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    
    if result.returncode == 0:
        print("Scan complete")
        return True
    else:
        print(f"Error: {result.stderr[:200]}")
        return False

def send_alert():
    """Send results via OpenClaw"""
    # Load latest results
    filepath = f"{DATA_DIR}/quantum_full_comparison.json"
    if not os.path.exists(filepath):
        print("No results to send")
        return
    
    with open(filepath) as f:
        data = json.load(f)
    
    # Extract buy signals
    buys = [r for r in data.get('results', []) if 'BUY' in r.get('consensus', '')]
    
    if buys:
        # Format message
        lines = [
            "DAILY QUANTUM SCAN",
            f"Time: {datetime.now().strftime('%H:%M %m/%d')}",
            "",
            f"BUY SIGNALS: {len(buys)}",
            ""
        ]
        
        for r in buys[:5]:
            lines.append(f"  {r['symbol']}: BUY {r['consensus_confidence']:.0%} (Score: {r['consensus_score']:.2f})")
        
        message = "\n".join(lines)
        
        # Save for OpenClaw pickup
        with open(f"{DATA_DIR}/openclaw_alerts.json", "a") as f:
            alert = {
                "timestamp": datetime.now().isoformat(),
                "type": "DAILY_QUANTUM_SCAN",
                "message": message,
                "channel": "telegram",
                "chat_id": "6643728142"
            }
            f.write(json.dumps(alert) + "\n")
        
        print(f"Alert saved: {len(buys)} BUY signals")
    else:
        print("No buy signals today")

def main():
    print("=" * 60)
    print("DAILY QUANTUM SCANNER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run scan
    if run_quantum_scan():
        send_alert()
    
    print("\nDone.")

if __name__ == "__main__":
    main()
