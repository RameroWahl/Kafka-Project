import json
import os
import traceback

from confluent_kafka import Consumer, Producer

consumer_config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    "group.id": os.getenv("KAFKA_GROUP_ID", "order-tracker"),
    "auto.offset.reset": os.getenv("KAFKA_OFFSET_RESET", "earliest")
}

producer_config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
}

consumer = Consumer(consumer_config)
producer = Producer(producer_config)

topic          = os.getenv("KAFKA_TOPIC", "orders")
consumed_topic = os.getenv("KAFKA_CONSUMED_TOPIC", "order-consumed")
dlt_topic      = os.getenv("KAFKA_DLT_TOPIC", "orders.DLT")

consumer.subscribe([topic])

print(f"Consumer running -> '{topic}' -> '{consumed_topic}' (DLT: '{dlt_topic}')")

processed = set()  # simple idempotency

def delivery_report(err, msg):
    if err:
        print(f"Failed to produce: {err}")
    else:
        print(f"Produced to {msg.topic()} | partition={msg.partition()} offset={msg.offset()}")

def send_to_dlt(order, error, msg):
    dlt_payload = {
        "original_order": order,
        "error": str(error),
        "source_topic": msg.topic(),
        "partition": msg.partition(),
        "offset": msg.offset()
    }

    producer.produce(
        topic=dlt_topic,
        value=json.dumps(dlt_payload).encode("utf-8")
    )
    producer.flush()

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("Kafka error:", msg.error())
            continue

        try:
            value = msg.value().decode("utf-8")
            order = json.loads(value)

            print(f"Received -> partition={msg.partition()} offset={msg.offset()} | {order}")

            #FAILURE CONDITION (DLT trigger)
            if order["quantity"] < 0:
                raise ValueError("Invalid quantity (negative)")

            #IDEMPOTENCY CHECK
            if order["order_id"] in processed:
                print("Duplicate detected, skipping")
                continue

            processed.add(order["order_id"])

            #SUCCESS -> confirmation event
            confirmation = {
                "order_id": order["order_id"],
                "user": order["user"],
                "item": order["item"],
                "quantity": order["quantity"],
                "status": "consumed",
                "source_partition": msg.partition(),
                "source_offset": msg.offset(),
            }

            producer.produce(
                topic=consumed_topic,
                key=order["user"].encode("utf-8"),
                value=json.dumps(confirmation).encode("utf-8"),
                callback=delivery_report
            )

            producer.poll(0)

            consumer.commit()

        except Exception as e:
            print("Processing failed:", e)

            try:
                send_to_dlt(order, e, msg)
                print("Sent to DLT")
            except Exception as dlt_err:
                print("DLT failure:", dlt_err)

            #CRITICAL: avoid infinite retry loop
            consumer.commit()

except KeyboardInterrupt:
    print("\nStopping consumer...")

finally:
    producer.flush()
    consumer.close()
    print("Consumer closed.")