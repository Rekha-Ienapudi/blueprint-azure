🚀 How to run everything now
▶️ A. Update your Terraform Code in infra folder
Go to:

infra-> main.tf and add the required module pull adding the required variables
Example
module "rg" {
  source = "git::https://github.com/Rekha-Ienapudi/terraform-modules.git//resource-group"

  name     = "rg-${var.usecase}-${var.env}-${var.owner}"
  location = var.location
  tags     = local.standard_tags
}

Add the variable defaults as required for your usecase in variables.tf
Example
variable "usecase" {
  description = "Usecase name"
  type        = string
  default     = "web-apitest"   # ✔ 3–20 chars, lowercase, alphanumeric + hyphens

  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.usecase))
    error_message = "usecase must be 3–20 chars, lowercase alphanumeric or hyphens."
  }
}

Code
GitHub → Actions → Generate Workflow Inputs → Run workflow
This regenerates:

Code
.github/workflows/deploy.yml
with one input per Terraform variable.

▶️ B. Deploy your Terraform infra
Go to:

Code
GitHub → Actions → Deploy Azure Infra (Terraform Only) → Run workflow
You will get Azure Device authentication finish that and the workflow will continue.
Once the plan succeeds the workflow will wait for manual approval and will deploy the Infra to Azure
