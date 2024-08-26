# GitlabBot

## Flux-local

```shell
DIFF="dyff between --omit-header --ignore-order-changes -o gitlab" \
        flux-local diff hr -A \
            --path cluster \
            --branch-orig main \
            --strip-attrs "helm.sh/chart,checksum/config,app.kubernetes.io/version,chart" \
            --output-file hr.diff
```

```shell
DIFF="dyff between --omit-header --ignore-order-changes -o gitlab" \
        flux-local diff ks -A \
            --path cluster \
            --branch-orig main \
            --strip-attrs "helm.sh/chart,checksum/config,app.kubernetes.io/version,chart" \
            --output-file ks.diff
```