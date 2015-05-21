from celery import Celery
from config import SQS_AWS_ACCESS_KEY_ID, SQS_AWS_SECRET_ACCESS_KEY, SQS_REGION, SQS_QUEUE
BROKER_URL = 'sqs://%s:%s@' % (SQS_AWS_ACCESS_KEY_ID, SQS_AWS_SECRET_ACCESS_KEY)
app = Celery('tasks', broker=BROKER_URL)

@app.task
def add(x, y):
    print '==================',x,y
    return x + y
