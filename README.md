# Weather App

A scalable, distributed, and Dockerized pipeline for weather prediction using Kafka, Cassandra, and Spark.

> **Note:** To customize the port numbers, host names, replication factor, et cetera, please modify the [config file](./files/config.py).


## Instructions

1. Start the Weather App

> **Note:** running this App will take up roughly 20G memory!

```sh
make start
```

2. Train the model with Spark ML

```sh
make trainer
```

3. Inference on stream data and save to Cassandra


```sh
make predictor
```

4.  View the data stored in Cassandra

```sh
make viewer
```

5. Clean up

```sh
make clean
```

## Appendix

1. To generate the gRPC proto

```sh
python3 -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. report.proto
```