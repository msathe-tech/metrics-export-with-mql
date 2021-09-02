#!/bin/bash
export PROJECT_ID=`gcloud config get-value core/project`
export PUBSUB_TOPIC=mql_metric_export
export BIGQUERY_DATASET=metric_export
export BIGQUERY_TABLE=mql_metrics
