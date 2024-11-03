from src.base_cloudwatch_log_handler import BaseCloudWatchLogHandler

## This class is a special log handler that will send logs to CloudWatch Logs that you specify in the constructor.
## This implementation batches the records and sends them in a single request to CloudWatch Logs periodically.
## It may be a good idea to use this handler if you have a high volume of logs.
## This implementation is unique in that the user will need to flush at the end of the script to ensure all logs are sent.
## Example usage:
## logger = logging.getLogger()
## logger.setLevel(logging.INFO)    
## bufferedHandler = BufferedCloudWatchLogHandler('log-group-name', 'log-stream-name')
## logger.addHandler(bufferedHandler)
## logger.info('Hello, CloudWatch Logs!')
## bufferedHandler.flush()
class BufferedCloudWatchLogHandler(BaseCloudWatchLogHandler):
    def __init__(self, log_group_name, log_stream_name, logsClient):
        super().__init__(log_group_name, log_stream_name, logsClient)
        self.logEvents = []

    ## This will flush the log events to CloudWatch Logs and empty the buffer.
    def flush(self):
        if len(self.logEvents) > 0:
            self.sendLogEvents(self.logEvents)
            self.logEvents = []

    def emit(self, record):
        # https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html
        # The maximum batch size 10,000 log events.
        # The maximum size of the log event is 256 KB.
        # The maximum size of the batch is 1,048,576 bytes.
        # There's a lot of room for optimization but to keep things simple for now we'll just send the logs every 10 records.
        self.logEvents.append({
            'timestamp': int(record.created * 1000),
            'message': self.format(record)
        })
        if len(self.logEvents) >= 10:
            self.flush()