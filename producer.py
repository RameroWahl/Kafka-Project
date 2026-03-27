import json
import uuid
import os
import time
import random

from confluent_kafka import Producer

producer_config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-service:9092"),
    "acks": "all"
}

producer = Producer(producer_config)

USERS  = ["lara", "john", "sara", "mike", "amy"]
ITEMS  = ["frozen yogurt", "ice cream", "coffee", "sandwich", "juice"]

delivered = 0
failed    = 0

def delivery_report(err, msg):
    global delivered, failed
    if err:
        failed += 1
        print(f"Delivery failed: {err}")
    else:
        delivered += 1
        print(f"[{delivered}/100] Delivered -> topic={msg.topic()} partition={msg.partition()} offset={msg.offset()}")

def generate_order():
    quantity = random.choice([random.randint(1, 20), -1])  #occasional failure trigger

    return {
        "order_id": str(uuid.uuid4()),
        "user":     random.choice(USERS),
        "item":     random.choice(ITEMS),
        "quantity": quantity
    }

def main():
    topic      = os.getenv("KAFKA_TOPIC", "orders")
    num_events = 100

    print(f"Producing {num_events} orders to topic '{topic}'...\n")

    start_time = time.time()

    for i in range(num_events):
        order = generate_order()
        value = json.dumps(order).encode("utf-8")
        key   = order["user"].encode("utf-8")  #CRITICAL (partitioning)

        producer.produce(
            topic=topic,
            key=key,                      # ensures ordering per user
            value=value,
            callback=delivery_report
        )

        producer.poll(0)

    print("All events queued. Waiting for delivery...\n")
    producer.flush()

    duration = time.time() - start_time

    print("\n--- Results ---")
    print(f"Total events         : {num_events}")
    print(f"Delivered            : {delivered}")
    print(f"Failed               : {failed}")
    print(f"Time taken           : {duration:.3f} sec")
    print(f"Throughput           : {num_events / duration:.1f} events/sec")

if __name__ == "__main__":
    main()
