# 🤖 AI RAG POC — AWS ECS + Terraform + GitHub Actions

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![AWS ECS](https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900?logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-7B42BC?logo=terraform&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)

### A production-ready AI RAG chatbot deployed on AWS ECS with full CI/CD automation.

**🌐 Live Demo:** http://rag-poc-alb-278508936.us-east-1.elb.amazonaws.com/docs

</div>

---

## 🎯 What This Does

This project is a **Retrieval-Augmented Generation (RAG)** AI API that:

- Accepts any documents you upload via a REST API
- Stores them in a **FAISS vector database** with OpenAI embeddings
- Answers natural language questions grounded in your own data
- Runs on **AWS ECS Fargate** — fully serverless, no servers to manage
- Auto-scales from 1 to 10 containers based on live traffic
- Deploys automatically on every `git push` via GitHub Actions CI/CD
- Monitored with CloudWatch dashboards and email alerts

---

## 🏗️ Architecture

```
Developer → git push → GitHub Actions CI/CD
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
           Test &         Build &         Terraform
           Lint           Push ECR         Apply
                              │
                              ▼
                    ┌─────────────────┐
                    │    AWS VPC      │
                    │                 │
                    │  ALB (public)   │
                    │       │         │
                    │  ECS Fargate    │
                    │  (private)      │
                    │  1–10 tasks     │
                    └─────────────────┘
                              │
                    CloudWatch Monitoring
```

**Traffic flow:** `User → ALB (public URL) → ECS Tasks (private subnet) → OpenAI API`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| AI / RAG | LangChain + FAISS + OpenAI |
| Container | Docker (multi-stage build) |
| Registry | Amazon ECR |
| Compute | AWS ECS Fargate |
| Networking | VPC + ALB + NAT Gateway |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |
| Secrets | AWS SSM Parameter Store |
| Monitoring | AWS CloudWatch + SNS Alerts |
| Scaling | App Auto Scaling |

---

## 📁 Project Structure

```
rag-poc/
├── app/
│   ├── main.py           # FastAPI app and all endpoints
│   ├── rag.py            # RAG engine (LangChain + FAISS + OpenAI)
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Multi-stage Docker build
│
├── terraform/
│   ├── main.tf           # VPC, subnets, NAT, security groups
│   ├── variables.tf      # All configurable settings
│   ├── outputs.tf        # Live URL and dashboard link
│   ├── ecr.tf            # ECR repository
│   ├── ecs.tf            # ECS cluster, task definition, IAM
│   ├── alb.tf            # Application Load Balancer
│   ├── autoscaling.tf    # Auto scaling policies
│   └── monitoring.tf     # CloudWatch alarms and dashboard
│
└── .github/workflows/
    └── deploy.yml        # 6-stage CI/CD pipeline
```

---

## ✅ Prerequisites

| Tool | Install |
|---|---|
| AWS CLI v2 | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| Terraform ≥ 1.5 | [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/install) |
| Docker Desktop | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Git | [git-scm.com](https://git-scm.com/) |
| OpenAI API Key | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

---

## 🚀 Setup Guide

### Step 1 — Clone the Repo

```bash
git clone https://github.com/Haseeb-Ahmed-AI/rag-poc.git
cd rag-poc
```

### Step 2 — Configure AWS CLI

```bash
aws configure
# Enter your Access Key, Secret Key, region (us-east-1), and output (json)
```

### Step 3 — Add GitHub Secrets

Go to: **GitHub repo → Settings → Secrets → Actions**

| Secret | Value |
|---|---|
| `AWS_ROLE_ARN` | Your GitHub OIDC IAM Role ARN |
| `OPENAI_API_KEY` | Your OpenAI API key |

### Step 4 — Deploy

Just push to main — the CI/CD pipeline handles everything:

```bash
git add .
git commit -m "Deploy"
git push origin main
```

Watch it run at: **GitHub repo → Actions tab**

### Step 5 — Tear Down (stop billing)

```bash
cd terraform
terraform destroy -auto-approve
```

---

## 🔄 CI/CD Pipeline

Every push to `main` runs 6 automated stages:

```
✅ Stage 1 — Test & Lint         (~1 min)
✅ Stage 2 — Build & Push ECR    (~3 min)
✅ Stage 3 — Terraform Apply     (~2 min)
✅ Stage 4 — Deploy to ECS       (~4 min)
✅ Stage 5 — Smoke Tests         (~1 min)
─────────────────────────────────────────
   Total deploy time:            ~11 min
```

Pull Requests only run Test + Terraform Plan — no deploy.

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/metrics` | Documents indexed and queries served |
| POST | `/ingest` | Upload documents |
| POST | `/query` | Ask a question |
| GET | `/docs` | Interactive Swagger UI |

**Try it live:** http://rag-poc-alb-278508936.us-east-1.elb.amazonaws.com/docs

### Ingest Documents

```bash
curl -X POST http://rag-poc-alb-278508936.us-east-1.elb.amazonaws.com/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Our refund policy allows returns within 30 days.",
      "Contact support at support@company.com"
    ],
    "metadata": [
      {"source": "refund-policy"},
      {"source": "support-docs"}
    ]
  }'
```

### Query the AI

```bash
curl -X POST http://rag-poc-alb-278508936.us-east-1.elb.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I get a refund?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "You can return items within 30 days of purchase.",
  "sources": ["refund-policy"],
  "model": "gpt-3.5-turbo"
}
```

---

## ⚙️ Auto Scaling

| Trigger | Threshold | Min Tasks | Max Tasks |
|---|---|---|---|
| CPU Utilization | > 60% | 1 | 10 |
| Memory Utilization | > 70% | 1 | 10 |
| ALB Requests/Task | > 500/min | 1 | 10 |

To change limits, edit `terraform/variables.tf` and push.

---

## 📊 Monitoring

CloudWatch Dashboard includes:
- ECS CPU and Memory utilization
- ALB request count per minute
- p95 response latency
- HTTP 4XX and 5XX error rates

**Email alerts fire when:**
- CPU > 80% for 2 minutes
- Memory > 85% for 2 minutes
- 5XX errors > 10 per minute
- p95 latency > 5 seconds
- Any ECS task fails health check

To receive alerts, update the email in `terraform/monitoring.tf`:
```hcl
resource "aws_sns_topic_subscription" "email_alert" {
  endpoint = "your-email@example.com"
}
```

---

## 💰 Estimated AWS Cost

| Resource | Est. $/month |
|---|---|
| ECS Fargate (2 tasks) | ~$25 |
| Application Load Balancer | ~$20 |
| NAT Gateway (2 AZs) | ~$65 |
| ECR + CloudWatch | ~$6 |
| **Total** | **~$116/month** |

> To reduce cost during testing: set `desired_count = 1` and use 1 AZ → reduces to ~$40/month

---

## 🔧 Common Issues

**ECS tasks restarting?**
```bash
aws logs tail /ecs/rag-poc --follow --region us-east-1
```

**Wrong OpenAI key?**
```bash
aws ssm put-parameter --name "/rag-poc/openai-api-key" \
  --value "sk-your-key" --type SecureString --overwrite
aws ecs update-service --cluster rag-poc-cluster \
  --service rag-poc-service --force-new-deployment
```

**ALB returns 502?** Check ECS logs — container likely crashed on boot.

---

<div align="center">

**Built by Haseeb Ahmed — AI Engineer**

*AWS ECS · Terraform · GitHub Actions · LangChain · FastAPI · OpenAI*

</div>