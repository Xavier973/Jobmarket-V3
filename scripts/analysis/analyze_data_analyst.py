import json
from pathlib import Path
from collections import Counter

# Charger les offres
offers = [json.loads(line) for line in 
          Path('data/raw/francetravail/offers_kw_data_analyst.jsonl').read_text(encoding='utf-8').strip().split('\n')]

print('📊 Analyse des 100 offres "data analyst":\n')

print('Top 15 titres:')
titles = Counter([o['intitule'] for o in offers])
for i, (title, count) in enumerate(titles.most_common(15), 1):
    print(f'  {i}. {title} ({count}x)')

print(f'\nCodes ROME:')
rome = Counter([f"{o.get('romeCode', 'N/A')} - {o.get('romeLibelle', '')[:40]}" for o in offers])
for code, count in rome.most_common(8):
    print(f'  {code} ({count}x)')

print(f'\nExemples de salaires:')
salaries = [o.get('salaire', {}).get('libelle', 'Non spécifié') for o in offers[:10]]
for i, sal in enumerate(salaries, 1):
    print(f'  {i}. {sal}')
