# URL Shortener with Click Analytics

A simple URL shortener service that generates short links and tracks click counts in real time.  
Built with **Django** (backend) and **React** (frontend), integrated with **Firebase Auth** and **Google Cloud Platform** for analytics.

## Features
- Generate short URLs from long links
- Track and display click counts
- Firebase authentication for secure access
- Real-time click tracking via **Pub/Sub → BigQuery**
- Backend API returns analytics to frontend for visualization

## Tech Stack
- **Backend:** Django, Google Cloud Pub/Sub, BigQuery
- **Frontend:** React
- **Authentication:** Firebase Auth
- **Cloud:** Google Cloud Platform (GCP)

## Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/url-shortener.git
   cd url-shortener
cd backend
pip install -r requirements.txt
# Set environment variables for Firebase and GCP
python manage.py runserver

