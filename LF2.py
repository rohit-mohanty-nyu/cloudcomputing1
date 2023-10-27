
import json
import boto3
import random
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    sns_topic='arn:aws:sns:us-east-1:068392994093:foodnotify'
    sns = boto3.client("sns")
    sqs = boto3.client("sqs")
    dynamodb = boto3.resource("dynamodb")
    queue_url = "https://sqs.us-east-1.amazonaws.com/068392994093/foodqueue"

   
    access_key  = ""
    secret_key  = ""
    host        = "search-cloudcomputingrm-lfzlzytfvvgq6enonduerfnc6u.us-east-1.es.amazonaws.com"
    region      = "us-east-1"
    service     = "es"
    
   
    awsauth = AWS4Auth (
        access_key, 
        secret_key, 
        region, 
        service
    )

    
    openSearch = OpenSearch(
                                hosts = [
                                    {
                                        'host': host, 
                                        'port': 443
                                    }
                                ],
                                http_auth           = awsauth, 
                                use_ssl             = True,
                                verify_certs        = True, 
                                connection_class    = RequestsHttpConnection
                            )

    
    resp = sqs.receive_message(
        QueueUrl                = queue_url,
        MaxNumberOfMessages     = 1,
        MessageAttributeNames   = ['All'],
        VisibilityTimeout       = 0,
        WaitTimeSeconds         = 0
    )

    
#    message         = resp['Messages'][0]
 #   cuisine         = message['MessageAttributes'].get('Cuisine').get('StringValue')
 #   time            = message['MessageAttributes'].get('Time').get('StringValue')
    # date          = message['MessageAttributes'].get('Date').get('StringValue')
  #  number          = message['MessageAttributes'].get('Number').get('StringValue')
  #  modifiedNumber  = "+1{}".format(number)
  #  print(message['MessageAttributes'])

if 'Messages' not in resp:
        # Handle the case when there are no messages in the queue
        return {
            'statusCode': 200,
            'body': 'No messages in the queue'
        }
    
    message = resp['Messages'][0]
    if 'MessageAttributes' in message:
        cuisine = message['MessageAttributes'].get('Cuisine', {}).get('StringValue')
        time = message['MessageAttributes'].get('Time', {}).get('StringValue')
        number = message['MessageAttributes'].get('Number', {}).get('StringValue')
    else:
        # Handle the case when 'MessageAttributes' is missing in the message
        cuisine = 'Unknown Cuisine'
        time = 'Unknown Time'
        number = 'Unknown Number'

    # Hit OpenSearch index clusters
    result = openSearch.search (
        index   = "restaurants", 
        body    = {
            "query": 
                {
                    "match" : {
                        "cuisine" : cuisine
                    }
                }
            }
        )
    
    # Variables for data cleaning
    candidate_list, ids = [], []
    print(result['hits']['hits'])

    # Create every restaurant indexed from OpenSearch
    for entry in result['hits']['hits']:
      candidate_list.append(entry["_source"])

    # Get business ids in a separate ID
    for c in candidate_list:
      ids.append(c.get("Business ID"))
    
    # Get a random business suggestion
    restaurantSuggestion = random.choice(ids)

    # Connect to DynamoDB database
    db_table = dynamodb.Table('yelp-restaurants-db')
    
    # Search through the database based on the key and get the item on the key
    info = db_table.get_item(
        Key = {
            'Business ID': restaurantSuggestion,
        }
    )
    

    # Get the final values to be printed on the text message
    Rating          = info["Item"]["rating"]
    Name            = info["Item"]["name"]
    RatingCount     = info["Item"]["review_count"]
    Address         = info["Item"]["address"]
    Address         = ''.join(list(Address))
    finalMessage    = """
    Hey...
I recommend going to: {} at {}.
It has {} reviews with an average rating of {}.
The address is: {}.
Hope you have a great time!
    """.format(Name, time, RatingCount, Rating, Address)

    # Call the SNS publish function to send the message
    print(finalMessage)
    messageSent = sns.publish(
        
        PhoneNumber= modifiedNumber,
        Message= finalMessage,
    )

    sns = boto3.client("sns")
    sns.publish(
        TopicArn=sns_topic,
        Message=finalMessage
    )
    
    # Delete the message from the queue
    receipt_handle = message['ReceiptHandle']
    sqs.delete_message(
        QueueUrl = queue_url,
        ReceiptHandle = receipt_handle
    )
    

    return {
        'statusCode': 200,
        'body': finalMessage
    }
