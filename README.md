# Bitwarden External Secrets for Kubernetes

![Bitwarden + External Secrets](https://img.shields.io/badge/Bitwarden-External%20Secrets-175DDC?style=for-the-badge&logo=bitwarden&logoColor=white)

A Kubernetes operator that integrates [Bitwarden](https://bitwarden.com)/[Vaultwarden](https://github.com/dani-garcia/vaultwarden) with the [External Secrets Operator](https://external-secrets.io/) to securely manage your Kubernetes secrets.

## 🚀 Quick Start

```bash
# Step 1: Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \ 
  -n external-secrets --create-namespace

# Step 2: Install Bitwarden External Secrets
helm repo add eznix86 https://eznix86.github.io/bitwarden-external-secrets
helm install bitwarden-external-secrets eznix86/bitwarden-external-secrets \ 
  -n bitwarden-external-secrets --create-namespace \ 
  --set secrets.bw_clientid="YOUR_CLIENT_ID" \ 
  --set secrets.bw_clientsecret="YOUR_CLIENT_SECRET" \ 
  --set secrets.bw_password="YOUR_MASTER_PASSWORD"

# Step 3: Verify installation
kubectl get pods -n external-secrets
kubectl get pods -n bitwarden-external-secrets
```

## 📖 Overview

This operator allows you to:
- Use your Bitwarden vault as a secure backend for Kubernetes secrets
- Automatically sync secrets from Bitwarden to Kubernetes
- Leverage the External Secrets Operator for secret rotation and management

> [!NOTE]
> This operator is different from the Bitwarden Kubernetes Operator. It uses Bitwarden as a source for secrets rather than managing Bitwarden itself.

## 🔧 Installation

### Prerequisites

- Kubernetes cluster (v1.19+)
- Helm v3
- Bitwarden or Vaultwarden account with API credentials

### Step 1: Install External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm install external-secrets external-secrets/external-secrets \
  -n external-secrets \
  --create-namespace

# Verify External Secrets installation
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=external-secrets \
  -n external-secrets --timeout=60s
```

### Step 2: Install Bitwarden External Secrets

```bash
helm repo add eznix86 https://eznix86.github.io/bitwarden-external-secrets
helm repo update

helm install bitwarden-external-secrets eznix86/bitwarden-external-secrets \
  -n bitwarden-external-secrets \
  --create-namespace \
  --set secrets.bw_clientid="YOUR_CLIENT_ID" \
  --set secrets.bw_clientsecret="YOUR_CLIENT_SECRET" \
  --set secrets.bw_password="YOUR_MASTER_PASSWORD" \
  --set secrets.bw_host="https://bitwarden.com" # or your Vaultwarden instance URL

# Verify Bitwarden External Secrets installation
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=bitwarden-external-secrets \
  -n bitwarden-external-secrets --timeout=60s

kubectl wait --for=condition=ready pod -l app=bitwarden-operator \
  -n bitwarden-external-secrets --timeout=60s
```

> **Note:** You can find `bw_clientid` and `bw_clientsecret` in your Bitwarden/Vaultwarden account settings under API Key.

## 📝 Usage

### Creating a BitwardenSecret

Create a YAML file with your BitwardenSecret definition:

```yaml
apiVersion: bitwarden.external-secrets.io/v1alpha1
kind: BitwardenSecret
metadata:
  name: my-application-secrets  # Name of the BitwardenSecret resource
spec:
  namespace: my-application     # Target namespace for the generated K8s Secret
  secrets:
    # Each key will be created in the resulting Secret
    db-username:
      itemRef:
        id: "your-bitwarden-item-id"   # On Bitwarden Web UI, Grab the itemId from the URL
        type: login                    # Type of Bitwarden item
        property: username             # Property to extract from the item
    
    db-password:
      itemRef:
        id: "your-bitwarden-item-id"
        type: login
        property: password
        
    ssh-key:
      itemRef:
        id: "your-ssh-key-item-id"
        type: sshKey
        property: privateKey           # Can be privateKey, publicKey, or keyFingerprint
```

Apply the configuration:

```bash
kubectl apply -f my-bitwarden-secret.yaml
```

The operator will automatically create a Kubernetes Secret with the specified values from your Bitwarden vault.

## 🔑 Supported Bitwarden Item Types

| Bitwarden Item Type | Supported Properties | Description |
|---------------------|----------------------|-------------|
| `login`             | `username`, `password` | Login credentials |
| `note`              | (entire note content) | Secure notes |
| `field`             | (custom field names) | Custom fields from any item |
| `sshKey`            | `privateKey`, `publicKey`, `keyFingerprint` | SSH keys |

## 🔍 Troubleshooting

### Checking BitwardenSecret Status

```bash
kubectl get bitwardensecrets
# or
kubectl get bws
```

### Viewing Operator Logs

```bash
kubectl logs -l app=bitwarden-operator -n bitwarden-external-secrets
```

## 🛑 Uninstallation

To cleanly uninstall the charts:

```bash
helm uninstall bitwarden-external-secrets -n bitwarden-external-secrets
helm uninstall external-secrets -n external-secrets
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
