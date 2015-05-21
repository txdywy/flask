import boto.sqs
from boto.sqs.message import Message
from config import SQS_AWS_ACCESS_KEY_ID, SQS_AWS_SECRET_ACCESS_KEY, SQS_REGION, SQS_QUEUE
conn = boto.sqs.connect_to_region(SQS_REGION,
                                  aws_access_key_id=SQS_AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=SQS_AWS_SECRET_ACCESS_KEY)
POLO_Q = conn.create_queue('polo_sqs')
print '------- SQS [%s] visability timeout: [%s] --------------------' % (POLO_Q.name, POLO_Q.get_timeout())

def send(message='Nothing', q=POLO_Q):
    m = Message()
    m.set_body('This is my first message.')
    print '========= sent message [%s] to SQS [%s] =========' % (message, q.name) 
    q.write(m)

def recv(q=POLO_Q):
    rs = q.get_messages()
    if rs:
        m = rs[0]
        print '============ get message [%s] from SQS [%s] ==========' % (m.get_body(), q.name)
        q.delete_message(m)
    else:
        print '============ got no message ============'

def count(q=POLO_Q):
    print '============ [%s] messages in SQS [%s] ==========' % (q.count(), q.name)

def purge(q=POLO_Q):
    q.purge()
    print '============ rm all messages in SQS [%s] ==========' % q.name

