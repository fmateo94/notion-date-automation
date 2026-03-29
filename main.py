import os
import requests
from datetime import date

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
TODAY = date.today().isoformat()

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

DATABASES = [
    {
        "name": "Personal",
        "id": "4e230399-f198-4c0d-8504-5a0c54dfa14d",
        "exclude_statuses": ["Done", "Notes", "Backlog"],
    },
    {
        "name": "Lightspeed",
        "id": "79e08774-3a4b-457c-aa88-8e2f66e1b66c",
        "exclude_statuses": ["Done", "Notes", "Backlog"],
    },
    {
        "name": "E-Commerce",
        "id": "22efb4df-9d88-80c4-b907-efdfd37f4b59",
        "exclude_statuses": ["Done", "Notes", "Backlog"],
    },
]


def query_database(database_id, exclude_statuses):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    filter_conditions = [
        {"property": "Status", "status": {"does_not_equal": s}}
        for s in exclude_statuses
    ]
    payload = {"filter": {"and": filter_conditions}, "page_size": 100}
    pages = []
    while True:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        pages.extend(data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return pages


def update_date(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {"Date": {"date": {"start": TODAY}}}}
    resp = requests.patch(url, headers=HEADERS, json=payload)
    resp.raise_for_status()


def main():
    print(f"Running date update for {TODAY}")
    total_updated = 0

    for db in DATABASES:
        pages = query_database(db["id"], db["exclude_statuses"])
        count = 0
        for page in pages:
            update_date(page["id"])
            count += 1
        print(f"  {db['name']}: updated {count} tasks")
        total_updated += count

    print(f"Done. Total tasks updated: {total_updated}")


if __name__ == "__main__":
    main()
