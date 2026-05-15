import pennylane as qml
import numpy as np

# Quantum device
n_qubits = 3
dev = qml.device("default.qubit", wires=n_qubits)

# Simple quantum pattern recognition circuit
@qml.qnode(dev)
def quantum_pattern_detector(inputs, weights):
    """
    Quantum circuit that detects patterns in data
    Inputs: classical data (3 features)
    Weights: trainable parameters
    """
    # Encode data (angle encoding)
    for i in range(n_qubits):
        qml.RX(inputs[i], wires=i)
    
    # Quantum processing layers
    for layer in range(2):
        # Rotation gates
        for i in range(n_qubits):
            qml.RY(weights[layer, i, 0], wires=i)
            qml.RZ(weights[layer, i, 1], wires=i)
        
        # Entanglement - quantum advantage here
        for i in range(n_qubits - 1):
            qml.CNOT(wires=[i, i + 1])
    
    # Measure - output quantum features
    return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

# Test with sample crypto data
# Features: price_change, volume_spike, sentiment_score
sample_data = np.array([0.05, 0.8, 0.3])  # Small pump signal
weights = np.random.randn(2, n_qubits, 2) * 0.1

print("Quantum Pattern Detector Demo")
print("=" * 40)
print(f"Input (price, volume, sentiment): {sample_data}")
print()

# Run quantum circuit
quantum_features = quantum_pattern_detector(sample_data, weights)
print(f"Quantum Features: {quantum_features}")
print()

# Interpret results
avg_signal = np.mean(quantum_features)
if avg_signal > 0.3:
    signal = "STRONG BUY"
elif avg_signal > 0:
    signal = "HOLD"
else:
    signal = "SELL"

print(f"Quantum Signal Strength: {avg_signal:.3f}")
print(f"Trading Signal: {signal}")
print()
print("Quantum advantage: Entanglement captures")
print("correlations classical ML might miss!")
