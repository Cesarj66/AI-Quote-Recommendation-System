from supabase import create_client
import os

# Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")


# Initialize Supabase client
supabase = create_client(url, key)

def insert_page(title, types, language_region, era):
    print("Inserting into 'Pages' table...")

    try:
        data = {"page_name": title, "type": types, "language_region": language_region, "era": era}
        response = supabase.table("pages").insert(data).execute()
        if response.data:
            print(f"✅ Inserted page: {title}")
        else:
            print(f"⚠️ No data inserted. Response: {response}")
    except Exception as e:
        print("❌ Database error:", e)

def insert_quote(page_id, quote_context, hierarchy, quote_info, quote):
    print("Inserting into 'Quotes' table...")

    try:
        data = {
            "page_id": page_id,
            "quote_context": quote_context,
            "hierarchy": hierarchy,
            "quote_info": quote_info,
            "quote": quote
        }
        response = supabase.table("quotes").insert(data).execute()
        if response.data:
            print(f"✅ Inserted quote: {quote}")
        else:
            print(f"⚠️ No data inserted. Response: {response}")
    except Exception as e:
        print("❌ Database error:", e)

def insert_provisional_quote(page_id, quote, hierarchy, quote_info):
    print("Inserting into 'provisional_quotes' table...")

    try:
        data = {
            "page_id": page_id,
            "quote": quote,
            "hierarchy": hierarchy,
            "quote_info": quote_info,
        }
        response = supabase.table("quotes").insert(data).execute()
        if response.data:
            print(f"✅ Inserted quote: {quote}")
        else:
            print(f"⚠️ No data inserted. Response: {response}")
    except Exception as e:
        print("❌ Database error:", e)

def get_all_pages():
    print("Fetching all rows from 'Pages' table...")

    try:
        response = supabase.table("pages").select("*").execute()
        if response.data:
            print(f"✅ Retrieved {len(response.data)} rows.")
            return response.data
        else:
            print("⚠️ No data found.")
            return []
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def get_all_quotes():
    print("Fetching all rows from 'Quotes' table...")

    try:
        response = supabase.table("quotes").select("*").execute()
        if response.data:
            print(f"✅ Retrieved {len(response.data)} rows.")
            return response.data
        else:
            print("⚠️ No data found.")
            return []
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def get_quotes_range(start_id, end_id, batch_size=1000):
    print(f"Fetching quotes with id from {start_id} to {end_id}...")

    all_quotes = []
    current_start = start_id

    try:
        while current_start <= end_id:
            current_end = min(current_start + batch_size - 1, end_id)

            response = (
                supabase.table("quotes")
                .select("*")
                .gte("id", current_start)
                .lte("id", current_end)
                .order("id", desc=False)
                .execute()
            )

            if response.data:
                print(f"✅ Retrieved {len(response.data)} quotes (ID {current_start} to {current_end})")
                all_quotes.extend(response.data)
            else:
                print(f"⚠️ No quotes found for IDs {current_start} to {current_end}")

            current_start = current_end + 1  # move to next batch

        print(f"\n✅ Total quotes retrieved: {len(all_quotes)}")
        return all_quotes

    except Exception as e:
        print(f"❌ Database error: {e}")
        return []
    
def update_embedding_for_quotes(quote, summary, embedding):
    quote_id = quote['id']
    quote = quote['quote']

    try:
        response = supabase.table("quotes").update({"summary": summary,"embedding": embedding}).eq("id", quote_id).execute()
        if response.data:
            print(f"✅ Updated embedding for quote ID {quote_id}")
        else:
            print(f"⚠️ No update made for quote ID {quote_id}")
    except Exception as e:
        print(f"❌ Failed to update quote ID {quote_id}: {e}")

def delete_page(page_id):
    print(f"Deleting page with ID {page_id}...")

    try:
        response = supabase.table("pages").delete().eq("id", page_id).execute()
        if response.data:
            print(f"✅ Deleted page with ID: {page_id}")
        else:
            print(f"⚠️ No page found with ID: {page_id}")
    except Exception as e:
        print(f"❌ Database error: {e}")

def delete_quote(quote_id):
    print(f"Deleting quote with ID {quote_id}...")

    try:
        response = supabase.table("quotes").delete().eq("id", quote_id).execute()
        if response.data:
            print(f"✅ Deleted quote with ID: {quote_id}")
        else:
            print(f"⚠️ No quote found with ID: {quote_id}")
    except Exception as e:
        print(f"❌ Database error: {e}")

def delete_all_pages():
    print("Deleting ALL rows from 'Pages' table...")

    try:
        response = supabase.table("pages").delete().neq("id", -1).execute()
        if response.data:
            print(f"✅ Deleted all pages.")
        else:
            print("⚠️ No pages to delete.")
    except Exception as e:
        print(f"❌ Database error: {e}")

def delete_all_quotes():
    print("Deleting ALL rows from 'Quotes' table...")

    try:
        response = supabase.table("quotes").delete().neq("id", -1).execute()
        if response.data:
            print(f"✅ Deleted all quotes.")
        else:
            print("⚠️ No quotes to delete.")
    except Exception as e:
        print(f"❌ Database error: {e}")

# Example usage:
# insert_page("Example Page Title")
# insert_quote(1, "Example Quote", "Example Hierarchy", "Example Info")

# pages = get_all_pages()
# quotes = get_all_quotes()

# delete_page(1)
# delete_quote(1)

# delete_all_pages()
# delete_all_quotes()
