# Local deployment runbook

This runbook deploys only the demo. It does not configure a cloud provider or use production
credentials.

## Docker Compose

From the repository root, build and start the local image:

```powershell
docker compose up --build
Invoke-RestMethod http://127.0.0.1:8000/health
```

The Compose file stores the SQLite file in a named local volume. Stop the container with
`docker compose down`; the named volume remains. Removing that volume deletes the local demo
database, so first confirm it contains no evidence you need. No registry publishing is configured.

## Kubernetes example

Prerequisites: a disposable local Kubernetes cluster, `kubectl` pointed at the intended context,
and an image named `enterprise-cloud-platform-demo:local` available to that cluster. Build/load
the image using the workflow supported by your local cluster; do not assume Docker Desktop,
kind, or minikube.

Review the current context and the manifests before applying:

```powershell
kubectl config current-context
kubectl apply --dry-run=client -f infra/kubernetes/namespace.yaml
kubectl apply --dry-run=client -f infra/kubernetes/auth-deployment.yaml
kubectl apply --dry-run=client -f infra/kubernetes/auth-service.yaml
```

Only after verifying the cluster context and obtaining the operator's explicit approval:

```powershell
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/auth-deployment.yaml
kubectl apply -f infra/kubernetes/auth-service.yaml
kubectl -n ecp-demo get deployments,services,pods
```

These manifests use an ephemeral `emptyDir` for SQLite data. They are illustrative, not a
production persistence or availability design. To remove resources from the intended disposable
cluster, first inspect the namespace and confirm that deletion is authorized, then run
`kubectl delete namespace ecp-demo`.

The Terraform configuration is provider-free and creates no resources; see
`infra/terraform/README.md`.
