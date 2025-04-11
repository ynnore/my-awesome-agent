# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "google_project_iam_member" "bigquery_data_editor" {

  project = var.dev_project_id
  role    = "roles/bigquery.dataEditor"
  member  = module.log_export_to_bigquery.writer_identity
}


module "log_export_to_bigquery" {

  source  = "terraform-google-modules/log-export/google"
  version = "10.0.0"

  log_sink_name          = var.telemetry_sink_name
  parent_resource_type   = "project"
  parent_resource_id     = var.dev_project_id
  destination_uri        = "bigquery.googleapis.com/projects/${var.dev_project_id}/datasets/${var.telemetry_bigquery_dataset_id}"
  filter                 = var.telemetry_logs_filter
  bigquery_options       = { use_partitioned_tables = true }
  unique_writer_identity = true
  depends_on             = [resource.google_project_service.services]
}

resource "google_bigquery_dataset" "feedback_dataset" {
  project       = var.dev_project_id
  dataset_id    = var.feedback_bigquery_dataset_id
  friendly_name = var.feedback_bigquery_dataset_id
  location      = var.region
  depends_on    = [resource.google_project_service.services]
}

module "feedback_export_to_bigquery" {
  source                 = "terraform-google-modules/log-export/google"
  version                = "10.0.0"
  log_sink_name          = var.feedback_sink_name
  parent_resource_type   = "project"
  parent_resource_id     = var.dev_project_id
  destination_uri        = "bigquery.googleapis.com/projects/${var.dev_project_id}/datasets/${var.feedback_bigquery_dataset_id}"
  filter                 = var.feedback_logs_filter
  bigquery_options       = { use_partitioned_tables = true }
  unique_writer_identity = true
  depends_on             = [resource.google_project_service.services]

}

resource "google_bigquery_dataset" "telemetry_logs_dataset" {
  project       = var.dev_project_id
  dataset_id    = var.telemetry_bigquery_dataset_id
  friendly_name = var.telemetry_bigquery_dataset_id
  location      = var.region
  depends_on    = [resource.google_project_service.services]
}