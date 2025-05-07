from models import BitwardenExternalSecretManifest
import kopf
import pydantic

def parse_body(body: dict) -> BitwardenExternalSecretManifest:
    try:
        return BitwardenExternalSecretManifest.model_validate(body)
    except pydantic.ValidationError as e:
        raise kopf.PermanentError(f"Failed to parse resource: {e}")

def get_name_namespace(crd: BitwardenExternalSecretManifest) -> tuple[str, str]:
    return crd.metadata.name, crd.spec.namespace