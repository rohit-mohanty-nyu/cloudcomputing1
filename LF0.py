
import json
import boto3

def lambda_handler(event, context):

    # Get unstructured text through number
    input_text = (event.get("messages")[0].get("unstructured").get("text"))

    # Set the names  
    client = boto3.client('lex-runtime')
    response = client.post_text (
            botName     = "foodapplication",
            botAlias    = "food_test",
            userId      = "userid",
            inputText   = input_text
        )
    return {
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'messages': [ 
            {
                'type': "unstructured", 
                'unstructured': 
                {
                    'text': response.get("message")
                }
            } 
        ]

    }
