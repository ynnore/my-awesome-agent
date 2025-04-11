# Data Ingestion Pipeline

This pipeline automates the ingestion of data into Vertex AI Search, streamlining the process of building Retrieval Augmented Generation (RAG) applications. 

It orchestrates the complete workflow: loading data, chunking it into manageable segments, generating embeddings using Vertex AI Embeddings, and importing the processed data into your Vertex AI Search datastore.

You can trigger the pipeline for an initial data load or schedule it to run periodically, ensuring your search index remains current. Vertex AI Pipelines provides the orchestration and monitoring capabilities for this process.

## Prerequisites

Before running the data ingestion pipeline, ensure you have completed the following:

1. **Set up Dev Terraform:** Follow the instructions in the parent [deployment/README.md - Dev Deployment section](../deployment/README.md#dev-deployment) to provision the necessary resources in your development environment using Terraform. This includes deploying a datastore and configuring the required permissions.

## Running the Data Ingestion Pipeline

After setting up the Terraform infrastructure, you can test the data ingestion pipeline.

> **Note:** The initial pipeline execution might take longer as your project is configured for Vertex AI Pipelines.

**Steps:**

**a. Navigate to the `data_ingestion` directory:**

```bash
cd data_ingestion
```

**b. Install Dependencies:**

Install the required Python dependencies using uv:

```bash
uv sync --frozen
```

**c. Execute the Pipeline:**

Run the following command to execute the data ingestion pipeline. Replace the placeholder values with your actual project details.

```bash
PROJECT_ID="YOUR_PROJECT_ID"
REGION="us-central1"
DATA_STORE_REGION="us"
uv run data_ingestion_pipeline/submit_pipeline.py \
    --project-id=$PROJECT_ID \
    --region=$REGION \
    --data-store-region=$DATA_STORE_REGION \
    --data-store-id="sample-datastore" \
    --service-account="vertexai-pipelines-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --pipeline-root="gs://$PROJECT_ID-pipeline-artifacts" \
    --pipeline-name="data-ingestion-pipeline"
```

**Parameter Explanation:**

*   `--project-id`: Your Google Cloud project ID.
*   `--region`: The region where Vertex AI Pipelines will run (e.g., `us-central1`).
*   `--data-store-region`: The region for Vertex AI Search operations (e.g., `us` or `eu`).
*   `--data-store-id`: The ID of your Vertex AI Search datastore.
*   `--service-account`: The service account email used for pipeline execution.  Ensure this service account has the necessary permissions (e.g., Vertex AI User, Storage Object Admin).
*   `--pipeline-root`: The Google Cloud Storage (GCS) bucket for storing pipeline artifacts.
*   `--pipeline-name`: A descriptive name for your pipeline.
*   `--schedule-only` (Optional): If specified, the pipeline will only be scheduled and not executed immediately. Requires `--cron-schedule`.
*   `--cron-schedule` (Optional): A cron expression defining the pipeline's schedule (e.g., `"0 9 * * 1"` for every Monday at 9:00 AM UTC).

**d. Pipeline Scheduling and Execution:**

The pipeline, by default, executes immediately. To schedule the pipeline for periodic execution without immediate initiation, use the `--schedule-only` flag in conjunction with `--cron-schedule`. If a schedule doesn't exist, it will be created. If a schedule already exists, its cron expression will be updated to the provided value.

**e. Monitoring Pipeline Progress:**

The pipeline's configuration and execution status will be printed to the console. For detailed monitoring, use the Vertex AI Pipelines dashboard in the Google Cloud Console. This dashboard provides real-time insights into the pipeline's progress, logs, and any potential issues.

## Testing Your RAG Application

Once the data ingestion pipeline completes successfully, you can test your RAG application with Vertex AI Search.

> **Troubleshooting:** If you encounter the error `"google.api_core.exceptions.InvalidArgument: 400 The embedding field path: embedding not found in schema"` after the initial data ingestion, wait a few minutes and try again. This delay allows Vertex AI Search to fully index the ingested data.
