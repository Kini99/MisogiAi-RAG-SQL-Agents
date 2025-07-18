# 💰 Quick Commerce Price Comparison Platform

A comprehensive real-time price comparison platform for quick commerce apps like Blinkit, Zepto, Instamart, BigBasket Now, and more. The platform tracks pricing, discounts, and availability across multiple platforms for thousands of products using natural language queries.

## 🚀 Features

### Core Features
- **Natural Language Queries**: Ask questions like "Which app has cheapest onions right now?"
- **Real-time Price Tracking**: Monitor prices across multiple platforms in real-time
- **Comprehensive Database**: 50+ tables covering products, pricing, availability, and analytics
- **Intelligent SQL Agent**: LangChain-powered SQL query generation and execution
- **Advanced Analytics**: Dashboard with pricing trends, platform comparisons, and insights
- **User Management**: Authentication, profiles, favorites, and price alerts

### Technical Features
- **High Performance**: Async FastAPI with connection pooling and caching
- **Scalable Architecture**: Microservices with Docker and Kubernetes support
- **Real-time Monitoring**: Prometheus, Grafana, and comprehensive metrics
- **Security**: JWT authentication, rate limiting, and security headers
- **Modern Frontend**: React 18+ with TypeScript and Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Monitoring    │
│   (Next.js)     │◄──►│   (Nginx)       │◄──►│   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   PostgreSQL    │    │   Redis Cache   │
│   Backend       │◄──►│   Database      │◄──►│   (Session/     │
└─────────────────┘    └─────────────────┘    │   Cache)        │
                              │               └─────────────────┘
                              ▼
                       ┌─────────────────┐
                       │   Celery        │
                       │   (Background   │
                       │   Tasks)        │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** (Python 3.11+) - High-performance async web framework
- **PostgreSQL 15+** - Primary database with async support
- **Redis** - Caching and session storage
- **SQLAlchemy 2.0** - Async ORM with connection pooling
- **LangChain 0.1+** - AI-powered SQL query generation
- **Celery** - Background task processing
- **JWT** - Authentication and authorization

### Frontend
- **Next.js 14** - React framework with SSR
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Server state management
- **Zustand** - Client state management

### Monitoring & DevOps
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards
- **Docker** - Containerization
- **Nginx** - Reverse proxy and load balancing
- **Flower** - Celery monitoring

## 📦 Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd price-comparison-platform
   ```

2. **Start the platform**
   ```bash
   ./start.sh
   ```

   Or manually:
   ```bash
   # Create environment file
   cp env.example .env
   
   # Start all services
   docker-compose up --build -d
   ```

3. **Access the platform**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001 (admin/admin)
   - Prometheus: http://localhost:9090
   - Flower: http://localhost:5555

### Development Setup

1. **Backend Development**
   ```bash
   cd price_comparison
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   uvicorn main:app --reload
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🗄️ Database Schema

The platform uses a comprehensive database schema with 50+ tables organized into modules:

### Core Models
- **Platforms**: Platform information and configuration
- **Categories**: Product categories and hierarchies
- **Brands**: Brand information and metadata
- **Products**: Product details, images, and specifications

### Pricing Models
- **Prices**: Current and historical pricing data
- **Discounts**: Discount information and calculations
- **Promotions**: Active promotions and offers

### Availability Models
- **Inventory**: Stock levels and availability
- **Delivery Slots**: Delivery time slots and scheduling

### Analytics Models
- **Query Analytics**: Search and query performance metrics
- **User Analytics**: User behavior and engagement data
- **Platform Analytics**: Platform performance and health metrics

## 🔍 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user

### Natural Language Query
- `POST /api/v1/query/natural-language` - Process natural language queries
- `GET /api/v1/query/suggestions` - Get query suggestions
- `GET /api/v1/query/popular` - Get popular queries

### Products
- `GET /api/v1/products/` - List products with filters
- `GET /api/v1/products/{id}` - Get product details
- `GET /api/v1/products/search` - Search products
- `GET /api/v1/products/best-deals` - Get best deals

### Analytics
- `GET /api/v1/analytics/dashboard` - Get dashboard metrics
- `GET /api/v1/analytics/trends` - Get pricing trends
- `GET /api/v1/analytics/platforms` - Get platform analytics

### Monitoring
- `GET /api/v1/monitoring/health` - Health check
- `GET /api/v1/monitoring/metrics` - Prometheus metrics
- `GET /api/v1/monitoring/performance` - Performance metrics

## 🎯 Usage Examples

### Natural Language Queries
```
"Which app has cheapest onions right now?"
"Show products with 30%+ discount on Blinkit"
"Compare fruit prices between Zepto and Instamart"
"Find best deals for ₹1000 grocery list"
"What's the cheapest milk delivery today?"
```

### API Usage
```python
import requests

# Natural language query
response = requests.post("http://localhost:8000/api/v1/query/natural-language", {
    "query": "Which app has cheapest onions right now?",
    "max_results": 10
})

# Get best deals
response = requests.get("http://localhost:8000/api/v1/products/best-deals")

# Get analytics
response = requests.get("http://localhost:8000/api/v1/analytics/dashboard")
```

## 📊 Monitoring & Analytics

### Metrics Tracked
- **API Performance**: Response times, request rates, error rates
- **Database Performance**: Connection pools, query performance, cache hit rates
- **System Resources**: CPU, memory, disk usage
- **Business Metrics**: User engagement, query success rates, platform health

### Dashboards
- **System Dashboard**: Infrastructure and performance metrics
- **Business Dashboard**: User engagement and business metrics
- **Platform Dashboard**: Platform-specific analytics and health

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API rate limiting with slowapi
- **CORS Protection**: Cross-origin resource sharing configuration
- **Security Headers**: XSS protection, content type validation
- **Input Validation**: Pydantic models for request validation

## 🚀 Deployment

### Production Deployment
```bash
# Set production environment
export ENVIRONMENT=production
export SECRET_KEY=your-secure-secret-key

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-secret-key
ENVIRONMENT=production

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_PASSWORD=secure-password
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write comprehensive tests
- Update documentation for new features
- Follow conventional commits

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Machine learning price predictions
- [ ] Integration with more platforms
- [ ] Advanced analytics and reporting
- [ ] Real-time notifications
- [ ] Social features and reviews
- [ ] B2B API access
- [ ] Multi-language support

---

**Built with ❤️ for smart shopping** 