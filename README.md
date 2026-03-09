# 🧵 THREAD: AI-Powered Contextual Memory Mapping System

> Bridges the gap between raw data and institutional reasoning using a hybrid RAG approach with Amazon Neptune (Graph) and OpenSearch (Vector).

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange)](https://aws.amazon.com/)
[![React](https://img.shields.io/badge/React-18.3.1-blue)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🌟 Overview

THREAD is a production-ready AI-powered contextual knowledge system that helps organizations learn faster and become more productive by capturing the intent, reasoning, and relationships behind decisions—not just storing files.

### Key Features

- 🤖 **Hybrid RAG System**: Combines vector search (OpenSearch) with graph relationships (Neptune)
- 💬 **ChatGPT-Style Interface**: Natural language queries with source attribution
- 🕸️ **Knowledge Graph**: Visual relationship mapping between projects, decisions, and people
- 📊 **Project Analytics**: Comprehensive dashboards and progress tracking
- 📁 **File Management**: Upload, download, and organize project files
- 🎯 **Decision Timeline**: Track and review decisions chronologically
- 🤖 **AI Assistant**: 4 specialized modes for code review, decision explanation, and more

## 🏗️ Architecture

### 4-Layer Serverless Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 18)                           │
│  Dashboard | Projects | Ask Memory | Knowledge Graph | AI Assistant │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     API GATEWAY + LAMBDA                             │
│  RAG | Ingestion | Projects | Decisions | Graph | File Upload       │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        AI/ML SERVICES                                │
│  AWS Bedrock (Llama 3 70B) | Titan Embeddings | Comprehend          │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        STORAGE LAYER                                 │
│  OpenSearch (Vectors) | Neptune (Graph) | DynamoDB | S3             │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- Node.js 18+ and npm
- Python 3.11+
- AWS CDK CLI
- AWS CLI configured

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/SaiSruthi-R/THREAD.git
cd THREAD
```

2. **Install dependencies**
```bash
# Frontend
cd frontend
npm install

# Backend (CDK)
cd ../infrastructure/cdk
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your AWS credentials and settings
```

4. **Deploy to AWS**
```bash
cd infrastructure/cdk
cdk bootstrap  # First time only
cdk deploy --all
```

5. **Seed sample data**
```bash
python scripts/seed_data.py
```

6. **Run frontend locally**
```bash
cd frontend
npm start
```

Visit `http://localhost:3000` to see the application!

## 📚 Documentation

- [Architecture Overview](ARCHITECTURE.md) - System design and data flow
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Quick User Guide](QUICK_GUIDE.md) - How to use the application
- [File Upload Feature](FILE_UPLOAD_FEATURE.md) - File management guide
- [Project Management](PROJECT_MANAGEMENT_FEATURES.md) - Project features
- [Model Benchmarks](MODEL_BENCHMARKS.md) - AI model performance
- [Requirements Verification](REQUIREMENTS_VERIFICATION.md) - Feature checklist

## 🎯 Use Cases

### 1. Project Knowledge Management
- Capture project decisions and rationale
- Track who made decisions and why
- Link decisions to source documents
- Visualize project relationships

### 2. Institutional Memory
- Preserve organizational knowledge
- Onboard new team members faster
- Avoid repeating past mistakes
- Learn from historical decisions

### 3. Research & Development
- Track research decisions
- Link experiments to outcomes
- Visualize research relationships
- Query past findings

### 4. Compliance & Audit
- Document decision-making process
- Maintain audit trail
- Link decisions to policies
- Generate compliance reports

## 🛠️ Technology Stack

### Frontend
- React 18.3.1
- Tailwind CSS
- D3.js (Knowledge Graph)
- Axios
- React Router

### Backend
- AWS Lambda (Python 3.11)
- AWS API Gateway
- AWS CDK (Infrastructure as Code)

### AI/ML
- AWS Bedrock (Llama 3 70B)
- Amazon Titan Embeddings (1536-dim)
- Amazon Comprehend (NER)

### Storage
- Amazon OpenSearch (Vector DB)
- Amazon Neptune (Knowledge Graph)
- Amazon DynamoDB (Metadata)
- Amazon S3 (File Storage)

### Additional Services
- Amazon SQS (Async Processing)
- Amazon Cognito (Authentication)
- Amazon CloudFront (CDN)

## 📊 Features

### ✅ Core Features
- [x] Natural language query interface (RAG)
- [x] Hybrid search (Vector + Graph)
- [x] Knowledge graph visualization
- [x] Decision timeline tracking
- [x] Project management
- [x] File upload and management
- [x] Project analytics dashboard
- [x] AI assistant with 4 modes
- [x] Source attribution
- [x] Real-time data ingestion

### 🔮 Planned Features
- [ ] File preview (PDF, images, code)
- [ ] Bulk file operations
- [ ] File versioning
- [ ] Advanced search filters
- [ ] Email integration
- [ ] Slack integration
- [ ] GitHub integration
- [ ] Export to PDF/Excel
- [ ] Role-based access control
- [ ] Multi-tenant support

## 🎨 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Ask Memory (RAG Query)
![Ask Memory](docs/screenshots/ask-memory.png)

### Knowledge Graph
![Knowledge Graph](docs/screenshots/knowledge-graph.png)

### Project Analytics
![Analytics](docs/screenshots/analytics.png)

## 🔒 Security

- Private S3 buckets with encryption
- IAM role-based access control
- HTTPS-only API endpoints
- Presigned URLs for file downloads
- VPC isolation for databases
- Cognito authentication (optional)

## 💰 Cost Estimation

### Monthly Costs (Typical Usage)
- Lambda: ~$5 (1M requests)
- OpenSearch: ~$50 (t3.small.search)
- Neptune: ~$100 (t3.medium)
- DynamoDB: ~$5 (on-demand)
- S3: ~$1 (100GB storage)
- Data Transfer: ~$5

**Total: ~$166/month**

*Note: Costs vary based on usage. Free tier available for 12 months.*

## 🧪 Testing

```bash
# Run frontend tests
cd frontend
npm test

# Run backend tests
cd backend
pytest

# Run integration tests
python scripts/test_integration.py
```

## 📈 Performance

- API Response Time: < 3 seconds (RAG queries)
- Lambda Cold Start: < 2 seconds
- OpenSearch Query: < 500ms
- Frontend Load: < 2 seconds
- CloudFront Cache Hit: < 100ms

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Sai Sruthi R** - [GitHub](https://github.com/SaiSruthi-R)

## 🙏 Acknowledgments

- AWS for cloud infrastructure
- Meta for Llama 3 model
- React community for frontend tools
- Open source contributors

## 📞 Support

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/SaiSruthi-R/THREAD/issues)
- 📖 Docs: [Documentation](docs/)

## 🗺️ Roadmap

### Q2 2026
- [ ] File preview functionality
- [ ] Bulk operations
- [ ] Advanced analytics

### Q3 2026
- [ ] Email/Slack integration
- [ ] Mobile app
- [ ] API v2

### Q4 2026
- [ ] Multi-tenant support
- [ ] Enterprise features
- [ ] Advanced security

## 📊 Project Stats

- **Lines of Code**: ~15,000
- **Lambda Functions**: 8
- **API Endpoints**: 12
- **Frontend Components**: 10
- **Documentation Pages**: 15+

---

**Built with ❤️ using AWS, React, and AI**

**Live Demo**: [https://d22o2tuls1800z.cloudfront.net](https://d22o2tuls1800z.cloudfront.net)

**Last Updated**: March 9, 2026
