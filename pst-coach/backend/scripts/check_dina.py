"""Quick script to check Dina Cartagena emails."""
import json

emails = json.load(open('data/extracted/bf424c1351d54de4-manual.json', encoding='utf-8'))

dina_emails = []
for e in emails:
    text = (e.get('from','') + ' ' + e.get('to','') + ' ' + e.get('body','')).lower()
    if 'dina cartagena' in text:
        dina_emails.append(e)

print(f"Found {len(dina_emails)} emails mentioning Dina Cartagena")
print()

for e in dina_emails[:10]:
    print("---")
    print(f"From: {e.get('from')}")
    print(f"To: {e.get('to','')[:100]}")
    print(f"Subject: {e.get('subject')}")
    print(f"Date: {e.get('date')}")
    print(f"Body preview: {e.get('body','')[:300]}")
    print()
