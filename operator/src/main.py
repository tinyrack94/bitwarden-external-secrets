import kopf
import logging
import asyncio
import pydantic
from kr8s import APIObject
from typing import Optional
from models import ExternalSecretResource
import kr8s
from utils import parse_body, get_name_namespace

logging.basicConfig(level=logging.INFO)

CRD_GROUP = "bitwarden.external-secrets.io"

RESOURCE = f"bitwardensecrets.{CRD_GROUP}"

VERSION = "v1alpha1"

FINALIZER = f"{CRD_GROUP}/bws-finalizer"


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):

    settings.persistence.finalizer = FINALIZER
    settings.persistence.progress_storage = kopf.SmartProgressStorage(
        prefix=CRD_GROUP, name="bws"
    )
    settings.persistence.diffbase_storage = kopf.AnnotationsDiffBaseStorage(
        prefix=CRD_GROUP
    )

@kopf.on.resume(RESOURCE)
def resume(body, **kwargs):
    try:
        manifest = parse_body(body)
        name, namespace = get_name_namespace(manifest)
        
        kopf.info(body, reason='Resuming', message=f"Resuming ExternalSecret for {name} in {namespace}")

        external_secret = manifest.convert_external_secret_manifest()
        external_secret_name = external_secret.metadata.name
        
        kopf.info(body, reason='Checking', message=f"Ensuring ExternalSecret {external_secret_name} exists")
        
        try:
            converted_resource = external_secret.as_resource()
            
            if not converted_resource.exists():
                kopf.warn(body, reason='NotFound', message=f"ExternalSecret {external_secret_name} does not exist, recreating")
                
                converted_resource.create()
                kopf.info(body, reason='Created', message=f"ExternalSecret {external_secret_name} created in {namespace}")
                
                manifest.as_resource().adopt(converted_resource)
                kopf.info(body, reason='Adopted', message=f"Ownership established for ExternalSecret {external_secret_name}")
            else:
                kopf.info(body, reason='Exists', message=f"ExternalSecret {external_secret_name} already exists in {namespace}")
            
        except kr8s.ServerError as e:
            kopf.exception(body, reason='ServerError', message=f"Kubernetes API error: {str(e)}")
            raise kopf.TemporaryError(f"API error: {e}", delay=30)
        except Exception as e:
            kopf.exception(body, reason='ResumeError', message=f"Error resuming ExternalSecret: {str(e)}")
            raise kopf.PermanentError(f"Failed to resume ExternalSecret: {e}")
    
    except pydantic.ValidationError as e:
        kopf.exception(body, reason='ValidationError', message=f"Failed to validate resource: {str(e)}")
        raise kopf.PermanentError(f"Validation error: {e}")

@kopf.on.create(RESOURCE)
def create(body, **kwargs):
    try:
        manifest = parse_body(body)
        name, namespace = get_name_namespace(manifest)
        
        kopf.info(body, reason='Creating', message=f"Creating ExternalSecret for {name} in {namespace}")

        external_secret = manifest.convert_external_secret_manifest()
        external_secret_name = external_secret.metadata.name
        
        kopf.info(body, reason='Checking', message=f"Ensuring ExternalSecret {external_secret_name} exists")
        
        try:
            converted_resource = external_secret.as_resource()
            
            if not converted_resource.exists():
                kopf.info(body, reason='Creating', message=f"ExternalSecret {external_secret_name} doesn't exist, creating")
                
                converted_resource.create()
                kopf.info(body, reason='Created', message=f"ExternalSecret {external_secret_name} created in {namespace}")
                
                manifest.as_resource().adopt(converted_resource)
                kopf.info(body, reason='Adopted', message=f"Ownership established for ExternalSecret {external_secret_name}")
            else:
                kopf.warn(body, reason='Exists', message=f"ExternalSecret {external_secret_name} already exists in {namespace}")
            
        except kr8s.ServerError as e:
            kopf.exception(body, reason='ServerError', message=f"Kubernetes API error: {str(e)}")
            raise kopf.TemporaryError(f"API error: {e}", delay=30)
        except kr8s.NotFoundError as e:
            kopf.exception(body, reason='NotFoundError', message=f"Resource not found: {str(e)}")
            raise kopf.TemporaryError(f"Resource not found: {e}", delay=10)
        except Exception as e:
            kopf.exception(body, reason='CreateError', message=f"Error creating ExternalSecret: {str(e)}")
            raise kopf.PermanentError(f"Failed to create ExternalSecret: {e}")
    
    except pydantic.ValidationError as e:
        kopf.exception(body, reason='ValidationError', message=f"Failed to validate resource: {str(e)}")
        raise kopf.PermanentError(f"Validation error: {e}")
    

@kopf.on.update(RESOURCE)
def update(body, **kwargs):
    try:
        manifest = parse_body(body)
        name, namespace = get_name_namespace(manifest)
        
        kopf.info(body, reason='Updating', message=f"Updating ExternalSecret for {name} in {namespace}")

        external_secret = manifest.convert_external_secret_manifest()
        external_secret_name = external_secret.metadata.name
        
        try:
            converted_resource = external_secret.as_resource()
            
            if converted_resource.exists():
                kopf.info(body, reason='Patching', message=f"Patching ExternalSecret {external_secret_name} in {namespace}")
                converted_resource.patch(converted_resource.spec)
                kopf.info(body, reason='Updated', message=f"ExternalSecret {external_secret_name} updated successfully")
            else:
                kopf.warn(body, reason='NotFound', message=f"ExternalSecret {external_secret_name} not found, cannot update")

                kopf.info(body, reason='Creating', message=f"Creating missing ExternalSecret {external_secret_name}")
                converted_resource.create()
                manifest.as_resource().adopt(converted_resource)
                kopf.info(body, reason='Created', message=f"ExternalSecret {external_secret_name} created instead of updated")
            
        except kr8s.ServerError as e:
            kopf.exception(body, reason='ServerError', message=f"Kubernetes API error: {str(e)}")
            raise kopf.TemporaryError(f"API error: {e}", delay=30)
        except Exception as e:
            kopf.exception(body, reason='UpdateError', message=f"Error updating ExternalSecret: {str(e)}")
            raise kopf.TemporaryError(f"Failed to update ExternalSecret: {e}", delay=10)
    
    except pydantic.ValidationError as e:
        kopf.exception(body, reason='ValidationError', message=f"Failed to validate resource: {str(e)}")
        raise kopf.PermanentError(f"Validation error: {e}")


@kopf.on.delete(RESOURCE)
def delete(body, **kwargs):
    try:
        manifest = parse_body(body)
        name, namespace = get_name_namespace(manifest)
        
        kopf.info(body, reason='Deleting', message=f"Deleting ExternalSecret for {name} in {namespace}")

        external_secret = manifest.convert_external_secret_manifest()
        external_secret_name = external_secret.metadata.name
        
        try:
            resource = external_secret.as_resource()

            if not resource.exists():
                kopf.info(body, reason='NotFound', message=f"ExternalSecret {external_secret_name} not found, nothing to delete")
                return

            resource.delete()
            kopf.info(body, reason='Deleted', message=f"ExternalSecret {external_secret_name} successfully deleted from {namespace}")
            
        except kr8s.ServerError as e:
            kopf.exception(body, reason='ServerError', message=f"Kubernetes API error: {str(e)}")
            kopf.warn(body, reason='DeleteWarning', message=f"Deletion had API errors but will proceed: {str(e)}")
        except kr8s.NotFoundError as e:
            kopf.info(body, reason='AlreadyDeleted', message=f"ExternalSecret {external_secret_name} already deleted or not found {e}")
        except Exception as e:
            kopf.exception(body, reason='DeleteError', message=f"Error deleting ExternalSecret: {str(e)}")

            kopf.warn(body, reason='FinalizeAnyway', message="Will remove finalizer despite errors")
    
    except pydantic.ValidationError as e:
        kopf.exception(body, reason='ValidationError', message=f"Failed to validate resource: {str(e)}")



@kopf.timer(RESOURCE, interval=10.0)
async def update_status(body, **kwargs):
    try:
        manifest = parse_body(body)
        name, namespace = get_name_namespace(manifest)
        

        external_secret_name = f"external-secret-{name}"
        

        kopf.info(body, reason='StatusCheck', message=f"Checking status of ExternalSecret {external_secret_name} in {namespace}")
        
        try:
            external_secrets = list(kr8s.get('ExternalSecrets', namespace=namespace))
            target_secret = None
            
            for item in external_secrets:
                if item.metadata.name == external_secret_name:
                    target_secret = item
                    break
            
            if not target_secret:
                kopf.warn(body, reason='NotFound', message=f"ExternalSecret {external_secret_name} not found in namespace {namespace}")
                return
                

            conditions = target_secret.raw.get('status', {}).get('conditions', [])
            

            ready_status = "Unknown"
            reason = "Pending"
            

            for condition in conditions:
                if condition.get('type') == 'Ready':
                    ready_status = condition.get('status', 'Unknown')
                    reason = condition.get('reason', 'Unknown')
                    break
                    

            is_ready = ready_status == "True"
            

            patch = {
                'status': {
                    'externalSecretStatus': reason,
                    'ready': is_ready,
                    'lastUpdated': target_secret.raw.get('status', {}).get('refreshTime', ''),
                    'message': target_secret.raw.get('status', {}).get('syncedResourceVersion', '')
                }
            }
            

            bws_resource = manifest.as_resource()
            bws_resource.patch(patch, subresource='status')
            
            event_type = 'Normal' if is_ready else 'Warning'
            kopf.event(
                body,
                type=event_type,
                reason=reason,
                message=f"ExternalSecret status: {reason}. Ready: {ready_status}"
            )
            
        except kr8s.ServerError as e:
            kopf.exception(body, reason='ServerError', message=f"Error accessing Kubernetes API: {str(e)}")
        except kr8s.NotFoundError as e:
            kopf.exception(body, reason='NotFound', message=f"Resource not found: {str(e)}")
        except ValueError as e:
            kopf.exception(body, reason='ValueError', message=f"Value error in status update: {str(e)}")
        except KeyError as e:
            kopf.exception(body, reason='KeyError', message=f"Missing key in resource data: {str(e)}")
            
    except pydantic.ValidationError as e:
        kopf.exception(body, reason='ValidationError', message=f"Failed to validate resource: {str(e)}")
    except Exception as e:
        kopf.exception(body, reason='UnhandledError', message=f"Unexpected error during status update: {str(e)}")
        raise
    
    
if __name__ == "__main__":
    asyncio.run(kopf.operator(clusterwide=True, liveness_endpoint="http://0.0.0.0:8080/up"))