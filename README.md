# ewapps_aws_ec2

This repository contains the backend for the ewapps_aws_ec2, which provides an AWS API Gateway to list, start and stop EC2 instances.

We will provide some clients

* Windows https://www.erpware.de/tools/ewapps_aws_ec2/
* Android https://play.google.com/store/apps/details?id=com.embarcadero.ewapps_aws_ec2

## setup - with terraform

Download or clone this repository and adjust the variable for the security token.
Run **terraform init** to download all necessary providers. After completion, run **terraform apply**. If you encouter any error of missing resources, run it a second time.

This will create an AWS API Gateway and integrates the Lambda function to it.

The output parameter will give you the generated URL of the API Gateway.

## setup - manually

We prefer using terraform, but ok, some of you want to create it manually or will integrate it in existing services:

* Create AWS Lambda function and upload the code from lambda_function.py
* Adjust the policy of the IAM User to be able to Describe, Start and Stop EC2 Instances
* Integrate the AWS Lambda to an API Gateway. 

## How it works

We provide three actions, which you have to send as POST request to the API Gateway. Each request need the securitystring, you added as environment variable to the AWS Lambda.

### status
With this request, you will receive a list of all EC2 instances (except terminated).

### start
The start request just starts an instance based on the instanceID, you provide during the request. There is no "WaitFor", so the Lambda will respond even the intance is not up and running.

### stop
To stop an EC2 instance, just provide the action "stop" with the instanceID for the EC2 instance, you want to stop. The Lambda will respond after sending this request and won't wait until the EC2 instance is stopped.

# erpware

ewapps_aws_ec2 is one of the tools, we are using within our company "erpware" (https://www.erpware.de (german) / https://www.erpware.co (english)). Apps for Android (possible later for iOS). Most of our tools are freeware or waiting for a small donation.
