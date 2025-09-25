from transformers import BertTokenizer
from model import BertForMultiLabelClassification
from multilabel_pipeline import MultiLabelPipeline

tokenizer = BertTokenizer.from_pretrained("monologg/bert-base-cased-goemotions-original")
model = BertForMultiLabelClassification.from_pretrained("monologg/bert-base-cased-goemotions-original")

goemotions = MultiLabelPipeline(
    model=model,
    tokenizer=tokenizer,
    threshold=0.3
)

# usage: goemotions('quote1') -> outputs list with one dict [{'labels': ['neutral'], 'scores': [0.9750906]}]
# usage: goemotions(['quote1','quote2']) -> outputs list of dict [{'labels': ['neutral'], 'scores': [0.9750906]},{'labels': ['neutral'], 'scores': [0.9750906]}]

from supabase import create_client
import os

url: str = "https://ekrumlfvpstscaavmdtx.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVrcnVtbGZ2cHN0c2NhYXZtZHR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAwNzk3MzksImV4cCI6MjA1NTY1NTczOX0.FuASP8XxbOkCQReAobHhKhsQCOrWA6oVwestAuoj8v0"
supabase = create_client(url, key)

records = supabase.table('wikiquote_duplicate').select('*').is_('Emotions', None).execute().data
print(f"Fetched {len(records)} records from the database.")
for record in records:
    emotions = goemotions(record['quote'])[0]
    print(f"Updating record ID {record['id']} with emotions: {emotions}")
    supabase.table('wikiquote_duplicate').update({'Emotions': emotions}).eq('id', record['id']).execute()