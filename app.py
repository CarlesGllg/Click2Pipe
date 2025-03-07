from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Endpoint to listen for the incoming webhook
@app.route('/webhook', methods=['POST'])
def listen_to_webhook():
    data = request.json  # This will contain the incoming JSON payload from ClickUp
    print("Received data:", data)  # Log the received data (for debugging purposes)

    custom_fields = data.get('custom_fields', [])
    
    print("PUNT 0. Custom = ",custom_fields)
    # Get the webhook data and split it into a list
    #elements = data.split(',')
    
    # Initialize a variable to hold the extracted value
    extracted_value = None

    # Iterate through the elements to find one containing "PDOID-"
    for field in custom_fields:
        if field['name'] == 'ROB: PipeDrive OrgID':  # Use the actual custom field name
            custom_field_value = field['value']
            print ("Valor custom: ",custom_field_value)
            break
                   
    if custom_field_value is not None:
        extracted_value = element.replace("PDOID-", "")
        print("Valor del PDOID: ", extracted_value)
    else:
        return jsonify({'error': 'Custom field not found'}), 404
                   
    # Prepare the output object
    #comment = data.get('comment')
    
    # Call Pipedrive API to create the follow-up activity
    
    #create_pipedrive_activity(pipedrive_oid, comment)
    return jsonify({"status": "success"}), 200

# Function to create an activity in Pipedrive
def create_pipedrive_activity(pipedrive_oid, comment):
    pipedrive_api_url = 'https://api.pipedrive.com/v1/activities'
    pipedrive_api_token = 'your_pipedrive_api_token'  # Replace with your Pipedrive API token

    data = {
        'subject': 'Follow-up Activity',
        'note': comment,  # The comment text from ClickUp
        'type': 'follow_up',  # You can choose the activity type
        'due_date': '2025-03-07',  # Optional due date (if you want to set one)
        'org_id': pipedrive_oid  # Link the activity to the correct Pipedrive organization
    }

    headers = {'Authorization': f'Bearer {pipedrive_api_token}'}

    response = requests.post(pipedrive_api_url, data=data, headers=headers)
    if response.status_code == 201:
        print("Follow-up activity created successfully.")
    else:
        print("Error creating activity:", response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
