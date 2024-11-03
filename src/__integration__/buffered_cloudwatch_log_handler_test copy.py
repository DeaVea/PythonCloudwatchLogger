import unittest
import boto3
import time
import logging
from botocore.exceptions import ClientError

from src.buffered_cloudwatch_log_handler import BufferedCloudWatchLogHandler

from botocore.config import Config

my_config = Config(
    region_name = 'us-east-1',
)

class TestStringMethods(unittest.TestCase):

    logs = boto3.client('logs', config=my_config)

    @classmethod
    def setUpClass(cls):
        ## Create the log group and log stream for the tests.
        try: 
            cls.logs.create_log_group(logGroupName='test-log-group-name')
        except ClientError as e:
            ## If the log group already exists then just keep going
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                pass
            else:
                raise e
        
        try:
            cls.logs.create_log_stream(logGroupName='test-log-group-name', logStreamName='test-log-stream-name')
        except ClientError as e:
            ## If the log stream already exists then just keep going
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                pass
            else:
                raise e

    @classmethod
    def tearDownClass(cls):
        try:
            cls.logs.delete_log_group(logGroupName='test-log-group-name')
        except:
            pass

        try:
            cls.logs.delete_log_group(logGroupName='test-log-group-name-2')
        except:
            pass

        try:
            cls.logs.delete_log_group(logGroupName='test-log-group-name-3')
        except:
            pass

        try:
            cls.logs.delete_log_group(logGroupName='test-log-group-name-4')
        except:
            pass

    def test_writes_record_to_stream_that_exists(self):
        handler = BufferedCloudWatchLogHandler('test-log-group-name', 'test-log-stream-name', self.logs)
        record = logging.LogRecord('name', 20, 'pathname', 1, "Test record", None, None)
        handler.emit(record)
        handler.flush()
        # It is async so we need to wait a bit before checking the logs

        ## Loop until the log event is found or until we have looped 10 times.
        ## This is because the logs are not always immediately available.
        for i in range(10):
            log_events = self.logs.get_log_events(logGroupName='test-log-group-name', logStreamName='test-log-stream-name')
            if len(log_events['events']) > 0:
                break
            time.sleep(0.25)
        self.assertEqual(log_events['events'][0]['message'], "Test record")

    def test_writes_record_to_stream_that_does_not_exist_but_group_exists(self):
        handler = BufferedCloudWatchLogHandler('test-log-group-name', 'test-log-stream-name-3', self.logs)
        record = logging.LogRecord('name', 20, 'pathname', 1, "Test record", None, None)
        handler.emit(record)
        handler.flush()
        # It is async so we need to wait a bit before checking the logs

        ## Loop until the log event is found or until we have looped 10 times.
        ## This is because the logs are not always immediately available.
        for i in range(10):
            log_events = self.logs.get_log_events(logGroupName='test-log-group-name', logStreamName='test-log-stream-name-3')
            if len(log_events['events']) > 0:
                break
            time.sleep(0.25)
        self.assertEqual(log_events['events'][0]['message'], "Test record")

    def test_writes_record_to_stream_and_group_that_does_not_exist(self):
        handler = BufferedCloudWatchLogHandler('test-log-group-name-4', 'test-log-stream-name', self.logs)
        record = logging.LogRecord('name', 20, 'pathname', 1, "Test record", None, None)
        handler.emit(record)
        handler.flush()
        # It is async so we need to wait a bit before checking the logs

        ## Loop until the log event is found or until we have looped 10 times.
        ## This is because the logs are not always immediately available.
        for i in range(10):
            log_events = self.logs.get_log_events(logGroupName='test-log-group-name-4', logStreamName='test-log-stream-name')
            if len(log_events['events']) > 0:
                break
            time.sleep(0.25)
        self.assertEqual(log_events['events'][0]['message'], "Test record")

if __name__ == '__main__':
    unittest.main()