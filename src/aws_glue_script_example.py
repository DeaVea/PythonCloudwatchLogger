import structlog
import sys
from awsglue.utils import getResolvedOptions
import logging
import os
import boto3

from src.cloudwatch_log_handler import CloudWatchLogHandler

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'JOB_RUN_ID'])
job_run_id = args['JOB_RUN_ID']

logsClient = boto3.client('logs')

level = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOG_LEVEL = getattr(logging, level) 

customhandler = CloudWatchLogHandler('/aws-glue/jobs/output', job_run_id, logsClient)

pythonLogger = logging.getLogger()
pythonLogger.setLevel(logging.INFO)
# Remove all handlers
for handler in pythonLogger.handlers[:]:
    pythonLogger.removeHandler(handler)
# Add custom handler
pythonLogger.addHandler(customhandler)

def config_logger():
    structlog.configure_once(
            wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),
            processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.TimeStamper(fmt='iso'),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer()
            ],
    )
    structlog.contextvars.bind_contextvars(workflow_run_id='unknown', component_name='unknown')
    return structlog.get_logger()

logger = config_logger()

def handle(event, context) -> None:
    logger.info("Creating new Lambda Handler")
    # print some JSON logs to the console in quick succession
    dictToPrint = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
        "key4": "value4",
        "key5": "value5"
    }

    for i in range(100):
        logger.info("Processing record", record_number=i)
        logger.info("Processing record", record_number=i, extra=dictToPrint)