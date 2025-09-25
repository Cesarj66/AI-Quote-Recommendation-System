from transformers import pipeline

classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

def goemotion(s,threshold=0.3):
    model_outputs = classifier(s)
    return {
        'labels':[e['label'] for e in model_outputs[0] if e['score']>threshold],
        'scores':[e['score'] for e in model_outputs[0] if e['score']>threshold]
    }

def goemotions(s_list,threshold=0.3):
    model_outputs = classifier(s_list)
    return [
        {
            'labels':[e['label'] for e in emotions if e['score']>threshold],
            'scores':[e['score'] for e in emotions if e['score']>threshold]
        } for emotions in model_outputs
    ]


# supabase
from supabase import create_client
import os

url: str = "https://ekrumlfvpstscaavmdtx.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVrcnVtbGZ2cHN0c2NhYXZtZHR4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MDA3OTczOSwiZXhwIjoyMDU1NjU1NzM5fQ.4VjsrieuyCn8EX94vWckCM_DbEe1Seb4Baa53siRwk4"
supabase = create_client(url, key)

records = supabase.table('wikiquote_duplicate').select('*').execute().data
print(f"Fetched {len(records)} records from the database.")
# for record in records:
#     emotions = goemotion(record['quote'])
#     print(f"Updating record ID {record['id']} with emotions: {emotions}")
#     supabase.table('wikiquote_duplicate').update({'Emotions': emotions}).eq('id', record['id']).execute()
for record in records:
    try:
        emotions = goemotion(record['quote'])
        print(f"Updating record ID {record['id']} with emotions: {emotions}")
        supabase.table('wikiquote_duplicate').update({'Emotions': emotions}).eq('id', record['id']).execute()
    except Exception as e:
        print(f"❌ Error processing record ID {record['id']}: {e}")
        break
