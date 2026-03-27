from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

import os

schema_registry_conf = {
    'url': 'http://schema-registry:8081'
}

schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# SAME schema as producer
schema_str = """
{
  "type": "record",
  "name": "Order",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "user", "type": "string"},
    {"name": "item", "type": "string"},
    {"name": "quantity", "type": "int"}
  ]
}
"""

avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)

consumer_conf = {
    'bootstrap.servers': 'kafka-service:9092',
    'group.id': 'order-tracker-avro',
    'auto.offset.reset': 'earliest',
    'value.deserializer': avro_deserializer
}

consumer = DeserializingConsumer(consumer_conf)

consumer.subscribe(["orders"])

print("Avro consumer running...")

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Error:", msg.error())
            continue

        order = msg.value()
        print("Received (Avro):", order)

        consumer.commit()

except KeyboardInterrupt:
    print("Stopping Avro consumer...")

finally:
    consumer.close()