import requests

AIRTABLE_API_KEY = "patS1VYb5EHfiXXBV.71390a90cefd89f88d05485625c803ba5df091b89acf76a160685dca3f4d46aa"
AIRTABLE_BASE_ID = "app2j2xblYodCdMZQ"
AIRTABLE_TABLE_NAME = "Table2"

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

response = requests.get(AIRTABLE_URL, headers=HEADERS)
print(response.status_code)
print(response.json())  # طباعة البيانات لمعرفة ما يتم إرجاعه
