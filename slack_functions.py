import requests
import json
with open('parameters.json') as f:
    parameters = json.load(f)

def slackhook(username,text):
    webhook_url = parameters["slackhookURL"]
    slack_data = {
        "text": text,
        "username": username,
        "link_names": 1
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )