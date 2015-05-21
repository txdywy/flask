from celery import Celery
from config import SQS_AWS_ACCESS_KEY_ID, SQS_AWS_SECRET_ACCESS_KEY, SQS_REGION, SQS_QUEUE
BROKER_USER = SQS_AWS_ACCESS_KEY_ID                                                                                                                                                   
BROKER_PASSWORD = SQS_AWS_SECRET_ACCESS_KEY
BROKER_TRANSPORT = 'sqs'
# Other docs suggest you should try this.  It didn't work for me
BROKER_URL = 'sqs://%s:%s@' % (BROKER_USER, BROKER_PASSWORD)
app = Celery('tasks', broker=BROKER_URL)
app.conf.BROKER_TRANSPORT_OPTIONS = { 
    'region': SQS_REGION,
}
app.conf.CELERY_DEFAULT_QUEUE = SQS_QUEUE
app.conf.CELERY_QUEUES = { 
    app.conf.CELERY_DEFAULT_QUEUE: {
        'exchange': app.conf.CELERY_DEFAULT_QUEUE,
        'binding_key': app.conf.CELERY_DEFAULT_QUEUE,
    }
}


@app.task
def add(x, y):
    print '==================',x,y
    return x + y
