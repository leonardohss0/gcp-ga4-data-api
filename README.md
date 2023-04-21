# Google Analytics 4 API Data Extraction and Processing in Batch.
Keywords: Python, AWS, GCP, Google Cloud, AWS S3, Data Lake, AWS RDS, ETL, Postgresql, Docker, Github Actions, AWS ECS, AWS ECR.


### Description:
This project aims to extract data from Google Analytics 4 API and process it to store it in AWS S3 and RDS database. To deploy the project into production, AWS ECS was used.

## Setup
1. Create a project in Google Cloud Console and activate the Google Analytics 4 API.

2. Create a service account in Google Cloud Console and download the JSON key file.

3. Set up your environment variables in the .env file using the .env.example file as a template.

4. Install the required Python packages by running the following command in the terminal: `pip install -r requirements.txt`

## Folder Structure
The project follows the following folder structure:
 
gcp-ga4-data-api/ <br>
├── analytics_flow/ <br>
│ ├── resources/ <br>
│ ├── secrets/ <br>
│ └── utils/ <br>
├── db/ <br>
├── .dockerignore <br>
├── Dockerfile<br>
├── ecs-task-definition.json<br>
├── requirements.txt<br>
└── README.md<br>

## Data Extraction
To extract data from the Google Analytics 4 API, the analytics_utils.py file contains a getReport() function that retrieves the specified metrics and dimensions for a given date range.

The app.py file is responsible for calling the getReport() function and pushing the raw data to AWS S3.

## Data Processing
After the raw data is pushed to AWS S3, it is then processed using the data_processing.py file. This file transforms the data and prepares it to be stored in AWS RDS database.

The processed data is then pushed to AWS S3 and AWS RDS using the push_to_s3.py and push_to_rds.py files respectively.

## Deployment
This project uses Github Actions for deployment. The .github/workflows/aws.yml file contains the steps required to deploy the project.

The deployment workflow involves building a Docker image of the project, pushing the image to AWS ECR, and deploying the image to AWS ECS.

To deploy the project, you will need to set up your AWS credentials and environment variables in Github Secrets.

## Conclusion
This project provides a simple way to extract data from the Google Analytics 4 API, process it, and store it in AWS S3 and RDS database. By automating the deployment process using Github Actions, the project can be deployed easily and efficiently.
