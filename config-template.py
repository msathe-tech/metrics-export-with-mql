# Replace the values as needed
PROJECT_ID = "$PROJECT_ID"
PUBSUB_TOPIC = "$PUBSUB_TOPIC"
BIGQUERY_DATASET = "$BIGQUERY_DATASET"
BIGQUERY_TABLE = "$BIGQUERY_TABLE"

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
# """
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
""",
"top_10_containers_by_cpu_seconds":
"""
fetch k8s_container
| metric 'kubernetes.io/anthos/process_cpu_seconds_total'
| align rate(1m)
| every 1m
""",
"top_10_containers_by_cpu_cores_requested":
"""
fetch k8s_container
| metric 'kubernetes.io/anthos/kube_pod_container_resource_requests_cpu_cores'
| group_by 1m,
    [value_kube_pod_container_resource_requests_cpu_cores_mean:
       mean(value.kube_pod_container_resource_requests_cpu_cores)]
| every 1m
| group_by
    [metric.container, metric.namespace, metric.node, metric.pod,
     resource.location, resource.cluster_name, resource.namespace_name,
     resource.pod_name, resource.container_name],
    [value_kube_pod_container_resource_requests_cpu_cores_mean_aggregate:
       aggregate(value_kube_pod_container_resource_requests_cpu_cores_mean)]
""",
"top_10_containers_by_memory_usage":
"""
fetch k8s_node
| metric 'kubernetes.io/anthos/container_memory_working_set_bytes'
| filter (metric.pod =~ '.+')
| group_by 1m,
    [value_container_memory_working_set_bytes_mean:
       mean(value.container_memory_working_set_bytes)]
| every 1m
| group_by
    [metric.container, metric.namespace, metric.pod, resource.project_id,
     resource.location, resource.cluster_name, resource.node_name],
    [value_container_memory_working_set_bytes_mean_aggregate:
       aggregate(value_container_memory_working_set_bytes_mean)]
""",
"top_10_containers_by_memory_requested":
"""
fetch k8s_container
| metric
    'kubernetes.io/anthos/kube_pod_container_resource_requests_memory_bytes'
| group_by 1m,
    [value_kube_pod_container_resource_requests_memory_bytes_mean:
       mean(value.kube_pod_container_resource_requests_memory_bytes)]
| every 1m
| group_by
    [metric.container, metric.namespace, metric.node, metric.pod,
     resource.location, resource.cluster_name, resource.namespace_name,
     resource.pod_name, resource.container_name],
    [value_kube_pod_container_resource_requests_memory_bytes_mean_aggregate:
       aggregate(value_kube_pod_container_resource_requests_memory_bytes_mean)]
""",
"k8s_node_filesystem_size":
"""
fetch k8s_node
| metric 'kubernetes.io/anthos/node_filesystem_files'
| filter (metric.fstype != 'tmpfs')
| group_by 1m,
    [value_node_filesystem_files_mean: mean(value.node_filesystem_files)]
| every 1m
| group_by
    [metric.device, metric.fstype, metric.mountpoint, resource.project_id,
     resource.location, resource.cluster_name, resource.node_name],
    [value_node_filesystem_files_mean_aggregate:
       aggregate(value_node_filesystem_files_mean)]
""",
"top_10_containers_by_storage_requested":
"""
fetch k8s_container
| metric 'kubernetes.io/anthos/kube_pod_container_resource_requests'
| filter (metric.resource == 'ephemeral_storage')
| group_by 1m,
    [value_kube_pod_container_resource_requests_mean:
       mean(value.kube_pod_container_resource_requests)]
| every 1m
| group_by
    [metric.container, metric.namespace, metric.node, metric.pod, metric.unit,
     resource.location, resource.cluster_name, resource.namespace_name,
     resource.pod_name, resource.container_name],
    [value_kube_pod_container_resource_requests_mean_aggregate:
       aggregate(value_kube_pod_container_resource_requests_mean)]
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