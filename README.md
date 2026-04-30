# Yelp Prototype - Lab 2
## Distributed Microservices with Docker, Kubernetes, Kafka, and AWS

**Course:** DATA 236 - Distributed Systems for Data Engineering  
**Lab:** Lab 2  
**Team:** Akash Kumar & Utkarsh Sharma  
**Due:** April 28, 2026

---

## 🌐 Live Application

**EKS Deployment:** http://abfa94f4cef484b41b5e734bdf375cf1-851799338.us-east-2.elb.amazonaws.com

---

## 📋 Lab 2 Requirements Completed

- ✅ **Part 1**: Docker & Kubernetes Setup (15 pts)
- ✅ **Part 2**: Kafka for Asynchronous Messaging (10 pts)
- ✅ **Part 3**: MongoDB Database (5 pts)
- ✅ **Part 4**: Redux Integration (5 pts)
- ✅ **Part 5**: JMeter Performance Testing (5 pts)

---

## 🏗️ Architecture Overview

### Producer → Kafka → Consumer Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Frontend (React + Redux)                  │
│                      Port: 80 (nginx)                      │
└──────┬───────────┬───────────┬───────────┬────────────────┘
       │           │           │           │
┌──────▼─────┐ ┌───▼──────┐ ┌──▼──────┐ ┌─▼────────┐ ┌──────────┐
│  User API  │ │Restaurant│ │Review   │ │Owner API │ │ Backend  │
│ (Producer) │ │API       │ │API      │ │(Producer)│ │(AI/Admin)│
│ Port: 8001 │ │(Producer)│ │(Producer│ │Port: 8004│ │Port: 8000│
│            │ │Port: 8002│ │Port:8003│ │          │ │          │
└──────┬─────┘ └───┬──────┘ └──┬──────┘ └──────────┘ └──────────┘
       │           │           │
       └───────────┼───────────┘
                   │ publish events
                   ▼
     ┌─────────────────────────────────┐
     │           Kafka API             │
     │─────────────────────────────────│
     │  Topic: review.created          │
     │  Topic: review.updated          │
     │  Topic: review.deleted          │
     │  Topic: restaurant.created      │
     │  Topic: restaurant.updated      │
     │  Topic: restaurant.claimed      │
     │  Topic: user.created            │
     │  Topic: user.updated            │
     │  Topic: user.login              │
     └─────────────────────────────────┘
                   │ consume events
       ┌───────────┼───────────┐
       │           │           │
┌──────▼─────┐ ┌───▼──────┐ ┌──▼──────┐
│User Worker │ │Restaurant│ │Review   │
│ (Consumer) │ │Worker    │ │Worker   │
│            │ │(Consumer)│ │(Consumer│
└──────┬─────┘ └───┬──────┘ └──┬──────┘
       │           │           │
       └───────────┼───────────┘
                   │
      ┌────────────▼────────────┐
      │      MongoDB Atlas      │
      │    (Cloud Database)     │
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │        AWS S3           │
      │  bucket: yelp-lab2-photos│
      └─────────────────────────┘
```

### Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `user.created` | User API | User Worker | New user registration |
| `user.updated` | User API | User Worker | Profile updates |
| `user.login` | User API | User Worker | Login events |
| `restaurant.created` | Restaurant API | Restaurant Worker | New restaurants |
| `restaurant.updated` | Restaurant API | Restaurant Worker | Restaurant updates |
| `restaurant.claimed` | Restaurant API | Restaurant Worker | Owner claims |
| `review.created` | Review API | Review Worker | New reviews → updates rating |
| `review.updated` | Review API | Review Worker | Review edits → updates rating |
| `review.deleted` | Review API | Review Worker | Review deletions → updates rating |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- kubectl (Kubernetes CLI)
- eksctl (for AWS EKS)
- AWS CLI configured
- MongoDB Atlas account
- Node.js 18+
- Python 3.9+

### 1. Local Development with Docker Compose

```bash
# Clone the repository
git clone https://github.com/Utkarshs9924/yelp-prototype.git
cd yelp-prototype

# Create .env file with required variables (see Environment Variables section)

# Start all services
docker-compose up --build

# Services available at:
# Frontend:        http://localhost:80
# User API:        http://localhost:8001
# Restaurant API:  http://localhost:8002
# Review API:      http://localhost:8003
# Owner API:       http://localhost:8004
# Backend:         http://localhost:8000
# Kafka:           localhost:29092
```

### 2. AWS EKS Deployment

```bash
# Install eksctl
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create EKS cluster (t3.medium nodes required)
eksctl create cluster \
  --name yelp-lab2-new \
  --region us-east-2 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed

# Configure kubectl
aws eks update-kubeconfig --region us-east-2 --name yelp-lab2-new

# Create ECR repositories
aws ecr create-repository --repository-name yelp-frontend --region us-east-2
aws ecr create-repository --repository-name yelp-backend --region us-east-2
aws ecr create-repository --repository-name yelp-user-api --region us-east-2
aws ecr create-repository --repository-name yelp-restaurant-api --region us-east-2
aws ecr create-repository --repository-name yelp-review-api --region us-east-2
aws ecr create-repository --repository-name yelp-owner-api --region us-east-2
aws ecr create-repository --repository-name yelp-user-worker --region us-east-2
aws ecr create-repository --repository-name yelp-restaurant-worker --region us-east-2
aws ecr create-repository --repository-name yelp-review-worker --region us-east-2
aws ecr create-repository --repository-name yelp-kafka --region us-east-2
aws ecr create-repository --repository-name yelp-zookeeper --region us-east-2

# Login to ECR and push images
ECR=425449348496.dkr.ecr.us-east-2.amazonaws.com
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ECR

docker compose build
docker tag yelp-prototype-frontend:latest $ECR/yelp-frontend:latest
docker tag yelp-prototype-backend:latest $ECR/yelp-backend:latest
docker tag yelp-prototype-user-api:latest $ECR/yelp-user-api:latest
docker tag yelp-prototype-restaurant-api:latest $ECR/yelp-restaurant-api:latest
docker tag yelp-prototype-review-api:latest $ECR/yelp-review-api:latest
docker tag yelp-prototype-owner-api:latest $ECR/yelp-owner-api:latest
docker tag yelp-prototype-user-worker:latest $ECR/yelp-user-worker:latest
docker tag yelp-prototype-restaurant-worker:latest $ECR/yelp-restaurant-worker:latest
docker tag yelp-prototype-review-worker:latest $ECR/yelp-review-worker:latest

docker push $ECR/yelp-frontend:latest
docker push $ECR/yelp-backend:latest
docker push $ECR/yelp-user-api:latest
docker push $ECR/yelp-restaurant-api:latest
docker push $ECR/yelp-review-api:latest
docker push $ECR/yelp-owner-api:latest
docker push $ECR/yelp-user-worker:latest
docker push $ECR/yelp-restaurant-worker:latest
docker push $ECR/yelp-review-worker:latest

# Deploy to Kubernetes
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/zookeeper.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/user-api.yaml
kubectl apply -f k8s/restaurant-api.yaml
kubectl apply -f k8s/review-api.yaml
kubectl apply -f k8s/owner-api.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/user-worker.yaml
kubectl apply -f k8s/restaurant-worker.yaml
kubectl apply -f k8s/review-worker.yaml

# Get frontend URL
kubectl get services | grep frontend
```

---

## 📦 Services

### API Services (Producers)

#### User API Service
- **Port**: 8001
- **Endpoints**: `/signup`, `/login`, `/users/{id}`, `/users/upload-picture`
- **Produces to**: `user.created`, `user.updated`, `user.login`

#### Restaurant API Service
- **Port**: 8002
- **Endpoints**: `/restaurants`, `/restaurants/{id}`, `/restaurants/search`, `/favorites`, `/preferences`, `/history`
- **Produces to**: `restaurant.created`, `restaurant.updated`, `restaurant.claimed`

#### Review API Service
- **Port**: 8003
- **Endpoints**: `/reviews`, `/reviews/upload-photo`, `/restaurants/{id}/reviews`
- **Produces to**: `review.created`, `review.updated`, `review.deleted`

#### Owner API Service
- **Port**: 8004
- **Endpoints**: `/owner/dashboard`, `/owner/restaurants`

#### Backend (AI + Admin)
- **Port**: 8000
- **Endpoints**: `/chat`, `/admin`
- **Features**: AI chatbot (Groq + LangChain + Tavily), admin panel

### Worker Services (Consumers)

#### User Worker
- **Consumes**: `user.created`, `user.updated`, `user.login`
- **Actions**: Log events, update analytics

#### Restaurant Worker
- **Consumes**: `restaurant.created`, `restaurant.updated`, `restaurant.claimed`
- **Actions**: Update metadata, sync search index

#### Review Worker
- **Consumes**: `review.created`, `review.updated`, `review.deleted`
- **Actions**: Recalculate restaurant average rating and review count in MongoDB

---

## 🗄️ MongoDB Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  name: String,
  email: String,
  password_hash: String,      // bcrypt encrypted
  role: String,               // "user", "owner", "admin"
  phone: String,
  city: String,
  country: String,
  profile_picture: String,    // S3 URL
  created_at: Date
}
```

### Restaurants Collection
```javascript
{
  _id: ObjectId,
  name: String,
  cuisine_type: String,
  description: String,
  address: String,
  city: String,
  state: String,
  phone: String,
  pricing_tier: String,       // "1"-"4" ($-$$$$)
  average_rating: Number,     // Updated by Review Worker via Kafka
  review_count: Number,       // Updated by Review Worker via Kafka
  owner_id: String,
  menu_items: Array,
  amenities: String,
  ambiance: String,
  hours_of_operation: String,
  created_at: Date
}
```

### Reviews Collection
```javascript
{
  _id: ObjectId,
  restaurant_id: String,
  user_id: String,
  rating: Number,             // 1-5
  comment: String,
  photo_url: String,          // S3 URL (optional)
  created_at: Date,
  updated_at: Date
}
```

### Photos Collection
```javascript
{
  _id: ObjectId,
  restaurant_id: String,
  user_id: String,
  photo_url: String,
  caption: String,
  created_at: Date
}
```

### Favorites Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  restaurant_id: String,
  created_at: Date
}
```

### Preferences Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  cuisine_preferences: Array,
  price_range: String,
  dietary_needs: Array,
  ambiance_preferences: Array,
  sort_preference: String,
  updated_at: Date
}
```

---

## 🔴 Redux State Management

### Store Structure

```javascript
{
  auth: {
    token: String,
    user: Object,
    isAuthenticated: Boolean,
    loading: Boolean,
    error: String
  },
  restaurants: {
    list: Array,
    total: Number,
    totalPages: Number,
    page: Number,
    searching: Boolean,
    error: String
  },
  reviews: {
    list: Array,
    loading: Boolean,
    error: String
  },
  favorites: {
    list: Array,
    favoriteIds: Array,
    loading: Boolean
  }
}
```

### Key Features
- ✅ JWT token management with localStorage persistence
- ✅ Async thunks for all API calls
- ✅ Restaurant search and pagination state
- ✅ Optimistic UI updates for favorites
- ✅ Error handling across all slices

---

## 📊 Performance Testing

### JMeter Test Suite

Located in `/jmeter-tests/`:

- `yelp_lab2_test.jmx` - Main test plan
- `yelp_performance_test.jmx` - Performance test
- `yelp_test_plan.jmx` - Full test plan
- `test-data.csv` - Test data

### APIs Tested
1. **User Authentication** - POST `/api/login`
2. **Restaurant Search** - GET `/api/restaurants/search`
3. **Review Submission** - POST `/api/reviews` (triggers Kafka flow)

### Running Tests

```bash
# Install JMeter: https://jmeter.apache.org/download_jmeter.cgi
cd jmeter-tests
jmeter -n -t yelp_lab2_test.jmx -l results.jtl -e -o results/
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - REST API framework
- **Apache Kafka** - Asynchronous message queue
- **MongoDB Atlas** - NoSQL cloud database
- **PyJWT** - JWT authentication
- **bcrypt** - Password hashing
- **boto3** - AWS S3 integration
- **LangChain + Groq** - AI chatbot (llama-3.1-8b-instant)
- **Tavily** - Real-time web search for AI

### Frontend
- **React 19** - UI framework
- **Redux Toolkit** - State management
- **TailwindCSS** - Styling
- **Vite** - Build tool
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Kubernetes (EKS)** - Container orchestration
- **AWS EKS** - Managed Kubernetes (us-east-2, t3.medium nodes)
- **AWS ECR** - Container registry (account: 425449348496)
- **AWS S3** - Photo storage (bucket: yelp-lab2-photos, us-east-2)
- **MongoDB Atlas** - Managed database (yelp_db)

---

## 📁 Project Structure

```
yelp-prototype/
├── common/                     # Shared libraries
│   ├── database/               # MongoDB connection helpers
│   ├── kafka/                  # Kafka producer/consumer base classes
│   └── utils/                  # S3 storage utilities
├── services/                   # Microservices
│   ├── user-api/
│   ├── user-worker/
│   ├── restaurant-api/
│   ├── restaurant-worker/
│   ├── review-api/
│   ├── review-worker/
│   └── owner-api/
├── backend/                    # Monolith (AI chat, admin)
│   ├── routes/
│   │   ├── chat.py
│   │   └── admin.py
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── redux/slices/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/api.js
│   ├── Dockerfile
│   └── nginx.conf
├── k8s/                        # Kubernetes manifests
├── jmeter-tests/               # JMeter performance tests
├── docker-compose.yml
└── README.md
```

---

## 🔐 Environment Variables

```bash
MONGO_URI=mongodb+srv://...
DB_NAME=yelp_db
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
JWT_SECRET=your_jwt_secret
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=yelp-lab2-photos
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

---

## 🐛 Troubleshooting

### Kafka Connection Issues
```bash
# Docker Compose
docker-compose logs kafka

# EKS
kubectl logs -l app=kafka --tail 50
```

### Pod Not Starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
```

### ECR Pull Issues
```bash
aws ecr get-login-password --region us-east-2 | \
  docker login --username AWS --password-stdin \
  425449348496.dkr.ecr.us-east-2.amazonaws.com
```

---

## 👥 Team Contributions

**Utkarsh Sharma:**
- Kafka producer/consumer implementation (P7)
- MongoDB migration and schema design
- Docker & Kubernetes configuration
- AWS EKS deployment
- Review worker rating recalculation
- AI chatbot (Groq + LangChain + Tavily)
- JMeter performance testing

**Akash Kumar:**
- Redux state management
- Frontend UI/UX
- S3 photo integration
- Restaurant data migration
- Lab 1 backend foundation

---

## 🔗 Links

- **GitHub**: https://github.com/Utkarshs9924/yelp-prototype
- **Live App (EKS)**: http://abfa94f4cef484b41b5e734bdf375cf1-851799338.us-east-2.elb.amazonaws.com

---

**Last Updated**: April 30, 2026
