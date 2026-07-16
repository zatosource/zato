# Zato Helm chart

Runs the Zato quickstart image on Kubernetes.

## Install

```bash
helm install zato ./kubernetes/helm/zato --set password.value=mypassword
```

The first boot creates a complete quickstart environment inside the pod, which takes a few minutes -
the startup probe allows up to 10 minutes before it gives up.

## Configuration through ConfigMaps

Both of the following are optional. When set, their contents are applied when the pod starts
and re-applied whenever the ConfigMap changes - no pod restart is needed.

### Enmasse - channels, security definitions, outgoing connections

```bash
kubectl create configmap zato-enmasse --from-file=enmasse.yaml
helm upgrade zato ./kubernetes/helm/zato --reuse-values --set enmasse.configMap=zato-enmasse
```

The ConfigMap must have an `enmasse.yaml` key. It is mounted at `/opt/hot-deploy/enmasse`.

### Services - Python source files

```bash
kubectl create configmap zato-services --from-file=my_service.py
helm upgrade zato ./kubernetes/helm/zato --reuse-values --set services.configMap=zato-services
```

The `.py` files are mounted at `/opt/hot-deploy/incoming/services` and hot-deployed from there.

## Values

| Value | Default | Meaning |
|-------|---------|---------|
| `password.value` | `""` | Environment password, stored in a chart-created Secret |
| `password.existingSecret` | `""` | Name of an existing Secret to use instead |
| `enmasse.configMap` | `""` | ConfigMap with an `enmasse.yaml` key |
| `services.configMap` | `""` | ConfigMap with `.py` service files |
| `service.type` | `ClusterIP` | Service type |
| `service.ssh.enabled` | `false` | Expose SSH port 22 |
| `image.tag` | `latest` | Image tag |
| `resources` | `{}` | Container resources |

All ports the image publishes are exposed by default: 17010 (server API), 8183/8184 (Dashboard),
8185/8186 (OpenAPI console), 11223/11224 (load balancer). SSH 22 is off by default - `kubectl exec`
covers that role on Kubernetes.

## Exposing Zato outside the cluster

See the `examples/` directory for a standard `Ingress` and a Gateway API `HTTPRoute`,
both routing to this chart's Service.
