from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

import json
import uuid
import os

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

schema_registry_conf = {
    'url': 'http://schema-registry:8081'
}

schema_registry_client = SchemaRegistryClient(schema_registry_conf)

avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer_conf = {
    'bootstrap.servers': 'kafka-service:9092',
    'value.serializer': avro_serializer
}

producer = SerializingProducer(producer_conf)

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Produced to {msg.topic()}")

order = {
    "order_id": str(uuid.uuid4()),
    "user": "ramero",
    "item": "coffee",
    "quantity": 2
}

producer.produce(
    topic="orders",
    value=order,
    on_delivery=delivery_report
)

producer.flush()