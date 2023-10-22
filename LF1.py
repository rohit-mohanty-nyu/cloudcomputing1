
import json
import boto3
import random
import re


def sqsEntry(city_name, cuisine, people, time, number):
    
    regionName  = "us-east-1"
    access_key  = ""
    api_key     = ""
    queue_url   = "https://sqs.us-east-1.amazonaws.com/068392994093/foodqueue"

    sqs = boto3.client (
                            service_name            = "sqs",
                            aws_access_key_id       = access_key,
                            aws_secret_access_key   = api_key,
                            region_name             = regionName,
                        )
    print("Message being sent to the SQS Queue...")
    response = sqs.send_message(
        QueueUrl = queue_url,
        DelaySeconds = 10,
        MessageAttributes = {
            'Location': {
                'DataType': 'String',
                'StringValue': city_name
            },
            'Cuisine': {
                'DataType': 'String',
                'StringValue': cuisine
            },
            'People': {
                'DataType': 'Number',
                'StringValue': "{}".format(people)
            },
            'Time': {
                'DataType': 'String',
                'StringValue': time
            },
            'Number': {
                'DataType': 'Number',
                'StringValue': "{}".format(number)
            }
        },
        MessageBody=(
            'User values in the attributes field'
        )
    )
    print(response)
    front_response = "We will send you our best recommendation shortly through a text, till then sit tight!"
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": front_response
            }
        }
    }

def lambda_handler(event, context):
    
    cuisine_list = ['indian', 'thai', 'mediterranean', 'chinese', 'italian']
    cities = ['manhattan', 'brooklyn', 'queens', 'staten island', 'bronx']
    
    intent_name = event.get("currentIntent").get("name")

    if intent_name == "greetingIntent":
        res = "Hey, what can I help you with?"
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": res
                }
            }
        }

    if intent_name == "thankyouintent":

        res = "Hope I was able to assist you!"
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": res
                }
            }
        }

    if intent_name == "diningIntent":

        cityName        = event.get("currentIntent").get("slots").get("Location")
        time            = event.get("currentIntent").get("slots").get("Time")
        cuisine         = event.get("currentIntent").get("slots").get("Cuisine")
        phone_number    = event.get("currentIntent").get("slots").get("Number")
        people          = event.get("currentIntent").get("slots").get("People")

        if cityName is None:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                      "contentType": "PlainText",
                      "content": "Which city do you want the reservation to be in?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "Location"
                }
            }
        
        elif cityName is not None and cityName.lower() not in cities:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                    "contentType": "PlainText",
                    "content": "Please enter from the following options: Manhattan, Brooklyn, Bronx, Queens and Staten Island?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "Location"
                }
            }

        elif people is None:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                      "contentType": "PlainText",
                      "content": "How many people should I book it for?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "People"
                }
            }

        elif people is not None and int(people) > 25:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                      "contentType": "PlainText",
                      "content": "Please enter any amount less than 25"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "People"
                }
            }

        elif time is None:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                      "contentType": "PlainText",
                      "content": "What time would you like your reservation to be at?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "Time"
                }
            }

        elif cuisine is None:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                      "contentType": "PlainText",
                      "content": "What Cuisine are you in the mood for (Indian, Thai, Mediterranean, Chinese or Italian)?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "Cuisine"
                }
            }
        
        
        elif cuisine is not None and cuisine.lower() not in cuisine_list:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                    "contentType": "PlainText",
                    "content": "Please enter from the following options: Indian, Thai, Mediterranean, Chinese, Italian?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "Cuisine"
                }
            }

        elif phone_number is None:
            return {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "message": {
                      "contentType": "PlainText",
                      "content": "What is your mobile number?"
                    },
                "intentName": "diningIntent",
                "slots": {
                    "Location": cityName,
                    "Cuisine": cuisine,
                    "People": people,
                    "Time":time,
                    "Number":phone_number
                },
                "slotToElicit" : "Number"
                }
            }
            
        elif phone_number is not None:
            PHONE_REGEX = re.compile(r'[0-9]{10}')
            if not PHONE_REGEX.match(phone_number):
                return {
                    "dialogAction" : {
                        "type" : "ElicitSlot",
                        "message": {
                            "contentType" : "PlainText",
                            "content": "You have entered an incorrect phone number. Please enter a 10 digit US phone number: "
                        },
                    "intentName" : "diningIntent",
                    "slots" : {
                        "Location": cityName,
                        "Cuisine": cuisine,
                        "People": people,
                        "Time":time,
                        "Number":phone_number
                    },
                    "slotToElicit" : "Number"
                    } 
                }
            else:
                return sqsEntry(cityName, cuisine, people, time, phone_number)
            
        else:
            return sqsEntry(cityName, cuisine, people, time, phone_number)
