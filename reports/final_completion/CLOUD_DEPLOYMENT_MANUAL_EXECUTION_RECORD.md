# CLOUD DEPLOYMENT MANUAL EXECUTION RECORD

**Project**: AI-Powered Scientific Image Data Management Platform  
**Status**: `REQUIRES_EXTERNAL_INFRASTRUCTURE` / `CLOUD_DEPLOYMENT_NOT_EXECUTED`  
**Prerequisites**: Active AWS / GCP / Azure subscription, authenticated CLI credentials, authorized billing.  

---

## 1. Operational Declaration
In accordance with the Scientific Integrity rules, cloud deployment was not executed during automated local testing because no third-party cloud credentials or public cloud environments are present on this local workstation. Terraform Infrastructure-as-Code blueprints and Kubernetes manifests have been statically verified offline.

## 2. Step-by-Step Manual Execution Protocol (AWS EKS Example)
1. **Configure Credentials**:
   ```bash
   aws configure
   ```
2. **Apply Infrastructure via Terraform**:
   ```bash
   cd platform/cloud/terraform/aws
   terraform init
   terraform plan -out=tfplan
   terraform apply tfplan
   ```
3. **Deploy Containerized Workloads to EKS**:
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name scidata-eks-cluster
   kubectl apply -f platform/cloud/kubernetes/
   ```
4. **Verify Public Ingress & SSL**:
   ```bash
   kubectl get ingress -n scidata-platform
   curl -f https://scidata.your-institution.edu/api/v1/health
   ```
5. **Capture Audit Evidence**:
   - Save cloud console screenshot, `kubectl get pods -o wide` log, and network latency benchmark.
