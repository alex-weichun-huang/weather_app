# Set heap size
sed -i "s/-Xms[0-9]*M/-Xms128M/" /apache-cassandra-4.1.3/conf/jvm-server.options
sed -i "s/-Xmx[0-9]*M/-Xmx128M/" /apache-cassandra-4.1.3/conf/jvm-server.options

# Listen on all interfaces
sed -i "s/^listen_address:.*/listen_address: "`hostname`"/" /apache-cassandra-4.1.3/conf/cassandra.yaml
sed -i "s/^rpc_address:.*/rpc_address: "`hostname`"/" /apache-cassandra-4.1.3/conf/cassandra.yaml

# change port
sed -i "s/^native_transport_port:.*/native_transport_port: $NATIVE_TRANSPORT_PORT" /apache-cassandra-4.1.3/conf/cassandra.yaml

# Configure seed nodes
sed -i "s/^# seed_provider:/seed_provider:/g" /apache-cassandra-4.1.3/conf/cassandra.yaml
sed -i "s/- seeds:.*/- seeds: cassandra1, cassandra2/" /apache-cassandra-4.1.3/conf/cassandra.yaml

# Start Cassandra
/apache-cassandra-4.1.3/bin/cassandra -f -R