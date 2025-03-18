# KUBERNETES CLUSTER & BLOCKCHAIN-BASED SYSTEM


# K3d Cluster Setup Documentation

## Prerequisites
Before starting, ensure your system is updated and has the necessary dependencies installed.

1. Update and Upgrade System:
    ```sh
    sudo apt update && sudo apt upgrade -y
    ```

2. Install Required Packages:
    ```sh
    sudo apt install -y docker.io git curl make python3-pip
    ```

3. Install K3d (Kubernetes in Docker):
    ```sh
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    ```

4. Install Helm (Kubernetes Package Manager):
    ```sh
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    ```

5. Start and Enable Docker:
    ```sh
    sudo systemctl enable docker && sudo systemctl start docker
    ```

6. Add User to Docker Group (Optional, for non-root usage):
    ```sh
    sudo usermod -aG docker $USER && newgrp docker
    ```

## Creating a K3d Cluster
To create a Kubernetes cluster using K3d with two agent nodes:
```sh
k3d cluster create ai-cluster \
  --agents 2 \
  --k3s-arg "--disable=traefik@server:0" \
  --agents-memory 4096MB \
  --servers-memory 4096MB \
  --registry-create myregistry
```

## Verifying the Cluster
After creation, verify that the cluster is running:
```sh
kubectl cluster-info
kubectl get nodes
```

### Notes
- `--disable=traefik@server:0`: Disables the built-in Traefik ingress controller.
- `--agents 2`: Creates 2 agent (worker) nodes.
- `--agents-memory 4096MB`: Allocates 4GB memory per agent.
- `--servers-memory 4096MB`: Allocates 4GB memory per server node.
- `--registry-create myregistry`: Creates a local container registry for the cluster.

This setup provides a lightweight Kubernetes cluster using K3d, suitable for local development and testing.

## Install Core Components

Check the status of the deployed pods:
```sh
kubectl --namespace default get pods -l "release=monitoring"
```

2. Get the Grafana admin password:
```sh
kubectl --namespace default get secrets monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

3. Access Grafana:
To access Grafana locally, use port forwarding. Run these commands:
```sh
export POD_NAME=$(kubectl --namespace default get pod -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=monitoring" -o name)
kubectl --namespace default port-forward $POD_NAME 3000
```

This will forward the Grafana port to localhost:3000, and you can access it through your browser at http://localhost:3000.

Once your Grafana pod is running, you can access the Grafana dashboard using the following credentials:
- Username: admin
- Password: prom-operator

## AI-Powered Autoscaling Setup

Install Kubeflow Pipelines:
```sh
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/base/crds?ref=release-1.8"
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=release-1.8"
kubectl get pods -n kubeflow
```
Wait until all pods are in Running state.

Access UI:
```sh
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
Go to: http://localhost:8080

Deploy your machine learning application:
```sh
kubectl apply -f ml-app.yaml
kubectl apply -f ml-app-service.yaml
```

Test the Deployment:
Get the external IP:
```sh
kubectl get svc scaling-model-service -o wide
```
Test API:
```sh
curl -X POST "http://EXTERNAL_IP/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [1, 50]}'
```
If successful, you will see a response like:
```json
{
  "prediction": [2.02]
}
```

## Implement Blockchain for Immutable Logs and Transaction Validation using Ethereum

This setup describes a blockchain-based logging system using Ganache (Ethereum Testnet) and Kubernetes. It includes the Python script for logging transactions, Kubernetes deployment configuration, and a Dockerfile to containerize the logger.

### Blockchain-Based Logging System with Ganache & Kubernetes (K3d)
This setup deploys a blockchain-based logging system using Ganache (Ethereum Testnet) and K3d (Kubernetes in Docker). It includes:
- A Python script for logging blockchain transactions
- Kubernetes manifests for deployment
- A Dockerfile to containerize the logger

### Deploy Ganache (Ethereum Testnet) in Kubernetes
```sh
kubectl apply -f ganache-pod.yaml
kubectl apply -f ganache-service.yaml
```

### Deploy Blockchain Logger
```sh
kubectl apply -f blockchain-logger-deployment.yaml
```

### Components
1. **Python Blockchain Logger (blockchain-logger.py)**: Logs transactions to the Ethereum testnet (Ganache).
2. **Dockerfile**: Containerizes the Python logger for Kubernetes deployment.
3. **Kubernetes Manifests**: Includes deployment configurations for Ganache and Logger.

### Verification
Check Ganache Logs:
```sh
kubectl logs -l app=ganache
```

Check Logger Service:
```sh
kubectl logs -l app=blockchain-logger
```

Inside the pod, run the Python script to log a test transaction:
```sh
python3 logger.py
```

Expected output:
```plaintext
[INFO] Sending test transaction...
[INFO] Transaction Hash: 0xabcdef123456...
[INFO] Transaction Confirmed!
```

## OPA Gatekeeper - Enforce Labels Policy
This repository contains Kubernetes OPA Gatekeeper policies to enforce mandatory labels on resources.

### Prerequisites
- Kubernetes cluster
- `kubectl` configured for the cluster
- Helm installed

### Installation
1. Install Gatekeeper:
    ```sh
    helm install gatekeeper gatekeeper \
      --repo https://open-policy-agent.github.io/gatekeeper/charts \
      --namespace gatekeeper-system \
      --create-namespace
    ```

2. Deploy the Constraint Template:
    ```sh
    cat <<EOF | kubectl apply -f -
    apiVersion: templates.gatekeeper.sh/v1beta1
    kind: ConstraintTemplate
    metadata:
      name: k8srequiredlabels
    spec:
      crd:
        spec:
          names:
            kind: K8sRequiredLabels
          validation:
            openAPIV3Schema:
              properties:
                labels:
                  type: array
                  items:
                    type: string
      targets:
        - target: admission.k8s.gatekeeper.sh
          rego: |
            package k8srequiredlabels
            violation[{"msg": msg}] {
              provided := {label | input.review.object.metadata.labels[label]}
              required := {label | label := input.parameters.labels[_]}
              missing := required - provided
              count(missing) > 0
              msg := sprintf("Missing labels: %v", [missing])
            }
    EOF
    ```

3. Deploy the Constraint:
    Create `enforce-labels.yaml` with the following content:
    ```yaml
    apiVersion: constraints.gatekeeper.sh/v1beta1
    kind: K8sRequiredLabels
    metadata:
      name: enforce-labels
    spec:
      match:
        kinds:
          - apiGroups: [""]
            kinds: ["Pod"]
      parameters:
        labels: ["app", "env"]
    ```
    Apply it using:
    ```sh
    kubectl apply -f enforce-labels.yaml
    ```

### Verification
Check if the constraint is applied:
```sh
kubectl get constraints
```

Test 1: Pod without Labels (Should Fail)
```sh
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: nginx
    image: nginx
EOF
```

Test 2: Pod with Required Labels (Should Succeed)
```sh
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: test-pod-valid
  labels:
    app: my-app
    env: dev
spec:
  containers:
  - name: nginx
    image: nginx
EOF
```

### Use Case & Benefits
- ✅ Ensures all resources follow organizational policies.
- ✅ Helps enforce best practices for resource labeling.
- ✅ Improves security and governance in Kubernetes clusters.

## Monitor Kubernetes Cluster with Prometheus & Grafana
This guide covers:
- ✅ Setting up Prometheus to collect cluster metrics
- ✅ Deploying Grafana for visualization
- ✅ Monitoring Kubernetes nodes, pods, CPU, memory, and more

### Installation
1. Install Prometheus and Grafana using Helm:
    ```sh
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    helm install prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
    ```

This will install:
- Prometheus (for metric collection)
- Alertmanager (for alerting)
- Grafana (for visualization)

### Access Prometheus and Grafana
Prometheus Dashboard:
To access Prometheus UI, run:
```sh
kubectl port-forward -n monitoring svc/prometheus-stack-prometheus 9090:9090
```
Open http://localhost:9090 to view Prometheus metrics.

Grafana Dashboard:
Get the Grafana admin password:
```sh
kubectl get secret --namespace monitoring prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

Expose Grafana:
```sh
kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80
```
Open http://localhost:3000, use `admin` as username and the retrieved password.

### Configure Grafana with Prometheus
Go to Grafana UI → Configuration → Data Sources
Select Prometheus
Set the URL to:
```plaintext
http://prometheus-stack-prometheus.monitoring.svc.cluster.local:9090
```
Click Save & Test

### Import Prebuilt Kubernetes Dashboards
Grafana provides ready-to-use dashboards for Kubernetes:
- Kubernetes Cluster Monitoring (Dashboard ID: 315)
- Node Exporter Full (Dashboard ID: 1860)

To import a dashboard:
Go to Grafana UI → Dashboards → Import
Enter the Dashboard ID (e.g., 315)
Select Prometheus as the data source
Click Import

### Enable Node Exporter for System Metrics
To monitor node-level CPU, memory, and disk usage, install node-exporter:
```sh
kubectl apply -f https://raw.githubusercontent.com/prometheus/node_exporter/master/examples/kubernetes/node-exporter-daemonset.yaml
```




## Video Guide
For a detailed video guide, please refer to the following link:
[Video Guide](https://drive.google.com/file/d/10RiDsMAuUJbJDAYytMgSY7Hz7M_JrZ12/view?usp=sharing)
```
