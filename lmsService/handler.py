import json
import boto3
import os

def s3assignment(event, context):

    print("In s3assignment, got event " + json.dumps(event))
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']

    print('Bucket', bucket_name, 'File', file_name)

    sns_client = boto3.client('sns')

    topic_arn = os.environ['sns_topic_arn'] 

    message = "Type:Assignment::Course:PyBasic::File:" + file_name
    pub_response = sns_client.publish(
                                  TopicArn= topic_arn,
                                  Message= message,
                                  Subject="Alert"
                                  )

    print(pub_response)
    response = {}
    return response

def notifier(event, context):

    print("In notifier, event:" + json.dumps(event))
    
    # This piece of code gets details like course id and new assignment,
    # and sends a notification email to the course Teacher about new assignment

    response= {}
    return response

def updatedb(event, context):

    print("In updatedb, event:" + json.dumps(event))

    # This piece of code gets details like course id and new assignment,
    # and updates the ToDo of the Teacher in the DynamoDB
    message = event['Records'][0]['Sns']['Message']
    print("In updatedb, printing message", message)

    sub_msg = message.split('::')
    msg_type = sub_msg[0].split(':')[1]
    course = sub_msg[1].split(':')[1]
    file_name = sub_msg[2].split(':')[1]

    # Now get the Teacher for the course from the dynamodb
    db_client = boto3.client('dynamodb')

    c_item = db_client.get_item(
                TableName='Courses',
                Key={
                    'CourseId': {'S': course}
                    }
            )
    print("DB item received", json.dumps(c_item))
    print(type(c_item['Item']['TeacherId']["N"]))

    # Update the ToDo attribute for the course Teacher
    updated_item = db_client.update_item(
                TableName='Teacher',
                Key={
                    'Id': {'N': c_item['Item']['TeacherId']["N"]}
                    },
                AttributeUpdates={
                    'ToDo': {
                        'Value': {
                            'SS': [ file_name]
                            }
                        }
                    },
                ReturnValues='UPDATED_NEW'
            )
    response= {}
    return response
