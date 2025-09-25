from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables from the .env file
load_dotenv()

def fetch_chat_completion(model, prompt):
    # Fetch the API key from environment variables
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable is not set.")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        })
    )
    
    # Check for HTTP errors
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def test_models_and_prompts(models, prompts, markdown_file_path):
    try:
        with open(markdown_file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()

        for model in models:
            print(f"\n{'='*40}\nTesting model: {model}\n{'='*40}")
            for quote in prompts:
                try:
                    prompt = f"{markdown_content}\nHere is the quote you need to clean:\n{quote}"
                    print(f"Testing model: {model} with quote: {quote}")
                    result = fetch_chat_completion(model, prompt)
                    print(f"Response from {model}:\n{result}\n")
                    print(f"{'-'*40}")
                except Exception as e:
                    print(f"Error with model {model} and quote {quote}: {e}")

    except FileNotFoundError:
        print(f"Error: The file {markdown_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def run_filter_tests():
    """
    Runs tests for the filter models and prompts using the filter markdown file.
    """
    filter_file_path = "prompts/prompt-1-filter.md"

    filter_models = [
        # "google/gemini-2.0-flash-001", # $0.1/M input tokens $0.4/M output tokens
        # "openai/gpt-4o-mini", # $0.15/M input tokens $0.6/M output tokens
        # "google/gemini-flash-1.5-8b", # $0.0375/M input tokens $0.15/M output tokens
        # "meta-llama/llama-3.3-70b-instruct", # $0.12/M input tokens $0.3/M output tokens; too slow!
        "qwen/qwen-2.5-7b-instruct", # $0.025/M input tokens $0.05/M output tokens
        # "deepseek/deepseek-r1:free" # Free
    ]

    filter_prompts = [
        "**'''Macbeth:''' Is this a dagger which I see before me, the handle toward my hand?**",
        # Quotable — classic literary dialogue

        "**'''Note:''' This page has been archived and will no longer be updated.**",
        # Not Quotable — editorial/system notice

        "**'''Hamlet''': To [[wikipedia:be|be]] or not to [[wikipedia:not|not to be]], that is the question.**",
        # Quotable — contains wiki links, but still clear content

        "**[[Category:18th-century British politicians]]**",
        # Not Quotable — metadata/navigation element
    ]

    test_models_and_prompts(filter_models, filter_prompts, filter_file_path)

def run_formatter_tests():
    """
    Runs tests for the formatter models and prompts using the formatter markdown file.
    """
    formatter_file_path = "prompts/prompt-2-formatter.md"

    formatter_models = [
        # "google/gemini-2.0-flash-001", # $0.1/M input tokens $0.4/M output tokens
        # "openai/gpt-4o-mini", # $0.15/M input tokens $0.6/M output tokens
        # "google/gemini-flash-1.5-8b", # $0.0375/M input tokens $0.15/M output tokens
        # "meta-llama/llama-3.3-70b-instruct", # $0.12/M input tokens $0.3/M output tokens; too slow!
        "qwen/qwen-2.5-7b-instruct", # $0.025/M input tokens $0.05/M output tokens
        # "deepseek/deepseek-r1:free" # Free
    ]

    formatter_prompts = [
        """
        <b>Valjean:</b> Who am I? Who am I? <br> <i> I'm Jean Valjean!</i><!-- iconic line -->
        """,
        # Expected to remove <b>, <i>, and the comment, keep <br> and speaker

        """
        <!-- intro line -->Truth&nbsp;is&nbsp;not always pretty. (wikipedia:Friedrich_Nietzsche)<br><p>But it is always true.</p>
        """,
        # Clean out HTML comment, entity, wikipedia link, <p>, but keep <br>

        """
        Data: I believe the (wikipedia:Captain) Captain is correct.&nbsp;<br><div>We should proceed.</div>
        """,
        # Remove link and entity, but keep speaker and <br>, strip <div>

        """
        <b>Warning:</b> The following section <!-- redacted --> contains graphic content.<br>Viewer discretion is advised.
        """,
        # Strip <b> and comment, but since it's not a quote, this tests how well it trims prefatory non-quote text
    ]


    test_models_and_prompts(formatter_models, formatter_prompts, formatter_file_path)

def run_extractor_tests():
    """
    Runs tests for the extractor models and prompts using the extractor markdown file.
    """
    extractor_file_path = "prompts/prompt-3-extractor.md"

    extractor_models = [
        # "google/gemini-2.0-flash-001", # $0.1/M input tokens $0.4/M output tokens
        # "openai/gpt-4o",
        # "openai/gpt-4o-mini", # $0.15/M input tokens $0.6/M output tokens
        # "google/gemini-flash-1.5-8b", # $0.0375/M input tokens $0.15/M output tokens
        # "meta-llama/llama-3.3-70b-instruct", # $0.12/M input tokens $0.3/M output tokens
        # "qwen/qwen-2.5-7b-instruct", # $0.025/M input tokens $0.05/M output tokens
        "deepseek/deepseek-r1:free" # Free
    ]

    extractor_prompts = [
    # a man may have lived long, and yet lived but a little
    """Wherever your life ends, it is all there. The utility of living consists not in the length of days, but in the use of time; a man may have lived long, and yet lived but a little. Make use of time while it is present with you. It depends upon your will, and not upon the number of days, to have a sufficient length of life. Is it possible you can imagine never to arrive at the place towards which you are continually going? and yet there is no journey but hath its end. And, if company will make it more pleasant or more easy to you, does not all the world go the self-same way?""",

    # 
    """Those who have handled sciences have been either men of experiment or men of dogmas. The men of experiment are like the ant, they only collect and use; the reasoners resemble spiders, who make cobwebs out of their own substance. But the bee takes a middle course: it gathers its material from the flowers of the garden and of the field, but transforms and digests it by a power of its own. Not unlike this is the true business of philosophy; for it neither relies solely or chiefly on the powers of the mind, nor does it take the matter which it gathers from natural history and mechanical experiments and lay it up in the memory whole, as it finds it, but lays it up in the understanding altered and digested. Therefore from a closer and purer league between these two faculties, the experimental and the rational (such as has never yet been made), much may be hoped.""",

    # ...only an utterly senseless person can fail to know that our characters are the result of our conduct
    """Therefore only an utterly senseless person can fail to know that our characters are the result of our conduct.""",

    # The wars of peoples will be more terrible than those of kings
    """In former days, when wars arose from individual causes, from the policy of a Minister or the passion of a King, when they were fought by small regular armies of professional soldiers, and when their course was retarded by the difficulties of communication and supply, and often suspended by the winter season, it was possible to limit the liabilities of the combatants. But now, when mighty populations are impelled on each other, each individual severally embittered and inflamed—when the resources of science and civilisation sweep away everything that might mitigate their fury, a European war can only end in the ruin of the vanquished and the scarcely less fatal commercial dislocation and exhaustion of the conquerors. Democracy is more vindictive than Cabinets. The wars of peoples will be more terrible than those of kings.""",

    # # mathematics may be defined as the subject in which we never know what we are talking about, nor whether what we are saying is true
    # """Pure mathematics consists entirely of assertions to the effect that, if such and such a proposition is true of anything, then such and such another proposition is true of that thing. It is essential not to discuss whether the first proposition is really true, and not to mention what the anything is, of which it is supposed to be true. Both these points would belong to applied mathematics. We start, in pure mathematics, from certain rules of inference, by which we can infer that if one proposition is true, then so is some other proposition. These rules of inference constitute the major part of the principles of formal logic. We then take any hypothesis that seems amusing, and deduce its consequences. If our hypothesis is about anything, and not about some one or more particular things, then our deductions constitute mathematics. Thus mathematics may be defined as the subject in which we never know what we are talking about, nor whether what we are saying is true. People who have been puzzled by the beginnings of mathematics will, I hope, find comfort in this definition, and will probably agree that it is accurate."""
]

        
    test_models_and_prompts(extractor_models, extractor_prompts, extractor_file_path)

if __name__ == "__main__":
    # run_filter_tests()

    # run_formatter_tests()

    # run_extractor_tests() 
    exit()
