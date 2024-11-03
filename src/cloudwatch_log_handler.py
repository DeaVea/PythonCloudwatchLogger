from src.base_cloudwatch_log_handler import BaseCloudWatchLogHandler

## This class is a special log handler that will send logs to CloudWatch Logs that you specify in the constructor.
## This implementation will send the logs as they come in. 
## Example usage:
## logger = logging.getLogger()
## logger.setLevel(logging.INFO)    
## logger.addHandler(CloudWatchLogHandler('log-group-name', 'log-stream-name'))
## logger.info('Hello, CloudWatch Logs!')
class CloudWatchLogHandler(BaseCloudWatchLogHandler):
    def __init__(self, log_group_name, log_stream_name, logsClient):
        super().__init__(log_group_name, log_stream_name, logsClient)

    def emit(self, record):
        logEvents = [{
            'timestamp': int(record.created * 1000),
            'message': self.format(record)
        }]
        try:
            self.sendLogEvents(logEvents)
        except Exception as e:
            # Something we can't recover from so just print to console and continue. 
            # We don't want to crash the entire function because of a logging error.
            print(f"Failed to send log events to CloudWatch Logs: {e}")