# GitlabBot

## Flux-local

```shell
DIFF="dyff between --omit-header --ignore-order-changes -o gitlab" \
        flux-local diff hr -A \
            --path cluster \
            --branch-orig main \
            --strip-attrs "helm.sh/chart,checksum/config,app.kubernetes.io/version,chart" \
            --output-file out.diff

gitlab-comment --diff_file out.diff --flux_resource hr --diff_mode dyff --comment_mode recreate
```

```shell
DIFF="dyff between --omit-header --ignore-order-changes -o gitlab" \
        flux-local diff ks -A \
            --path cluster \
            --branch-orig main \
            --strip-attrs "helm.sh/chart,checksum/config,app.kubernetes.io/version,chart" \
            --output-file ks.diff

gitlab-comment --diff_file out.diff --flux_resource ks --diff_mode dyff --comment_mode recreate
```