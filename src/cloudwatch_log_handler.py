
import logging
import os
import json
import boto3
from botocore.exceptions import ClientError

## This class is a special log handler that will send logs to CloudWatch Logs that you specify in the constructor.
## It will also send logs to the console, so you can see them in the AWS Lambda console.
## Example usage:
## logger = logging.getLogger()
## logger.setLevel(logging.INFO)    
## logger.addHandler(CloudWatchLogHandler('log-group-name', 'log-stream-name'))
## logger.info('Hello, CloudWatch Logs!')
class CloudWatchLogHandler(logging.StreamHandler):
    def __init__(self, log_group_name, log_stream_name, logsClient):
        super().__init__()
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.sequence_token = None
        self.client = logsClient

    ## This will attempt to create a log group and return it.
    ## If the log group already exists then it will simply return it.
    def getOrCreateLogGroup(self):
        # first attempt to creat the log group. It'll throw an exception if it already exists.
        try:
            self.client.create_log_group(logGroupName=self.log_group_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                # The log group already exists so simply return it now.
                pass
            else:
                # Else some other error occurred so re-raise the exception.
                raise e
        return self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)['logGroups'][0]
    
    def getOrCreateLogStream(self):
        # first attempt to creat the log stream. It'll throw an exception if it already exists.
        try:
            self.client.create_log_stream(logGroupName=self.log_group_name, logStreamName=self.log_stream_name)
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                # The log stream already exists so simply return it now.
                pass
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # The log group doesn't exist so create it now then try to create the log stream again.
                self.getOrCreateLogGroup()
                # Now try to create the log stream again.
                return self.getOrCreateLogStream()
            else:
                # Else some other error occurred so re-raise the exception.
                raise e
        return self.client.describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.log_stream_name)['logStreams'][0]

    def emit(self, record):
        try:
            print("Emitted log to CloudWatch Logs")
            print(self.format(record))
            response = self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(record.created * 1000),
                        'message': self.format(record)
                    }
                ],
                sequenceToken="These are ignored nowe"
            )
            print(response)
        except ClientError as e:
            # Check if the log stream exists and then create it if not. Then try to send the log again.
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self.getOrCreateLogStream()
                self.emit(record)
            else:
                # Else some other error occurred so re-raise the exception. There's nothign we can do.
                print(e)
        except Exception as e:
            # Something categorically went wrong so print the exception.
            print(e)