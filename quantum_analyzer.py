import pennylane as qml
import torch
import torch.nn as nn
import numpy as np
import json
import sys

class QuantumCryptoAnalyzer(nn.Module):
    """
    Hybrid Quantum-Classical Neural Network for Crypto Signal Detection
    Uses quantum circuits to capture non-linear patterns classical NNs miss
    """
    
    def __init__(self, n_qubits=4, n_layers=3):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        
        # Quantum device (simulator - free, no quantum hardware needed)
        self.dev = qml.device("default.qubit", wires=n_qubits)
        
        # Quantum circuit as a PyTorch layer
        @qml.qnode(self.dev, interface="torch")
        def quantum_circuit(inputs, weights):
            # Ensure inputs is proper size
            input_list = inputs[0] if len(inputs.shape) > 1 else inputs
            
            # Angle encoding: map classical data to quantum states
            for i in range(n_qubits):
                if i < len(input_list):
                    qml.RX(input_list[i] * np.pi, wires=i)
                else:
                    qml.RX(0.0, wires=i)
            
            # Variational quantum layers
            for layer in range(n_layers):
                # Rotation gates (trainable)
                for i in range(n_qubits):
                    qml.RY(weights[layer, i, 0], wires=i)
                    qml.RZ(weights[layer, i, 1], wires=i)
                
                # Entanglement - creates quantum correlations
                for i in range(n_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
                # Ring connection for full correlation
                qml.CNOT(wires=[n_qubits - 1, 0])
            
            # Measure in Z basis - outputs quantum features
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        
        self.quantum_circuit = quantum_circuit
        
        # Trainable quantum weights
        self.quantum_weights = nn.Parameter(
            torch.randn(n_layers, n_qubits, 2) * 0.1
        )
        
        # Classical pre-processing (compress to n_qubits dimensions)
        self.classical_encoder = nn.Sequential(
            nn.Linear(10, 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, n_qubits),
            nn.Tanh()  # Scale to [-1, 1] for quantum input
        )
        
        # Classical post-processing (decision layers)
        self.classical_decoder = nn.Sequential(
            nn.Linear(n_qubits, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 3),  # 3 classes: BUY, HOLD, SELL
        )
        
        # Softmax for probabilities
        self.softmax = nn.Softmax(dim=-1)
    
    def forward(self, x):
        # Encode classical features to quantum-ready format
        encoded = self.classical_encoder(x)
        
        # Process through quantum circuit
        quantum_features = []
        for i in range(encoded.shape[0]):
            qf = self.quantum_circuit(encoded[i], self.quantum_weights)
            quantum_features.append(torch.stack(qf))
        quantum_features = torch.stack(quantum_features)
        
        # Classical post-processing for decision
        quantum_features_float = quantum_features.float()
        logits = self.classical_decoder(quantum_features_float)
        probabilities = self.softmax(logits)
        
        return probabilities, quantum_features


def analyze_crypto_signal(price_change, volume_change, rsi, macd, 
                          sentiment, fear_greed, btc_dominance, 
                          liquidity, whale_activity, social_volume):
    """
    Analyze crypto market conditions and return quantum-enhanced signal
    """
    # Initialize model
    model = QuantumCryptoAnalyzer(n_qubits=4, n_layers=3)
    model.eval()
    
    # Prepare input tensor
    features = torch.tensor([[
        price_change, volume_change, rsi, macd, sentiment,
        fear_greed, btc_dominance, liquidity, whale_activity, social_volume
    ]], dtype=torch.float32)
    
    # Get prediction
    with torch.no_grad():
        probabilities, quantum_features = model(features)
    
    probs = probabilities[0].numpy()
    q_features = quantum_features[0].numpy()
    
    # Map to signal
    classes = ['SELL', 'HOLD', 'BUY']
    signal_idx = np.argmax(probs)
    signal = classes[signal_idx]
    confidence = float(probs[signal_idx])
    
    # Quantum advantage metrics
    entanglement_strength = float(np.std(q_features))
    
    return {
        'signal': signal,
        'confidence': round(confidence, 3),
        'probabilities': {
            'sell': round(float(probs[0]), 3),
            'hold': round(float(probs[1]), 3),
            'buy': round(float(probs[2]), 3)
        },
        'quantum_features': [round(float(x), 3) for x in q_features],
        'entanglement_strength': round(entanglement_strength, 3),
        'model_type': 'Hybrid Quantum-Classical'
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run test with sample data
        test_data = {
            'price_change': 0.15,      # +15% pump
            'volume_change': 0.85,     # High volume
            'rsi': 0.72,               # Overbought but strong
            'macd': 0.3,               # Bullish crossover
            'sentiment': 0.8,          # Very positive
            'fear_greed': 0.75,        # Greed
            'btc_dominance': 0.45,     # Low BTC dominance (alt season)
            'liquidity': 0.6,          # Moderate liquidity
            'whale_activity': 0.9,     # Whale buying
            'social_volume': 0.88      # Viral on social
        }
        
        result = analyze_crypto_signal(**test_data)
        print(json.dumps(result, indent=2))
    
    elif len(sys.argv) > 10:
        # Parse CLI arguments
        result = analyze_crypto_signal(
            float(sys.argv[1]),   # price_change
            float(sys.argv[2]),   # volume_change
            float(sys.argv[3]),   # rsi
            float(sys.argv[4]),   # macd
            float(sys.argv[5]),   # sentiment
            float(sys.argv[6]),   # fear_greed
            float(sys.argv[7]),   # btc_dominance
            float(sys.argv[8]),   # liquidity
            float(sys.argv[9]),   # whale_activity
            float(sys.argv[10])   # social_volume
        )
        print(json.dumps(result))
    
    else:
        print("Usage:")
        print("  python quantum_analyzer.py --test")
        print("  python quantum_analyzer.py <price> <volume> <rsi> <macd> <sentiment> <fear_greed> <btc_dom> <liquidity> <whale> <social>")
