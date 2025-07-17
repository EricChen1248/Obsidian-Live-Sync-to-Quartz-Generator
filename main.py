import os
import requests
import urllib.parse
import dotenv
import shutil

dotenv.load_dotenv()

SYNC_BASE_DIR = 'sync'
SYNC_DIR = os.path.join(SYNC_BASE_DIR, "workspace")
if not os.path.exists(SYNC_BASE_DIR):
    os.mkdir(SYNC_BASE_DIR)

exclude_extensions = os.environ['EXCLUDE_EXTENSIONS'].split(',')
host = os.environ['COUCHDB_HOST']
database = os.environ['COUCHDB_DATABASE']
auth = (os.environ['COUCHDB_USERNAME'], os.environ['COUCHDB_PASSWORD'])

json_headers = {'Content-Type': 'application/json'}

if os.path.exists(SYNC_DIR):
     shutil.rmtree(SYNC_DIR)

os.mkdir(SYNC_DIR)

res = requests.get(f'{host}/{database}/_all_docs', auth=auth)
for doc in res.json()['rows']:
    if doc['id'].endswith('.md'):

        # skip files that have certain extensions. (For example, .excalidraw.md files that are useless for quartz rendering)
        if doc['id'].endswith(tuple(exclude_extensions)):
            continue
        
        path = urllib.parse.quote_plus(doc['id'])
        doc_data = requests.get(f'{host}/{database}/{path}', auth=auth).json()
        if 'deleted' in doc_data:
            continue

        print(f'Syncing {doc["id"]}')
        if 'children' in doc_data:
            # if 'children' is missing, that means the file is empty(?) no reason to create the empty file.

            file_path = doc_data['path']
            os.makedirs(os.path.join(SYNC_DIR, os.path.dirname(file_path)), exist_ok=True)
            with open(f'{SYNC_DIR}/{file_path}', 'w') as f:
                # The children of a file are the contents. In the order they appear in the document.
                # Use the _bulk_get API to get the contents of the children.
                # https://docs.couchdb.org/en/stable/api/database/bulk-api.html#db-bulk-get
                children = {"docs": [{'id': val } for val in doc_data['children']]}
                res = requests.post(f'{host}/{database}/_bulk_get', auth=auth, json=children, headers=json_headers)

                for content in res.json()['results']:
                    f.write(content['docs'][0]['ok']['data'])

# move synced folder to final destination
final_destination = "/quartz/content"
# final_destination = os.path.join(SYNC_BASE_DIR, database)

# delete the path to skip handling deleted files.
if os.path.exists(final_destination):
    shutil.rmtree(final_destination)

os.rename(SYNC_DIR, final_destination)
print(f'Synced files moved to {final_destination}')