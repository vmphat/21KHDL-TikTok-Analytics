# Import PySpark and initialize Spark session
import pyspark
from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder.appName("PySparkExample").getOrCreate()

# Create a DataFrame with sample data
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
df = spark.createDataFrame(data, ["Name", "Age"])

# Show the DataFrame
df.show()

# Stop the Spark session
spark.stop()
