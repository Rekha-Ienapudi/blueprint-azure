🚀 How to run everything now
▶️ A. Generate workflow inputs manually
Go to:

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
You will now see all variables from variables.tf as input fields.
