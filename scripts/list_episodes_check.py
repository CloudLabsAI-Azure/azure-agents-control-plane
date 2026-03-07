#!/usr/bin/env python3
"""List episodes and check episode count."""
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
    r = requests.post(url, json={
        'jsonrpc': '2.0', 'id': 1,
        'method': 'tools/call',
        'params': {'name': name, 'arguments': args}
    }, timeout=180)
    result = r.json()
    content = result.get('result', {}).get('content', [])
    if content:
        text = content[0].get('text', '')
        try:
            return json.loads(text)
        except:
            return {'text': text}
    return result

# List episodes
r = call_tool('lightning_list_episodes', {'agent_id': 'autonomous-agent', 'limit': 50})
episodes = r.get('episodes', [])
print(f'Total episodes: {len(episodes)}')
rewarded = [e for e in episodes if e.get('reward') is not None and e.get('reward', 0) > 0]
print(f'Rewarded episodes (>0): {len(rewarded)}')
for e in episodes:
    eid = e.get('id', '?')[:12]
    reward = e.get('reward', 'N/A')
    status = e.get('status', '?')
    print(f'  {eid}... reward={reward} status={status}')
