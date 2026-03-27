Multi-Broker Kafka Order Processing Platform
1. Overview

This project implements a fault-tolerant, event-driven order processing platform using Apache Kafka deployed on Kubernetes. The system is designed to simulate a production-style streaming architecture with multiple brokers, consumer groups, topic governance, and failure handling.

The platform consists of a three-broker Kafka cluster running in KRaft mode, a producer that generates order events, and a consumer group that processes these events and emits confirmation messages. Failed messages are routed to a dedicated Dead Letter Topic (DLT) for later inspection and replay.

In addition, Avro serialization is implemented using Schema Registry to demonstrate structured messaging between producers and consumers.

2. Architecture

The system is composed of the following components:

Kafka Cluster (3 brokers, KRaft mode)
Kafka Services (headless and cluster access)
Topic Initialisation Job
Producer (JSON and Avro)
Consumer Group (3 replicas)
Dead Letter Topic (DLT)
Schema Registry (Avro support)
Kafka UI (observability)
Orchestration Script
Message Flow

orders -> consumer
  |__ order-consumed (successful processing)
  |__ orders.DLT (failed processing)

3. Kafka Cluster Design

The Kafka cluster is deployed as a StatefulSet with three replicas to ensure fault tolerance.

Key configurations include:

KRaft mode enabled (no ZooKeeper)
Replication factor of 3
Minimum in-sync replicas set to 2
Offset and transaction logs replicated across all brokers

This configuration allows the system to tolerate the failure of one broker without data loss.

4. Topic Design and Governance

Topics are created using a dedicated Kubernetes Job to ensure consistent configuration.

The following topics are defined:

Topic	Purpose	Retention
orders	Incoming order events	7 days
order-consumed	Successfully processed orders	3 days
orders.DLT	Failed messages for analysis	30 days

All topics are configured with:

3 partitions
replication factor of 3
min.insync.replicas = 2

5. Producer Design

The system includes two producers:

5.1 JSON Producer

The primary producer generates 100 order events and sends them to the orders topic.

Key features:

Key-based partitioning using user field
Throughput measurement
Delivery reporting
Failure simulation via invalid quantity values

5.2 Avro Producer

An Avro-based producer is implemented using Schema Registry.

Features:

Schema-defined message structure
Avro serialization
Integration with Schema Registry

6. Consumer Design

The consumer is deployed as a 3-replica Deployment, forming a consumer group.

Key Features:
Manual offset management (auto-commit disabled)
Idempotent processing using order_id tracking
Outbox pattern implementation (producing to order-consumed)
Dead Letter Topic handling

If processing fails, the message is routed to orders.DLT with metadata including:

original message
error details
source partition and offset

7. Avro Deserialization

A dedicated Avro consumer is implemented to demonstrate schema-based message consumption.

This consumer:

Uses Schema Registry
Deserializes Avro messages into structured objects
Commits offsets after successful processing

8. Schema Registry

Schema Registry is deployed to support Avro serialization.

It enables:

Centralized schema management
Structured message validation
Compatibility between producers and consumers

Schemas are defined in the producer and reused by the consumer to ensure consistency.

9. Deployment Process

Deployment is automated using an orchestration script.

Execution order:

Deploy Kafka cluster
Wait for broker readiness
Run topic initialisation job
Deploy consumer group
Deploy producer
Deploy Schema Registry
Deploy Kafka UI

10. Observability

Kafka UI is deployed to provide visibility into:

Topics and partitions
Message flow
Consumer group activity
Offset tracking

This allows verification of:

successful message processing
failure routing to DLT
consumer scaling behaviour

11. Fault Tolerance and Reliability

The system ensures reliability through:

replication factor of 3
minimum in-sync replicas of 2
manual offset commits
idempotent consumer logic
Dead Letter Topic handling

These mechanisms prevent data loss and ensure safe replay of events.

12. Security Considerations

Security features such as TLS, SASL authentication, and ACLs were not implemented.

The cluster operates in PLAINTEXT mode and is intended for development and demonstration purposes.

In a production environment, these features would be required to control access and secure communication between components.

13. Conclusion

This project demonstrates a complete event-driven architecture using Kafka, including:

multi-broker fault-tolerant cluster
structured topic governance
producer and consumer pipelines
failure handling using a Dead Letter Topic
schema-based messaging with Avro
observability via Kafka UI

The system reflects real-world design patterns used in distributed streaming platforms and provides a foundation for further enhancements such as schema evolution, security, and monitoring.