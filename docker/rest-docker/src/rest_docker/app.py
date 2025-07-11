from flask import Flask, request, jsonify
import boto3
import os
import time

app = Flask(__name__)

# AWS clients
ssm = boto3.client('ssm', region_name=os.environ.get(
    'AWS_REGION', 'us-east-1'))
sqs = boto3.client('sqs', region_name=os.environ.get(
    'AWS_REGION', 'us-east-1'))


def get_expected_token():
    param_name = os.environ.get('TOKEN_PARAM_NAME', '/myapp/token')
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response['Parameter']['Value']


EXPECTED_TOKEN = get_expected_token()


@app.route("/", methods=["POST"])
def handle_event():
    try:
        payload = request.get_json()
        if not payload or "data" not in payload or "token" not in payload:
            return jsonify({"error": "Invalid request"}), 400

        token = payload["token"]
        data = payload["data"]

        # Token validation
        if token != EXPECTED_TOKEN:
            return jsonify({"error": "Invalid token"}), 403

        # ensure email timestream is present and valid
        ts = data.get("email_timestream")
        try:
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts)))
        except:
            return jsonify({"error": "Invalid email_timestream"}), 400

        # Send to SQS
        queue_url = os.environ["SQS_QUEUE_URL"]
        sqs.send_message(QueueUrl=queue_url, MessageBody=request.data.decode())

        return jsonify({"message": "Accepted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
