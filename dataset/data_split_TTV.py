"""
Dataset Split (Train, Test, Validation) - updated 10/9/2026

Usage:
- To help split the dataset into Train, Test and Validation Set
- Current distribution are 80/10/10
- Mostly used for the Chinese Face Dataset (CFD) and CE-OWN
- Distribution will be balanced between each class

To use:
- change the source and output to what you desire 
- run the code 
"""


import os
import shutil
import random

# Change this based on the Dataset Needed for splitting
source_dir = "compound_emotions"  
output_dir = "CE_split_wv"

# Create train/test/valid folders
for split in ["train", "test", "valid"]:
    for compound_emotions in os.listdir(source_dir):
        os.makedirs(os.path.join(output_dir, split, compound_emotions), exist_ok=True)

# Process each class separately
for compound_emotions in os.listdir(source_dir):
    emotion_path = os.path.join(source_dir, compound_emotions)

    if not os.path.isdir(emotion_path):
        continue

    files = os.listdir(emotion_path)
    random.shuffle(files)

    # Split the dataset to each percentage
    total = len(files)
    split_index_1 = int(0.8 * total)   # 80% point
    split_index_2 = int(0.9 * total)   # 90% point

    train_files = files[:split_index_1]
    test_files = files[split_index_1:split_index_2]
    valid_files = files[split_index_2:]

    # Image will be copy and move to their suppose folder 
    for file in train_files:
        src = os.path.join(emotion_path, file)
        dst = os.path.join(output_dir, "train", compound_emotions, file)
        shutil.copy(src, dst)

    for file in test_files:
        src = os.path.join(emotion_path, file)
        dst = os.path.join(output_dir, "test", compound_emotions, file)
        shutil.copy(src, dst)

    for file in valid_files:
        src = os.path.join(emotion_path, file)
        dst = os.path.join(output_dir, "valid", compound_emotions, file)
        shutil.copy(src, dst)

    print(f"{compound_emotions}: {len(train_files)} train, {len(test_files)} test, {len(valid_files)} valid")

print("✅ Dataset split complete!")