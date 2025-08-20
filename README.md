# 🚀 Real-Time Clickstream Intelligence & Error Monitoring Platform

**Tech Stack:** Python, Apache Kafka, Apache Flink, InfluxDB, Grafana, Docker, Faker

This project implements a comprehensive, end-to-end data engineering pipeline designed to ingest, process, and visualize high-volume website clickstream data in real-time. By leveraging a modern, open-source technology stack, this platform showcases a scalable and fault-tolerant architecture for stream processing, data orchestration, and live operational intelligence.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [How It Works: A Deeper Dive](#how-it-works-a-deeper-dive)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Running the Pipeline](#running-the-pipeline)
- [Grafana Dashboards](#grafana-dashboards)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
In today's digital landscape, understanding user behavior as it happens is critical for business success. This platform simulates, processes, and monitors user clickstream data in real-time, providing immediate insights into application health and user engagement. By tracking metrics on the fly, businesses can react instantly to production issues, understand feature adoption, and make data-driven decisions without delay.

The system provides insights such as:
- **Live Error Rate Monitoring:** Instantly identify spikes in HTTP error codes (e.g., 404s, 500s) to detect and diagnose production issues.
- **Real-time Engagement Metrics:** Track event counts per URL to see which parts of an application are most active.
- **User Activity Trends:** Analyze time-series data to understand patterns in user interactions over time.

The entire platform is containerized using Docker Compose, ensuring a reproducible and scalable environment that's easy to deploy.

---

## Architecture

The data flows through the system in a classic, event-driven streaming architecture:

```
+-----------------+      +-----------------+       +-----------------+       +-----------------+
| Faker Producer  | ---> | Kafka Broker    | --->  | Flink Stream    | --->  | InfluxDB        |
| (Synthetic data)|      | (clickstream)   |       | Processing      |       | (Time-series DB)|
+-----------------+      +-----------------+       +-----------------+       +-----------------+
                                                                                  |
                                                                                  v
                                                                            +----------------+
                                                                            | Grafana        |
                                                                            | Visualization  |
                                                                            +----------------+
```
1.  **Data Production:** A Python script using the `Faker` library generates synthetic but realistic user click events and sends them to a Kafka topic.
2.  **Ingestion:** **Apache Kafka** acts as the central message bus, ingesting the high-throughput stream of events and decoupling the producer from the consumer.
3.  **Stream Processing:** **Apache Flink** consumes the raw data stream from Kafka. It performs stateful, windowed aggregations (e.g., counting events by status code every 10 seconds) to transform the raw clicks into meaningful metrics.
4.  **Storage:** The processed, time-stamped metrics are written to **InfluxDB**, a database optimized for time-series data.
5.  **Visualization:** **Grafana** connects to InfluxDB as a data source and provides interactive, auto-refreshing dashboards for monitoring and analytics.

---
## How It Works: A Deeper Dive

1.  **The Producer (`producer.py`):**
    - This standalone Python script runs on the host machine.
    - It establishes a connection to the Kafka broker, which is exposed on `localhost:9092`.
    - In an infinite loop, it generates a JSON object containing a fake `user_id`, `url`, `http_status`, and a current `event_timestamp`.
    - Each JSON object is serialized and sent as a message to the `clickstream_events` topic in Kafka.

2.  **Kafka (The Message Bus):**
    - The Kafka service, running in Docker, receives messages from the producer.
    - It uses a special listener configuration (`ADVERTISED_LISTENERS`) to be accessible from both the host machine (`localhost:9092`) and from within the Docker network (`kafka:29092`).
    - The topic `clickstream_events` acts as a durable, ordered log. This means Flink can consume from it without worrying about data loss if the Flink job restarts.

3.  **Flink (`process_stream.py`):**
    - The Flink job is submitted to the `jobmanager` container. The `jobmanager` then deploys the job to the `taskmanager` container for execution.
    - The `taskmanager` connects to Kafka using the internal Docker address `kafka:29092`.
    - **Data Consumption:** It reads the raw string data from the `clickstream_events` topic.
    - **Parsing & Filtering:** Each string is parsed into a Python dictionary. Any malformed JSON is filtered out.
    - **Keying:** The stream is "keyed by" the `http_status`. This groups all events with the same status code (e.g., all 200s, all 404s) into logical sub-streams.
    - **Windowing:** Flink applies a "tumbling window" of 10 seconds. This means it collects events for each key for 10 seconds, then processes them as a batch.
    - **Aggregation:** At the end of each 10-second window, a function is applied to count the number of events that occurred for each key.
    - **The Sink:** The final result (e.g., `(200, 15, timestamp)`) is sent to the custom `InfluxDBSink`. This sink function establishes a connection to the InfluxDB container at `http://influxdb:8086` and writes the data as a new time-series point.

4.  **InfluxDB & Grafana:**
    - InfluxDB receives the data points and stores them in the `clickstream` bucket.
    - Grafana, which is connected to InfluxDB as a data source, periodically runs Flux queries against the database to fetch the latest data points and update the dashboard visualizations.

---

## Features
- **Real-time Event Ingestion:** A fault-tolerant Kafka Producer continuously sends clickstream events.
- **Stateful Stream Processing:** Apache Flink performs time-windowed aggregations to calculate metrics over specific intervals.
- **Error Rate Tracking:** The pipeline specifically tracks and aggregates HTTP status codes, making it easy to monitor application health.
- **Time-Series Storage:** InfluxDB efficiently stores and serves the time-series data required for trend analysis.
- **Interactive Live Dashboards:** Grafana provides rich, interactive dashboards with auto-refresh for at-a-glance monitoring.
- **Containerized Deployment:** The entire multi-service application is defined in a single `docker-compose.yml` file for easy setup and deployment.

---

## Setup & Installation
### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### Steps
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/realtime-clickstream-monitoring.git](https://github.com/yourusername/realtime-clickstream-monitoring.git)
    cd realtime-clickstream-monitoring
    ```
2.  **Configure InfluxDB Credentials:** Before launching, you must set a secure admin token for InfluxDB.
    - **Generate a Token:** Use a password manager or command-line tool to create a strong, random string.
    - **Update `docker-compose.yml`:** Replace `your_secure_token_here` with your new token.
    - **Update `process_stream.py`:** Open `flink/process_stream.py` and replace the token there as well.

3.  **Build and start all services:** This command builds the custom Flink image and starts the entire stack.
    ```bash
    docker-compose up -d --build
    ```
4.  **(Optional) Check if services are running:**
    ```bash
    docker-compose ps
    ```
    All services should have a status of `running` or `Up`.

---

## Running the Pipeline
1.  **Start the Kafka Producer:** In a new terminal, start the script to send synthetic clickstream events.
    ```bash
    python producer.py
    ```
2.  **Verify Data in Kafka (Optional):** In another terminal, you can listen to the Kafka topic to see the raw data flow.
    ```bash
    docker-compose exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic clickstream_events
    ```
3.  **Submit the Flink job:** In a third terminal, submit the processing job to the Flink cluster.
    ```bash
    docker-compose exec jobmanager flink run --python /opt/flink/usrlib/process_stream.py
    ```
4.  **Verify InfluxDB is receiving data** by visiting `http://localhost:8086` and using the Data Explorer.

---

## Grafana Dashboards
1.  **Open Grafana:** `http://localhost:3000`
2.  **Login** with credentials:
    - **Username:** `admin`
    - **Password:** `admin123`
3.  **Add InfluxDB as a data source:**
    - **URL:** `http://influxdb:8086`
    - **Token:** The same token you set in Docker Compose.
4.  **Create Panels:** Create a new dashboard and add panels. Here is a sample **Flux query** for a time-series graph of events grouped by status code:
    ```flux
    from(bucket: "clickstream")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "http_counts")
      |> filter(fn: (r) => r["_field"] == "count")
      |> group(columns: ["status_code"])
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
      |> yield(name: "mean")
    ```
5.  **Set Auto-refresh** to `5s` for real-time monitoring.

---
## Troubleshooting

- **`NoBrokersAvailable` from `producer.py`:**
  - **Cause:** The Kafka container is not running or not accessible from your host machine.
  - **Solution:** Ensure `docker-compose ps` shows the `kafka` service as `Up`. Check your firewall or VPN settings. Try changing `localhost` to `127.0.0.1` in `producer.py`.

- **Flink job fails with `TimeoutException`:**
  - **Cause:** The Flink `taskmanager` container cannot connect to the Kafka container.
  - **Solution:** This is a Docker networking issue. Ensure the `KAFKA_ADVERTISED_LISTENERS` in your `docker-compose.yml` is configured correctly for both internal and external traffic. Perform a clean restart with `docker-compose down -v` and `docker-compose up -d --build`.

- **No data in Grafana/InfluxDB:**
  - **Cause:** The Flink job is crashing, or the InfluxDB credentials are incorrect.
  - **Solution:** Check the `taskmanager` logs with `docker-compose logs -f taskmanager` for any Python tracebacks. Meticulously verify that the InfluxDB token, org, and bucket in `process_stream.py` match the values in `docker-compose.yml`.

---

## Project Structure
```
.
├── docker-compose.yml      # Defines and orchestrates all services.
├── flink/
│   ├── Dockerfile          # Builds the custom Flink image with dependencies.
│   ├── requirements.txt      # Python dependencies for the Flink job.
│   └── process_stream.py     # The core Flink stream processing logic.
├── producer.py             # Python script to generate and send clickstream data.
└── README.md               # You are here!
```

---

## Contributing
Contributions are welcome! Please follow these steps:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Commit changes (`git commit -m 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature`).
5.  Open a Pull Request.

---

## License
This project is licensed under the MIT License.
