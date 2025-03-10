from flask import Flask, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)

# Endpoint to listen for the incoming webhook
@app.route('/webhook', methods=['POST'])
def listen_to_webhook():
    data = request.json  # This will contain the incoming JSON payload from ClickUp
    #print("Received data:", data)  # Log the received data (for debugging purposes)

    payload = data.get('payload',[])
    task_id = payload.get('id')
    print("ID: ", task_id)
    #print("PAYLOAD: ",payload)

    # Define the URL for getting task comments
    url = f'https://api.clickup.com/api/v2/task/{task_id}/comment'

    # Set the headers for the API request, including the Authorization token
    HEADERS = {
        'Authorization': 'pk_82705525_4FUTKYOJDRLEJSF270VOWZW3RQZ80F0T'
    }
    
    # Send GET request to the ClickUp API
    response = requests.get(url, headers=HEADERS)
    
    # Check the response status code
    if response.status_code == 200:
        # If the request was successful, parse the JSON response
        comments = response.json()
        
        # Extract and print comments
        if comments.get('comments'):
            for comment in comments['comments']:
                #print(f"COMENTARI: {comment}")
                print(f"User: {comment['user']['username']}")
                com_user = comment['user']['username']
                print(f"Comment: {comment['comment_text']}")
                com_text = comment['comment_text']
                timestamp = comment['date']
                timestamp_in_seconds = int(timestamp) / 1000
                date_time = datetime.utcfromtimestamp(timestamp_in_seconds)
                formatted_date = date_time.strftime('%d/%m/%Y')
                print(f"DATA: {formatted_date}")
                com_data = {formatted_date}
                print('-' * 100)
                break
        else:
            print("No comments found for this task.")
    else:
        # If the request failed, print the error
        print(f"Error fetching comments: {response.status_code} - {response.text}")


    
    custom_fields = payload.get('custom_fields', [])
    #print("CUSTOM: ", custom_fields)
    
    #print("PUNT 0. Custom = ",custom_fields)
    # Get the webhook data and split it into a list
    #elements = data.split(',')
    
    # Initialize a variable to hold the extracted value
    extracted_value = None

    # Iterate through the elements to find one containing "PDOID-"
    for field in custom_fields:
        if field['name'] == 'ROB: PipeDrive OrgID':  # Use the actual custom field name
            custom_field_value = field['value']
            print ("Valor custom: ",custom_field_value)
            if custom_field_value is not None:
                extracted_value = custom_field_value.replace("PDOID-", "")
                print("Valor del PDOID: ", extracted_value)
            else:
                return jsonify({'error': 'Custom field not found'}), 404            
            break
                   

                   
    # Prepare the output object
    #comment = data.get('comment')
    
    # Call Pipedrive API to get OrgID
    pdoid = get_PD_organization_info ('61283559c8d298f5a3fc1eece05d7c2b1e5617c3', extracted_value)
    
    if (pdoid is not None):
        print(f"PD-OID: {pdoid}")
        activity = create_PD_follow_up_activity('61283559c8d298f5a3fc1eece05d7c2b1e5617c3', pdoid, com_user, com_text, com_data)
        if activity:
            print("Follow-up Activity Created:", activity)
    
    return jsonify({"status": "success"}), 200


def get_PD_organization_info(api_key, org_id):
    # Endpoint to get the organization info
    url = f'https://api.pipedrive.com/v1/organizations/{org_id}?api_token={api_key}'
    
    # Make a GET request to the Pipedrive API
    response = requests.get(url)
    
    if response.status_code == 200:
        # Return the organization data if successful
        return response.json()['data']
    else:
        # Handle error response
        print(f"Error: {response.status_code}")
        return None

# Function to create a follow-up activity
def create_PD_follow_up_activity(api_key, org_id, user, activity_text, activity_date):
    # Endpoint to create a follow-up activity
    url = 'https://api.pipedrive.com/v1/activities?api_token={}'.format(api_key)
    
    # Payload for the new activity (a follow-up in this case)
    activity_data = {
        'subject': 'CS: Comentari a ClickUp',  # Always set this subject 
        'due_date': activity_date,  # Due date from the passed parameter
        'type': 'follow_up',  # Type of activity
        'organization_id': org_id,  # Organization ID
        'user_id': 5371109,
        'note': activity_text  # The body of the activity (text)
    }
    
    # Make a POST request to create the activity
    response = requests.post(url, data=activity_data)
    
    if response.status_code == 201:
        # Return the response data if activity is created successfully
        return response.json()['data']
    else:
        # Handle error response
        print(f"Error: {response.status_code}")
        return None


if __name__ == '__main__':
    app.run(debug=True, port=5000)
