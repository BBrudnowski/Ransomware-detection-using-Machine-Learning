import os
import re
import json
import pandas as pd
from utils.shannon_entropy import calculate_shannon_entropy


napierone_path = "./NapierOne-tiny"
id=0
types=[]
results = []
for dir in os.listdir(napierone_path):
    for file in os.listdir(napierone_path+'/'+dir):
        if bool(re.match(r'^\d{4}-', file)):
            entropy, variance = calculate_shannon_entropy(napierone_path+'/'+dir+'/'+file)
            size= os.path.getsize(napierone_path+'/'+dir+'/'+file)
            file=re.split(r'[-.,]',file)
            if file[1] not in types:
                types.append(file[1])
            results.append({
                'id': id,
                'type': types.index(file[1]),
                'size' : size,
                'entropy': entropy,
                'variance': variance,
                'label': 1 if dir.startswith("RANSOMWARE") else 0
            })
            id+=1
df = pd.DataFrame(results)
df.to_csv('napierone_entropy_data.csv', index=False)
with open('types.json', 'w', encoding='utf-8') as f:
    json.dump({value: index for index, value in enumerate(types)}, f, ensure_ascii=False, indent=2)