import time
import uuid
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.utils.pinecone import store_vectors

# In-memory data stores for tasks
tasks = {"task_id": {"visited_urls": set(), "status": ""}}


# Function to split text into chunks less than 7000 tokens
def split_text_into_chunks(text, chunk_size):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i : i + chunk_size])


def is_same_domain(url, domain):
    parsed_url = urlparse(url)
    return parsed_url.netloc == domain


def perform_crawl(start_url, depth, task_id):
    queue = deque([(start_url, 0)])
    batch = []
    chunk_size = 4000  # Define the chunk size

    parsed_start_url = urlparse(start_url)
    domain = parsed_start_url.netloc

    while queue:
        current_url, current_depth = queue.popleft()

        print("Begin processing url: " + current_url)

        if current_depth > depth or current_url in tasks[task_id]["visited_urls"]:
            continue

        try:
            success = False
            for _ in range(3):  # Retry logic
                try:
                    response = requests.get(current_url, timeout=10)
                    response.raise_for_status()  # Raise an HTTPError for bad responses
                    success = True
                    break
                except (requests.RequestException, requests.Timeout):
                    time.sleep(1)  # Wait 1 second before retrying

            if not success:
                print(f"Failed to retrieve {current_url} after 3 attempts. Skipping.")
                continue

            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")

            content = soup.get_text(separator="\n").strip()

            if content:
                chunks = split_text_into_chunks(content, chunk_size)
                for chunk in chunks:
                    document = {"task_id": task_id, "url": current_url, "text": chunk}
                    batch.append(document)
                    if len(batch) >= 10:
                        print()
                        print("Indexing batch to vector store!!!")
                        print()
                        store_vectors(batch)
                        batch = []

            print("Processed content length: " + str(len(content)))

            tasks[task_id]["visited_urls"].add(current_url)

            if current_depth < depth:
                links = soup.find_all("a")
                for link in links:
                    href = link.get("href")
                    if href:
                        full_url = urljoin(current_url, href)
                        if is_same_domain(full_url, domain):
                            queue.append((full_url, current_depth + 1))

            # Artificial stop to avoid server overload
            time.sleep(1)  # Wait 1 second before processing the next URL

        except Exception as e:
            print(f"Error processing {current_url}: {e}")
            tasks[task_id]["status"] = "failed"
            continue

    if batch:
        store_vectors(batch)

    tasks[task_id]["status"] = "completed"


def start_crawl(start_url, depth=2):
    if not start_url:
        return {"error": "Start URL is required"}, 400

    task_id = str(uuid.uuid4())
    print(task_id)
    tasks[task_id] = {"status": "in_progress", "visited_urls": set()}

    perform_crawl(start_url, depth, task_id)

    tasks[task_id]["status"] = "completed"
    return {"message": "Crawling started", "task_id": task_id}, 200


def get_crawl_status(task_id):
    if not task_id or task_id not in tasks:
        return {"error": "Invalid task ID"}, 400

    return {
        "task_id": task_id,
        "status": tasks[task_id]["status"],
        "visited_urls": list(tasks[task_id]["visited_urls"]),
    }, 200
