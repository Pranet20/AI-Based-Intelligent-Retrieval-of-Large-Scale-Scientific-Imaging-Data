# CLOUD DEPLOYMENT MANUAL EXECUTION PROTOCOL

**Document**: Phase 1–20 Master Final Completion — Cloud Deployment Protocol  
**Operational Status**: `CLOUD_DEPLOYMENT_NOT_EXECUTED` (Automated execution blocked: zero cloud provider credentials on local host)  
**Configuration Status**: Terraform IaC blueprints and Kubernetes manifests statically verified offline  

---

## 1. Why Automation Cannot Complete This Step
Production cloud infrastructure provisioning requires active authenticated credentials (e.g., AWS Access Key/Secret Key, GCP Service Account JSON, or Azure Service Principal), an active subscription billing account, and assigned network VPC permissions. Because no third-party cloud credentials exist on this local workstation, real cloud deployment cannot be executed automatically. Fabricating cloud deployment without live cloud infrastructure is strictly forbidden by the Absolute Immutability and Scientific Integrity rules.

---

## 2. Prerequisites
1. Dedicated cloud account with administrative or DevOps provisioning permissions.
2. Installed CLI tools: `terraform >= 1.5.0`, `kubectl >= 1.28`, `aws-cli` / `gcloud` / `az`.
3. Domain name with DNS zone access for SSL/TLS certificate issuing (Let's Encrypt / Cloudflare).
4. Cloud object storage bucket provisioned for immutable raw micrograph backups.

---

## 3. Step-by-Step Deployment Protocols

### Option A: AWS EKS Cloud Deployment

#### Step 1: Configure Cloud Credentials
```bash
aws configure
# Enter AWS Access Key ID, Secret Access Key, Default Region (e.g., us-east-1)
```

#### Step 2: Initialize & Apply Terraform Infrastructure
```bash
cd platform/cloud/terraform/aws
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```
Expected provisioned resources:
- Virtual Private Cloud (VPC) with public/private subnets across 3 Availability Zones.
- Amazon EKS Cluster (`scidata-eks-cluster`) with managed node group (GPU-enabled `g4dn.xlarge` or compute `c5.2xlarge`).
- Amazon RDS PostgreSQL 15 instance with multi-AZ replication.
- Amazon S3 bucket (`scidata-micrographs-storage`) with server-side encryption (SSE-KMS).

#### Step 3: Configure Kubernetes Context & Ingress
```bash
aws eks update-kubeconfig --region us-east-1 --name scidata-eks-cluster
kubectl apply -f platform/cloud/kubernetes/
```

#### Step 4: Verify Live Cloud Deployment
```bash
kubectl get nodes
kubectl get pods -n scidata-platform
kubectl get services -n scidata-platform
```
Expected output: all backend, frontend, and vector-search pods in `Running` state with external LoadBalancer IP assigned.

---

### Option B: Provider-Neutral Kubernetes / On-Premise Core Facility
```bash
# Apply secrets (from local environment templates)
kubectl apply -f platform/cloud/kubernetes/secrets.yaml

# Apply database & persistent volume claims
kubectl apply -f platform/cloud/kubernetes/pvc.yaml
kubectl apply -f platform/cloud/kubernetes/postgres-statefulset.yaml

# Apply backend and frontend deployments
kubectl apply -f platform/cloud/kubernetes/backend-deployment.yaml
kubectl apply -f platform/cloud/kubernetes/frontend-deployment.yaml

# Apply ingress controller
kubectl apply -f platform/cloud/kubernetes/ingress.yaml
```

---

## 4. Health Checks & Verification
1. Query external cloud ingress endpoint:
   ```bash
   curl -f https://scidata.your-institution.edu/api/v1/health
   ```
2. Verify automated SSL/TLS handshake:
   ```bash
   openssl s_client -connect scidata.your-institution.edu:443 -servername scidata.your-institution.edu
   ```
3. Test end-to-end ingestion and vector search under public internet latency.

---

## 5. Required Evidence to Capture for Publication
1. Cloud console screenshot showing running EKS cluster / RDS instance.
2. Terminal output showing `kubectl get pods -o wide` with external IP.
3. Ingress SSL certificate validation log.
4. Latency report comparing cloud-hosted API latency vs local host-side baseline.
