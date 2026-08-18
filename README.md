# Kubernetes Flask Application — Minikube

A hands-on Kubernetes project demonstrating how to deploy, expose, scale, update, and roll back a Flask application using Kubernetes and Minikube.

This project was built to understand Kubernetes fundamentals through practical implementation rather than only theory.

---

## 📌 Project Overview

This project deploys a containerized Flask application to a local Kubernetes cluster running on Minikube.

The project demonstrates:

- Kubernetes Namespace
- Pods
- Deployments
- ReplicaSets
- Services
- NodePort
- Kubernetes desired state
- Replica scaling
- Rolling updates
- Deployment revision history
- Rollbacks
- Pod logs
- Pod execution
- Basic application health endpoint

---

## 🏗️ Architecture

```text
                         Local Mac
                            |
                            | HTTP Request
                            | localhost:<minikube-port>
                            v
                    +----------------+
                    |   Minikube     |
                    |    Node        |
                    +----------------+
                            |
                            | NodePort
                            v
                    +----------------+
                    | Flask Service  |
                    |    NodePort    |
                    +----------------+
                            |
                     selector: app=flask
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        +---------+    +---------+    +---------+
        | Flask   |    | Flask   |    | Flask   |
        | Pod     |    | Pod     |    | Pod     |
        +---------+    +---------+    +---------+
             |              |              |
             v              v              v
        Flask Container :5006
```

---

## 🔄 Kubernetes Object Relationship

```text
Deployment
    |
    v
ReplicaSet
    |
    v
Pods
    |
    v
Container
```

### Deployment

The Deployment defines the desired state of the application, including:

- Number of replicas
- Pod template
- Container image
- Rolling update strategy

### ReplicaSet

The ReplicaSet ensures that the desired number of Pods exists.

For example:

```text
Desired: 3
Current: 3
Ready:   3
```

If a Pod is deleted, the ReplicaSet creates a replacement Pod.

### Pod

The Pod is the Kubernetes execution unit that contains the Flask container.

### Container

The container runs the Flask application on port `5006`.

---

# 📁 Project Structure

```text
kubernetes-flask-minikube-v2/
│
├── app/
│   └── app.py
│
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🐍 Flask Application

The Flask application provides two endpoints.

## Application Endpoint

```text
GET /
```

Example response:

```json
{
  "application": "Kubernetes Flask Demo",
  "version": "v2",
  "pod": "flask-deployment-xxxx",
  "status": "running"
}
```

The Pod hostname is returned so that Kubernetes Service routing can be observed.

## Health Endpoint

```text
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

# 🐳 Docker

The Flask application is containerized using Docker.

Example Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

EXPOSE 5006

CMD ["python", "app.py"]
```

---

# ☸️ Kubernetes Namespace

A dedicated namespace is used for the project:

```text
flask-dev
```

Create it with:

```bash
kubectl create namespace flask-dev
```

Check namespaces:

```bash
kubectl get namespaces
```

---

# 🚀 Run the Project

## 1. Start Minikube

```bash
minikube start
```

Verify the cluster:

```bash
kubectl cluster-info
```

Check nodes:

```bash
kubectl get nodes
```

---

## 2. Build the Docker Image

Build the Flask application image:

```bash
docker build -t kubernetes-flask:v1 .
```

For the updated application:

```bash
docker build -t kubernetes-flask:v2 .
```

---

## 3. Load the Image into Minikube

Because this project uses a local Minikube cluster, the image needs to be available inside Minikube.

```bash
minikube image load kubernetes-flask:v2
```

Verify:

```bash
minikube image ls | grep kubernetes-flask
```

---

# 📦 Deployment

The Deployment is defined in:

```text
kubernetes/deployment.yaml
```

Example:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: flask-deployment
  namespace: flask-dev

spec:
  replicas: 3

  selector:
    matchLabels:
      app: flask

  template:
    metadata:
      labels:
        app: flask

    spec:
      containers:
        - name: flask
          image: kubernetes-flask:v2
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5006
```

Apply the Deployment:

```bash
kubectl apply -f kubernetes/deployment.yaml
```

Check the Deployment:

```bash
kubectl get deployments -n flask-dev
```

Expected:

```text
NAME               READY   UP-TO-DATE   AVAILABLE
flask-deployment   3/3     3            3
```

---

# 🔍 ReplicaSet

Check ReplicaSets:

```bash
kubectl get replicasets -n flask-dev
```

Example:

```text
NAME                          DESIRED   CURRENT   READY
flask-deployment-695cddff49   3         3         3
```

The Deployment manages the ReplicaSet, and the ReplicaSet manages the Pods.

---

# 🧩 Pods

Check Pods:

```bash
kubectl get pods -n flask-dev
```

For detailed information:

```bash
kubectl get pods -n flask-dev -o wide
```

Example:

```text
NAME                                READY   STATUS
flask-deployment-xxxx-xxxxx         1/1     Running
flask-deployment-xxxx-xxxxx         1/1     Running
flask-deployment-xxxx-xxxxx         1/1     Running
```

---

# 📜 Pod Logs

View application logs:

```bash
kubectl logs <pod-name> -n flask-dev
```

---

# 🖥️ Execute Commands Inside a Pod

Example:

```bash
kubectl exec <pod-name> -n flask-dev -- python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5006/health').read().decode())"
```

Expected:

```json
{ "status": "healthy" }
```

---

# 🌐 Kubernetes Service

The Flask application is exposed using a NodePort Service.

Service configuration:

```yaml
apiVersion: v1
kind: Service

metadata:
  name: flask-service
  namespace: flask-dev

spec:
  selector:
    app: flask

  ports:
    - port: 5006
      targetPort: 5006
      nodePort: 30006

  type: NodePort
```

Apply it:

```bash
kubectl apply -f kubernetes/service.yaml
```

Check the Service:

```bash
kubectl get service -n flask-dev
```

---

# 🔀 Service Traffic Flow

```text
Mac
 |
 | localhost:<Minikube URL>
 v
Minikube Node
 |
 | NodePort
 v
Service
 |
 | selector: app=flask
 v
One Flask Pod
 |
 v
Flask Container :5006
```

The Service provides a stable endpoint while individual Pod IP addresses can change.

---

# 🌍 Access the Application

Get the Minikube Service URL:

```bash
minikube service flask-service -n flask-dev --url
```

Example:

```text
http://127.0.0.1:58300
```

Test the application:

```bash
curl http://127.0.0.1:58300
```

Test the health endpoint:

```bash
curl http://127.0.0.1:58300/health
```

---

# 📈 Scaling

Scale from 3 to 5 replicas:

```bash
kubectl scale deployment flask-deployment --replicas=5 -n flask-dev
```

Check:

```bash
kubectl get deployment -n flask-dev
kubectl get pods -n flask-dev
```

The existing ReplicaSet adjusts its desired number of Pods.

Scale back to 3:

```bash
kubectl scale deployment flask-deployment --replicas=3 -n flask-dev
```

---

# 🔄 Rolling Updates

The original application used:

```text
kubernetes-flask:v1
```

The updated application uses:

```text
kubernetes-flask:v2
```

The image can be updated with:

```bash
kubectl set image deployment/flask-deployment flask=kubernetes-flask:v2 -n flask-dev
```

Kubernetes creates a new ReplicaSet for the new Pod template.

Conceptually:

```text
Old ReplicaSet
     |
     | v1
     v
3 old Pods

        ↓ Rolling Update

New ReplicaSet
     |
     | v2
     v
3 new Pods
```

Check the rollout:

```bash
kubectl rollout status deployment/flask-deployment -n flask-dev
```

---

# 🕐 Deployment History

View Deployment revisions:

```bash
kubectl rollout history deployment/flask-deployment -n flask-dev
```

Inspect a revision:

```bash
kubectl rollout history deployment/flask-deployment --revision=2 -n flask-dev
```

---

# ↩️ Rollback

A deliberately broken `v3` image was used during the learning exercise to demonstrate rollback.

The broken version produced:

```text
HTTP 500 Internal Server Error
```

while Kubernetes still considered the containers running because no application-level readiness probe had been configured yet.

Rollback:

```bash
kubectl rollout undo deployment/flask-deployment -n flask-dev
```

Verify:

```bash
kubectl rollout status deployment/flask-deployment -n flask-dev
kubectl get replicasets -n flask-dev
curl http://127.0.0.1:58300
```

The application returned version `v2`.

```text
v2
 ↓
v3 ❌
 ↓
rollback
 ↓
v2 ✅
```

---

# 🎯 Key Kubernetes Concepts Learned

## Pods

Smallest deployable unit in Kubernetes.

## Deployment

Manages the desired state of an application and handles ReplicaSets and rolling updates.

## ReplicaSet

Maintains the desired number of Pods.

## Service

Provides a stable endpoint for accessing Pods.

## NodePort

Exposes a Service through a port on the Kubernetes node.

## Namespace

Provides logical isolation within the Kubernetes cluster.

## Desired State

Example:

```yaml
replicas: 3
```

## Reconciliation

```text
Desired: 3 Pods
Actual:  2 Pods
       ↓
ReplicaSet creates another Pod
       ↓
Actual: 3 Pods
```

## Rolling Update

Gradually replaces old Pods with new Pods when the Pod template changes.

## Rollback

Returns a Deployment to a previous revision.

---

# 🧠 Application Traffic vs Kubernetes Control Flow

### Application traffic

```text
Mac
 ↓
NodePort
 ↓
Service
 ↓
Pod
 ↓
Container
 ↓
Flask
```

### Kubernetes control/reconciliation flow

```text
kubectl
 ↓
API Server
 ↓
Controllers / Scheduler
 ↓
Node
 ↓
Kubelet
 ↓
Pod
 ↓
Container
```

The API Server, etcd, controllers, scheduler, and kubelet are part of Kubernetes' control and management processes; they are not the normal path taken by an HTTP request to the Flask application.

---

# 🧪 Commands Used

```bash
# Cluster
minikube start
kubectl cluster-info
kubectl get nodes

# Namespace
kubectl create namespace flask-dev
kubectl get namespaces

# Deployments
kubectl apply -f kubernetes/deployment.yaml
kubectl get deployments -n flask-dev

# ReplicaSets
kubectl get replicasets -n flask-dev

# Pods
kubectl get pods -n flask-dev
kubectl get pods -n flask-dev -o wide
kubectl describe pod <pod-name> -n flask-dev
kubectl logs <pod-name> -n flask-dev
kubectl exec <pod-name> -n flask-dev -- <command>

# Scaling
kubectl scale deployment flask-deployment --replicas=5 -n flask-dev

# Service
kubectl apply -f kubernetes/service.yaml
kubectl get service -n flask-dev
minikube service flask-service -n flask-dev --url

# Rolling updates
kubectl set image deployment/flask-deployment flask=kubernetes-flask:v2 -n flask-dev
kubectl rollout status deployment/flask-deployment -n flask-dev

# History
kubectl rollout history deployment/flask-deployment -n flask-dev

# Rollback
kubectl rollout undo deployment/flask-deployment -n flask-dev
```

---

# 🛠️ Technologies Used

- Kubernetes
- Minikube
- Docker
- Docker Desktop
- Python
- Flask
- kubectl
- YAML

---

# 📚 What I Learned

1. How Pods run containers
2. How Deployments manage application workloads
3. How ReplicaSets maintain the desired number of Pods
4. How Kubernetes reconciles desired and actual state
5. Why Pod IPs should not be treated as permanent endpoints
6. How Services provide stable connectivity
7. How NodePort exposes applications outside the cluster
8. How Deployments perform rolling updates
9. How Kubernetes maintains Deployment revision history
10. How failed releases can be rolled back
11. The difference between container state and application health
12. The importance of keeping Kubernetes YAML synchronized with the intended state

---

# 🚧 Future Improvements

- Readiness probes
- Liveness probes
- ConfigMaps
- Secrets
- PostgreSQL
- Persistent Volumes
- Persistent Volume Claims
- Ingress
- Horizontal Pod Autoscaler
- StatefulSets
- Helm
- RBAC
- Network Policies
- AWS EKS
- GitHub Actions CI/CD

---

## 👨‍💻 Learning Goal

This project is part of a practical DevOps and Kubernetes learning path focused on building production-oriented skills through hands-on projects.

The goal is to understand not only what Kubernetes objects are, but also how they interact during deployment, scaling, service discovery, rolling updates, failures, and recovery.
