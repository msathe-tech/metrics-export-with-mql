# Replace the values as needed
PROJECT_ID = "abm-on-gcctdemo"
PUBSUB_TOPIC = "mql_metric_export"
BIGQUERY_DATASET = "metric_export"
BIGQUERY_TABLE = "mql_metrics"

# Add/Update the queries for your metrics
MQL_QUERYS = {
# "instance/cpu/utilization":
# """
# fetch gce_instance::compute.googleapis.com/instance/cpu/utilization
# | bottom 3, max(val()) | within 5m
# """,

# "bigquery/slots/total_available":
# """
# fetch global
# | metric 'bigquery.googleapis.com/slots/total_available'
# | group_by 5m, [value_total_available_mean: mean(value.total_available)]
# | every 5m | within 1h
# """,

# "bigquery/slots/allocated_for_project":
# """
# fetch global
# | metric 'bigquery.googleapis.com/slots/allocated_for_project'
# | group_by 5m,
#     [value_allocated_for_project_mean: mean(value.allocated_for_project)]
# | every 5m | within 1h
# """,

"k8s_node_total_containers_cpu_allocation_percentage":
"""
{ t_0:
    fetch k8s_container
    | metric
        'kubernetes.io/anthos/kube_pod_container_resource_requests_cpu_cores'
    | group_by 1m,
        [value_kube_pod_container_resource_requests_cpu_cores_mean:
           mean(value.kube_pod_container_resource_requests_cpu_cores)]
    | every 1m
    | group_by [node: metric.node],
        [value_kube_pod_container_resource_requests_cpu_cores_mean_aggregate:
           aggregate(value_kube_pod_container_resource_requests_cpu_cores_mean)]
; t_1:
    fetch k8s_container
    | metric 'kubernetes.io/anthos/kube_node_status_allocatable_cpu_cores'
    | group_by 1m,
        [value_kube_node_status_allocatable_cpu_cores_mean:
           mean(value.kube_node_status_allocatable_cpu_cores)]
    | every 1m
    | group_by [node: metric.node],
        [value_kube_node_status_allocatable_cpu_cores_mean_aggregate:
           aggregate(value_kube_node_status_allocatable_cpu_cores_mean)] }
| join
| value
    [v_0:
       cast_units(
         div(
           t_0.value_kube_pod_container_resource_requests_cpu_cores_mean_aggregate,
           t_1.value_kube_node_status_allocatable_cpu_cores_mean_aggregate)
         * 100,
         '%')]
| top 10, v_0
""",
"k8s_node_total_containers_memory_allocation_percentage":
"""
{ t_0:
    fetch k8s_container
    | metric
        'kubernetes.io/anthos/kube_pod_container_resource_requests_memory_bytes'
    | group_by 1m,
        [value_kube_pod_container_resource_requests_memory_bytes_mean:
           mean(value.kube_pod_container_resource_requests_memory_bytes)]
    | every 1m
    | group_by [node: metric.node],
        [value_memory_requested_bytes:
           aggregate(
             value_kube_pod_container_resource_requests_memory_bytes_mean)]
; t_1:
    fetch k8s_container
    | metric 'kubernetes.io/anthos/kube_node_status_allocatable_memory_bytes'
    | group_by 1m,
        [value_kube_node_status_allocatable_memory_bytes_mean:
           mean(value.kube_node_status_allocatable_memory_bytes)]
    | every 1m
    | group_by [node: metric.node],
        [value_allocatable_memory_bytes:
           aggregate(value_kube_node_status_allocatable_memory_bytes_mean)] }
| join
| value
    [v_0:
       cast_units(
         div(t_0.value_memory_requested_bytes,
           t_1.value_allocatable_memory_bytes) * 100,
         '%')]
| top 10, v_0
""",
"k8s_node_total_containers_storage_allocation_percentage":
"""
{ t_0:
    fetch k8s_container
    | metric 'kubernetes.io/anthos/kube_pod_container_resource_requests'
    | filter (metric.resource == 'ephemeral_storage')
    | group_by 1m,
        [value_kube_pod_container_resource_requests_mean:
           mean(value.kube_pod_container_resource_requests)]
    | every 1m
    | group_by [node: metric.node],
        [value_kube_pod_container_resource_requests_mean_aggregate:
           aggregate(value_kube_pod_container_resource_requests_mean)]
; t_1:
    fetch k8s_node
    | metric 'kubernetes.io/anthos/node_filesystem_avail_bytes'
    | filter (metric.fstype != 'tmpfs')
    | group_by 1m,
        [value_node_filesystem_avail_bytes_mean:
           mean(value.node_filesystem_avail_bytes)]
    | every 1m
    | group_by [node: resource.node_name],
        [value_node_filesystem_avail_bytes_mean_aggregate:
           aggregate(value_node_filesystem_avail_bytes_mean)] }
| join
| value
    [v_0:
       cast_units(
         div(t_0.value_kube_pod_container_resource_requests_mean_aggregate,
           t_1.value_node_filesystem_avail_bytes_mean_aggregate) * 100,
         '%')]
| top 10, v_0
""",
"k8s_node_disk_usage_percentage":
"""
{ t_0:
    fetch k8s_node
    | metric 'kubernetes.io/anthos/node_filesystem_avail_bytes'
    | filter (metric.fstype != 'tmpfs')
    | group_by 1m,
        [value_node_filesystem_avail_bytes_mean:
           mean(value.node_filesystem_avail_bytes)]
    | every 1m
    | group_by
        [device: metric.device, node: resource.node_name],
        [value_node_filesystem_avail_bytes_mean_aggregate:
           aggregate(value_node_filesystem_avail_bytes_mean)]
; t_1:
    fetch k8s_node
    | metric 'kubernetes.io/anthos/node_filesystem_size_bytes'
    | filter (metric.fstype != 'tmpfs')
    | group_by 1m,
        [value_node_filesystem_size_bytes_mean:
           mean(value.node_filesystem_size_bytes)]
    | every 1m
    | group_by
        [device: metric.device, node: resource.node_name],
        [value_node_filesystem_size_bytes_mean_aggregate:
           aggregate(value_node_filesystem_size_bytes_mean)] }
| join
| value
    [v_0:
       cast_units(
         div(
           sub(t_1.value_node_filesystem_size_bytes_mean_aggregate,
             t_0.value_node_filesystem_avail_bytes_mean_aggregate),
           t_1.value_node_filesystem_size_bytes_mean_aggregate) * 100,
         '%')]
""",
"k8s_node_network_receive_rate":
"""
fetch k8s_node
| metric 'kubernetes.io/anthos/node_network_receive_bytes_total'
| align rate(1m)
| every 1m
| group_by [resource.node_name],
    [value_node_network_receive_bytes_total_aggregate:
       aggregate(value.node_network_receive_bytes_total)]
""",
"k8s_node_network_transmit_rate":
"""
fetch k8s_node
| metric 'kubernetes.io/anthos/node_network_transmit_bytes_total'
| align rate(1m)
| every 1m
| group_by [resource.node_name],
    [value_node_network_transmit_bytes_total_aggregate:
       aggregate(value.node_network_transmit_bytes_total)]
""",
"k8s_api_servers_count":
"""
fetch k8s_container
| metric 'kubernetes.io/anthos/up'
| filter (resource.container_name == 'kube-apiserver')
| group_by 1m, [value_up_mean: mean(value.up)]
| every 1m
| group_by [resource.cluster_name],
    [value_up_mean_aggregate: aggregate(value_up_mean)]
"""


}

BASE_URL = "https://monitoring.googleapis.com/v3/projects"
QUERY_URL = f"{BASE_URL}/{PROJECT_ID}/timeSeries:query"


BQ_VALUE_MAP = {
    "INT64": "int64_value",
    "BOOL": "boolean_value",
    "DOUBLE": "double_value",
    "STRING": "string_value",
    "DISTRIBUTION": "distribution_value"
}

API_VALUE_MAP = {
    "INT64": "int64Value",
    "BOOL": "booleanValue",
    "DOUBLE": "doubleValue",
    "STRING": "stringValue",
    "DISTRIBUTION": "distributionValue"
}