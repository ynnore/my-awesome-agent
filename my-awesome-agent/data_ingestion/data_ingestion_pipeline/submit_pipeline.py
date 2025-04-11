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

import argparse
import logging
import os
import sys

from data_ingestion_pipeline.pipeline import pipeline
from google.cloud import aiplatform
from kfp import compiler

PIPELINE_FILE_NAME = "data_processing_pipeline.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for pipeline configuration."""

    parser = argparse.ArgumentParser(description="Pipeline configuration")
    parser.add_argument(
        "--project-id", default=os.getenv("PROJECT_ID"), help="GCP Project ID"
    )
    parser.add_argument(
        "--region", default=os.getenv("REGION"), help="Vertex AI Pipelines region"
    )
    parser.add_argument(
        "--data-store-region",
        default=os.getenv("DATA_STORE_REGION"),
        help="Data Store region",
    )
    parser.add_argument(
        "--data-store-id", default=os.getenv("DATA_STORE_ID"), help="Data store ID"
    )
    parser.add_argument(
        "--service-account",
        default=os.getenv("SERVICE_ACCOUNT"),
        help="Service account",
    )
    parser.add_argument(
        "--pipeline-root",
        default=os.getenv("PIPELINE_ROOT"),
        help="Pipeline root directory",
    )
    parser.add_argument(
        "--pipeline-name", default=os.getenv("PIPELINE_NAME"), help="Pipeline name"
    )
    parser.add_argument(
        "--disable-caching",
        type=bool,
        default=os.getenv("DISABLE_CACHING", "false").lower() == "true",
        help="Enable pipeline caching",
    )
    parser.add_argument(
        "--cron-schedule",
        default=os.getenv("CRON_SCHEDULE", None),
        help="Cron schedule",
    )
    parser.add_argument(
        "--schedule-only",
        type=bool,
        default=os.getenv("SCHEDULE_ONLY", "false").lower() == "true",
        help="Schedule only (do not submit)",
    )
    parsed_args = parser.parse_args()

    # Validate required parameters
    missing_params = []
    required_params = {
        "project_id": parsed_args.project_id,
        "region": parsed_args.region,
        "data_store_region": parsed_args.data_store_region,
        "data_store_id": parsed_args.data_store_id,
        "service_account": parsed_args.service_account,
        "pipeline_root": parsed_args.pipeline_root,
        "pipeline_name": parsed_args.pipeline_name,
    }

    for param_name, param_value in required_params.items():
        if param_value is None:
            missing_params.append(param_name)

    if missing_params:
        logging.error("Error: The following required parameters are missing:")
        for param in missing_params:
            logging.error(f"  - {param}")
        logging.error(
            "\nPlease provide these parameters either through environment variables or command line arguments."
        )
        sys.exit(1)

    return parsed_args


if __name__ == "__main__":
    args = parse_args()

    if args.schedule_only and not args.cron_schedule:
        logging.error("Missing --cron-schedule argument for scheduling")
        sys.exit(1)

    # Print configuration
    logging.info("\nConfiguration:")
    logging.info("--------------")
    logging.info(f"project_id: {args.project_id}")
    logging.info(f"region: {args.region}")
    logging.info(f"region_data_store: {args.data_store_region}")
    logging.info(f"data_store_id: {args.data_store_id}")
    logging.info(f"service_account: {args.service_account}")
    logging.info(f"pipeline_root: {args.pipeline_root}")
    logging.info(f"cron_schedule: {args.cron_schedule}")
    logging.info(f"pipeline_name: {args.pipeline_name}")
    logging.info(f"disable_caching: {args.disable_caching}")
    logging.info(f"schedule_only: {args.schedule_only}")
    logging.info("--------------\n")

    compiler.Compiler().compile(pipeline_func=pipeline, package_path=PIPELINE_FILE_NAME)
    # Create common pipeline job parameters
    pipeline_job_params = {
        "display_name": args.pipeline_name,
        "template_path": PIPELINE_FILE_NAME,
        "pipeline_root": args.pipeline_root,
        "project": args.project_id,
        "enable_caching": (not args.disable_caching),
        "location": args.region,
        "parameter_values": {
            "project_id": args.project_id,
            "location": args.region,
            "data_store_region": args.data_store_region,
            "data_store_id": args.data_store_id,
        },
    }

    # Create pipeline job instance
    job = aiplatform.PipelineJob(**pipeline_job_params)

    if not args.schedule_only:
        logging.info("Running pipeline and waiting for completion...")
        job.submit(service_account=args.service_account)
        job.wait()
        logging.info("Pipeline completed!")

    if args.cron_schedule and args.schedule_only:
        # No need to create new job instance since we already have one with the same params
        pipeline_job_schedule = aiplatform.PipelineJobSchedule(
            pipeline_job=job,
            display_name=f"{args.pipeline_name} Weekly Ingestion Job",
        )

        schedule_list = pipeline_job_schedule.list(
            filter=f'display_name="{args.pipeline_name} Weekly Ingestion Job"',
            project=args.project_id,
            location=args.region,
        )
        logging.info("Schedule lists found: %s", schedule_list)
        if not schedule_list:
            pipeline_job_schedule.create(
                cron=args.cron_schedule, service_account=args.service_account
            )
            logging.info("Schedule created")
        else:
            schedule_list[0].update(cron=args.cron_schedule)
            logging.info("Schedule updated")

    # Clean up pipeline file
    if os.path.exists(PIPELINE_FILE_NAME):
        os.remove(PIPELINE_FILE_NAME)
        logging.info(f"Deleted {PIPELINE_FILE_NAME}")
