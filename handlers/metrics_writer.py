import os, json, time, boto3

TABLE_NAME = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb").Table(TABLE_NAME)

def handler(event, context):
    if isinstance(event, dict) and "body" in event and isinstance(event["body"], str):
        try:
            body = json.loads(event["body"])
        except Exception:
            body = {}
    elif isinstance(event, dict):
        body = event
    else:
        body = {}

    repo = body.get("repo")
    if not repo:
        return {"statusCode": 400, "body": json.dumps({"ok": False, "error": "Missing 'repo'"})}

    user_id = body.get("userId", "unknown")
    metrics = body.get("metrics", {"status": "ok"})
    ts = int(time.time())
    ts_str = str(ts)  
    ddb.put_item(Item={"repo": repo, "ts": ts_str, "userId": user_id, "metrics": metrics})

    return {"statusCode": 200, "body": json.dumps({"ok": True, "saved": {"repo": repo, "ts": ts}})}
