CONFIG = {
    "kafka": {
        "host_name": ["kafka1", "kafka2"], # these need to match the service names in the docker-compose file
        "port_num": ["9091", "9092"], # these need to match the port numbers in the docker-compose file
        "replication_factor": 2, # this cannot be more than the number of hosts
        "num_partitions": 4,
    },
    "cassandra": {
        "host_name": ["cassandra1", "cassandra2"], # these need to match the names in cassandra.sh and the docker-compose file
        "port_num": ["9041", "9042"], # these need to match the port numbers in the docker-compose file
        "replication_factor": 2, # this cannot be more than the number of hosts
    },
    "spark": {
        "shuffle_partitions": 10,
        "awaitTermination": 60,
        "processingTime": "2 minute",
    }
}