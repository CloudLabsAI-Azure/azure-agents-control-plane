#!/usr/bin/env python3
"""Start fine-tuning via MCP."""
import requests, json

base_url = 'http://localhost:8000/runtime/webhooks/mcp'

def get_session():
    r = requests.get(f'{base_url}/sse', stream=True, timeout=15)
    for line in r.iter_lines(decode_unicode=True):
        if line and line.startswith('data: '):
            r.close()
            return f'{base_url}/{line[6:].strip()}'
    return None

def call_tool(name, args):
    url = get_session()
    print(f'Session: {url}')
    r = requests.post(url, json={
        'jsonrpc': '2.0', 'id': 1,
        'method': 'tools/call',
        'params': {'name': name, 'arguments': args}
    }, timeout=300)
    result = r.json()
    content = result.get('result', {}).get('content', [])
    if content:
        text = content[0].get('text', '')
        try:
            return json.loads(text)
        except:
            return {'text': text}
    return result

print('=== STARTING FINE-TUNING JOB ===')
print('Parameters:')
print('  dataset_id: 1c47aa12-2e07-4d0e-8674-4f65164e3c85')
print('  agent_id: autonomous-agent') 
print('  base_model: gpt-4o-mini')
print('  n_epochs: 3')
print('  learning_rate_multiplier: 1.0 (config default)')
print()

result = call_tool('lightning_start_training', {
    'dataset_id': '1c47aa12-2e07-4d0e-8674-4f65164e3c85',
    'agent_id': 'autonomous-agent',
    'base_model': 'gpt-4o-mini',
    'n_epochs': 3,
})
print(json.dumps(result, indent=2))
