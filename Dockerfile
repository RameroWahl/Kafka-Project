FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir confluent-kafka fastavro
COPY producer.py tracker.py ./
COPY producer_avro.py consumer_avro.py ./
ENV MODE=producer
CMD ["sh", "-c", "\
if [ \"$MODE\" = 'producer' ]; then python producer.py; \
elif [ \"$MODE\" = 'consumer' ]; then python tracker.py; \
elif [ \"$MODE\" = 'avro-producer' ]; then python producer_avro.py; \
else python consumer_avro.py; fi"]