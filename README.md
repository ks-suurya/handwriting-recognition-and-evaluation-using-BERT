# Handwriting Recognition and Evaluation API

This project is the **production-ready, service-oriented version** of the original proof-of-concept: *Handwritten Text Detection and Answer Evaluation using BERT*.  

It transforms the initial Jupyter Notebook scripts into a **scalable, robust backend service** designed to be deployed in the cloud and consumed by a modern frontend application.

---

## Project Status: Under Development
This application is currently under active development.  
The core functionalities are being **refactored into a scalable architecture**, but it is not yet ready for a full production deployment.  
The **API endpoints and database models are subject to change.**

---

## Core Features

This service provides an **end-to-end pipeline** for evaluating handwritten answer scripts:

- **Handwriting Recognition (OCR):**  
  Utilizes an advanced HTR (Handwriting Text Recognition) pipeline to detect and transcribe text from uploaded images.

- **AI-Powered Text Correction:**  
  Leverages the **Gemini Pro model** to correct common OCR errors and improve the accuracy of the transcribed text.

- **Semantic Answer Evaluation:**  
  Uses a **BERT model** to perform a semantic comparison between the student's transcribed answer and the teacher's model answer, providing a similarity score.

- **Automated Scoring:**  
  Calculates a **final score** for each question based on semantic similarity, answer length, and allotted marks.

---

## Technology Stack

This project is built with a **modern, scalable backend architecture**:

- **Backend Framework:** Flask  
- **Database:** MySQL (for structured data) & Redis (for caching and task queuing)  
- **ORM:** SQLAlchemy with Flask-Migrate for schema management  
- **Asynchronous Tasks:** Celery with a Redis broker to handle long-running OCR and evaluation tasks in the background  
- **Cloud Storage:** Amazon S3 for storing all images and result files  
- **Containerization:** Docker & Docker Compose for a consistent development and production environment  
- **Planned Deployment:** AWS ECS (Elastic Container Service)  
- **Planned Frontend:** React  

---

## Local Development Setup

To run this project locally, you will need **Docker** and **Docker Compose** installed.

### 1. Clone the Repository
```bash
git clone <your_repository_url>
cd handwriting-recognition-and-evaluation-using-BERT
```

### 2. Configure Environment Variables
Create a `.env` file in the project root by copying the example:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in your specific credentials:

- `GEMINI_API_KEY`  
- `AWS_ACCESS_KEY_ID`  
- `AWS_SECRET_ACCESS_KEY`  
- `AWS_REGION`  
- `S3_BUCKET_NAME`  

The database and Celery URLs are pre-configured for the Docker environment and do not need to be changed for local development.

### 3. Initialize the Database
The database migration commands need to be run from within the Docker container after it's running.

First, start all the services in detached mode:
```bash
docker-compose up --build -d
```

Next, execute the database migration commands inside the web container:

```bash
# Initialize the migrations folder (only run this once ever)
docker-compose exec web flask db init

# Create the initial migration script
docker-compose exec web flask db migrate -m "Initial database schema"

# Apply the migration to create the tables in the database
docker-compose exec web flask db upgrade
```

### 4. Run the Application
Your application stack should now be running.  

- Flask API: [http://localhost:5000](http://localhost:5000)  
- View real-time logs:
  ```bash
  docker-compose logs -f
  ```
- Stop the application:
  ```bash
  docker-compose down
  ```

---

## Future Roadmap

- Finalize all API endpoints for **Students, Categories, and Submissions**.  
- Build a comprehensive **React-based frontend** for the teacher interface.  
- Implement **user authentication and authorization**.  
- Write comprehensive **unit and integration tests**.  
- Create a **CI/CD pipeline** for automated deployment to AWS ECS.  
- Add detailed **API documentation** (e.g., using Swagger/OpenAPI).  

---
