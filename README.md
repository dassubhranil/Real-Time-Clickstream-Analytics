# 🚀 Real-Time Clickstream Intelligence & Error Monitoring Platform

**Tech Stack:** Python, Kafka, Flink, InfluxDB, Grafana, Docker, Faker

This project demonstrates a real-time data pipeline that ingests synthetic clickstream events, processes them with Apache Flink, stores them in InfluxDB, and visualizes key metrics and error rates in Grafana dashboards.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Running the Pipeline](#running-the-pipeline)
- [Grafana Dashboards](#grafana-dashboards)
- [Sample Data](#sample-data)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
The platform is designed to simulate, process, and monitor user clickstream data in real-time. It provides insights such as:

- Error rates per HTTP status code
- Event counts per URL
- Time-series trends for user interactions
- Real-time visualization for monitoring application health

The system leverages containerized services for scalability and reproducibility using Docker Compose.

---

## Architecture

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
- **Kafka:** Handles real-time messaging.
- **Flink:** Performs stream processing, parsing events, and transforming data for storage.
- **InfluxDB:** Stores time-series data.
- **Grafana:** Provides interactive dashboards for monitoring and analytics.

---

## Features
- Real-time ingestion of clickstream events using Kafka Producer
- Stream processing and enrichment using Apache Flink
- Error tracking for HTTP status codes
- Count and group events by user and URL
- Time-series storage in InfluxDB
- Interactive Grafana dashboards with auto-refresh
- Fully containerized with Docker Compose for easy deployment

---

## Setup & Installation
### Prerequisites
- Docker
- Docker Compose
- Python 3.10+

### Steps
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/realtime-clickstream-monitoring.git](https://github.com/yourusername/realtime-clickstream-monitoring.git)
    cd realtime-clickstream-monitoring
    ```
2.  **Build and start services (except the producer):**
    ```bash
    docker-compose up -d
    ```
3.  **(Optional) Check if services are running:**
    ```bash
    docker ps
    ```

---

## Running the Pipeline
1.  **Start the Kafka Producer** to send synthetic clickstream events:
    ```bash
    python producer/producer.py
    ```
2.  **Submit the Flink job** to process events:
    ```bash
    docker-compose exec jobmanager flink run --python /opt/flink/usrlib/process_stream.py
    ```
    *Note: Ensure Kafka is running and the topic `clickstream_events` exists.*

3.  **Verify InfluxDB** is receiving data by visiting: `http://localhost:8086`

---

## Grafana Dashboards
1.  **Open Grafana:** `http://localhost:3000`
2.  **Login** with default credentials:
    - **Username:** `admin`
    - **Password:** `admin123`
3.  **Add InfluxDB as a data source:**
    - **URL:** `http://influxdb:8086`
    - **Token:** Same as set in Docker Compose
4.  **Import the dashboard JSON** (provided in `/grafana/dashboards`) or create panels for:
    - Error rate by HTTP status code
    - Count of events per user or URL
5.  **Auto-refresh** every 5-10 seconds for real-time monitoring.

---

## Sample Data
```json
{
  "user_id": "5d529ba5-063a-45dc-a405-04dc2eebd26b",
  "url": "search/categories",
  "http_status": 404,
  "event_timestamp": 1755720654.4831822
}
```
Events are generated every second with randomized data for demonstration.

---

## Contributing
Contributions are welcome! Please follow these steps:
1.  Fork the repository
2.  Create a new branch (`git checkout -b feature/your-feature`)
3.  Commit changes (`git commit -m 'Add new feature'`)
4.  Push to the branch (`git push origin feature/your-feature`)
5.  Open a Pull Request

---

## License
This project is licensed under the MIT License.
