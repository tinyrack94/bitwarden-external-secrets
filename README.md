# External Secrets Bitwarden

A Helm chart for using Bitwarden with External Secrets Operator in Kubernetes.

## Purpose

This is a chart to use [vaultwarden](https://github.com/dani-garcia/vaultwarden) or even [bitwarden](https://bitwarden.com) with kubernetes secrets.

> [!NOTE]
> This is not similar to bitwarden kubernetes operator, which uses bitwarden as a secrets manager under the hood.

### Usage

```bash
helm repo add eznix86 https://eznix86.github.io/bitwarden-external-secrets

helm repo update

helm install bitwarden-external-secrets eznix86/bitwarden-external-secrets \
  -n bitwarden-external-secrets \
  --create-namespace \
  --set secrets.bw_clientid="" \
  --set secrets.bw_clientsecret="" \
  --set secrets.bw_password="" # used to decrypt your vault
```

`bw_clientid` and `bw_clientsecret` can be found on your vaultwarden/bitwarden app settings.

### Supported Fields


| Field | Supported | Cluster Store Name | Property |
| --- | --- | --- | --- |
| username | ✅ | bitwarden-login | username |
| password | ✅ | bitwarden-login | password |
| notes | ✅ | bitwarden-notes | - |
| custom fields | ✅ | bitwarden-fields | - |
| private key | ✅ | bitwarden-ssh-key | privateKey |
| public key | ✅ | bitwarden-ssh-key | publicKey |
| key fingerprint | ✅ | bitwarden-ssh-key | keyFingerprint |
| attachments | ❌ | - | - |

### Deploying a secret

```yaml
apiVersion: bitwarden.external-secrets.io/v1alpha1
kind: BitwardenSecret
metadata:
  name: bitwarden-secrets
spec:
  namespace: bitwarden-external-secrets
  secrets:
    username:
      itemRef:
        id: "d0a5c1a7-dcc1-4562-9ca7-b2d201564347" 
        type: login
        property: username
    password:
      itemRef:
        id: "d0a5c1a7-dcc1-4562-9ca7-b2d201564347"
        type: login
        property: password
    bitwarden-public-key:
      itemRef:
        id: "d0a5c1a7-dcc1-4562-9ca7-b2d201564347"
        type: sshKey
        property: publicKey # publicKey or privateKey or keyFingerprint
```

This will create a secret with the following secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secrets
  namespace: bitwarden-external-secrets
data:
  username: <base64>
  password: <base64>
  bitwarden-public-key: <base64>
type: Opaque
```




