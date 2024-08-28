# GitlabBot

## Flux-local

### Bot User

Setup your bot account and generate a PAT token.
Then, add the bot to your project with the reporter permission.
Finally , store the pat token in the `GITLAB_BOT_PAT` CI/CD variable.


### CI
You can use the following content to setup GitLab CI to post the diff comment.
```yaml
---
.flux-local-diff:
  stage: flux-local
  image:
    name: ghcr.io/alexsaphir/gitlabbot:v0.2.6
  parallel:
    matrix:
      - FLUX_RESOURCE:
          - hr
          - ks
  variables:
    GIT_DEPTH: "0"  # Tells git to fetch all the branches of the project, required by the analysis task
    CONFIG_FILE: '.gitlabbot.yaml'
  script:
    - |
      DIFF="dyff between --omit-header --ignore-order-changes -o gitlab" \
      flux-local diff $FLUX_RESOURCE -A \
      --path $CLUSTER_PATH \
      --branch-orig main \
      --strip-attrs "helm.sh/chart,checksum/config,app.kubernetes.io/version,chart" \
      --output-file out.diff
    - |
      gitlab-comment --diff_file out.diff \
        --flux_resource $FLUX_RESOURCE \
        --diff_mode dyff \
        --comment_mode $COMMENT_MODE
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

flux-local-diff:
  extends: .flux-local-diff
  variables:
    CLUSTER_PATH: cluster
    COMMENT_MODE: recreate
```