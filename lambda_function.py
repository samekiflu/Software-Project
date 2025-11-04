import json
from model_evaluator import ModelEvaluator

def lambda_handler(event=None, context=None):
    evaluator = ModelEvaluator()
    evaluator.setup_logging()

    try:
        #  1. Parse URLs dynamically from event["body"]
        if event and "body" in event:
            body = event["body"]
            # Handle both stringified JSON and direct dict
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = {}

        urls = body.get("urls") if isinstance(body, dict) else None

        # 🛠️ 2. Validate input
        if not urls or not isinstance(urls, list):
            return {
                "statusCode": 400,
                "body": {"error": "Missing or invalid 'urls' in request body. Expected: {'urls': ['url1', 'url2']}."}
            }

        # 3. Run evaluation
        results = evaluator.evaluate_urls(urls)

        #  4. Return pretty JSON
        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        #  Handle unexpected errors gracefully
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }

#  Local testing (run from terminal)
if __name__ == "__main__":
    # Example event for local test
    test_event = {
        "body": json.dumps({
            "urls": ["https://huggingface.co/google-bert/bert-base-uncased"]
        })
    }

    response = lambda_handler(test_event)
    print(json.dumps(response, indent=2))

