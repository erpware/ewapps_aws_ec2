import json
import os

import boto3
from botocore import exceptions

ec2client = boto3.resource('ec2')

# Responses
# 200:  Request was executed successful
# 400:  No action or invalid action requested
# 401:  Secure String not send
# 403:  Secure String does not match
# 412:  Secure String is not set in environment variables
# 417:  Missing EC2 Instances IDs to fulfill the action
# 500:  Errors during execution of specific actions
# 502:  Bad request -> mostly an configuration issue of API Gateway


def lambda_handler(event, context):
    # do all necessary pre checks
    # 1. is the environment variable set?
    try:
        securestring = os.environ['SECURESTRING']
    except KeyError:
        return {
            'statusCode': 412,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Environment variable SECURESTRING not set.'
            })
        }
    # 2. is the securestring send by your request
    if 'body' in event:
        body = json.loads(event['body'])
        if 'securestring' not in body:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'message': 'Necessary secure token not provided by your request.'
                })
            }
        # 3. does the securestring match the environment variable
        if not (body['securestring'] == securestring):
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'message': 'You are not allowed to execute this function.'
                })
            }
        # now, everything is fine, let's do our action
        if 'action' in body:
            action = body['action']
            if action == 'status':
                return get_all_instances()
            if action == 'stop':
                if 'ec2id' not in body:
                    return {
                        'statusCode': 417,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps({
                            'message': 'Necessary EC2 Instance ID not provided by your request.'
                        })
                    }
                return stop_instance(body['ec2id'])
            if action == 'start':
                if 'ec2id' not in body:
                    return {
                        'statusCode': 417,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps({
                            'message': 'Necessary EC2 Instance ID not provided by your request.'
                        })
                    }
                return start_instance(body['ec2id'])

    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'No action or an invalid action send. Nothing to do.'
        })
    }


def get_all_instances():
    instances = []
    for ec2instance in ec2client.instances.all():
        inst_names = [tag['Value'] for tag in ec2instance.tags if tag['Key'] == 'Name']
        # we can't start/stop terminated instances, so we won't send them back to the client
        if not ec2instance.state['Name'] == 'terminated':
            instance = {
                'ec2id': ec2instance.id,
                'ipaddress': ec2instance.public_ip_address,
                'state': ec2instance.state['Name'],
                'name': inst_names[0]
            }
            instances.append(instance)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'instances': instances
        })
    }


def stop_instance(ec2id):
    try:
        ec2client.instances.stop(
            InstanceIds=[
                ec2id
            ])
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Instance {0} successfully stopped'.format(ec2id)
            })
        }
    except exceptions.ClientError as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': repr(e)
            })
        }


def start_instance(ec2id):
    try:
        ec2client.instances.start(
            InstanceIds=[
                ec2id
            ])
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Instance {0} successfully started'.format(ec2id)
            })
        }
    except exceptions.ClientError as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': repr(e)
            })
        }
