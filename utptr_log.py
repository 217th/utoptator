import logging
import datetime

# formatter = logging.Formatter(datetime.datetime.now().strftime("%H:%M:%S.%f") + ' :: %(name)s :: %(levelname)s :: %(message)s')

logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
file = logging.FileHandler('logs\log.' + datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + '.csv')
file.setLevel(logging.DEBUG)
formatter = logging.Formatter(datetime.datetime.now().strftime("%H:%M:%S.%f") + ' ; %(levelname)s ; %(message)s')
file.setFormatter(formatter)
logger.addHandler(file)

logger.info('taskId ; '
            'candId ; '
            'relId ; '
            'devId ; '
            'operationName ; '
            'value')

def general(text):
    logger.info('; ; ; ;' + text + ';')

def dev(devId, operation, value):
    logger.info(('; ; ; %s ; %s ; %s') % (devId, operation, value))

def task(taskId, operation, value):
    logger.info(('%s ; ; ; ; %s ; %s') % (taskId, operation, value))

def taskAndDev(taskId, devId, operation, value):
    logger.info(('%s ; ; ; %s ; %s ; %s') % (taskId, devId, operation, value))


'''
logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')
'''