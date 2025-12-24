
import pickle
import os
import sys

# Path to the model file
file_path = r"c:\Users\pahad\Desktop\AutoGen\data\model\xray_task_embeddings_resnet18_train_only.pkl"

print(f"Loading {file_path}...")

try:
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    
    print(f"Type: {type(data)}")
    
    with open("keys_dump.txt", "w") as out:
        if isinstance(data, dict):
            out.write(f"Number of items: {len(data)}\n")
            keys = list(data.keys())
            out.write("First 5 keys:\n")
            for k in keys[:5]:
                out.write(f"Key: '{k}'\n")
                
            first_key = keys[0]
            out.write(f"Value for {first_key}: {type(data[first_key])}\n")
            try:
                out.write(f"Shape of value: {data[first_key].shape}\n")
            except:
                pass
            out.write(f"Sample value: {data[first_key]}\n")
        
        else:
             out.write(f"Content Type: {type(data)}\n")

except Exception as e:
    print(f"Error loading pickle: {e}")
