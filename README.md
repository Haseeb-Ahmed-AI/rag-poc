# 🤖 AI RAG POC — AWS ECS + Terraform + GitHub Actions CI/CD

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![AWS ECS](https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900?logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-7B42BC?logo=terraform&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)

**A production-ready Proof of Concept: deploy an AI RAG chatbot on AWS in under 30 minutes.**

</div>

---

## 📋 Table of Contents

1. [What This POC Does](#-what-this-poc-does)
2. [Architecture Overview](#-architecture-overview)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites-install-these-first)
6. [Step-by-Step Setup](#-step-by-step-setup)
7. [API Usage](#-api-usage)
8. [Auto Scaling](#-auto-scaling)
9. [Monitoring & Alerts](#-monitoring--alerts)
10. [CI/CD Pipeline Explained](#-cicd-pipeline-explained)
11. [Estimated AWS Cost](#-estimated-aws-cost)
12. [Troubleshooting](#-troubleshooting)

---

## 🎯 What This POC Does

This project deploys a **Retrieval-Augmented Generation (RAG)** AI system that:

- Accepts **any documents** you upload via an API
- Stores them in a **FAISS vector database** with OpenAI embeddings
- Answers **natural language questions** using GPT-3.5-turbo grounded on your data
- Runs on **AWS ECS Fargate** (serverless containers — no EC2 servers to manage)
- **Auto-scales** from 1 to 10 tasks based on CPU, memory, or request load
- Deploys automatically via **GitHub Actions** on every `git push`
- Is fully monitored with **CloudWatch dashboards and email alerts**

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPER                                │
│                    git push → main                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GITHUB ACTIONS (CI/CD)                        │
│  Test → Lint → Build Image → Push ECR → Terraform → Deploy ECS │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────────┐    ┌──────────────────────┐
    │   Amazon ECR     │    │     Terraform IaC     │
    │  (Docker images) │    │  (AWS infrastructure) │
    └──────────────────┘    └──────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AWS VPC                                 │
│                                                                 │
│   Public Subnets                  Private Subnets              │
│   ┌──────────────┐                ┌──────────────────────────┐ │
│   │     ALB      │──── routes ───▶│   ECS Fargate Tasks      │ │
│   │  (port 80)   │                │  ┌──────┐  ┌──────┐     │ │
│   └──────────────┘                │  │Task 1│  │Task 2│ ... │ │
│   ┌──────────────┐                │  └──────┘  └──────┘     │ │
│   │ NAT Gateway  │◀── outbound ───│   Auto Scaling (1–10)   │ │
│   └──────────────┘                └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OBSERVABILITY                             │
│   CloudWatch Logs │ Metrics │ Alarms │ Dashboard │ SNS Alerts  │
└─────────────────────────────────────────────────────────────────┘
```

**Traffic flow:** `User → ALB DNS (public) → ALB → ECS Tasks (private subnet) → OpenAI API`

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API** | FastAPI + Uvicorn | REST API serving RAG queries |
| **AI / RAG** | LangChain + FAISS + OpenAI | Embeddings, retrieval, generation |
| **Container** | Docker (multi-stage) | Lightweight, secure image |
| **Registry** | Amazon ECR | Private Docker image storage |
| **Compute** | AWS ECS Fargate | Serverless container execution |
| **Networking** | VPC + ALB + NAT | Secure, public-facing load balancer |
| **IaC** | Terraform ≥ 1.5 | All infra as code — reproducible |
| **CI/CD** | GitHub Actions | Automated test → build → deploy |
| **Secrets** | AWS SSM Parameter Store | Encrypted API key storage |
| **Monitoring** | AWS CloudWatch | Metrics, logs, alarms, dashboard |
| **Alerting** | AWS SNS | Email notifications on alarms |
| **Scaling** | App Auto Scaling | CPU / Memory / Request-based |

---

## 📁 Project Structure

```
rag-poc/
│
├── 📂 app/                        # Application code
│   ├── main.py                    # FastAPI app — all endpoints
│   ├── rag.py                     # RAG engine (LangChain + FAISS + OpenAI)
│   ├── requirements.txt           # Python dependencies
│   └── Dockerfile                 # Multi-stage Docker build
│
├── 📂 terraform/                  # AWS infrastructure (IaC)
│   ├── main.tf                    # VPC, subnets, NAT, security groups
│   ├── variables.tf               # ⚙️  All tunable settings live here
│   ├── outputs.tf                 # Prints live URL + dashboard link after deploy
│   ├── ecr.tf                     # ECR repository + lifecycle policy
│   ├── ecs.tf                     # ECS cluster, task definition, service, IAM
│   ├── alb.tf                     # Application Load Balancer + target group
│   ├── autoscaling.tf             # Auto scaling (CPU, memory, ALB requests)
│   └── monitoring.tf              # CloudWatch alarms, dashboard, SNS alerts
│
└── 📂 .github/workflows/
    └── deploy.yml                 # Full 6-stage CI/CD pipeline
```

> **💡 Tip:** To change region, instance size, min/max tasks, or LLM model — edit only `terraform/variables.tf`. No code changes needed.

---

## ✅ Prerequisites (Install These First)

Before running anything, make sure you have all of these:

| Tool | Version | Install Link |
|---|---|---|
| **AWS CLI** | v2+ | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| **Terraform** | ≥ 1.5 | [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/install) |
| **Docker Desktop** | any recent | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git** | any | [git-scm.com](https://git-scm.com/) |
| **OpenAI API Key** | — | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **AWS Account** | — | Needs permissions for: ECS, ECR, VPC, IAM, SSM, CloudWatch, S3 |

**Verify everything is installed:**

```bash
aws --version          # should show: aws-cli/2.x.x
terraform --version    # should show: Terraform v1.x.x
docker --version       # should show: Docker version 2x.x
git --version          # should show: git version 2.x
```

**Configure AWS CLI** (if not done yet):

```bash
aws configure
# AWS Access Key ID:     <paste your key>
# AWS Secret Access Key: <paste your secret>
# Default region name:   us-east-1
# Default output format: json
```

---

## 🚀 Step-by-Step Setup

### Step 1 — Clone & Configure

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rag-poc.git
cd rag-poc
```

If you're starting a fresh GitHub repo:

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/rag-poc.git
git branch -M main
```

---

### Step 2 — Set GitHub Secrets

> ⚠️ **This step is required before CI/CD will work. Do not skip it.**

Go to your GitHub repo page:
**Settings → Secrets and variables → Actions → New repository secret**

Add these two secrets exactly:

| Secret Name | Value | Notes |
|---|---|---|
| `AWS_ROLE_ARN` | `arn:aws:iam::123456789012:role/github-oidc-role` | See IAM setup below |
| `OPENAI_API_KEY` | `sk-proj-...` | From OpenAI dashboard |

**One-time IAM Setup for GitHub OIDC (run in terminal):**

```bash
# 1. Create the OIDC Identity Provider in AWS
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. Create the IAM Role via AWS Console:
#    → IAM → Roles → Create Role
#    → Trusted entity type: "Web Identity"
#    → Identity provider: token.actions.githubusercontent.com
#    → Audience: sts.amazonaws.com
#    → Add condition: repo:YOUR_GITHUB_USERNAME/rag-poc:*
#    → Attach policy: AdministratorAccess  (use tighter policy in production)
#    → Name it: github-oidc-role
#    → Copy the Role ARN and paste it into the GitHub secret above
```

---

### Step 3 — Bootstrap AWS Infrastructure

> This creates all AWS resources: VPC, ECS, ALB, ECR, CloudWatch, etc.
> **Run this once.** CI/CD handles all future updates automatically.

```bash
cd terraform

# Download required Terraform providers (~30 seconds)
terraform init

# Preview all resources that will be created (safe — no changes made)
terraform plan -var="openai_api_key=sk-YOUR_REAL_KEY_HERE"

# Create everything (~5 to 10 minutes)
terraform apply -var="openai_api_key=sk-YOUR_REAL_KEY_HERE"
# Type "yes" when prompted
```

When complete, Terraform prints your live outputs:

```
Apply complete! Resources: 42 added, 0 changed, 0 destroyed.

Outputs:

app_url                  = "http://rag-poc-alb-1234567890.us-east-1.elb.amazonaws.com"
ecr_repository_url       = "123456789.dkr.ecr.us-east-1.amazonaws.com/rag-poc-app"
ecs_cluster_name         = "rag-poc-cluster"
ecs_service_name         = "rag-poc-service"
cloudwatch_dashboard_url = "https://us-east-1.console.aws.amazon.com/cloudwatch/..."
```

> 📌 **Save the `app_url` — this is your live endpoint to share with the client!**

---

### Step 4 — Trigger CI/CD Pipeline

Every push to `main` runs the full automated pipeline.

```bash
cd ..   # go back to project root

git add .
git commit -m "feat: initial RAG POC deployment"
git push origin main
```

**Watch it run live:**
GitHub repo → **Actions tab** → click the running workflow

You will see 6 jobs completing in sequence:

```
✅ Job 1 — Test & Lint           (~1 min)
✅ Job 2 — Terraform Plan (PR)   (skipped on push to main)
✅ Job 3 — Build & Push to ECR   (~3 min)
✅ Job 4 — Terraform Apply       (~2 min)
✅ Job 5 — Deploy to ECS         (~4 min)
✅ Job 6 — Smoke Tests           (~1 min)
─────────────────────────────────────────
   Total first deploy:           ~11 min
   Subsequent deploys:           ~6 min
```

---

### Step 5 — Verify Live Deployment

Replace `<ALB_URL>` with the URL printed in Step 3.

```bash
# ✅ Health check — should return 200
curl http://<ALB_URL>/health

# ✅ Ask a question
curl -X POST http://<ALB_URL>/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AWS ECS Fargate?", "top_k": 3}'

# ✅ Open the interactive API docs in your browser
open http://<ALB_URL>/docs
```

**Expected health check response:**
```json
{"status": "healthy", "service": "RAG POC", "version": "1.0.0"}
```

---

## 🧪 API Usage

### Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info and available endpoints |
| `GET` | `/health` | Health check (polled by ALB every 30s) |
| `GET` | `/metrics` | Number of documents indexed and queries served |
| `POST` | `/ingest` | Upload documents to the vector store |
| `POST` | `/query` | Ask a question, get a grounded AI answer |
| `GET` | `/docs` | Swagger UI — try all endpoints in browser |

---

### 📥 Ingest Your Own Documents

```bash
curl -X POST http://<ALB_URL>/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Our refund policy allows returns within 30 days of purchase.",
      "To contact support, email support@company.com or call 1-800-XXX-XXXX.",
      "Premium members get free shipping on all orders over $50."
    ],
    "metadata": [
      {"source": "refund-policy"},
      {"source": "support-docs"},
      {"source": "membership-benefits"}
    ]
  }'
```

**Response:**
```json
{"message": "Successfully ingested 3 documents", "total_docs": 3}
```

---

### 🔍 Query the RAG System

```bash
curl -X POST http://<ALB_URL>/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I get a refund?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "You can return items within 30 days of purchase for a full refund.",
  "sources": ["refund-policy"],
  "model": "gpt-3.5-turbo"
}
```

**Request parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `question` | string | required | The question to ask the AI |
| `top_k` | integer | 3 | How many document chunks to retrieve |

---

## ⚙️ Auto Scaling

The service automatically scales between **1 and 10 ECS tasks** based on three signals:

| Trigger | Scales Out When | Scale-Out Cooldown | Scale-In Cooldown |
|---|---|---|---|
| **CPU Utilization** | > 60% average | 60 seconds | 5 minutes |
| **Memory Utilization** | > 70% average | 60 seconds | 5 minutes |
| **ALB Requests / Task** | > 500 req/min | 60 seconds | 5 minutes |

Scale **out** is fast (60s) to handle traffic spikes.
Scale **in** is slow (300s) to avoid flapping.

**To adjust limits**, edit `terraform/variables.tf`:

```hcl
variable "min_count"     { default = 1  }   # Never go below this
variable "max_count"     { default = 10 }   # Never exceed this
variable "desired_count" { default = 2  }   # Initial count on deploy
```

Then re-run `terraform apply`.

---

## 📊 Monitoring & Alerts

### CloudWatch Dashboard

After deploying, open the dashboard URL from Terraform outputs.

**Panels included:**
- ECS CPU & Memory utilization (real-time graph)
- ALB request count per minute
- p95 response latency
- HTTP 4XX and 5XX error rates

---

### Alarms (Auto-configured)

| Alarm Name | Triggers When | Action |
|---|---|---|
| `rag-poc-cpu-high` | CPU > 80% for 2 min | Email via SNS |
| `rag-poc-memory-high` | Memory > 85% for 2 min | Email via SNS |
| `rag-poc-alb-5xx-errors` | 5XX errors > 10/min | Email via SNS |
| `rag-poc-alb-high-latency` | p95 latency > 5s | Email via SNS |
| `rag-poc-unhealthy-hosts` | Any task fails health check | Email via SNS |

**To receive email alerts**, update `terraform/monitoring.tf`:

```hcl
resource "aws_sns_topic_subscription" "email_alert" {
  endpoint = "your-email@example.com"   # ← change this line
}
```

Then run `terraform apply`. Check your inbox for a confirmation email — click the link to activate.

---

### View Logs in Terminal

```bash
# Stream live logs from all ECS containers
aws logs tail /ecs/rag-poc --follow --region us-east-1

# Filter for errors only
aws logs filter-log-events \
  --log-group-name /ecs/rag-poc \
  --filter-pattern "ERROR" \
  --region us-east-1
```

---

## 🔄 CI/CD Pipeline Explained

```
Push to main
     │
     ▼
┌──────────────┐    ┌──────────────────┐    ┌────────────────────┐
│  1. Test &   │───▶│  2. Build Docker │───▶│  3. Terraform      │
│     Lint     │    │     Push to ECR  │    │     Apply (infra)  │
└──────────────┘    └──────────────────┘    └────────────────────┘
                                                      │
                    ┌─────────────────────────────────┘
                    ▼
          ┌──────────────────┐    ┌──────────────────────────┐
          │  4. Rolling ECS  │───▶│  5. Smoke Tests (live)   │
          │     Deploy       │    │  Health + Query checks    │
          └──────────────────┘    └──────────────────────────┘
```

**Key behaviours:**

- **Pull Requests** — runs Test + Terraform Plan only (no deploy, safe to review)
- **Push to `main`** — full pipeline triggers automatically
- **Auto-rollback** — ECS circuit breaker rolls back if new tasks fail health checks
- **Zero downtime** — rolling update keeps old tasks running until new ones pass health checks
- **Build caching** — GitHub Actions cache makes repeat builds 2× faster

---

## 💰 Estimated AWS Cost

| Resource | Spec | Est. $/month |
|---|---|---|
| ECS Fargate | 0.5 vCPU, 1 GB RAM × 2 tasks | ~$25 |
| Application Load Balancer | 1 ALB | ~$20 |
| NAT Gateway | 2 AZs × 1 NAT each | ~$65 |
| Amazon ECR | ~1 GB image storage | ~$1 |
| CloudWatch | Metrics + Logs + Dashboard | ~$5 |
| **Total** | | **~$116/month** |

> **💡 To cut costs during POC testing:**
> - Set `desired_count = 1` and `min_count = 1` → saves ~$12/month
> - Use one AZ: `public_subnet_cidrs = ["10.0.1.0/24"]` → removes 1 NAT Gateway, saves ~$32/month
> - **Minimum POC cost ≈ ~$40/month** with both changes applied

---

## 🔧 Troubleshooting

### ❌ `terraform apply` fails: permissions error

```
Error: AccessDenied — User is not authorized to perform: iam:CreateRole
```

**Fix:** Attach `AdministratorAccess` to your AWS IAM user (acceptable for a POC).

---

### ❌ GitHub Actions fails: "Could not assume role with OIDC"

**Check these three things:**

1. The OIDC provider exists in IAM (`token.actions.githubusercontent.com`)
2. The Role's trust policy includes your repo: `repo:YOUR_USERNAME/rag-poc:*`
3. The `AWS_ROLE_ARN` secret starts with `arn:aws:iam::` and is the full ARN

---

### ❌ ECS tasks keep restarting / failing health checks

Check the ECS logs for the real error:

```bash
aws logs tail /ecs/rag-poc --follow --region us-east-1
```

Most common cause — wrong or missing OpenAI key in SSM. Fix it:

```bash
# Update the key in SSM
aws ssm put-parameter \
  --name "/rag-poc/openai-api-key" \
  --value "sk-YOUR_CORRECT_KEY" \
  --type SecureString \
  --overwrite \
  --region us-east-1

# Force ECS to restart with the new key
aws ecs update-service \
  --cluster rag-poc-cluster \
  --service rag-poc-service \
  --force-new-deployment \
  --region us-east-1
```

---

### ❌ ALB returns 502 Bad Gateway

The container started but the app crashed on boot. Check logs:

```bash
aws logs tail /ecs/rag-poc --follow --region us-east-1
```

---

### ❌ Test Docker build locally before pushing

```bash
cd app
docker build -t rag-poc:local .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... rag-poc:local

# Test it
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

---

### 🗑️ Tear Down Everything (stop all billing)

```bash
cd terraform
terraform destroy -var="openai_api_key=placeholder"
# Type "yes" when prompted
# All AWS resources will be deleted within ~5 minutes
```

> ⚠️ This permanently deletes all infrastructure and cannot be undone.
> FAISS data is in-memory only — it is not persisted between container restarts.

---

<div align="center">

**Built by Muhammad Faraan — AI Engineer**

*AWS ECS · Terraform · GitHub Actions · LangChain · FastAPI · OpenAI*

</div>
#   R A G   P O C  
 