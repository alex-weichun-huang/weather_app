from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DateType, DoubleType, IntegerType
from pyspark.sql.functions import date_add, month, year, dayofmonth
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from config import CONFIG


# get the configs for Kafka
brokers = []
for i in range(len(CONFIG["kafka"]["host_name"])):
    brokers.append(f'{CONFIG["kafka"]["host_name"][i]}:{CONFIG["kafka"]["port_num"][i]}')


# get the configs for Spark
shuffle_partitions = CONFIG["spark"]["shuffle_partitions"]
awaitTermination = CONFIG["spark"]["awaitTermination"]
processingTime = CONFIG["spark"]["processingTime"]


# Create a SparkSession
spark = (SparkSession.builder.appName("weather-app")
         .config("spark.sql.shuffle.partitions", shuffle_partitions)
         .config("spark.ui.showConsoleProgress", False)
         .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.2')
         .getOrCreate())


# initialize Kafka stream
stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", ",".join(brokers))
    .option("subscribe", "weather-stations-json")
    .option("startingOffsets", "earliest")
    .load()
)


# define schema 
schema = StructType([
    StructField("station", StringType()),
    StructField("date", DateType()),
    StructField("degrees", DoubleType()),
    StructField("raining", IntegerType())
])


# get features
df = stream.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
yesterday = df.select("station", date_add("date", -1).alias("date"), "degrees", "raining").withColumnRenamed("degrees", "prev1_degrees").withColumnRenamed("raining", "prev1_raining")
two_days_ago = df.select("station", date_add("date", -2).alias("date"), "degrees", "raining").withColumnRenamed("degrees", "prev2_degrees").withColumnRenamed("raining", "prev2_raining")
features = (
    df.withColumn("year", year("date"))
    .withColumn("month", month("date"))
    .withColumn("day", dayofmonth("date"))
    .join(yesterday, ["station", "date"])
    .join(two_days_ago, ["station", "date"]).repartition(1)
)


# save training data to parquet files
query = (
    features.writeStream 
    .outputMode("append") 
    .format("parquet") 
    .option("path", "/files/training_data") 
    .option("checkpointLocation", "checkpoint") 
    .trigger(processingTime=processingTime)
    .start()
)
query.awaitTermination(awaitTermination)
query.stop()


# load training data from parquet files
data = spark.read.parquet("./files/training_data/*.parquet")
vector_assembler = VectorAssembler(inputCols=["year", "month", "day", "prev1_degrees", "prev1_raining", "prev2_degrees", "prev2_raining"], outputCol="features")
data = vector_assembler.transform(data)


# train the model
print("\n\n\n")
print("Training the model...")
train_data, test_data = data.randomSplit([0.8, 0.2])
dt_classifier = DecisionTreeClassifier(labelCol="raining", featuresCol="features")
dt_model = dt_classifier.fit(train_data)


# evaluate the model
predictions = dt_model.transform(test_data)
evaluator = MulticlassClassificationEvaluator(labelCol="raining", predictionCol="prediction", metricName="accuracy")
evaluator.evaluate(predictions)


# save model (overwrite if exists)
print("Model accuracy: ", evaluator.evaluate(predictions))
dt_model.write().overwrite().save("/files/model/dt_model")
print("Model saved to /files/model/dt_model")