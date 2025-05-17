from datasets import load_from_disk

# Load the dataset
dataset = load_from_disk("/project/phan/sj863/datasets/seed3/")

# Function to rename 'content' key to 'seed'
def rename_content_to_seed(example):
    # Rename 'content' key to 'seed'
    example['seed'] = example.pop('content')
    return example

# Apply the renaming function to all the entries in the dataset
dataset = dataset.map(rename_content_to_seed)

# Save the updated dataset to a new JSONL file
dataset.to_json("/project/phan/sj863/datasets/final_seed.jsonl")

