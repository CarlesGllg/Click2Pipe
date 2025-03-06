from flask import Flask, request

app = Flask(__name__)

# Define a route that listens for POST requests
@app.route('/webhook', methods=['POST'])
def webhook():
    # When the webhook is received, print a message
    data = request.json  # If the webhook sends JSON data
    print("Webhook received with data:", data)
    
    # Respond to the webhook sender
    return 'Webhook received successfully!', 200

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)
