terraform {
  required_version = "= 1.5.7"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.99.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# -----------------------------
# Resource Group
# -----------------------------
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.usecase}-${var.env}-${var.owner}"
  location = var.location
}

# -----------------------------
# Azure Container Registry
# -----------------------------
resource "azurerm_container_registry" "acr" {
  name                = "acr${var.usecase}${var.env}${var.owner}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true
}

# -----------------------------
# Container App Environment
# -----------------------------
resource "azurerm_container_app_environment" "cae" {
  name                = "cae-${var.usecase}-${var.env}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
}

# -----------------------------
# Container App (VALID for 3.99.0)
# -----------------------------
resource "azurerm_container_app" "app" {
  name                         = "app-${var.usecase}-${var.env}"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.cae.id

  revision_mode = "Single"

  identity {
    type = "SystemAssigned"
  }

  template {
    container {
      name   = "app"
      image  = "${azurerm_container_registry.acr.login_server}/${var.image_name}:latest"

      resources {
        cpu    = 1.0
        memory = "2Gi"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }
}

# -----------------------------
# ACR Pull Permission
# -----------------------------
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.app.identity[0].principal_id
}
