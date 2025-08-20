import json
import time
import random
from faker import Faker
from kafka import KafkaProducer

# Initialize Faker for data generation
fake = Faker()

# Initialize Kafka Producer
# This connects to the Kafka broker exposed on your host machine
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC_NAME = 'clickstream_events'

print("Starting to send clickstream events to Kafka... Press Ctrl+C to stop.")

try:
    while True:
        # Generate a realistic-looking click event
        event = {
            'user_id': fake.uuid4(),
            'url': fake.uri_path(),
            'http_status': random.choice([200, 201, 302, 404, 500]),
            'event_timestamp': time.time()
        }
        
        # Send the event to the Kafka topic
        producer.send(TOPIC_NAME, value=event)
        
        # Log to console
        print(f"Sent event: {event}")
        
        # Wait for 1 second before sending the next event
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nProducer stopped by user.")
finally:
    # Ensure all buffered messages are sent
    producer.flush()
    producer.close()
    print("Kafka producer closed.")