# StreamBuddy

StreamBuddy is a scalable video streaming platform built using Django REST API, DASH, and AWS S3 for storage. It features an asynchronous video processing pipeline, adaptive bitrate streaming, and comprehensive API documentation.

![Project Image](app/image.png)

## Features

- **Scalable Video Streaming**: Architected using Django REST API, DASH, and AWS S3 for efficient storage and streaming.
- **Asynchronous Video Processing**: Utilizes Celery and Redis to handle concurrent video uploads efficiently.
- **Adaptive Bitrate Streaming**: Achieves 60-80% size reduction while maintaining 85-90% quality through multi-resolution encoding using FFMPEG.
- **Comprehensive API Documentation**: Designed with Swagger/OpenAPI, including rate limiting and monitoring.

## Architecture Diagram
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

## Project Structure