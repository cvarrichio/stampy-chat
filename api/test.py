import aiohttp
import asyncio
import logging
import csv
import datetime

logging.basicConfig(level=logging.DEBUG)

async def send_to_api(question, session):
    url = f'https://chat.stampy.ai:8443/chat/{question}'
    logging.debug(url)
    RETRIES = 3
    retry_count = 0
    while retry_count < RETRIES:
        try:
            async with session.get(url) as resp:
                response_text = await resp.text()
                logging.debug(f"API response: {response_text}")
                if resp.status != 200:
                    logging.info(f"Error on API request: {await resp.json()}")
                return await resp.json(content_type=None),question if resp.status == 200 else None
        except (Exception) as e:
                logging.info(f"Error on API request, retrying: {e}")
                retry_count += 1
                if retry_count >= RETRIES:
                    logging.info(f"Unexpected error on API request: {e}")
                    return None
                else:
                    await asyncio.sleep(2)  

        finally:
            await asyncio.sleep(0.1) 


async def call_api(questions):
    async with aiohttp.ClientSession() as session:
        tasks = [send_to_api(question, session) for question in questions]
        results = await asyncio.gather(*tasks)

    from chat import construct_prompt
    for result, question in results:
        if result is not None:  # Check if the result is not None
            result['prompt'] = construct_prompt(question,[],[])
            result['query'] = question

    return [result for result, question in results]

import nest_asyncio
nest_asyncio.apply()

def format_citations(citations):
    formatted_citations = []
    for key, citation in citations.items():
        formatted_citation = f"[{key}]{citation['title']} - {citation['author']} - {citation['date']}"
        formatted_citations.append(formatted_citation)
    return '\n'.join(formatted_citations)

if __name__ == '__main__':

    # Run the function
    questions = [
        "Can AI take over the world?",
        "Can we just turn off AI if it becomes dangerous?",
        "Can AI become conscious or have feelings?"
    ]

    with open('../tests/query_tests.csv', 'r') as file:
        questions = list(csv.reader(file))
    results = asyncio.run(call_api(questions))

    # Prepare data for CSV
    csv_data = [['query', 'generated_response', 'citations', 'prompt_template']]

    # Iterate over each response in the list
    for json_obj in results:
        # Update the 'citations' field in the JSON object
        json_obj['formatted_citations'] = format_citations(json_obj['citations'])

        # Extract prompt template from prompt
        prompt_template = next((item for item in json_obj['prompt'] if item["role"] == "system"), None)['content']

        # Append data to CSV data list
        csv_data.append([json_obj['query'], json_obj['response'], json_obj['formatted_citations'], prompt_template])

    now = datetime.datetime.now() # current date and time
    timestamp = now.strftime("%Y%m%d%H%M%S")

    with open(f'../tests/results/prompt_test_results_{timestamp}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)