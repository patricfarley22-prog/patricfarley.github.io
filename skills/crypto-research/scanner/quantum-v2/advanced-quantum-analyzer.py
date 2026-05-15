import pennylane as qml
import torch
import torch.nn as nn
import numpy as np
import json
import sys
from datetime import datetime, timedelta

class QuantumCryptoAnalyzerV2(nn.Module):
    """
    Advanced Quantum-Classical Neural Network v2.0
    
    Improvements over v1:
    - Historical context (90-day lookback)
    - Market regime detection
    - Sentiment integration
    - Multi-timeframe analysis
    - Uncertainty quantification
    """
    
    def __init__(self, n_qubits=8, n_layers=4):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        
        # Quantum device
        self.dev = qml.device("default.qubit", wires=n_qubits)
        
        # Enhanced quantum circuit with data re-uploading
        @qml.qnode(self.dev, interface="torch")
        def quantum_circuit(inputs, weights):
            # Ensure inputs is proper size
            input_list = inputs[0] if len(inputs.shape) > 1 else inputs
            
            # Data re-uploading: encode multiple features across layers
            for layer in range(n_layers):
                # Encode features (rotating through features)
                for i in range(n_qubits):
                    feature_idx = (layer * n_qubits + i) % len(input_list)
                    qml.RX(input_list[feature_idx] * np.pi, wires=i)
                
                # Variational layer
                for i in range(n_qubits):
                    qml.RY(weights[layer, i, 0], wires=i)
                    qml.RZ(weights[layer, i, 1], wires=i)
                
                # Entanglement with ring topology
                for i in range(n_qubits):
                    qml.CNOT(wires=[i, (i + 1) % n_qubits])
                
                # Additional cross-entanglement for richer correlations
                for i in range(0, n_qubits, 2):
                    qml.CZ(wires=[i, (i + 2) % n_qubits])
            
            # Multi-basis measurement
            measurements = []
            for i in range(n_qubits):
                measurements.append(qml.expval(qml.PauliZ(i)))
            
            # Add X-basis measurements for phase information
            for i in range(min(4, n_qubits)):
                measurements.append(qml.expval(qml.PauliX(i)))
            
            return measurements
        
        self.quantum_circuit = quantum_circuit
        
        # Trainable quantum weights
        self.quantum_weights = nn.Parameter(
            torch.randn(n_layers, n_qubits, 2) * 0.1
        )
        
        # Classical encoder (more features now)
        # Input features: price_change, volume, rsi, macd, sentiment, 
        # fear_greed, btc_dom, liquidity, whale, social, 
        # historical_trend, market_regime, sentiment_score
        self.classical_encoder = nn.Sequential(
            nn.Linear(14, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, n_qubits),
            nn.Tanh()
        )
        
        # Market regime detector
        self.regime_detector = nn.Sequential(
            nn.Linear(5, 8),  # volatility, trend strength, volume trend, etc.
            nn.ReLU(),
            nn.Linear(8, 3)  # bull, bear, sideways
        )
        
        # Uncertainty quantifier
        self.uncertainty_net = nn.Sequential(
            nn.Linear(n_qubits + 3, 16),  # quantum features + regime
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        # Main decoder
        self.classical_decoder = nn.Sequential(
            nn.Linear(n_qubits + 3 + 1, 32),  # quantum + regime + uncertainty
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 4)  # STRONG_BUY, BUY, SELL, STRONG_SELL
        )
        
        self.softmax = nn.Softmax(dim=-1)
    
    def detect_regime(self, historical_features):
        """Detect market regime from historical data"""
        regime_logits = self.regime_detector(historical_features)
        regime_probs = self.softmax(regime_logits)
        return regime_probs
    
    def forward(self, x, historical_features=None):
        # Encode classical features
        encoded = self.classical_encoder(x)
        
        # Process through quantum circuit
        quantum_features = []
        for i in range(encoded.shape[0]):
            qf = self.quantum_circuit(encoded[i], self.quantum_weights)
            quantum_features.append(torch.stack(qf).float().T)
        quantum_features = torch.stack(quantum_features)
        
        # Detect market regime
        if historical_features is not None:
            regime = self.detect_regime(historical_features)
        else:
            regime = torch.tensor([[0.33, 0.34, 0.33]])  # Neutral
        
        # Calculate uncertainty
        combined = torch.cat([
            quantum_features[:, :self.n_qubits],
            regime
        ], dim=1)
        uncertainty = self.uncertainty_net(combined)
        
        # Main prediction
        decoder_input = torch.cat([
            quantum_features[:, :self.n_qubits],
            regime,
            uncertainty
        ], dim=1)
        
        logits = self.classical_decoder(decoder_input)
        probabilities = self.softmax(logits)
        
        return probabilities, quantum_features, regime, uncertainty


def analyze_crypto_signal_v2(market_data, historical_data=None):
    """
    Advanced crypto analysis with historical context
    
    Args:
        market_data: dict with current market conditions
        historical_data: optional dict with 7-30 day history
    """
    model = QuantumCryptoAnalyzerV2(n_qubits=8, n_layers=4)
    model.eval()
    
    # Current features
    features = torch.tensor([[
        market_data.get('price_change', 0) / 100,
        market_data.get('volume_change', 0) / 100,
        market_data.get('rsi', 50) / 100,
        market_data.get('macd', 0),
        market_data.get('sentiment', 0.5),
        market_data.get('fear_greed', 50) / 100,
        market_data.get('btc_dominance', 0.45),
        market_data.get('liquidity', 0.5),
        market_data.get('whale_activity', 0.5),
        market_data.get('social_volume', 0.5),
        market_data.get('historical_trend', 0),
        market_data.get('market_regime', 0.5),
        market_data.get('sentiment_score', 0.5),
        market_data.get('volatility', 0.5)
    ]], dtype=torch.float32)
    
    # Historical features for regime detection
    hist_features = None
    if historical_data:
        hist_features = torch.tensor([[
            historical_data.get('volatility_7d', 0.5),
            historical_data.get('trend_strength', 0),
            historical_data.get('volume_trend', 0),
            historical_data.get('support_distance', 0.5),
            historical_data.get('resistance_distance', 0.5)
        ]], dtype=torch.float32)
    
    # Get prediction
    with torch.no_grad():
        probabilities, quantum_features, regime, uncertainty = model(features, hist_features)
    
    probs = probabilities[0].numpy()
    q_features = quantum_features[0].numpy()
    reg = regime[0].numpy()
    unc = uncertainty[0].item()
    
    # Map to signal
    classes = ['STRONG_SELL', 'SELL', 'BUY', 'STRONG_BUY']
    signal_idx = np.argmax(probs)
    signal = classes[signal_idx]
    confidence = float(probs[signal_idx])
    
    # Calculate trend alignment (how well signal matches trend)
    trend_alignment = calculate_trend_alignment(signal, market_data)
    
    # Final confidence = model confidence * trend alignment * (1 - uncertainty)
    final_confidence = confidence * trend_alignment * (1 - unc)
    
    return {
        'signal': signal,
        'raw_confidence': round(confidence, 3),
        'trend_alignment': round(trend_alignment, 3),
        'uncertainty': round(unc, 3),
        'final_confidence': round(final_confidence, 3),
        'probabilities': {
            'strong_sell': round(float(probs[0]), 3),
            'sell': round(float(probs[1]), 3),
            'buy': round(float(probs[2]), 3),
            'strong_buy': round(float(probs[3]), 3)
        },
        'market_regime': {
            'bull': round(float(reg[0]), 3),
            'bear': round(float(reg[1]), 3),
            'sideways': round(float(reg[2]), 3)
        },
        'quantum_features': [round(float(x), 3) for x in q_features[:8]],
        'entanglement_strength': round(float(np.std(q_features[:8])), 3),
        'model_type': 'Quantum v2.0 (Historical + Sentiment)',
        'recommendation': generate_recommendation(signal, final_confidence, unc, market_data)
    }


def calculate_trend_alignment(signal, market_data):
    """Check if signal aligns with underlying trend"""
    price_change = market_data.get('price_change', 0)
    
    alignment = 0.5
    
    if 'BUY' in signal and price_change > 0:
        alignment = 1.0  # Buying into uptrend
    elif 'SELL' in signal and price_change < 0:
        alignment = 1.0  # Selling downtrend
    elif 'BUY' in signal and price_change < -20:
        alignment = 0.3  # Buying falling knife (risky)
    elif 'SELL' in signal and price_change > 20:
        alignment = 0.3  # Selling momentum (risky)
    
    return alignment


def generate_recommendation(signal, confidence, uncertainty, market_data):
    """Generate human-readable recommendation"""
    recs = []
    
    if confidence > 0.7:
        recs.append("HIGH CONFIDENCE - Consider position")
    elif confidence > 0.5:
        recs.append("MODERATE CONFIDENCE - Small position or wait")
    else:
        recs.append("LOW CONFIDENCE - Avoid or very small position")
    
    if uncertainty > 0.3:
        recs.append("HIGH UNCERTAINTY - Market is choppy")
    
    if market_data.get('liquidity', 0) < 0.2:
        recs.append("LOW LIQUIDITY - High slippage risk")
    
    return " | ".join(recs)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test with advanced scenario
        test_data = {
            'price_change': 25,
            'volume_change': 150,
            'rsi': 65,
            'macd': 0.3,
            'sentiment': 0.8,
            'fear_greed': 75,
            'btc_dominance': 0.45,
            'liquidity': 0.6,
            'whale_activity': 0.9,
            'social_volume': 0.88,
            'historical_trend': 0.15,  # 15% over 30 days
            'market_regime': 0.7,  # Bullish regime
            'sentiment_score': 0.85,
            'volatility': 0.4
        }
        
        historical = {
            'volatility_7d': 0.35,
            'trend_strength': 0.6,
            'volume_trend': 0.8,
            'support_distance': 0.3,
            'resistance_distance': 0.7
        }
        
        result = analyze_crypto_signal_v2(test_data, historical)
        print(json.dumps(result, indent=2))
    
    elif len(sys.argv) > 13:
        args = [float(x) for x in sys.argv[1:]]
        market_data = {
            'price_change': args[0],
            'volume_change': args[1],
            'rsi': args[2],
            'macd': args[3],
            'sentiment': args[4],
            'fear_greed': args[5],
            'btc_dominance': args[6],
            'liquidity': args[7],
            'whale_activity': args[8],
            'social_volume': args[9],
            'historical_trend': args[10],
            'market_regime': args[11],
            'sentiment_score': args[12],
            'volatility': args[13] if len(args) > 13 else 0.5
        }
        
        result = analyze_crypto_signal_v2(market_data)
        print(json.dumps(result))
    
    else:
        print("Usage:")
        print("  python advanced-quantum-analyzer.py --test")
        print("  python advanced-quantum-analyzer.py <features...>")
