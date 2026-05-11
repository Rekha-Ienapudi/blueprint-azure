locals {
  standard_tags = merge(
    var.tags,
    {
      usecase = var.usecase
      env     = var.env
      owner   = var.owner
    }
  )
}

module "rg" {
  source = "git::https://github.com/Rekha-Ienapudi/terraform-modules.git//resource-group"

  name     = "rg-${var.usecase}-${var.env}-${var.owner}"
  location = var.location
  tags     = local.standard_tags
}

module "acr" {
  source = "git::https://github.com/<ORG>/<REPO>.git//acr"

  name                = "acr${var.usecase}${var.env}${var.owner}"
  location            = var.location
  resource_group_name = module.rg.name
  tags                = local.standard_tags
}

module "cae" {
  source = "git::https://github.com/Rekha-Ienapudi/terraform-modules.git//container-app-env"

  name                = "cae-${var.usecase}-${var.env}"
  location            = var.location
  resource_group_name = module.rg.name
  tags                = local.standard_tags
}

module "app" {
  source = "git::https://github.com/Rekha-Ienapudi/terraform-modules.git//container-app"

  name                = "app-${var.usecase}-${var.env}"
  resource_group_name = module.rg.name
  environment_id      = module.cae.id

  image              = "${module.acr.login_server}/${var.image_name}:latest"
  registry_server    = module.acr.login_server
  registry_username  = module.acr.username
  registry_password  = module.acr.password

  tags = local.standard_tags
}

module "acr_pull" {
  source = "git::https://github.com/Rekha-Ienapudi/terraform-modules.git//role-assignment"

  scope        = module.acr.id
  role         = "AcrPull"
  principal_id = module.app.principal_id
}

output "acr_login_server" {
  value = module.acr.login_server
}
