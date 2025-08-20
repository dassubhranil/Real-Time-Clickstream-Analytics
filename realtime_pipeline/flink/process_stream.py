# process_stream.py
import json
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from influxdb_client import InfluxDBClient, Point, WriteOptions


# ---------- InfluxDB Setup ----------
INFLUXDB_URL = "http://influxdb:8086"   # use container name inside docker network
INFLUXDB_TOKEN = "rIwFfRQc4bjPsA1a45jkBOWaVurgPC9TTOBV9tmPbMpg8wpfDP7jzFn2_X6CEYRTsV5ISr-CXSQEYtjRTvVwaQ=="             # set in docker-compose.yml
INFLUXDB_ORG = "my-org"
INFLUXDB_BUCKET = "clickstream"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))  # write immediately


# ---------- Flink Setup ----------
env = StreamExecutionEnvironment.get_execution_environment()

kafka_consumer = FlinkKafkaConsumer(
    topics="clickstream_events",
    deserialization_schema=SimpleStringSchema(),
    properties={
        "bootstrap.servers": "kafka:29092",   # kafka container name
        "group.id": "flink-consumer"
    }
)

stream = env.add_source(kafka_consumer)


# ---------- Business Logic ----------
def process_event(value: str):
    try:
        event = json.loads(value)

        # Build InfluxDB point
        point = (
            Point("clickstream")
            .tag("user_id", event.get("user_id", "unknown"))
            .tag("url", event.get("url", "unknown"))
            .field("http_status", int(event.get("http_status", 0)))
            .time(int(event.get("event_timestamp", 0)) * 1_000_000_000)  # ns
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        print(f"✔ Saved to InfluxDB: {event}")
    except Exception as e:
        print(f"❌ Failed to process {value} -> {e}")

    return value


stream.map(process_event)

env.execute("Kafka-Flink-InfluxDB Pipeline")
