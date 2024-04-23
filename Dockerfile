FROM ubuntu:22.04

# Install dependencies (general, Python, Kafka, Spark, Cassandra)
RUN apt-get update; apt-get install -y wget curl openjdk-11-jdk python3-pip net-tools lsof nano
RUN pip3 install jupyterlab==4.0.3 pandas==2.1.1 matplotlib==3.8.0 kafka-python==2.0.2 grpcio==1.58.0 grpcio-tools==1.58.0 pyspark==3.5.0 cassandra-driver==3.28.0
RUN wget https://downloads.apache.org/kafka/3.6.2/kafka_2.13-3.6.2.tgz && tar -xf kafka_2.13-3.6.2.tgz && rm kafka_2.13-3.6.2.tgz
RUN wget https://dlcdn.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz && tar -xf spark-3.5.1-bin-hadoop3.tgz && rm spark-3.5.1-bin-hadoop3.tgz
RUN wget https://dlcdn.apache.org/cassandra/4.1.3/apache-cassandra-4.1.3-bin.tar.gz; tar -xf apache-cassandra-4.1.3-bin.tar.gz; rm apache-cassandra-4.1.3-bin.tar.gz
RUN wget https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.5.0/spark-cassandra-connector_2.12-3.5.0.jar
RUN cp /spark-cassandra-connector_2.12-3.5.0.jar /spark-3.5.1-bin-hadoop3/jars/