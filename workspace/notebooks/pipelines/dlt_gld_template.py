# Databricks notebook source
# MAGIC #%pip install git+https://github.com/okube-ai/laktory.git@
# MAGIC %pip install 'laktory==0.0.17'

# COMMAND ----------
import pyspark.sql.functions as F
import importlib
import sys
import os

from laktory import dlt
from laktory import read_metadata
from laktory import get_logger

dlt.spark = spark
logger = get_logger(__name__)

# Read pipeline definition
pl_name = spark.conf.get("pipeline_name", "pl-stock-prices")
pl = read_metadata(pipeline=pl_name)

# Import User Defined Functions
sys.path.append("/Workspace/pipelines/")
udfs = []
for udf in pl.udfs:
    if udf.module_path:
        sys.path.append(os.path.abspath(udf.module_path))
    module = importlib.import_module(udf.module_name)
    udfs += [getattr(module, udf.function_name)]


# --------------------------------------------------------------------------- #
# Tables                                                                      #
# --------------------------------------------------------------------------- #

def define_table(table):
    @dlt.table(
        name=table.name,
        comment=table.comment,
    )
    def get_df():
        logger.info(f"Building {table.name} table")

        # Read Source
        df = table.builder.read_source(spark)
        df.printSchema()

        # Process
        df = table.builder.process(df, udfs=udfs, spark=spark)

        # Return
        return df

    return get_df


# --------------------------------------------------------------------------- #
# Execution                                                                   #
# --------------------------------------------------------------------------- #

# Build tables
for table in pl.tables:
    if table.builder.template == "GOLD":
        wrapper = define_table(table)
        df = dlt.get_df(wrapper)
        display(df)