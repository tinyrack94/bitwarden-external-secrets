from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Type
from kr8s.objects import new_class, APIObject

ExternalSecretResource: Type[APIObject] = new_class(
    kind="ExternalSecret", version="external-secrets.io/v1beta1", namespaced=True
)

BitwardenSecretResource: Type[APIObject] = new_class(
    kind="BitwardenSecret", version="bitwarden.external-secrets.io/v1alpha1", namespaced=False
)


class StoreRef(BaseModel):
    name: str
    kind: str


class SourceRef(BaseModel):
    storeRef: StoreRef


class RemoteRef(BaseModel):
    key: str
    property: Optional[str] = None


class DataItem(BaseModel):
    secretKey: str
    sourceRef: SourceRef
    remoteRef: RemoteRef


class Template(BaseModel):
    type: str = "Opaque"
    data: Dict[str, str] = Field(default_factory=dict)

    def add_data(self, key: str, value: str):
        self.data[key] = value


class Target(BaseModel):
    name: str
    template: Template


class Spec(BaseModel):
    refreshPolicy: str = "Periodic"
    refreshInterval: str = "1m"
    target: Target
    data: List[DataItem]


class Metadata(BaseModel):
    name: str
    namespace: str
    labels: Optional[Dict[str, str]] = None


class ExternalSecret(BaseModel):
    apiVersion: str = "external-secrets.io/v1beta1"
    kind: str = "ExternalSecret"
    metadata: Metadata
    spec: Spec

    def as_resource(self) -> APIObject:
        """Convert the CRD to a kr8s APIObject"""
        return ExternalSecretResource(self.model_dump())


class ItemRef(BaseModel):
    id: str
    property: Optional[str] = None
    type: str


class SecretEntry(BaseModel):
    itemRef: ItemRef


class CRDMetadata(BaseModel):
    name: str
    uid: Optional[str] = None


class BitwardenExternalSecretManifestSpec(BaseModel):
    namespace: str
    secrets: Dict[str, SecretEntry]


class BitwardenExternalSecretManifest(BaseModel):
    apiVersion: str = "bitwardensecrets.external-secrets.io/v1alpha1"
    kind: str = "BitwardenSecret"
    metadata: CRDMetadata
    spec: BitwardenExternalSecretManifestSpec

    @classmethod
    def from_api_object(cls, api_obj: APIObject) -> "BitwardenExternalSecretManifest":
        """Create a CRD instance from a kr8s APIObject"""
        return cls.model_validate(api_obj.raw)

    def convert_external_secret_manifest(self) -> ExternalSecret:
        template = Template(type="Opaque")

        for entry in self.spec.secrets.keys():
            template.add_data(entry, "{{ .%s }}" % (entry))

        spec = Spec(
            refreshPolicy="Periodic",
            refreshInterval="1m",
            target=Target(name=self.metadata.name, template=template),
            data=[
                DataItem(
                    secretKey=entry,
                    sourceRef=SourceRef(
                        storeRef=StoreRef(
                            kind="ClusterSecretStore",
                            name=f"bitwarden-{value.itemRef.type}",
                        )
                    ),
                    remoteRef=RemoteRef(
                        key=value.itemRef.id,
                        property=value.itemRef.property
                        if value.itemRef.property
                        else None,
                    ),
                )
                for entry, value in self.spec.secrets.items()
            ],
        )
        return ExternalSecret(
            metadata=Metadata(
                name=f"external-secret-{self.metadata.name}",
                namespace=self.spec.namespace,
                labels={
                    "bitwarden.external-secrets.io/managed-by": "bitwarden-operator",
                    "bitwarden.external-secrets.io/owner": self.metadata.name,
                },
            ),
            spec=spec,
        )
        
    def as_resource(self) -> APIObject:
        """Convert the CRD to a kr8s APIObject"""
        return BitwardenSecretResource(self.model_dump())
