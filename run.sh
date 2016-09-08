export PYSPARK_PYTHON=python3

if [ -z $OPH_MONGO_URL ]; then
    echo "OPH_MONGO_URL not provided"
    exit 1
fi

if [ -z $OPH_SPARK_MASTER_URL ]; then
    echo "OPH_SPARK_MASTER_URL not provided"
    exit 1
fi

export OPH_DBURL=$OPH_MONGO_URL
export OPH_MASTER=$OPH_SPARK_MASTER_URL

exec spark-submit --master $OPH_MASTER ./app.py
