"""Quick check that the two APIs in config/settings.yaml work.

Run it from the project folder:  python scripts/check_apis.py
It downloads nothing big - it only asks each API a small question.
"""

import requests
import yaml

# Say who is asking. Some sites (like OpenPrescribing) block requests that
# arrive with Python's default name, so we send our own.
HEADERS = {"User-Agent": "nhs-prescribing-savings (portfolio project; github)"}

# 1. Read my settings file
with open("config/settings.yaml") as f:
    settings = yaml.safe_load(f)

nhsbsa = settings["sources"]["nhsbsa"]
op = settings["sources"]["openprescribing"]

# 2. NHSBSA: ask which monthly prescribing files exist
print("1) NHSBSA - which months are published?")
url = f"{nhsbsa['ckan_base_url']}/package_show"
resp = requests.get(url, params={"id": nhsbsa["epd_dataset_id"]}, headers=HEADERS, timeout=60)
resp.raise_for_status()  # stop here if the API gave an error
files = [r["name"] for r in resp.json()["result"]["resources"]]
months = sorted(name for name in files if name.upper().startswith(nhsbsa["resource_prefix"]))
print(f"   {len(months)} monthly files. Newest: {months[-3:]}")

# 3. NHSBSA: read 3 rows from the newest month with SQL (no big download)
print("2) NHSBSA - a small sample of the newest month")
newest = months[-1]
sql = f'SELECT * FROM "{newest}" LIMIT 3'
url = f"{nhsbsa['ckan_base_url']}/datastore_search_sql"
resp = requests.get(url, params={"sql": sql}, headers=HEADERS, timeout=60)
if resp.ok:
    rows = resp.json()["result"]["records"]
    print(f"   Columns: {list(rows[0].keys())}")
else:
    # the SQL table name sometimes differs from the file name - not a problem for the pipeline
    print(f"   SQL sample not available for {newest} (status {resp.status_code}) - that's OK")

# 4. OpenPrescribing: national spending on the benchmark drug
print("3) OpenPrescribing - national totals for the benchmark drug")
url = f"{op['base_url']}/spending/"
params = {"code": op["benchmark_bnf_code"], "format": "json"}
resp = requests.get(url, params=params, headers=HEADERS, timeout=60)
if resp.status_code == 403:
    # OpenPrescribing sits behind Cloudflare, which now blocks most scripts.
    # It's only used as an outside cross-check, so warn instead of failing.
    print("   Blocked (403) - OpenPrescribing is refusing scripted requests right now.")
    print("   The pipeline will use NHSBSA data only. Check the site in a browser instead.")
else:
    resp.raise_for_status()  # any other error is a real problem
    latest = resp.json()[-1]  # the last row is the newest month
    print(f"   Latest month: {latest['date']}")
    print(f"   Items: {latest['items']:,}  Cost: £{latest['actual_cost']:,.0f}")

print("Done - the NHSBSA API works, so the pipeline can download data.")
