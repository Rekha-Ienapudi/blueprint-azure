🚀 How to run everything (step‑by‑step)
✅ Step 1 — Commit your variables.tf
Whenever you update:

Code
infra/variables.tf
GitHub Actions automatically runs:

Generate Workflow Inputs

This workflow:

Parses your Terraform variables

Builds the workflow inputs

Updates .github/workflows/deploy.yml

Commits the new workflow

You don’t run this manually — it triggers on push.

✅ Step 2 — Open GitHub Actions → Run the Deploy Workflow
Go to:

Code
GitHub → Actions → Deploy Azure Infra (Terraform Only)
You will now see one input field per Terraform variable, for example:

subscription_id

location

environment

project_name

etc.

These fields are generated automatically from your variables.tf.

Fill them in and click:

Run workflow

🎯 Step 3 — Terraform Plan runs
The workflow:

Logs into Azure

Builds workflow.auto.tfvars from your inputs

Runs terraform init

Runs terraform plan

You’ll see the plan output in the Actions logs.

🛑 Step 4 — Manual approval (environment gate)
Your second job:

Code
terraform-apply
is protected by:

yaml
environment:
  name: manual-approval
So GitHub will show an approval button:

"Review deployments" → Approve"

🚀 Step 5 — Terraform Apply runs
Once approved:

Terraform initializes again

Applies the plan

Deploys your Azure infrastructure
