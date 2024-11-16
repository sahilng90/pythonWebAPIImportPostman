from bs4 import BeautifulSoup
import json
import requests

# URL of the Help page
HELP_URL = "http://localhost:1212/Help"

# Base URL for APIs (adjust as needed)
BASE_URL = "http://localhost:1212"

# Output Postman collection file
OUTPUT_FILE = "postman_collection_with_folders_and_headers.json"

def fetch_help_page(url):
    """Fetch the HTML content of the help page."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_help_page(html):
    """Parse the help page HTML to extract API details."""
    soup = BeautifulSoup(html, "html.parser")
    
    folders = []
    
    # Iterate over each <h2> and the corresponding <table>
    for section in soup.find_all("h2"):
        section_name = section.text.strip()
        table = section.find_next("table", class_="help-page-table")
        if table:
            apis = []
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                api_link = row.find("a")
                description = row.find("td", class_="api-documentation").text.strip()
                
                if api_link:
                    api_url = api_link["href"]
                    method, endpoint = api_link.text.split(" ", 1)
                    apis.append({
                        "method": method.strip(),
                        "endpoint": endpoint.strip(),
                        "description": description
                    })
            if apis:
                folders.append({
                    "name": section_name,
                    "apis": apis
                })
    return folders

def generate_postman_collection(folders):
    """Generate a Postman collection with folders from API details."""
    collection = {
        "info": {
            "name": "API Collection",
            "description": "Generated from the Help page",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {
                "key": "baseUrl",
                "value": BASE_URL,
                "type": "string"
            }
        ],
        "item": []
    }

    for folder in folders:
        folder_item = {
            "name": folder["name"],
            "item": []
        }

        for api in folder["apis"]:
            # Parse query parameters from the endpoint
            url_parts = api["endpoint"].split("?")
            path = url_parts[0].lstrip("/").split("/")
            queries = []

            if len(url_parts) > 1:
                query_params = url_parts[1].split("&")
                for param in query_params:
                    key = param.split("=")[0]
                    queries.append({"key": key, "value": f"{{{{{key}}}}}"})

            # Construct the Postman request item
            api_item = {
                "name": api["endpoint"],
                "request": {
                    "method": api["method"],
                    "header": [
                        {
                            "key": "apiKey",
                            "value": "U2hyZWVTYWlFbnRlcnByaXNlcw==",
                            "description": "API key for authentication"
                        }
                    ],
                    "url": {
                        "raw": "{{baseUrl}}/" + api["endpoint"],
                        "host": ["{{baseUrl}}"],
                        "path": path,
                        "query": queries
                    },
                    "description": api["description"]
                }
            }
            folder_item["item"].append(api_item)

        collection["item"].append(folder_item)

    return collection

def save_collection_to_file(collection, filename):
    """Save the Postman collection to a JSON file."""
    with open(filename, "w") as f:
        json.dump(collection, f, indent=4)

def main():
    print(f"Fetching help page from {HELP_URL}...")
    html = fetch_help_page(HELP_URL)

    print("Parsing help page...")
    folders = parse_help_page(html)
    print(f"Found {len(folders)} sections with APIs.")

    print("Generating Postman collection with folders and headers...")
    collection = generate_postman_collection(folders)

    print(f"Saving Postman collection to {OUTPUT_FILE}...")
    save_collection_to_file(collection, OUTPUT_FILE)

    print(f"Postman collection saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
