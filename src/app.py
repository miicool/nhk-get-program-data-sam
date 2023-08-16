import sys
from code import cli
import os

# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)


def handler(event, context):
    #    logger.info('## ENVIRONMENT VARIABLES')
    #    logger.info(os.environ)
    #    logger.info('## EVENT')
    #    logger.info(event)
    print("=====START=====")
    cli.main()
    print("=====END=====")
    return "Executed from AWS Lambda using Python" + sys.version + "!"
