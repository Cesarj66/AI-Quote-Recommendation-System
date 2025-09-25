import os
from dotenv import load_dotenv
from collections import OrderedDict
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions import extract_and_insert_matching_pages_dict, extract_quotes  # Replace 'some_function' with the actual function(s) you need to import
from supabase_utils import get_quotes_range, update_embedding_for_quotes
from openRouterClient import fetch_chat_completion
import re

load_dotenv()
embedding_key = os.getenv("EMBEDDING_KEY")

# # read every line in a file and return a list of names
# def read_names(file_path):
#     if not os.path.exists(file_path):
#         print(f"Error: File '{file_path}' does not exist.")
#         return []
#     with open(file_path, 'r') as file:
#         print(f"Reading names from {file_path}")
#         names = [line.strip() for line in file]
#     return names

# file_path = 'list/names.txt'  # Replace with your file path
# names = read_names(file_path)
# no_duplicates = list(set(names))

# # Create an ordered dictionary
# ordered_dict_names = OrderedDict()
# for name in no_duplicates:
#     try:
#         key, values = name.split(" — ")
#         # remove the leading number from the key with regex
#         key = key.split(". ")[1].strip() if ". " in key else key
#         values = values.strip().split(", ")

#         values[0] = values[0].strip().split("/")
#         values[2] = int(values[2].strip())
#         ordered_dict_names[key] = values
#     except ValueError:
#         print(f"Skipping invalid entry: {name}")

# ordered_dict_names = OrderedDict(sorted(ordered_dict_names.items(), key=lambda item: (item[1][2], item[0])))

# # print(ordered_dict_names)
# # print(f"Number of names: {len(ordered_dict_names)}")

# # create a list of names from the ordered dictionary
# names_list = []
# for key, values in ordered_dict_names.items():
#     # print(f"Key: {key}, Values: {values}")
#     names_list.append(key)

# print(f"Number of names: {len(names_list)}")

# matched_pages = extract_and_insert_matching_pages_dict(ordered_dict_names)

# print(f"Number of matched pages: {len(matched_pages)}")
# print(f"Matched pages: {matched_pages}")

# extract_quotes()

# quotes = get_quotes_range(0, 5000)
# for quote in quotes:
#     print(f"Quote ID: {quote['id']}")
#     print(f"Quote Text: {quote['quote'][:100]}")
# exit()

from supabase import create_client

# Supabase credentials
url = "https://ekrumlfvpstscaavmdtx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVrcnVtbGZ2cHN0c2NhYXZtZHR4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MDA3OTczOSwiZXhwIjoyMDU1NjU1NzM5fQ.4VjsrieuyCn8EX94vWckCM_DbEe1Seb4Baa53siRwk4"

# Initialize Supabase client
supabase = create_client(url, key)

from openai import OpenAI
client = OpenAI(api_key=embedding_key)

def generate_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

instructions = "Generate a semantically rich, self-contained, very concise, one sentence version of a quote provided suitable for vector embedding in English. Keep it in English. Start the sentence with \"[Q]\".\n\nSample format:\n[Q] core sentence.\nProvided quote:\n{quote}\n\n"

# quotes = get_quotes_range(7867, 10316)
# # print(f"Number of quotes: {len(quotes)}")
# # print(f"Quotes: {quotes[0].get('quote')}")

# # iterate over the quotes and update the embedding for each quote
# for quote in quotes:
#     quote_id = quote['id']
#     quote_text = quote.get('quote')
#     if quote_text: 
#         # print(f"Quote: {quote_text}")
#         # print(f"Quote ID: {quote.get('id')}")
#         # print(f"Quote Text: {quote_text}")
#         if len(quote_text) > 200:
#             response = fetch_chat_completion(model = "qwen/qwen-2.5-7b-instruct", prompt = instructions.format(quote=quote_text))
#             if response:
#                 match = re.search(r'\[Q\]\s*(.*)', response)
#                 summary = match.group(1) if match else response
#                 quote_id = quote.get('id')
#                 # print(f"Quote ID: {quote_id}")
#                 # print(f"Quote Text: {quote_text}")
#                 # print(f"Summary: {summary}")
#                 # print(f"Embedding for Quote ID {quote_id}: {embedding}")
#                 embedding = generate_embedding(summary)
#                 try:
#                     response = supabase.table("quotes").update({"summary": summary,"embedding": embedding}).eq("id", quote_id).execute()
#                     if response.data:
#                         print(f"✅ Updated embedding for quote ID {quote_id}")
#                     else:
#                         print(f"⚠️ No update made for quote ID {quote_id}")
#                 except Exception as e:
#                     print(f"❌ Failed to update quote ID {quote_id}: {e}")
#         else:
#             embedding = generate_embedding(quote_text)
#             try:
#                 response = supabase.table("quotes").update({"embedding": embedding}).eq("id", quote_id).execute()
#                 if response.data:
#                     print(f"✅ Updated embedding for quote ID {quote_id}")
#                 else:
#                     print(f"⚠️ No update made for quote ID {quote_id}")
#             except Exception as e:
#                 print(f"❌ Failed to update quote ID {quote_id}: {e}")

# # update_embedding_for_quotes(quotes, extract_quotes)


from transformers import pipeline

classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

def goemotion(s,threshold=0.2):
    model_outputs = classifier(s)
    return {
        'labels':[e['label'] for e in model_outputs[0] if e['score']>threshold],
        'scores':[e['score'] for e in model_outputs[0] if e['score']>threshold]
    }

def goemotions(s_list,threshold=0.2):
    model_outputs = classifier(s_list)
    return [
        {
            'labels':[e['label'] for e in emotions if e['score']>threshold],
            'scores':[e['score'] for e in emotions if e['score']>threshold]
        } for emotions in model_outputs
    ]

records = get_quotes_range(5908, 10316)

# records = get_quotes_range(5908, 5928)

# records = supabase.table('quotes').select('*').execute().data
# print(f"Fetched {len(records)} records from the database.")
for record in records:
    try:
        quote_text = record['quote']
        if len(quote_text) > 200:
            emotions = goemotion(record['quote'])        
        else:
            emotions = goemotion(record['summary'])
        print(f"Quote: {quote_text[:200]}...")
        print(f"Updating record ID {record['id']} with emotions: {emotions}")
        print("-" * 50)
        supabase.table('quotes').update({'emotions': emotions}).eq('id', record['id']).execute()
        
    except Exception as e:
        print(f"❌ Error processing record ID {record['id']}: {e}")
        break
