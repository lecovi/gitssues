import hmac
import json
import os

from flask import Flask, abort, current_app, jsonify, request

SECRET = os.getenv("GITHUB_SECRET")


app = Flask(__name__)


def abort_if_signature_is_invalid(signature, secret, digestmod="sha1"):
    if signature is None:
        abort(403)

    sha_name, signature = signature.split("=")
    if sha_name != digestmod:
        abort(501)

    # HMAC requires the key to be bytes, but data is string
    mac = hmac.new(secret.encode(), msg=request.data, digestmod=digestmod)

    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        abort(403)

    return True


def parse_issue_data(body):
    """Returns title and content for Jira"""
    number = body["issue"]["number"]
    title = body["issue"]["title"]
    url = body["issue"]["url"]
    user = body["issue"]["user"]["login"]
    labels = [label["name"] for label in body["issue"]["labels"]]
    description = body["issue"]["body"]

    title = f"{labels} #{number} {title} by {user}"
    content = f"""{description}

----
URL: {url}
    """

    return title, content


def register_webhook_ping(body):
    hook_id = body.get("hook_id")
    zen = body.get("zen")

    if not zen and not hook_id:
        return

    current_app.logger.info(f"New webhook #{hook_id} detected: '{zen}'")


@app.route("/")
def index():
    return jsonify({"Status": "It works!"})


@app.route("/github", methods=("POST", "GET"))
def github():
    header_signature = request.headers.get("X-Hub-Signature")
    abort_if_signature_is_invalid(signature=header_signature, secret=SECRET)

    body = request.get_json()
    register_webhook_ping(body)
    action = body.get("action")

    # When action is not present, hook is not about an Issue
    # When action is "opened" it means a New Issue
    # When action is "created" it means a New Comment on the Issue
    # When action is "closed" it means the Issue is Closed
    if action != "opened":
        response = {"message": "Not a new issue"}
    else:
        title, content = parse_issue_data(body)
        response = {"title": title, "content": content}

    current_app.logger.debug(json.dumps(response))

    return jsonify(response)
