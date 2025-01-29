# **MLB Sluggers Backend Services 🏆⚾**
This repository contains the backend services for **MLB Sluggers**, handling **game highlights processing**, **AI content generation**, and **Pub/Sub event-driven workflows** using **Google Cloud Functions (2nd Gen)**.

## **🚀 Services Overview**
### **1️⃣ Flask API (`/api`)**
A RESTful Flask API for serving highlights and processing game data.

### **2️⃣ Cloud Functions**
- **`process-game-status-event`**: Listens for game status updates via Pub/Sub and triggers AI processing when a game reaches `Final`.
- **`ai-processing-service`**: Handles AI-powered content generation for highlights.

## **📂 Directory Structure**
```
/backend
│── /api                          # Flask API Directory
│   ├── main.py                   # Flask API Entry Point
│   ├── requirements.txt           # Flask API Dependencies
│   ├── Dockerfile                 # (If using Docker for App Engine)
│
│── /cloud-functions               # Cloud Functions Directory
│   ├── /process-game-status-event # Cloud Function 1 Directory
│   │   ├── main.py                # Function for processing game status updates
│   │   ├── requirements.txt       # Dependencies
│   │
│   ├── /ai-processing-service     # Cloud Function 2 Directory
│   │   ├── main.py                # Function for AI-powered content generation
│   │   ├── requirements.txt       # Dependencies
│
│── README.md                      # Project Documentation
│── .gitignore                      # Ignore unnecessary files
```

## **🌎 Environment Setup**
### **1️⃣ Prerequisites**
- Install **Google Cloud SDK**: [Install Guide](https://cloud.google.com/sdk/docs/install)
- Enable APIs in Google Cloud:
  ```sh
  gcloud services enable cloudfunctions.googleapis.com \
    pubsub.googleapis.com \
    firestore.googleapis.com \
    artifactregistry.googleapis.com
  ```
- Authenticate with Google Cloud:
  ```sh
  gcloud auth application-default login
  ```

### **2️⃣ Setting Up Local Development**
1. **Clone the repository**  
   ```sh
   git clone https://github.com/your-repo/mlb-sluggers-backend.git
   cd mlb-sluggers-backend/backend
   ```
2. **Setup Flask API**  
   ```sh
   cd api
   pip install -r requirements.txt
   python main.py
   ```

## **🚀 Deploying Services**
### **1️⃣ Deploy Flask API**
- **Build & Push Docker Image**
  ```sh
  gcloud builds submit --tag gcr.io/slimeify/mlb-sluggers-api
  ```
- **Deploy to Cloud Run**
  ```sh
  gcloud run deploy mlb-sluggers-api \
    --image gcr.io/slimeify/mlb-sluggers-api \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated
  ```

### **2️⃣ Deploy Cloud Functions**
#### **🚀 Deploy `process-game-status-event`**
```sh
gcloud functions deploy process-game-status-event \
  --gen2 \
  --runtime python39 \
  --region us-central1 \
  --trigger-topic sluggers-process-game-status \
  --source=cloud-functions/process-game-status-event \
  --entry-point=process_game_status_event \
  --memory=256MB \
  --timeout=300s
```

#### **🚀 Deploy `ai-processing-service`**
```sh
gcloud functions deploy ai-processing-service \
  --gen2 \
  --runtime python39 \
  --region us-central1 \
  --trigger-topic sluggers-ai-processing \
  --source=cloud-functions/ai-processing-service \
  --entry-point=ai_processing_service \
  --memory=256MB \
  --timeout=300s
```

## **🔍 Monitoring & Debugging**
### **1️⃣ Check Running Functions**
```sh
gcloud functions list
```
### **2️⃣ Check Function Logs**
```sh
gcloud functions logs read process-game-status-event --limit 50
```
```sh
gcloud functions logs read ai-processing-service --limit 50
```

### **3️⃣ View Logs in Google Cloud Console**
- [**Logs Viewer**](https://console.cloud.google.com/logs/viewer?project=slimeify&resource=cloud_function&minLogLevel=0)
- [**Cloud Run Services**](https://console.cloud.google.com/run)

## **📌 Pub/Sub Topics**
| **Topic Name**                 | **Trigger**                                      |
|---------------------------------|-------------------------------------------------|
| `sluggers-process-game-status`  | Triggers `process-game-status-event` function  |
| `sluggers-ai-processing`        | Triggers `ai-processing-service` function      |

## **🛠️ Managing Cloud Functions**
### **🛑 Deleting a Function**
```sh
gcloud functions delete process-game-status-event --region us-central1
```
```sh
gcloud functions delete ai-processing-service --region us-central1
```

### **🛑 Deleting Cloud Run API**
```sh
gcloud run services delete mlb-sluggers-api --region us-central1
```

## **⚙️ Automating Deployment with GitHub Actions**
To automate deployments:
1. **Set up Google Cloud authentication in GitHub Actions**  
   - Store `GOOGLE_APPLICATION_CREDENTIALS` in GitHub Secrets.
2. **Create a GitHub Actions Workflow (`.github/workflows/deploy.yml`)**
```yaml
name: Deploy Cloud Functions

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Authenticate with Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}

      - name: Deploy `process-game-status-event`
        run: |
          gcloud functions deploy process-game-status-event \
            --gen2 \
            --runtime python39 \
            --region us-central1 \
            --trigger-topic sluggers-process-game-status \
            --source=cloud-functions/process-game-status-event \
            --entry-point=process_game_status_event \
            --memory=256MB \
            --timeout=300s

      - name: Deploy `ai-processing-service`
        run: |
          gcloud functions deploy ai-processing-service \
            --gen2 \
            --runtime python39 \
            --region us-central1 \
            --trigger-topic sluggers-ai-processing \
            --source=cloud-functions/ai-processing-service \
            --entry-point=ai_processing_service \
            --memory=256MB \
            --timeout=300s
```

## **📜 License**
MIT License.

## **📞 Support**
For questions, contact **[Your Name]** at **your-email@example.com**.
