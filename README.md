# Kubernetes Flask Application — Minikube

A hands-on Kubernetes project demonstrating how to deploy, expose, scale, update, and roll back a Flask application using Kubernetes and Minikube.

## Kubernetes Learning Roadmap Completed So Far

```text
1. Kubernetes Architecture
        ↓
2. Pods
        ↓
3. Namespaces
        ↓
4. kubectl
        ↓
5. Deployment
        ↓
6. Service
        ↓
7. ConfigMap
        ↓
8. Secret
        ↓
9. Flask + PostgreSQL
        ↓
10. Kubernetes Networking
        ↓
11. Ingress
        ↓
12. HPA
        ↓
13. PV / PVC
        ↓
14. StatefulSet
```

## Architecture

```text
Local Mac
   |
   v
Minikube Cluster
   |
   +--> Flask Service --> Flask Deployment --> Flask Pods
   |
   +--> PostgreSQL Service --> PostgreSQL StatefulSet
                                      |
                                      v
                                postgres-0
                                      |
                                      v
                                  PVC / PV
                                      |
                                      v
                              Persistent Storage
```

## Kubernetes Object Relationships

### Flask — Stateless

```text
Deployment
    ↓
ReplicaSet
    ↓
Pods
    ↓
Container
```

### PostgreSQL — Stateful

```text
StatefulSet
    ↓
Pod
    ↓
Container
    ↓
VolumeMount
    ↓
PVC
    ↓
PV
    ↓
Persistent Storage
```

## Deployment

The Deployment defines the desired state of the Flask application.

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
          ports:
            - containerPort: 5006
```

Apply:

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl get deployments -n flask-dev
```

## ReplicaSet

A ReplicaSet maintains the desired number of Pods.

```text
Desired: 3
Current: 3
Ready:   3
```

```bash
kubectl get replicasets -n flask-dev
```

If a Pod is deleted, the ReplicaSet creates a replacement.

## Pods

Pods are the smallest deployable units in Kubernetes.

Example Flask Pods:

```text
flask-deployment-f6c9f76f4-cw974
flask-deployment-f6c9f76f4-dwx2c
```

Example StatefulSet Pod:

```text
postgres-0
```

Useful commands:

```bash
kubectl get pods -n flask-dev
kubectl get pods -n flask-dev -o wide
kubectl describe pod <pod-name> -n flask-dev
kubectl logs <pod-name> -n flask-dev
```

## Namespaces

The project uses:

```text
flask-dev
```

```bash
kubectl create namespace flask-dev
kubectl get namespaces
```

## kubectl

`kubectl` communicates with the Kubernetes API Server.

Examples:

```bash
kubectl get pods -n flask-dev
kubectl get deployments -n flask-dev
kubectl get services -n flask-dev
kubectl describe pod <pod-name> -n flask-dev
kubectl logs <pod-name> -n flask-dev
kubectl exec -it <pod-name> -n flask-dev -- bash
```

## Service

A Service provides a stable network endpoint for Pods.

Example:

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

Traffic flow:

```text
Client
  ↓
NodePort
  ↓
Service
  ↓
Flask Pod
  ↓
Flask Container :5006
```

## ConfigMap

ConfigMaps store non-sensitive configuration separately from application images.

```text
ConfigMap
   ↓
Pod
   ↓
Container
```

## Secret

Secrets provide sensitive configuration such as database credentials.

PostgreSQL receives its credentials from `flask-secret`.

```yaml
env:
  - name: POSTGRES_USER
    valueFrom:
      secretKeyRef:
        name: flask-secret
        key: DB_USER

  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: flask-secret
        key: DB_PASSWORD
```

## Flask + PostgreSQL

PostgreSQL runs on:

```text
5432
```

Database:

```text
employees
```

The database credentials are supplied through the Kubernetes Secret.

## Kubernetes Networking

Pods have IP addresses, but Pod IPs are not stable.

Therefore applications should normally communicate through Services rather than directly using Pod IPs.

## PostgreSQL Service

The PostgreSQL StatefulSet uses:

```text
postgres-service
```

It is a headless Service:

```text
ClusterIP: None
```

Check:

```bash
kubectl get svc postgres-service -n flask-dev
```

## StatefulSet DNS

The PostgreSQL Pod has stable identity:

```text
postgres-0
```

It can be reached using:

```text
postgres-0.postgres-service
```

Full DNS:

```text
postgres-0.postgres-service.flask-dev.svc.cluster.local
```

Test:

```bash
kubectl exec -n flask-dev <flask-pod> -- getent hosts postgres-0.postgres-service
```

## Persistent Storage

Persistent storage allows database data to survive Pod recreation.

```text
Pod
 ↓
Container
 ↓
VolumeMount
 ↓
PVC
 ↓
PV
 ↓
Persistent Storage
```

Memory rule:

```text
Pod → PVC → PV → Storage
```

## PersistentVolume (PV)

A PersistentVolume represents storage available to Kubernetes workloads.

Check:

```bash
kubectl get pv
```

## PersistentVolumeClaim (PVC)

A PVC requests storage.

Example:

```yaml
resources:
  requests:
    storage: 1Gi
```

Check:

```bash
kubectl get pvc -n flask-dev
```

## StatefulSet

PostgreSQL is stateful because its data must persist and the Pod needs stable identity.

A StatefulSet provides:

- Stable Pod identity
- Stable Pod naming
- Stable network identity
- Per-Pod persistent storage
- Ordered Pod creation and termination

Example:

```yaml
apiVersion: apps/v1
kind: StatefulSet

metadata:
  name: postgres
  namespace: flask-dev

spec:
  serviceName: postgres-service
  replicas: 1

  selector:
    matchLabels:
      app: postgres

  template:
    metadata:
      labels:
        app: postgres

    spec:
      containers:
        - name: postgres
          image: postgres:16

          ports:
            - containerPort: 5432

          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: flask-secret
                  key: DB_USER

            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: flask-secret
                  key: DB_PASSWORD

            - name: POSTGRES_DB
              value: employees

          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data

  volumeClaimTemplates:
    - metadata:
        name: postgres-storage

      spec:
        accessModes:
          - ReadWriteOnce

        storageClassName: standard

        resources:
          requests:
            storage: 1Gi
```

## StatefulSet Identity

Deployment Pods have dynamically generated names:

```text
flask-deployment-f6c9f76f4-cw974
```

StatefulSet Pods have predictable names:

```text
postgres-0
postgres-1
postgres-2
```

## volumeClaimTemplates

`volumeClaimTemplates` creates a separate PVC for each StatefulSet Pod.

With:

```yaml
replicas: 3
```

Kubernetes creates:

```text
postgres-0 → postgres-storage-postgres-0
postgres-1 → postgres-storage-postgres-1
postgres-2 → postgres-storage-postgres-2
```

Check:

```bash
kubectl get pvc -n flask-dev
```

## StatefulSet Persistence Test

The project tested persistence by creating data in PostgreSQL, deleting the Pod, and checking the data after Kubernetes recreated the Pod.

Example:

```sql
SELECT * FROM stateful_test;
```

Result:

```text
1 | StatefulSet storage survives Pod deletion
```

This demonstrated that deleting the Pod did not delete the persistent database data.

## Deployment vs StatefulSet

| Feature                 | Deployment     | StatefulSet                         |
| ----------------------- | -------------- | ----------------------------------- |
| Typical use             | Stateless apps | Stateful apps                       |
| Pod identity            | Dynamic        | Stable                              |
| Pod naming              | Generated      | Ordered                             |
| Example                 | Flask          | PostgreSQL                          |
| Stable network identity | Not guaranteed | Yes                                 |
| Per-Pod storage         | Not automatic  | Supported with volumeClaimTemplates |

Memory rule:

```text
Deployment  → Stateless
StatefulSet → Stateful
```

## Ingress

Ingress provides HTTP/HTTPS routing into Kubernetes Services.

```text
Browser
  ↓
Ingress
  ↓
Service
  ↓
Pods
```

## HPA

Horizontal Pod Autoscaler can adjust replicas based on resource metrics such as CPU utilization.

```text
Traffic increases
       ↓
CPU utilization increases
       ↓
Metrics Server
       ↓
HPA
       ↓
Deployment
       ↓
More Pods
```

## Desired State and Reconciliation

Kubernetes compares desired state with actual state.

```text
Desired: 3 Pods
Actual:  2 Pods
     ↓
Controller detects difference
     ↓
New Pod created
     ↓
Actual: 3 Pods
```

## Application Traffic vs Kubernetes Control Flow

### Application traffic

```text
Client
  ↓
Ingress / Service
  ↓
Pod
  ↓
Container
  ↓
Flask
```

### Kubernetes control flow

```text
kubectl
  ↓
API Server
  ↓
Controllers / Scheduler
  ↓
Kubelet
  ↓
Pod
  ↓
Container
```

## Docker

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

Build:

```bash
docker build -t kubernetes-flask:v2 .
```

Load into Minikube:

```bash
minikube image load kubernetes-flask:v2
```

## Run the Project

Start Minikube:

```bash
minikube start
kubectl cluster-info
kubectl get nodes
```

Create namespace:

```bash
kubectl create namespace flask-dev
```

Apply Kubernetes resources:

```bash
kubectl apply -f kubernetes/
```

Access Flask:

```bash
minikube service flask-service -n flask-dev --url
```

Test:

```bash
curl <service-url>
curl <service-url>/health
```

## Scaling

```bash
kubectl scale deployment flask-deployment --replicas=5 -n flask-dev
kubectl get pods -n flask-dev
```

Scale back:

```bash
kubectl scale deployment flask-deployment --replicas=3 -n flask-dev
```

## Rolling Updates

```bash
kubectl set image deployment/flask-deployment flask=kubernetes-flask:v2 -n flask-dev

kubectl rollout status deployment/flask-deployment -n flask-dev
kubectl rollout history deployment/flask-deployment -n flask-dev
```

## Rollback

```bash
kubectl rollout undo deployment/flask-deployment -n flask-dev
kubectl rollout status deployment/flask-deployment -n flask-dev
```

## Useful Debugging Commands

```bash
kubectl get pods -n flask-dev
kubectl get pods -n flask-dev -o wide
kubectl describe pod <pod-name> -n flask-dev
kubectl logs <pod-name> -n flask-dev
kubectl exec -it <pod-name> -n flask-dev -- bash
kubectl get svc -n flask-dev
kubectl get endpoints -n flask-dev
kubectl get endpointslice -n flask-dev
kubectl get pvc -n flask-dev
kubectl get pv
kubectl get statefulset -n flask-dev
```

## PostgreSQL Commands

Connect:

```bash
kubectl exec -it -n flask-dev postgres-0 -- psql -U Ayush -d employees
```

Useful commands:

```sql
\l
\dt
SELECT * FROM stateful_test;
\q
```

## Technologies Used

- Kubernetes
- Minikube
- Docker
- Docker Desktop
- Python
- Flask
- PostgreSQL
- kubectl
- YAML

## What I Learned So Far

1. Kubernetes architecture and control flow
2. Pods and containers
3. Namespaces
4. kubectl
5. Deployments and ReplicaSets
6. Desired state and reconciliation
7. Services and NodePort
8. ConfigMaps
9. Secrets
10. Flask + PostgreSQL
11. Kubernetes networking and DNS
12. Ingress
13. HPA
14. PersistentVolumes and PersistentVolumeClaims
15. VolumeMounts and persistent storage
16. StatefulSets
17. Stable StatefulSet Pod identity
18. volumeClaimTemplates and per-Pod PVCs
19. StatefulSet persistence after Pod deletion
20. Rolling updates, revision history, and rollback
21. Difference between Deployment and StatefulSet

## Current Kubernetes Learning Progress

```text
✅ Kubernetes Architecture
✅ Pods
✅ Namespaces
✅ kubectl
✅ Deployment
✅ ReplicaSet
✅ Service
✅ ConfigMap
✅ Secret
✅ Flask + PostgreSQL
✅ Kubernetes Networking
✅ Ingress
✅ HPA
✅ PV / PVC
✅ StatefulSet

⬜ Helm
⬜ RBAC
⬜ Network Policies
⬜ Probes / Production Health Checks
⬜ Advanced Networking
⬜ GitOps
⬜ AWS EKS
⬜ CI/CD
```

## Next Learning Topics

- Helm
- RBAC
- Network Policies
- Readiness Probes
- Liveness Probes
- Resource Requests and Limits
- Advanced StatefulSet concepts
- Kubernetes Security
- GitOps with Argo CD
- AWS EKS
- Production Kubernetes architecture
- CI/CD

## Learning Goal

This project is part of a practical DevOps and Kubernetes learning path focused on building production-oriented skills through hands-on implementation.

The goal is to understand not only what Kubernetes resources are, but also how they interact during deployment, scheduling, scaling, networking, service discovery, configuration, secret management, persistent storage, stateful workloads, rolling updates, failures, and recovery.

add helm
add readme
