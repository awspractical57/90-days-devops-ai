# 📖 DevOps + AI Glossary

> A personal reference glossary built on Day 1 of my 90-days DevOps + AI journey.  
> Written in my own words, AI-assisted, updated as I learn.  
> If something is wrong or can be improved — open an Issue!

---

## 🔧 Core DevOps Concepts

| Term | What it means in plain English |
|------|-------------------------------|
| **CI/CD** | Continuous Integration / Continuous Delivery. Automatically build, test, and deploy your code every time you push a change. I've been using AWS CodePipeline for this — GitHub Actions is the modern standard. |
| **Infrastructure as Code (IaC)** | Writing your cloud infrastructure (servers, networks, databases) as code files instead of clicking through a console. Tools: Terraform, Ansible, AWS CloudFormation. |
| **GitOps** | Using Git as the single source of truth for both application code AND infrastructure. If it's not in Git, it doesn't exist. Tools: ArgoCD, Flux. |
| **Shift Left** | Moving testing and security checks earlier in the development process — catch bugs before they reach production, not after. |
| **Idempotency** | Running the same operation multiple times gives the same result. Critical for IaC — running `terraform apply` twice shouldn't create two servers. |
| **Immutable Infrastructure** | Instead of updating a running server, you destroy it and create a new one from scratch. Containers make this easy. |
| **Observability** | The ability to understand what's happening inside your system from the outside. The 3 pillars: Logs, Metrics, Traces. |
| **SRE (Site Reliability Engineering)** | Google's approach to operations — treat infrastructure like a software engineering problem. Focus on reliability, SLOs, and error budgets. |
| **SLO / SLA / SLI** | SLI = what you measure (e.g. latency). SLO = your internal target (99.9% uptime). SLA = the contract you sign with customers. |
| **Toil** | Repetitive, manual, automatable operational work. SREs try to eliminate toil. AI is now helping automate it further. |

---

## 🐳 Containers & Orchestration

| Term | What it means in plain English |
|------|-------------------------------|
| **Container** | A lightweight, portable package that includes your app and everything it needs to run. Like a shipping container — works the same anywhere. |
| **Docker Image** | A blueprint/template for creating containers. Built from a `Dockerfile`. Stored in registries like Docker Hub or AWS ECR. |
| **Dockerfile** | A text file with instructions to build a Docker image. Like a recipe — `FROM`, `RUN`, `COPY`, `CMD`. |
| **Docker Compose** | A tool to define and run multi-container apps with a single YAML file. Good for local development (e.g. app + database + cache). |
| **Kubernetes (K8s)** | A system for automating deployment, scaling, and management of containers across a cluster of machines. The industry standard. |
| **Pod** | The smallest deployable unit in Kubernetes. Usually 1 container, sometimes a few tightly coupled ones. |
| **Deployment** | A Kubernetes object that manages a set of identical pods and ensures the desired number are always running. |
| **Service** | A Kubernetes object that exposes your pods to network traffic — either internally or externally. |
| **Namespace** | A way to divide a Kubernetes cluster into virtual sub-clusters. Good for separating dev/staging/prod environments. |
| **Helm** | The package manager for Kubernetes. Helm Charts are pre-packaged K8s configurations you can install with one command. |
| **ArgoCD** | A GitOps tool that continuously syncs your Kubernetes cluster to match whatever is in your Git repo. |

---

## ☁️ Cloud & Infrastructure

| Term | What it means in plain English |
|------|-------------------------------|
| **Terraform** | An IaC tool that lets you define cloud resources in HCL (HashiCorp Configuration Language) and provision them across AWS, Azure, GCP, etc. |
| **Terraform State** | A file that tracks what infrastructure Terraform has created. It's how Terraform knows what exists and what needs to change. |
| **VPC (Virtual Private Cloud)** | A private, isolated section of the AWS cloud where you launch your resources. You control the networking. |
| **IAM (Identity & Access Management)** | AWS's system for controlling who (users, services, roles) can do what to which AWS resources. |
| **EC2** | AWS virtual machines. You pick the size, OS, and region. The foundational compute service. |
| **S3** | AWS's object storage service. Store files, backups, static websites, ML datasets — anything. Infinitely scalable. |
| **Lambda** | AWS serverless compute. Run code without managing servers — you just upload a function, AWS handles the rest. |
| **ECS / EKS** | AWS's container services. ECS = managed Docker. EKS = managed Kubernetes. |

---

## 📊 Monitoring & Observability

| Term | What it means in plain English |
|------|-------------------------------|
| **Prometheus** | An open-source monitoring system that scrapes and stores time-series metrics from your applications and infrastructure. |
| **Grafana** | A visualization tool that connects to Prometheus (and others) to build dashboards and charts from your metrics. |
| **Loki** | Grafana's log aggregation system. Like Prometheus, but for logs instead of metrics. |
| **Alertmanager** | Part of the Prometheus ecosystem. Routes alerts to Slack, PagerDuty, email, etc. when metrics cross thresholds. |
| **Distributed Tracing** | Tracking a single request as it travels through multiple services. Tools: Jaeger, Zipkin, AWS X-Ray. |
| **MTTR / MTBF** | Mean Time To Recovery (how fast you fix incidents) and Mean Time Between Failures (how reliable your system is). |

---

## 🤖 AI & MLOps

| Term | What it means in plain English |
|------|-------------------------------|
| **LLM (Large Language Model)** | An AI model trained on huge amounts of text that can understand and generate human language. Examples: GPT-4, Claude, Gemini. |
| **Prompt Engineering** | The skill of writing effective instructions (prompts) to get the best output from an AI model. |
| **GitHub Copilot** | An AI coding assistant built into VS Code. Suggests code, explains errors, generates boilerplate — powered by OpenAI. |
| **MLOps** | Applying DevOps practices (CI/CD, versioning, monitoring) to machine learning models. The bridge between data science and production. |
| **Model Serving** | Making a trained ML model available as an API so applications can send data and get predictions back. Tools: FastAPI, TorchServe, TF Serving. |
| **MLflow** | An open-source platform for tracking ML experiments, versioning models, and managing the ML lifecycle. |
| **AIOps** | Using AI and ML to enhance IT operations — automatic anomaly detection, intelligent alerting, predictive incident management. |
| **AI Agent** | An AI system that can take actions, use tools, and complete multi-step tasks autonomously. Example: an agent that reads alerts and auto-remediates issues. |
| **LangChain** | A Python framework for building applications powered by LLMs — chains of prompts, tools, memory, and agents. |
| **RAG (Retrieval Augmented Generation)** | A technique where an LLM is given relevant documents/data at query time to answer questions about your specific knowledge base. |
| **Vector Database** | A database that stores data as mathematical vectors (embeddings) for fast similarity search. Used in RAG systems. Examples: Pinecone, Weaviate, pgvector. |
| **DVC (Data Version Control)** | Like Git, but for datasets and ML models. Track changes to your training data and model files over time. |

---

## 🔐 Security (DevSecOps)

| Term | What it means in plain English |
|------|-------------------------------|
| **DevSecOps** | Integrating security into every stage of the DevOps pipeline — not just at the end. "Shift left" on security. |
| **SAST** | Static Application Security Testing. Scans your source code for vulnerabilities before it runs. |
| **DAST** | Dynamic Application Security Testing. Tests your running application for vulnerabilities by attacking it. |
| **CVE** | Common Vulnerabilities and Exposures. A publicly listed security vulnerability with a unique ID (e.g. CVE-2021-44228 = Log4Shell). |
| **Trivy** | An open-source vulnerability scanner for Docker images, filesystems, and Git repos. Fast and easy to add to CI pipelines. |
| **Snyk** | A developer-first security tool that scans code, containers, and IaC for vulnerabilities and suggests fixes. |
| **HashiCorp Vault** | A tool for securely storing and accessing secrets (API keys, passwords, certificates). Never hardcode secrets in code. |
| **RBAC** | Role-Based Access Control. Assigning permissions based on roles, not individuals. Core to Kubernetes security. |

---

## 📡 Networking Basics

| Term | What it means in plain English |
|------|-------------------------------|
| **Load Balancer** | Distributes incoming traffic across multiple servers so no single server gets overwhelmed. AWS: ALB/NLB. K8s: Ingress. |
| **DNS** | Domain Name System. Translates human-readable domain names (google.com) into IP addresses. |
| **Ingress (K8s)** | A Kubernetes object that manages external HTTP/HTTPS access to services in a cluster. Think of it as a reverse proxy. |
| **Service Mesh** | Infrastructure layer for service-to-service communication — adds security, observability, and traffic control. Tools: Istio, Linkerd. |
| **CDN** | Content Delivery Network. Distributes your static content (images, JS, CSS) from servers close to your users. AWS: CloudFront. |

---

*Last updated: Day 1 — April 25, 2026*  
*This glossary grows as I learn. Each week I'll add terms from that week's topic.*
