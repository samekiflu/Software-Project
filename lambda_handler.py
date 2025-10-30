import json
from model_evaluator import ModelEvaluator  # Import the class, not a function

def lambda_handler(event, context):
    try:
        # Parse input
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event  # direct invocation for local testing

        # Get URLs from request body
        urls = body.get("urls", [])

        # Initialize the evaluator
        evaluator = ModelEvaluator()
        evaluator.setup_logging()

        # Run evaluation on the URLs
        results = evaluator.evaluate_urls(urls)

        # Return results
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


# local test block
if __name__ == "__main__":
    test_event = {
        "urls": [
            "https://huggingface.co/google-bert/bert-base-uncased",
            "https://huggingface.co/datasets/squad",
            "https://github.com/google-research/bert"
        ]
    }

    print(lambda_handler(test_event, None))
