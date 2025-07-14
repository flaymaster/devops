from flask import Flask, request, jsonify
import boto3
import os
import time
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# AWS clients
ssm = boto3.client('ssm', region_name=os.environ.get(
    'AWS_REGION', 'us-east-1'))
sqs = boto3.client('sqs', region_name=os.environ.get(
    'AWS_REGION', 'us-east-1'))


def get_expected_token():
    param_name = os.environ.get('TOKEN_PARAM_NAME', '/elb/token')
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    param_value = response['Parameter']['Value']
    # Parse the JSON string and extract the token
    return json.loads(param_value)['token']


@app.route("/", methods=["POST"])
def handle_event():
    try:
        payload = request.get_json()
        if not payload or "data" not in payload or "token" not in payload:
            return jsonify({"error": "Invalid request"}), 400

        token = payload["token"]
        data = payload["data"]

        EXPECTED_TOKEN = get_expected_token()
        logger.info(f"Expected token: {EXPECTED_TOKEN}")
        # Token validation
        if token != EXPECTED_TOKEN:
            return jsonify({"error": f"Invalid token: {token}"}), 403
        logger.info("Token validated successfully")
        # ensure email timestream is present and valid
        ts = data.get("email_timestream")
        try:
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts)))
            logger.info(f"Email timestream is valid: {ts}")
        except Exception:
            return jsonify({"error": "Invalid email_timestream"}), 400

        # Send to SQS
        queue_url = os.environ["SQS_QUEUE_URL"]
        sqs.send_message(QueueUrl=queue_url,
                         MessageBody=json.dumps(payload['data']))
        logger.info(
            f"SQS event sent to {queue_url} with data: {payload['data']}")
        return jsonify({"message": "token and email_timestream validated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200


if __name__ == "__main__":
    handle_event()
    app.run(host='0.0.0.0', port=80)
