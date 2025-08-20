# Start with the official Flink image
FROM apache/flink:1.16.0-scala_2.12

# Switch to root to install dependencies
USER root

# Install Python 3 and pip
# Install Python 3 and pip
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*


# Upgrade pip to avoid version issues
RUN python3 -m pip install --upgrade pip

# Copy the requirements file
COPY requirements.txt /opt/flink/usrlib/requirements.txt

# Install Python dependencies system-wide (accessible for flink user too)
RUN python3 -m pip install --no-cache-dir -r /opt/flink/usrlib/requirements.txt

# Copy Kafka connector JAR
COPY jars/flink-sql-connector-kafka-3.0.2-1.18.jar /opt/flink/lib/

# Switch back to flink user
USER flink
