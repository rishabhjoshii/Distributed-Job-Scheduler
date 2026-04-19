"""Log job handler."""
import logging

logger = logging.getLogger("LogHandler")


def execute(job):
    logger.info("Executing job %s with payload %s", job.id, job.payload)
    raise Exception("Forced failure")

