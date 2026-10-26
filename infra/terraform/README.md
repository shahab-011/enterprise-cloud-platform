# Terraform planning scaffold

This Terraform configuration is intentionally provider-free: `terraform plan` and
`terraform apply` only evaluate and display local application metadata. It creates no cloud
resources, opens no cloud connection, and incurs no cost. Cloud provider assumptions and
resource definitions are deliberately omitted until a separately approved deployment design
exists.

With Terraform 1.5 or newer:

```powershell
terraform -chdir=infra/terraform init
terraform -chdir=infra/terraform validate
terraform -chdir=infra/terraform plan
```

The output documents the naming convention `<project>-<environment>` and the corresponding
Kubernetes namespace and image. If real resources are later added, first document the provider,
required credentials, resource costs, data classification, and cleanup procedure. Review a plan
and obtain explicit approval before any apply operation. Never commit state files or credentials.
