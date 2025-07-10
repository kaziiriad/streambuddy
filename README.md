# StreamBuddy: Video Streaming Platform with DASH Support

StreamBuddy is a scalable video streaming platform built using Django REST API, DASH, and AWS S3 for storage. It features an asynchronous video processing pipeline, adaptive bitrate streaming, and comprehensive API documentation.

![Project Image](docs/assets/image.png)

## 🚀 Features

- **User Authentication**: Secure user registration and login using `dj-rest-auth` and `django-allauth`.
- **Automated Deployment**: CI/CD pipeline using GitHub Actions, Pulumi, and Ansible.
- **Secure Video Upload**
  - Support for large file uploads (up to 10GB)
  - Mime type validation

- **Video Processing**
  - Asynchronous processing using Celery
  - Multi-resolution encoding (480p to 4K)
  - DASH manifest generation
  - 60-80% size reduction while maintaining 85-90% quality

- **Streaming Capabilities**
  - DASH (Dynamic Adaptive Streaming over HTTP) support
  - Adaptive bitrate streaming
  - Real-time quality switching
  - Low latency streaming

- **Security & Performance**
  - Rate limiting for API endpoints
  - AWS S3 integration for scalable storage
  - Comprehensive API documentation
  - CORS support


## 🏗️ Architecture Diagram
```mermaid
graph TB
    subgraph Client["Client Layer"]
        VP[Video Player]
        AD[Adaptive DASH Player]
    end

    subgraph API["API Layer"]
        REST[Django REST API]
        RL[Rate Limiter]
        SW[Swagger/OpenAPI Docs]
    end

    subgraph Processing["Processing Layer"]
        CW[Celery Workers]
        RD[Redis Queue]
        FF[FFMPEG Processor]
    end

    subgraph Storage["Storage Layer"]
        S3[AWS S3]
        META[Metadata Storage]
    end

    %% Client Layer Connections
    VP --> |HTTP Requests| REST
    AD --> |DASH Streaming| REST

    %% API Layer Connections
    REST --> |Rate Limited| RL
    REST --> |Documents| SW
    REST --> |Async Tasks| CW

    %% Processing Layer Connections
    CW --> |Queue Tasks| RD
    RD --> |Process Tasks| CW
    CW --> |Transcode| FF
    FF --> |Multi-resolution| CW

    %% Storage Layer Connections
    CW --> |Store Videos| S3
    CW --> |Store Data| META
    REST --> |Fetch Videos| S3
    REST --> |Fetch Metadata| META

    style VP fill:#3498db,stroke:#fff,stroke-width:2px
    style AD fill:#3498db,stroke:#fff,stroke-width:2px
    style REST fill:#2ecc71,stroke:#fff,stroke-width:2px
    style RL fill:#2ecc71,stroke:#fff,stroke-width:2px
    style SW fill:#2ecc71,stroke:#fff,stroke-width:2px
    style CW fill:#e74c3c,stroke:#fff,stroke-width:2px
    style RD fill:#9b59b6,stroke:#fff,stroke-width:2px
    style FF fill:#f1c40f,stroke:#fff,stroke-width:2px
    style S3 fill:#e67e22,stroke:#fff,stroke-width:2px
    style META fill:#e67e22,stroke:#fff,stroke-width:2px
```

## 🛠️ Technical Stack

- **Backend**: Django REST Framework
- **Authentication**: `dj-rest-auth`, `django-allauth`
- **CI/CD**: GitHub Actions, Pulumi, Ansible
- **Video Processing**: FFMPEG
- **Task Queue**: Celery with Redis
- **Storage**: AWS S3 / Local Storage
- **Documentation**: Swagger/OpenAPI
- **Container**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.10 or higher
- FFmpeg
- Celery
- Redis
- Docker & Docker Compose (optional)
- AWS Account (optional, for S3 storage)

## 🚀 Deployment

The deployment of this application is fully automated using a CI/CD pipeline powered by GitHub Actions. When changes are pushed to the `main` branch, the following process is triggered:

1.  **Infrastructure Provisioning**: Pulumi is used to define and provision the necessary cloud infrastructure on AWS, including the VPC, EC2 instances, and S3 buckets.
2.  **Application Deployment**: An Ansible playbook is executed to configure the server, deploy the latest version of the application using Docker, and ensure all services are running correctly.

This automated workflow ensures that deployments are consistent, repeatable, and require no manual intervention.

### Local Development

For local development and testing, you can use the provided Docker Compose setup:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/streambuddy.git
    cd streambuddy
    ```

2.  **Create and configure the `.env` file:**
    ```bash
    cp .env.template .env
    # Edit .env with your local settings
    ```

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

## ⚙️ Configuration

Key configuration options in `.env`:

```env
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
MAX_UPLOAD_SIZE=10737418240
DEFAULT_VIDEO_QUALITY=1080p

# AWS Configuration (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=your-region
```

## 🔐 Security Settings

The platform includes several security measures:

- Rate limiting:
  - Anonymous users: 100 requests/day
  - Authenticated users: 1000 requests/day
  - Video uploads: 10/day
  - Streaming: 1000 requests/hour

- CORS configuration in settings.py
- AWS S3 secure configuration
- Input validation and sanitization

## 📚 API Documentation

API documentation is available at `/swagger/` or `/redoc/` after starting the server.

Key endpoints:
- `POST /api/videos/upload/`: Upload new video
- `GET /api/videos/`: List all videos
- `GET /api/videos/{title}/`: Stream video

## 📦 Production Deployment

For production deployment:

1. Update `.env` with production settings:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
USE_S3=True
```
## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FFmpeg team for the excellent video processing library
- Celery and Redis for task queue management
- Django and Django REST Framework communities
- AWS for providing scalable storage solutions
