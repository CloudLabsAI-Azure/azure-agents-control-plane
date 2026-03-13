# Exercise 3: Review Agents Control Plane

**Duration:** 30 minutes

## Overview

In this exercise, you are to inspect the complete Azure Agents Control Plane to understand how identity, security, governance, memory, and observability works for your new agent. You will be asked answer some questions about the implementation.

---

## Step 3.1: Check APIM – Policies (Security/Management/Governance)

Azure API Management enforces governance policies for all agent traffic. In this accelerator, APIM serves as the centralized gateway that fronts all MCP tool calls and agent-to-agent communication, enforcing OAuth authentication, request routing to the AKS-hosted MCP server, rate limiting, and policy-based security so that every interaction between agents and tools is authenticated, authorized, and observable.

### Navigate to APIM

1. Open Azure Portal
2. Navigate to **API Management** → Your APIM instance
3. Go to **APIs** → **MCP API** → **Design** → **Inbound processing** (Can be found to the right of Frontend)
4. Click on the `</>` Icon

### View the policy

Ask yourself (or the Azure Copilot) the following questions.

- What authentication controls are in place for this policy?
- What happens if an unauthenticated request is made to an endpoint in this APIM?
- Can you think of other policies that should be added to govern, manage and security APIs?

---

## Step 3.2: Check Cosmos DB (Short-Term Memory)

Cosmos DB stores plans and tasks. In this accelerator, Cosmos DB serves as the agent's short-term memory provider, storing session-scoped planning artifacts—including intent decomposition, multi-step task plans, and individual task execution state—with TTL-based automatic expiration so that ephemeral reasoning data is cleaned up after the session ends. Each memory entry is partitioned by session ID and includes vector embeddings, enabling the agent to perform cosine-similarity searches over recent context and retrieve relevant conversation history or prior plan steps during agentic reasoning.

### Navigate to Cosmos DB

1. Open Azure Portal
2. Navigate to **Azure Cosmos DB** → Your account
3. Go to **Data Explorer**

### View Plans and Tasks

Click on plans and then Items.

Review tasks, intent and steps.

Click on tasks and then Items.

Take note that embeddings have been stored.


---

## Step 3.3: Check Azure AI Foundry / AI Search (Long-Term Memory)

Azure AI Search provides vector search for long-term memory retrieval. In this accelerator, Azure AI Foundry's agentic retrieval pipeline powers the agent's long-term memory by indexing durable knowledge sources and knowledge bases that persist beyond any single session. When the agent needs to recall prior experience or domain knowledge, the pipeline performs source selection and query planning across multiple knowledge sources, ranks results through L2/L3 classifiers, and optionally reflects and iterates before merging final results. The pipeline's reasoning effort level (Minimal, Low, or Medium) controls how much computation is applied at each stage—higher levels enable query planning, L3 classification, and reflection/iteration loops for deeper, more accurate retrieval at the cost of additional latency, while lower levels skip those stages for faster responses.

### Temporarily Enable Public Access on AI Search

> [WARNING]
> The AI Search instance is deployed with public network access **disabled** by default. When you open the service in the Azure portal you will see:
>
> *"Restricted access: An admin of your search service has disabled public network access, so some features of the Azure portal may be disabled. You can view and manage service level information, but portal access to indexes, indexers, and other top-level resources may be restricted."*
>
> You must temporarily enable public access so the portal (and your local machine) can interact with indexes, knowledge sources, and the agentic retrieval chat panel. **Remember to disable public access again after you finish this exercise** (see the end of this step).

Copilot Prompt:

```
Temporarily enable public network access on the AI Search instance in the apim-mcp-aks resource group so I can use the Azure portal to browse indexes and knowledge bases. Run:

az search service update -g apim-mcp-aks -n $(az resource list --resource-type Microsoft.Search/searchServices --query "[0].name" -o tsv) --public-access enabled
```

Copilot will resolve the search service name and enable public access. Once the command succeeds, you can proceed to explore the knowledge base in the portal.

### Navigate to the Knowledge Base

1. Open Azure Portal
2. Navigate to **Azure AI Search** → Your service → **Agentic retrieval** → **Knowledge bases**
3. Open the **task-instructions-kb** knowledge base

### Review Knowledge Base Configuration

In the left panel, review the following settings:

| Setting | Expected Value | Purpose |
|---------|---------------|---------|
| Knowledge sources | task-instructions-source | Indexed task instruction documents |
| Chat completion model | (see note below) | Required for reasoning effort above Minimal |
| Reasoning effort | Minimal (default) | Controls depth of retrieval pipeline |
| Retrieval mode | Retrieval (recommended) | Uses agentic retrieval with ranking |

> **Note:** If no **Chat completion model** is configured, the reasoning effort must be set to **Minimal**. To use **Low** or **Medium** reasoning effort (which enables query planning, L3 classification, and reflection/iteration), click **+ Add model deployment** and select a deployed chat completion model (e.g., GPT-4o). Without a model, attempting a higher reasoning effort will produce the error: *"A Knowledge Base model must be specified to use any reasoning effort other than 'Minimal'"*.

### Query the Knowledge Base

In the knowledge base chat panel, enter a query thats specific to your domain / specification.

```
What are the steps for customer churn analysis?
```

```
How do I set up a CI/CD Kubernetes pipeline?
```

```
What is the REST API user management workflow?
```

Review the response and note how the knowledge base retrieves relevant task instructions from the **task-instructions-source** knowledge source.


### Restore Security – Disable Public Access

Once you have finished reviewing AI Search, disable public access to restore the service's security posture.

Copilot Prompt:

```
Disable public network access on the AI Search instance to restore its security posture. Run:

az search service update -g apim-mcp-aks -n $(az resource list --resource-type Microsoft.Search/searchServices --query "[0].name" -o tsv) --public-access disabled
```

---

## Step 3.4: Check Facts/Ontology

Ontologies provide grounded facts for agent reasoning. In agentic systems, an ontology is a structured representation of domain knowledge—defining entity types, relationships, and facts—that the agent uses to anchor its reasoning in verified, real-world data rather than relying solely on the LLM's parametric knowledge. This grounding is critical because it prevents hallucination, ensures consistency across agent sessions, and enables the agent to reason over domain-specific concepts (e.g., "Customer has churn risk 0.85") that the base model was never trained on.

Facts within ontologies serve as the agent's source of truth. When the agent retrieves context during planning or task execution, ontology facts provide deterministic, structured data points—such as customer segments, churn predictions with confidence scores, pipeline failure categories, or API endpoint schemas—that complement the probabilistic outputs of the LLM. This combination of structured facts and generative reasoning is what enables agents to produce accurate, actionable recommendations grounded in your organization's actual data.

In this accelerator, ontologies are stored as JSON files and uploaded to a storage account (or Microsoft Fabric OneLake), where the agent can retrieve them at runtime. Three domain ontologies are included:

| Ontology | Domain | Key Facts |
|----------|--------|-----------|
| `customer_churn_ontology.json` | Customer Analytics | Churn risk predictions, segment retention insights, engagement metrics |
| `cicd_pipeline_ontology.json` | DevOps | Pipeline failure categories, deployment events, cluster health |
| `user_management_ontology.json` | API Management | User roles, endpoint schemas, access control patterns |

> **Note:** Review the locally generated ontology files under the `facts/ontology/` folder in this repository (e.g. `facts/ontology/<domain>.json`). This step will be fully fleshed out once the Fabric IQ environment is ready.


---

## Step 3.5: Check Log Analytics (Observability)

Azure Monitor collects logs, metrics, and traces from all agents.

### Navigate to Log Analytics Workspaces

1. Open Azure Portal
2. Navigate to **Log Analytics Workspaces** → Your workspace
3. Go to **Logs**
4. Change from simple to KQL mode

### Query Agent Logs

> **Note:** This accelerator uses the legacy `ContainerLog` table (v1) rather than `ContainerLogV2`. The v1 table uses `LogEntry` instead of `LogMessage`, and container metadata fields (`Name`, `Image`) may be empty when using the AMA agent with the OMS addon.


```
// Agent container logs (ContainerLog v1)
ContainerLog
| where TimeGenerated < ago(60m)
| where LogEntry !contains "/health"
| project TimeGenerated, LogEntry, LogEntrySource, ContainerID
| order by TimeGenerated desc
| take 100
```

The logs reflect the runtime behavior of `next_best_action_agent.py` — a FastAPI MCP server that initializes CosmosDB clients for task and plan storage, sets up memory providers (short-term via CosmosDB, long-term via AI Search, and facts via Fabric IQ), generates embeddings for semantic similarity search, analyzes user intent, produces action plans, and optionally leverages Agent Lightning for fine-tuning — along with standard HTTP request handling from the Uvicorn server.

---

## Step 3.6: Check Entra ID / RBAC

### Obtain the Agent Managed Identity Client ID

The agent's managed identity client ID is stored as an annotation on the Kubernetes service account used by the agent pods. This is **not** the same as the OAuth app registration (e.g., `MCP-OAuth-app-*`) visible in Entra ID → App registrations — that app is used by APIM for OAuth token validation.

Retrieve the managed identity client ID from the service account:

#### Get the managed identity client ID from the service account annotation
```
kubectl get serviceaccount mcp-agent-sa -n mcp-agents -o jsonpath='{.metadata.annotations.azure\.workload\.identity/client-id}'
```

Save the output — you will use it in the commands below.

### Review Role Assignments

#### List role assignments for agent identity (replace with your client ID from above)
```
az role assignment list --assignee <managed-identity-client-id> --all --output table
```

### Expected Roles

| Role | Resource | Purpose |
|------|----------|---------|
| Cognitive Services User | AI Foundry | LLM inference |
| Cosmos DB Data Contributor | Cosmos DB | Read/write sessions |
| Storage Blob Data Reader | Storage Account | Read ontologies |
| Search Index Data Reader | AI Search | Query long-term memory |

### Verify Workload Identity

#### Check service account annotation

```
kubectl get serviceaccount mcp-agent-sa -n mcp-agents -o yaml
```

Expected output:

> | Field | Value |
> |-------|-------|
> | **Name** | `mcp-agent-sa` |
> | **Namespace** | `mcp-agents` |
> | **Managed Identity Client ID** | `000a4749-749d-4088-a8ba-6eb06e9211fd` |
> | **Tenant ID** | `ac13813e-46f5-48f7-a829-34d31dc94495` |
> | **Workload Identity Enabled** | `true` (`azure.workload.identity/use: "true"`) |
> | **Identity Type Label** | `entra-agent-identity` |
> 
> The workload identity federation is properly configured — the service account has both the
> `azure.workload.identity/client-id` and `azure.workload.identity/tenant-id` annotations,
> and the `azure.workload.identity/use: "true"` label is set. This allows pods using this 
> service account to authenticate to Azure services (Cosmos DB, AI Foundry, AI Search, 
> Storage) > via Entra ID without storing any secrets.

---

## Step 3.8: Identify Problems

Based on your review, identify any issues with your agents:

### Checklist

| Component | Status | Issue Found | Notes |
|-----------|--------|-------------|-------|
| APIM Policies | ✅ / ❌ | | |
| Short Term Memory (CosmosDB Plans/Tasks) | ✅ / ❌ | | |
| Long Term Memory (FoundryIQ Instructions) | ✅ / ❌ | | |
| Facts (Fabric IQ Ontologies) | ✅ / ❌ | | |
| Log Analytics | ✅ / ❌ | | |
| Entra ID + RBAC | ✅ / ❌ | | |

### Common Problems

| Problem | Symptom | Solution |
|---------|---------|----------|
| High latency | P95 > 2s | Check AI Foundry throttling, scale pods |
| Failed tool calls | Error rate > 5% | Review logs for exceptions |
| Missing traces | No transactions in App Insights | Verify OpenTelemetry configuration |
| RBAC errors | 403 responses | Add missing role assignments |

---

## Completion Checklist

Before proceeding to Exercise 4, please confirm the following:

- [ ] Reviewed APIM policies and understand security, manageability and governance controls
- [ ] Verified Cosmos DB is storing plans and tasks
- [ ] Confirmed FoundryIQ (AI Search) has agentic retrieval of instructions
- [ ] Reviewed ontology files in storage account / Fabric IQ
- [ ] Queried Log Analytics for agent logs
- [ ] Verified Entra ID + RBAC role assignments
- [ ] Take note of problems found

---

To continue the lab, click on the **Next** button.
