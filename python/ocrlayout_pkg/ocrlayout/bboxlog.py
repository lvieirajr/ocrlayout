import logging

def get_logger():
    bboxlogger = logging.getLogger('bboxhelper')
    bboxlogger.setLevel(logging.INFO)
    return bboxlogger
