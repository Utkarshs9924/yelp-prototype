# Yelp Prototype - Lab 2
## Distributed Microservices with Docker, Kubernetes, Kafka, and AWS

**Course:** DATA 236 - Distributed Systems for Data Engineering  
**Lab:** Lab 2  
**Team:** Akash Kumar & Utkarsh Sharma  
**Due:** April 28, 2026

---

## 📋 Lab 2 Requirements Completed

- ✅ **Part 1**: Docker & Kubernetes Setup (15 pts)
- ✅ **Part 2**: Kafka for Asynchronous Messaging (10 pts)
- ✅ **Part 3**: MongoDB Database (5 pts)
- ✅ **Part 4**: Redux Integration (5 pts)
- ✅ **Part 5**: JMeter Performance Testing (5 pts)

---

## 🏗️ Architecture Overview

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend (React + Redux)                   │
│                         Port: 80 (nginx)                             │
└────────────────┬────────────────┬────────────────┬───────────────────┘
                 │                │                │
        ┌────────▼────────┐ ┌────▼──────────┐ ┌──▼────────────────┐
        │   User API      │ │ Restaurant API│ │   Review API      │
        │   (Producer)    │ │  (Producer)   │ │  (Producer)       │
        │   Port: 8001    │ │  Port: 8002   │ │  Port: 8003       │
        └────────┬────────┘ └────┬──────────┘ └──┬────────────────┘
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Kafka Message Queue    │
                    │   (Zookeeper + Kafka)      │
                    │     Port: 9092             │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
        ┌────────▼────────┐ ┌────▼──────────┐ ┌──▼────────────────┐
        │  User Worker    │ │Restaurant      │ │  Review Worker    │
        │  (Consumer)     │ │Worker          │ │  (Consumer)       │
        │                 │ │(Consumer)      │ │                   │
        └────────┬────────┘ └────┬──────────┘ └──┬────────────────┘
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    MongoDB Atlas          │
                    │    (Cloud Database)       │
                    └───────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    AWS S3                 │
                    │    (Photo Storage)        │
                    └───────────────────────────┘
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
| `review.created` | Review API | Review Worker | New reviews |
| `review.updated` | Review API | Review Worker | Review edits |
| `review.deleted` | Review API | Review Worker | Review deletions |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- kubectl (Kubernetes CLI)
- eksctl (for AWS EKS)
- AWS CLI configured
- MongoDB Atlas account
- Node.js 18+ (for local frontend development)
- Python 3.9+ (for local backend development)

### 1. Local Development with Docker Compose

```bash
# Clone the repository
git clone https://github.com/Utkarshs9924/yelp-prototype.git
cd yelp-prototype

# Start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:5173
# - User API: http://localhost:8001
# - Restaurant API: http://localhost:8002
# - Review API: http://localhost:8003
# - Kafka: localhost:9092
```

### 2. AWS EKS Deployment

```bash
# Create EKS cluster
eksctl create cluster \
  --name yelp-lab2 \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2

# Build and push Docker images to ECR
./deploy/build-and-push.sh

# Deploy to Kubernetes
kubectl apply -f k8s/

# Get service URLs
kubectl get services
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

---

## 📦 Services

### API Services (Producers)

#### User API Service
- **Port**: 8001
- **Endpoints**: `/signup`, `/login`, `/users/{id}`
- **Produces to**: `user.created`, `user.updated`, `user.login`

#### Restaurant API Service
- **Port**: 8002
- **Endpoints**: `/restaurants`, `/restaurants/{id}`, `/restaurants/search`
- **Produces to**: `restaurant.created`, `restaurant.updated`

#### Review API Service
- **Port**: 8003
- **Endpoints**: `/reviews`, `/restaurants/{id}/reviews`
- **Produces to**: `review.created`, `review.updated`, `review.deleted`

### Worker Services (Consumers)

#### User Worker
- **Consumes from**: `user.created`, `user.updated`, `user.login`
- **Actions**: Log events, update analytics, send notifications

#### Restaurant Worker
- **Consumes from**: `restaurant.created`, `restaurant.updated`, `restaurant.claimed`
- **Actions**: Update search index, sync external systems

#### Review Worker
- **Consumes from**: `review.created`, `review.updated`, `review.deleted`
- **Actions**: Update restaurant ratings, trigger notifications

---

## 🗄️ MongoDB Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  name: String,
  email: String,
  password_hash: String,
  role: String,  // "user", "owner", "admin"
  is_approved: Boolean,
  phone: String,
  city: String,
  country: String,
  profile_picture: String,
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
  pricing_tier: String,
  average_rating: Number,
  review_count: Number,
  owner_id: String,
  created_at: Date
}
```

### Reviews Collection
```javascript
{
  _id: ObjectId,
  restaurant_id: String,
  user_id: String,
  rating: Number,  // 1-5
  comment: String,
  created_at: Date,
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
    isAuthenticated: Boolean
  },
  restaurants: {
    list: Array,
    currentRestaurant: Object,
    searchResults: Array
  },
  reviews: {
    list: Array,
    loading: Boolean
  },
  favorites: {
    list: Array,
    favoriteIds: Array
  }
}
```

### Key Features

- ✅ JWT token management
- ✅ Persistent authentication state
- ✅ Async thunks for API calls
- ✅ Optimistic UI updates
- ✅ Error handling

See Redux DevTools screenshots in `/docs/redux-screenshots/`

---

## 📊 Performance Testing

### JMeter Test Suite

Located in `/jmeter-tests/`:

1. **Login Test** (`login.jmx`)
2. **Restaurant Search Test** (`search.jmx`)
3. **Review Submission Test** (`review.jmx`)

### Running Tests

```bash
cd jmeter-tests

# Run all tests at all concurrency levels (100-500)
./run-all-tests.sh

# Generate performance graphs
python generate-graph.py
```

### Test Results

See `/jmeter-tests/results/` for detailed reports.

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - REST API framework
- **Kafka** - Message queue
- **MongoDB** - NoSQL database
- **PyJWT** - JWT authentication
- **bcrypt** - Password hashing
- **boto3** - AWS S3 integration

### Frontend
- **React 19** - UI framework
- **Redux Toolkit** - State management
- **TailwindCSS 4** - Styling
- **Vite** - Build tool
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **AWS EKS** - Managed Kubernetes
- **AWS S3** - Object storage
- **AWS ECR** - Container registry
- **MongoDB Atlas** - Managed database

---

## 📁 Project Structure

```
yelp-prototype/
├── common/                  # Shared libraries
│   ├── database/           # MongoDB connection
│   ├── kafka/              # Kafka producer/consumer
│   └── utils/              # S3 storage utilities
├── services/               # Microservices
│   ├── user-api/          # User API service
│   ├── user-worker/       # User worker service
│   ├── restaurant-api/    # Restaurant API service
│   ├── restaurant-worker/ # Restaurant worker service
│   ├── review-api/        # Review API service
│   └── review-worker/     # Review worker service
├── frontend/              # React frontend
│   ├── src/
│   │   ├── redux/        # Redux store and slices
│   │   ├── components/   # React components
│   │   └── pages/        # Page components
│   ├── Dockerfile        # Frontend container
│   └── nginx.conf        # Nginx configuration
├── k8s/                   # Kubernetes manifests
│   ├── configmap.yaml
│   ├── user-api.yaml
│   ├── restaurant-api.yaml
│   ├── review-api.yaml
│   ├── kafka.yaml
│   └── frontend.yaml
├── jmeter-tests/          # JMeter test plans
│   ├── login.jmx
│   ├── search.jmx
│   └── review.jmx
├── docker-compose.yml     # Local development
└── README.md              # This file
```

---

## 🔐 Environment Variables

### MongoDB
```
MONGO_URI=mongodb+srv://...
DB_NAME=yelp_db
```

### Kafka
```
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### AWS
```
AWS_REGION=us-east-1
S3_BUCKET_NAME=yelp-restaurant-photos-akash-lab2
```

### Authentication
```
JWT_SECRET=your_secret_key
```

---

## 🧪 Testing

### Unit Tests
```bash
# Backend tests
cd services/user-api
pytest

# Frontend tests
cd frontend
npm test
```

### Integration Tests
```bash
# Test Kafka message flow
docker-compose exec user-api python test_kafka.py
```

### Load Tests
```bash
cd jmeter-tests
./run-all-tests.sh
```

---

## 📸 Screenshots

Required screenshots are in `/docs/screenshots/`:

1. ✅ All services running on AWS EKS
2. ✅ Kafka topics and message flow
3. ✅ MongoDB Atlas database
4. ✅ Redux DevTools state changes
5. ✅ JMeter performance results

---

## 🚢 Deployment

### Build Docker Images
```bash
./deploy/build-images.sh
```

### Push to AWS ECR
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  149410638858.dkr.ecr.us-east-1.amazonaws.com

./deploy/push-to-ecr.sh
```

### Deploy to EKS
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/zookeeper.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/
```

---

## 🐛 Troubleshooting

### Kafka Connection Issues
```bash
# Check Kafka logs
docker-compose logs kafka

# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### MongoDB Connection Issues
```bash
# Test connection
python test_mongodb.py
```

### Kubernetes Issues
```bash
# Check pod status
kubectl get pods

# View logs
kubectl logs <pod-name>

# Describe pod
kubectl describe pod <pod-name>
```

---

## 📚 Documentation

- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Diagram](./docs/architecture-diagram.png)
- [API Documentation](./docs/API.md)
- [JMeter Test Guide](./jmeter-tests/README.md)

---

## 👥 Team Contributions

**Utkarsh Sharma (Backend):**
- Microservices architecture design
- Kafka producer/consumer implementation
- MongoDB migration
- Docker & Kubernetes configuration
- AWS deployment

**Akash Kumar (Frontend):**
- Redux state management
- UI/UX enhancements
- S3 integration
- JMeter performance testing
- Documentation

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- **GitHub**: https://github.com/Utkarshs9924/yelp-prototype
- **Report**: See `docs/Lab2_Report.pdf`
- **Demo Video**: [YouTube Link]

---

**Last Updated**: April 20, 2026
