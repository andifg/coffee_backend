from confluent_kafka import Consumer

c = Consumer({
    'bootstrap.servers': 'localhost:9094',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})

c.subscribe(['coffee-images'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue


    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))
    
    c.commit(asynchronous=False)

c.close()