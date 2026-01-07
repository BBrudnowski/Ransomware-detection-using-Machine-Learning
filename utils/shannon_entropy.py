from collections import Counter
from math import log2
import numpy as np

def calculate_shannon_entropy(file_path, block_size=2048):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except:
        return None, None
    
    if not data:
        return 0, 0
    
    byte_counts = Counter(data)
    total_bytes = len(data)
    entropy = 0
    
    for count in byte_counts.values():
        probability = count / total_bytes
        entropy -= probability * log2(probability)
    
    block_entropies = []
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        if len(block) < 10:
            continue
            
        block_counts = Counter(block)
        block_entropy = 0
        
        for count in block_counts.values():
            probability = count / len(block)
            block_entropy -= probability * log2(probability)
        
        block_entropies.append(block_entropy)
    
    variance = np.var(block_entropies) if block_entropies else 0
    
    return entropy, variance