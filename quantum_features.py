import pennylane as qml
import numpy as np
import json
import sys

class QuantumFeatureExtractor:
    """
    Quantum Feature Extractor for Classical ML Models
    Uses quantum circuits to generate enhanced feature representations
    that capture non-linear correlations classical methods miss.
    """
    
    def __init__(self, n_qubits=8, n_layers=4):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        
        # Quantum device
        self.dev = qml.device("default.qubit", wires=n_qubits)
        
        # Define quantum feature map
        @qml.qnode(self.dev, interface="numpy")
        def feature_map(inputs, weights):
            """
            Quantum circuit that maps classical data to quantum feature space
            Uses amplitude encoding + variational circuit for rich representations
            """
            # Amplitude encoding (efficient for n features → log(n) qubits)
            # Normalize inputs to valid quantum state
            normalized = inputs / np.linalg.norm(inputs)
            qml.AmplitudeEmbedding(normalized, wires=range(n_qubits), normalize=True)
            
            # Variational layers for feature transformation
            for layer in range(n_layers):
                # Rotation layer
                for i in range(n_qubits):
                    qml.RX(weights[layer, i, 0], wires=i)
                    qml.RY(weights[layer, i, 1], wires=i)
                    qml.RZ(weights[layer, i, 2], wires=i)
                
                # Entanglement layer (creates quantum correlations)
                for i in range(0, n_qubits - 1, 2):
                    qml.CNOT(wires=[i, i + 1])
                for i in range(1, n_qubits - 1, 2):
                    qml.CNOT(wires=[i, i + 1])
                # Ring connection
                qml.CNOT(wires=[n_qubits - 1, 0])
            
            # Measure multiple observables for feature extraction
            features = []
            # Z-basis measurements (computational basis)
            for i in range(n_qubits):
                features.append(qml.expval(qml.PauliZ(i)))
            
            # X-basis measurements (superposition information)
            for i in range(min(4, n_qubits)):
                features.append(qml.expval(qml.PauliX(i)))
            
            # Entanglement entropy (correlation measure)
            features.append(qml.vn_entropy(wires=[0]))
            
            return features
        
        self.feature_map = feature_map
        
        # Initialize weights (in practice, these would be trained)
        self.weights = np.random.randn(n_layers, n_qubits, 3) * 0.1
    
    def extract(self, data):
        """
        Extract quantum-enhanced features from classical data
        
        Args:
            data: numpy array of features (length must be <= 2^n_qubits)
        
        Returns:
            dict with original + quantum features
        """
        # Ensure data is proper size for amplitude encoding
        target_size = 2 ** self.n_qubits
        padded_data = np.zeros(target_size)
        padded_data[:len(data)] = data
        
        # Extract quantum features
        quantum_features = self.feature_map(padded_data, self.weights)
        
        # Separate feature types
        n_z = self.n_qubits
        n_x = min(4, self.n_qubits)
        
        z_features = quantum_features[:n_z]
        x_features = quantum_features[n_z:n_z + n_x]
        entanglement = quantum_features[-1]
        
        return {
            'original_features': [round(float(x), 4) for x in data[:10]],  # First 10
            'quantum_z_features': [round(float(x), 4) for x in z_features],
            'quantum_x_features': [round(float(x), 4) for x in x_features],
            'entanglement_entropy': round(float(entanglement), 4),
            'total_quantum_features': len(quantum_features),
            'feature_dimensionality': f"{len(data)} classical to {len(quantum_features)} quantum"
        }
    
    def extract_batch(self, data_list):
        """Extract features for multiple data points"""
        return [self.extract(d) for d in data_list]
    
    def get_enhanced_representation(self, data):
        """
        Get combined classical + quantum features for ML model input
        Concatenates original features with quantum features
        """
        result = self.extract(data)
        
        # Combine all features
        combined = (
            result['original_features'] + 
            result['quantum_z_features'] + 
            result['quantum_x_features'] + 
            [result['entanglement_entropy']]
        )
        
        return {
            'enhanced_features': [round(float(x), 4) for x in combined],
            'original_dim': len(result['original_features']),
            'quantum_dim': len(result['quantum_z_features']) + len(result['quantum_x_features']) + 1,
            'total_dim': len(combined),
            'feature_boost': f"{len(combined) / len(result['original_features']):.1f}x feature expansion"
        }


def extract_crypto_features(price_data, volume_data, indicators):
    """
    Extract quantum-enhanced features from crypto market data
    
    Args:
        price_data: dict with OHLCV data
        volume_data: dict with volume metrics
        indicators: dict with technical indicators
    
    Returns:
        dict with enhanced feature representation
    """
    # Combine all features into single vector
    features = []
    
    # Price features (normalized)
    if 'change_24h' in price_data:
        features.append(np.tanh(price_data['change_24h'] / 100))
    if 'change_7d' in price_data:
        features.append(np.tanh(price_data['change_7d'] / 100))
    if 'volatility' in price_data:
        features.append(price_data['volatility'])
    
    # Volume features
    if 'volume_change' in volume_data:
        features.append(np.tanh(volume_data['volume_change'] / 100))
    if 'volume_profile' in volume_data:
        features.append(volume_data['volume_profile'])
    
    # Technical indicators
    if 'rsi' in indicators:
        features.append(indicators['rsi'] / 100)
    if 'macd' in indicators:
        features.append(np.tanh(indicators['macd']))
    if 'bb_position' in indicators:
        features.append(indicators['bb_position'])
    
    # Pad to minimum size
    while len(features) < 8:
        features.append(0.0)
    
    # Extract quantum features
    extractor = QuantumFeatureExtractor(n_qubits=3, n_layers=2)
    return extractor.get_enhanced_representation(np.array(features))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test with sample crypto data
        print("Testing Quantum Feature Extractor")
        print("=" * 50)
        
        # Sample features from a typical crypto token
        sample_features = np.array([
            0.25,   # 24h price change (+25%)
            1.50,   # 7d price change (+150%)
            0.45,   # Volatility
            2.30,   # Volume change (+230%)
            0.75,   # Volume profile
            0.68,   # RSI (68)
            0.25,   # MACD
            0.80,   # Bollinger position
        ])
        
        print(f"Input features: {sample_features[:5]}...")
        print()
        
        # Extract features
        extractor = QuantumFeatureExtractor(n_qubits=4, n_layers=3)
        
        print("Standard Extraction:")
        result = extractor.extract(sample_features)
        for key, value in result.items():
            if isinstance(value, list) and len(value) > 5:
                print(f"  {key}: {value[:5]}... ({len(value)} total)")
            else:
                print(f"  {key}: {value}")
        
        print()
        print("Enhanced Representation (for ML model):")
        enhanced = extractor.get_enhanced_representation(sample_features)
        for key, value in enhanced.items():
            if key == 'enhanced_features':
                print(f"  {key}: {value[:8]}... ({len(value)} total)")
            else:
                print(f"  {key}: {value}")
        
        print()
        print("Crypto Integration Test:")
        crypto_result = extract_crypto_features(
            price_data={'change_24h': 25, 'change_7d': 150, 'volatility': 0.45},
            volume_data={'volume_change': 230, 'volume_profile': 0.75},
            indicators={'rsi': 68, 'macd': 0.25, 'bb_position': 0.8}
        )
        print(json.dumps(crypto_result, indent=2))
    
    elif len(sys.argv) > 1:
        # Parse features from CLI
        features = [float(x) for x in sys.argv[1:]]
        extractor = QuantumFeatureExtractor()
        result = extractor.get_enhanced_representation(np.array(features))
        print(json.dumps(result))
    
    else:
        print("Usage:")
        print("  python quantum_features.py --test")
        print("  python quantum_features.py <feature1> <feature2> ...")
