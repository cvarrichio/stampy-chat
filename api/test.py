
import aiohttp
import asyncio
import logging

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
                    logging.info(f"Error on API request: {await resp.json(content_type=None)}")
                    return None
                result = await resp.json(content_type=None)
                from chat import construct_prompt
                result['prompt'] = construct_prompt(question,[],[])
                return result
        except (Exception) as e:
                logging.info(f"Error on API request, retrying: {e}")
                retry_count += 1
                if retry_count >= RETRIES:
                    logging.info(f"Unexpected error on API request: {e}")
                    raise  # Re-raise any other exceptions
                else:
                    await asyncio.sleep(2)  # Use asyncio.sleep instead of time.sleep

        finally:
            await asyncio.sleep(0.1) 

async def call_api(questions):
    async with aiohttp.ClientSession() as session:
        tasks = [send_to_api(question, session) for question in questions]
        results = await asyncio.gather(*tasks)
    return results

import nest_asyncio
nest_asyncio.apply()

# Run the function
import sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
questions = [
    "Can AI take over the world?",
    "Can we just turn off AI if it becomes dangerous?",
    "Can AI become conscious or have feelings?",
    "Will AI replace all human jobs?",
    "Can AI be ethical or moral?",
    "Will you kill us all?",
    "What is AI alignment, and why is it important?",
    "What are some potential risks associated with advanced AI, and how can they be mitigated?",
    "Can AI be programmed to behave ethically, and how can we ensure that it does?",
    "How can we ensure that AI systems are transparent and explainable in their decision-making processes?",
    "What is the difference between narrow and general AI, and how does this impact safety and alignment?"
]
results = asyncio.run(call_api(questions))