import json
from logging import log
from kafka import KafkaProducer
from kafka.errors import KafkaError

# produce json messages
# configure multiple retries
# produce asynchronously with callbacks
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         retries=5,
                         value_serializer=lambda m: json.dumps(m).encode('ascii'))

def on_send_success(record_metadata):
    print("%s:%d:%d" % (record_metadata.topic, 
                                 record_metadata.partition,
                                 record_metadata.offset))

def on_send_error(excp):
    log.error('I am an errback', exc_info=excp)
    # handle exception

for item in range(10):
    producer.send('emqx-to-kafka', {item: 'awesome-' + str(item**2)}).add_callback(on_send_success).add_errback(on_send_error)

# block until all async messages are sent
producer.flush()