# This is an example of how to use Transkribus API
# It is copied and modified from somewhere in GitHub 
# and Transkribus API's documentation. Thanks for everyone
# whose examples have been used!

import requests
from lxml import objectify
from pathlib import Path

# Define building blocks for the endpoints:
api_base_url = "https://transkribus.eu/TrpServer/rest/"
login_endpoint = "auth/login"
collections_endpoint = "collections/list"
logout_endpoint = "auth/logout"

username = '' # email address you use to login to Transkribus
password = '' # maybe come up with some other way to store the password

# Log in:
## Prepare the payload for the POST request:
credentials = {'user': username,
               'pw': password}
## Create the POST request (the requests package converts the credentials into JSON automatically):
response = requests.post(api_base_url + login_endpoint, data=credentials)

if response:
    r = objectify.fromstring(response.content)
    print(f"TRANSKRIBUS: User {r.firstname} {r.lastname} ({r.userId}) logged in successfully.")
    session_id = str(r.sessionId)
else:
    sys.exit("TRANSKRIBUS: Login failed. Check your credentials!")
    
# View your collections

cookies = dict(JSESSIONID=session_id)
response = requests.get(api_base_url + collections_endpoint, cookies=cookies)
if response:
    collections = response.json()
    print("Your collections:")
    for collection in collections:
#        print(collection)
        print(f"– {collection['colName']}: {collection['colId']}")
else:
    sys.exit("Could not retrieve collections.")

# Select the collection id you are interested about and view the documents in it

col_id = '0000'

response = requests.get(f"https://transkribus.eu/TrpServer/rest/collections/{col_id}/list", cookies=cookies)

for document in response.json():
    
    print(f"{document['title']}: {document['docId']}")

# This would be the way to get the document object

doc_id = '0000'

document = requests.get(f"https://transkribus.eu/TrpServer/rest/collections/{col_id}/{doc_id}/fulldoc", cookies=cookies)

# Let's say we want to save all ground truth pages as files, as we often want to do 
# when we train models locally

def write_gt(document, directory = 'ground_truth'):

    Path(directory).mkdir(parents=True, exist_ok=True)

    for page in document.json()['pageList']['pages']:

        file = f"{directory}/{page['imgFileName']}"

        if page['tsList']['transcripts'][0]['status'] == 'GT' and not Path(file).is_file():

            image = requests.get(page['url'], allow_redirects=True)

            open(file, 'wb').write(image.content)

        if page['tsList']['transcripts'][0]['status'] == 'GT':

            transcript = requests.get(page['tsList']['transcripts'][0]['url'], allow_redirects=True)

            open(Path(file).with_suffix('.xml'), 'wb').write(transcript.content)

# Example call
write_gt(document)
