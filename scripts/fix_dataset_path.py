#!/usr/bin/env python3
"""Fix dataset path in Cosmos DB to point to /tmp in the pod."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

os.environ['COSMOS_ACCOUNT_URI'] = 'https://cosmos-vzzyfygthfu2w.documents.azure.com:443/'
os.environ['COSMOS_AUTH_MODE'] = 'aad'
os.environ['COSMOS_DATABASE_NAME'] = 'agent_rl'

from lightning.rl_ledger_cosmos import get_rl_ledger

ledger = get_rl_ledger()
ledger._ensure_initialized()

# Get the dataset
dataset = ledger.get_dataset('1c47aa12-2e07-4d0e-8674-4f65164e3c85', 'autonomous-agent')
print('Current dataset:')
print(f'  local_path: {dataset.local_path}')
val_path = dataset.metadata.get('validation_path', 'N/A')
print(f'  validation_path: {val_path}')

# Update local_path to /tmp
dataset.local_path = '/tmp/autonomous-agent-v1_train_20260307_020652.jsonl'
dataset.metadata['validation_path'] = '/tmp/autonomous-agent-v1_val_20260307_020652.jsonl'

# Store updated record
ledger.store_dataset(dataset)
print()
print('Updated dataset:')
print(f'  local_path: {dataset.local_path}')
print(f'  validation_path: {dataset.metadata["validation_path"]}')
print('Done!')
