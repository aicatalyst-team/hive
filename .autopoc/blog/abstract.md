# Blog Abstract: Deploying Hive on OpenShift AI

## Thesis
Deploying Hive, an AI agent orchestration layer, on OpenShift AI demonstrates that CPU-only agent infrastructure runs efficiently on enterprise Kubernetes with minimal resources and zero GPU requirements.

## Target Audience
Platform engineers and ML engineers building AI agent systems who want to reduce LLM token costs and add memory/routing capabilities to their agent workflows.

## Blog Type
Red Hat Developer Blog

## Key Points
1. Hive's CPU-side routing and context compression reduce LLM token usage by 64%, translating to significant cost savings
2. The UBI 9 containerization and OpenShift deployment required minimal adaptation from the original project
3. All core endpoints (routing, compression, memory) validated with sub-20ms response times on OpenShift

## Products/Projects
- Red Hat OpenShift AI
- Open Data Hub
- Hive (hive-agent-memory)

## CTA
Try deploying Hive on your own OpenShift cluster to reduce agent LLM costs.

## Section Outline
1. What is Hive? (project overview and the problem it solves)
2. Why deploy agent infrastructure on OpenShift AI?
3. Containerizing with UBI 9 (Dockerfile decisions)
4. Building and deploying on OpenShift
5. Validating the deployment (test results)
6. What we learned
7. Try it yourself
