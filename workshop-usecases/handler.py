import json
import boto3
import os
import smtplib

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

    # Get details from SNS message
    message = event['Records'][0]['Sns']['Message']
    print("In updatedb, printing message", message)

    sub_msg = message.split('::')
    course = sub_msg[1].split(':')[1]
    file_name = sub_msg[2].split(':')[1]

    # Now get the Teacher of the course from the dynamodb
    db_client = boto3.client('dynamodb')

    c_item = db_client.get_item(
                TableName='Course',
                Key={
                    'CourseId': {'S': course}
                    }
            )

    # Get Teacher's email Id
    t_item = db_client.get_item(
                TableName='Teacher',
                Key={
                    'Id': {'N': c_item['Item']['TeacherId']["N"]}
                    }
            )
    print(t_item['Item']['email']['S'])
    gmail_user = 'demoghci@gmail.com'
    gmail_password = 'NewP@ssword!'

    sent_from = gmail_user
    to = t_item['Item']['email']['S']
    subject = 'Course Message'
    body = 'You have a new assignment: ' + file_name + ' to grade!'

    email_text = """From: %s  
To: %s  
Subject: %s

%s
""" % (sent_from, to, subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent to', to)
    except:
        print('Something went wrong while sending email to', to)

    response= {}
    return response

def updatedb(event, context):


    # This piece of code gets details like course id and new assignment,
    # and updates the ToDo of the Teacher in the DynamoDB
    message = event['Records'][0]['Sns']['Message']

    sub_msg = message.split('::')
    msg_type = sub_msg[0].split(':')[1]
    course = sub_msg[1].split(':')[1]
    file_name = sub_msg[2].split(':')[1]

    # Now get the Teacher for the course from the dynamodb
    db_client = boto3.client('dynamodb')

    c_item = db_client.get_item(
                TableName='Course',
                Key={
                    'CourseId': {'S': course}
                    }
            )

    # Update the ToDo attribute for the course Teacher
    updated_item = db_client.update_item(
                TableName='Teacher',
                Key={
                    'Id': {'N': c_item['Item']['TeacherId']['N']}
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
