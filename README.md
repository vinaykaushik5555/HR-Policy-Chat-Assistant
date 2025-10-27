Software Requirements Specification (SRS) — HR Policy Chat Assistant
Domain: HR Policy Chat Assistant Use Case Summary: Employees can search HR policies and apply for leaves via a conversational interface. Architecture Goals: Cost-effective GenAI system with LLM provider switching via configuration/minimal changes, RAG, MCP for enterprise actions, GuardRails for safety, LangSmith for tracing, and a Python-based UI.

1. Introduction
1.1 Purpose
Define functional and non-functional requirements, flows, and architecture for a GenAI-powered HR Policy Chat Assistant that supports policy search and leave application with configurable LLM backends and cost controls.
1.2 Scope
	•	Chat search over HR policies (structured/unstructured).
	•	Apply leave via enterprise HR systems.
	•	Python-based web UI.
	•	RAG with Vector DB.
	•	MCP APIs for HR actions (e.g., leave).
	•	Guardrails for safety/compliance.
	•	LangSmith for monitoring/tracing.
	•	Pluggable LLM with minimal configuration.
1.3 Stakeholders
	•	Product, HR Operations, Engineering, Security/Compliance, SRE/Platform.
1.4 Definitions & Acronyms
	•	RAG: Retrieval-Augmented Generation.
	•	MCP: Model Context Protocol (hosted HR domain tools).
	•	LLM: Large Language Model (pluggable).
	•	LangGraph/Chain: Orchestration and tool routing.
	•	GuardRails: Policy/safety validation/filtering.
	•	LangSmith: Tracing/observability.

2. System Overview
2.1 High-Level Description
A web-based chat app where authenticated employees can search HR policies through RAG and execute leave workflows via MCP. The agent orchestrates intent detection, retrieval, tool calls, response generation, guardrail checks, and telemetry.
2.2 Implementation Flow (Conceptual)
	1	UI (Python) → Agent: Receive utterance + user context.
	2	GuardRails (input): Validate/redact/jailbreak protection.
	3	Agent (LangGraph): Route to RAG or MCP path.
	4	RAG: Retrieve top-k chunks from Vector DB → LLM synthesis.
	5	MCP: Call HR APIs (leave eligibility, apply).
	6	GuardRails (output): Enforce policy/safety.
	7	LangSmith: Trace, metrics, error analysis.
	8	UI: Render with citations (policy) or confirmation (leave).

3. Functional Requirements
ID
Requirement
FR-1
Chat-based interface for HR policy Q&A.
FR-2
RAG pipeline to retrieve HR policy chunks with citations.
FR-3
Intent detection & state management with LangGraph (policy search vs leave application).
FR-4
Leave application via MCP tools: balance check, date validation, create request, status return.
FR-5
GuardRails on both input and output (toxicity, PII minimization, policy constraints).
FR-6
LangSmith tracing for all agent steps, tools, errors, latencies, costs.
FR-7
Authentication via SSO/OAuth2; use JWT in session.
FR-8
Vector DB for embeddings (create/update/delete documents; reindex jobs).
FR-9
Multilingual queries (EN + configured locales) with locale-aware retrieval.
FR-10
UI shows sources, confidence, and request IDs.
FR-11
LLM provider switching via configuration (env/config file/feature flag) with minimal or no code changes.
FR-12
Cost controls: per-request max tokens, model routing by budget, automatic fallbacks.
FR-13
Admin operations: document ingestion, re-embed, purge; MCP endpoint config.
FR-14
Telemetry dashboard (LangSmith + infra metrics) visible to admins.
FR-15
Redaction of sensitive content before persistence/logging.

4. Non-Functional Requirements
4.1 Performance & Scale
	•	P1 queries (simple policy search): p95 < 3s with cached embeddings.
	•	P2 queries (leave application + MCP): p95 < 5s.
	•	Concurrency target: 2k active sessions, horizontally scalable on K8s.
4.2 Reliability & Availability
	•	99.5% monthly availability.
	•	Graceful degradation: if LLM-A fails, route to LLM-B; if RAG fails, present fallback FAQ link.
4.3 Security & Privacy
	•	TLS 1.2+; JWT session tokens; role-based authorization for HR actions.
	•	Data minimization: store hashed user IDs; scrub PII from logs.
	•	Vector store restricted to HR policy corpus; no cross-tenant leakage.
4.4 Compliance
	•	Retention per enterprise policy; configurable data residency.
	•	Audit trail for all MCP actions with user, time, parameters (redacted).
4.5 Observability
	•	LangSmith traces for: prompts, tools, token usage, latencies, errors.
	•	Prometheus/Grafana for infra; alerts on error-rate/cost spikes.
4.6 Maintainability & Portability
	•	Modular services: UI, Agent, RAG, MCP client, GuardRails adapter.
	•	IaC for repeatable deploys; Helm charts; twelve-factor app config.
4.7 Cost Effectiveness
	•	Token budgets by route (search vs leave).
	•	Model router: map intents to tiered models (cheap → default, premium → complex).
	•	Caching: prompt templates, retrieved chunks, and embeddings.
	•	Batch & streaming where applicable; max_new_tokens caps.
	•	Shadow eval off by default in production to reduce overhead.

5. Use Cases & Flows
5.1 Use Case: Search HR Policy
Actors: Employee, System Preconditions: Authenticated user; RAG index ready. Postconditions: Answer with citations; trace recorded.
Main Flow
	1	User asks a policy question.
	2	Input GuardRails.
	3	Agent detects policy_search.
	4	Retrieve top-k chunks from Vector DB.
	5	Synthesize with LLM; attach citations.
	6	Output GuardRails.
	7	Return response; record trace/metrics.
Sequence Diagram
sequenceDiagram
  autonumber
  actor Emp as Employee (Browser)
  participant UI as Py UI (Flask/Streamlit)
  participant GuardIn as GuardRails (Input)
  participant Agent as LangGraph Agent
  participant Ret as RAG Retriever
  database VDB as Vector DB (FAISS/Chroma/Pinecone)
  participant LLM as LLM (Config-Routed)
  participant GuardOut as GuardRails (Output)
  participant LS as LangSmith (Tracing)

  Emp->>UI: "What is the maternity leave policy?"
  UI->>GuardIn: validate(utterance, pii, jailbreak)
  GuardIn-->>UI: sanitized_utterance | block
  UI->>Agent: submit(query, user_ctx)
  Agent->>LS: start_trace(session)
  Agent->>Agent: intent = policy_search
  Agent->>Ret: retrieve(query, top_k=n)
  Ret->>VDB: similarity_search(emb(query))
  VDB-->>Ret: chunks + scores
  Ret-->>Agent: ranked_chunks (citations)
  Agent->>LLM: prompt(context=chunks, template=policy_answer)
  LLM-->>Agent: draft answer + citations
  Agent->>GuardOut: enforce_policies(answer)
  GuardOut-->>Agent: safe_answer
  Agent->>LS: end_trace(status=ok, tokens, latency)
  Agent-->>UI: answer + citations
  UI-->>Emp: Render with sources
5.2 Use Case: Apply for Leave
Actors: Employee, System Preconditions: Authenticated; MCP HR tool online; leave policy available. Postconditions: Leave request created; confirmation with request ID.
Main Flow
	1	User requests leave with dates and type.
	2	Input GuardRails.
	3	Agent detects leave_application.
	4	LLM extracts slots (type, start/end, reason).
	5	MCP call to validate balance and create request.
	6	Output GuardRails.
	7	Return confirmation with request ID; record trace.
Alternate Flows
	•	Insufficient balance → Explain policy and remaining balance.
	•	Invalid date range/holiday overlap → Suggest valid alternatives.
Sequence Diagram
sequenceDiagram
  autonumber
  actor Emp as Employee (Browser)
  participant UI as Py UI (Flask/Streamlit)
  participant GuardIn as GuardRails (Input)
  participant Agent as LangGraph Agent
  participant LLM as LLM (Config-Routed)
  participant MCPc as MCP Client
  participant MCPs as MCP Server (HR Tools)
  participant HR as HR Core APIs
  participant GuardOut as GuardRails (Output)
  participant LS as LangSmith (Tracing)

  Emp->>UI: "Apply 2 days casual leave from 15 Nov"
  UI->>GuardIn: validate(input)
  GuardIn-->>UI: sanitized_input | block
  UI->>Agent: submit(utterance, user_ctx)
  Agent->>LS: start_trace(session)
  Agent->>Agent: intent = leave_application
  Agent->>LLM: extract_slots(JSON schema)
  LLM-->>Agent: {type: CL, start: 2025-11-15, end: 2025-11-16}
  Agent->>MCPc: call("leave.apply", slots, user_ctx)
  MCPc->>MCPs: RPC/HTTP invoke tool
  MCPs->>HR: POST /leave/applications
  HR-->>MCPs: 200 {req_id, balance, status}
  MCPs-->>MCPc: tool_result
  MCPc-->>Agent: result
  Agent->>GuardOut: enforce_policies(confirmation)
  GuardOut-->>Agent: safe_confirmation
  Agent->>LS: end_trace(status=ok, tokens, latency)
  Agent-->>UI: confirmation + request_id
  UI-->>Emp: "Leave submitted. ID: LV-2025-1034"

6. System Architecture & Components
6.1 Logical Components
	•	Python UI (Flask/Streamlit): Auth, chat, citations, confirmations.
	•	LangGraph Agent: Intent routing, state machine, tool orchestration.
	•	RAG Service: Embedding generator, retriever, re-index jobs.
	•	Vector DB: FAISS/Chroma/Pinecone (configurable).
	•	MCP Client/Server: Hosted HR tools (balance check, apply leave).
	•	GuardRails Adapter: Input/output checks, policy enforcement.
	•	LLM Provider Abstraction: Config-driven model selection and fallbacks.
	•	LangSmith: Tracing, evaluation, cost metrics.
6.2 Pluggable LLM & Cost-Control Design
	•	Provider Interface (strategy pattern):
	◦	Provider: complete(), chat(), supports max_tokens, temperature, top_p, json_mode.
	◦	Implementations: OpenAIProvider, AnthropicProvider, AzureOpenAIProvider, LocalOllamaProvider, etc.
	•	Routing Policy (config):
	◦	default_model: cheap/general (e.g., gpt-4o-mini/claude-haiku/local).
	◦	premium_model: complex queries or low confidence.
	◦	routing_rules: by intent, confidence, context length, cost budget.
	•	Configuration:
	◦	ENV/YAML: provider keys, endpoints, model IDs, per-route token caps.
	◦	Hot-reload or at least rolling-restart reconfiguration.
	•	Fallbacks:
	◦	If provider A errors or exceeds SLA, fallback to provider B.
	◦	If token estimate > cap → compress context or ask for clarification.
	•	Cost Defender:
	◦	Preflight token estimation; deny or downshift to cheaper model.
	◦	Cache deterministic steps (e.g., slot extraction prompts).

7. Data & Interfaces
7.1 Policy Corpus & Embeddings
	•	Accepted types: PDF, DOCX, HTML, Markdown, FAQs.
	•	Preprocess: chunking (e.g., 512–1024 tokens overlap 10–20%), metadata (policy ID, section, effective date, locale).
	•	Re-embed jobs on document updates.
7.2 MCP Tool Contracts (Examples)
	•	leave.balance.get(user_id) → {balance_by_type}
	•	leave.apply(user_id, type, start_date, end_date, reason?) → {req_id, status, remaining_balance}
	•	calendar.validate_range(start_date, end_date) → {is_valid, conflicts[]}
7.3 GuardRails Policies
	•	Input: profanity, prompt injection, secrets, PII.
	•	Output: hallucination guard (cite-or-say-I-don’t-know), legal/policy compliance.

8. Technology Stack
Layer
Technology/Option
Notes
UI
Python (Flask or Streamlit)
Web chat, auth, templating.
Agent
LangChain + LangGraph
Tools, state, routing.
LLM
Config-routed (OpenAI/Anthropic/Azure/Open Router/Ollama)
Minimal config switch.
Embeddings
Configurable (e.g., text-embedding-3-large, nomic-embed, local)
Cost/accuracy trade-offs.
Vector DB
FAISS / Chroma / Pinecone
Choose per environment.
Safety
GuardRails
Input/output enforcement.
Monitoring
LangSmith (+ Prometheus/Grafana)
Traces, costs, SLOs.
APIs
MCP (HR tools)
Balance/apply, calendar validation.
AuthN/Z
SSO/OAuth2 + JWT
RBAC for actions.
Platform
Docker, Kubernetes, Helm
Horizontal scale, canary.
CI/CD
GitHub Actions/GitLab CI
Tests, image build, deploy.

9. Constraints & Assumptions
	•	Enterprise SSO available; HR APIs accessible via MCP.
	•	Policy corpus owned by HR and updated periodically.
	•	Network egress limits and data residency constraints respected.

10. Acceptance Criteria
	•	AC-1: Users can retrieve policy answers with at least one citation.
	•	AC-2: Users can submit leave requests and receive a request ID.
	•	AC-3: Admin can switch LLM provider via config without code changes.
	•	AC-4: p95 latency targets met with load test.
	•	AC-5: GuardRails blocks unsafe inputs/outputs per policy suite.
	•	AC-6: LangSmith shows traces, token usage, and error rates.

11. Testing Strategy (High-Level)
	•	Unit tests: agent nodes, tool adapters, LLM provider interface.
	•	Contract tests: MCP tools (mocked + integration).
	•	Retrieval tests: relevance@k; citation correctness.
	•	Red-team tests: prompt injection, data leakage.
	•	Load tests: concurrency and p95 targets.
	•	Cost tests: routing correctness under budget caps.

12. Deployment & Environments
	•	Dev: Local (Docker Compose) with FAISS, local/cheap LLM, mock MCP.
	•	Staging: Chroma/Pinecone, real MCP sandbox, full GuardRails, LangSmith on.
	•	Prod: HA K8s, HPA, managed Vector DB, primary + fallback LLMs, SSO.

13. Future Enhancements
	•	Voice I/O (ASR/TTS).
	•	Proactive notifications (policy updates, leave status changes).
	•	Multimodal RAG (scanned forms/images).
	•	HR analytics dashboard (trends, gaps).
	•	Domain-tuned LLM for HR compliance.

14. Diagrams
14.1 Sequence — Search HR Policy
sequenceDiagram
  autonumber
  actor Emp as Employee (Browser)
  participant UI as Py UI (Flask/Streamlit)
  participant GuardIn as GuardRails (Input)
  participant Agent as LangGraph Agent
  participant Ret as RAG Retriever
  database VDB as Vector DB (FAISS/Chroma/Pinecone)
  participant LLM as LLM (Config-Routed)
  participant GuardOut as GuardRails (Output)
  participant LS as LangSmith (Tracing)

  Emp->>UI: "What is the maternity leave policy?"
  UI->>GuardIn: validate(utterance, pii, jailbreak)
  GuardIn-->>UI: sanitized_utterance | block
  UI->>Agent: submit(query, user_ctx)
  Agent->>LS: start_trace(session)
  Agent->>Agent: intent = policy_search
  Agent->>Ret: retrieve(query, top_k)
  Ret->>VDB: similarity_search(emb(query))
  VDB-->>Ret: chunks + scores
  Ret-->>Agent: ranked_chunks (citations)
  Agent->>LLM: prompt(context=chunks, template=policy_answer)
  LLM-->>Agent: draft answer + citations
  Agent->>GuardOut: enforce_policies(answer)
  GuardOut-->>Agent: safe_answer
  Agent->>LS: end_trace(status=ok, tokens, latency)
  Agent-->>UI: answer + citations
  UI-->>Emp: Render with sources
14.2 Sequence — Apply for Leave
sequenceDiagram
  autonumber
  actor Emp as Employee (Browser)
  participant UI as Py UI (Flask/Streamlit)
  participant GuardIn as GuardRails (Input)
  participant Agent as LangGraph Agent
  participant LLM as LLM (Config-Routed)
  participant MCPc as MCP Client
  participant MCPs as MCP Server (HR Tools)
  participant HR as HR Core APIs
  participant GuardOut as GuardRails (Output)
  participant LS as LangSmith (Tracing)

  Emp->>UI: "Apply 2 days casual leave from 15 Nov"
  UI->>GuardIn: validate(input)
  GuardIn-->>UI: sanitized_input | block
  UI->>Agent: submit(utterance, user_ctx)
  Agent->>LS: start_trace(session)
  Agent->>Agent: intent = leave_application
  Agent->>LLM: extract_slots(JSON schema)
  LLM-->>Agent: {type: CL, start: 2025-11-15, end: 2025-11-16}
  Agent->>MCPc: call("leave.apply", slots, user_ctx)
  MCPc->>MCPs: RPC/HTTP invoke tool
  MCPs->>HR: POST /leave/applications
  HR-->>MCPs: 200 {req_id, balance, status}
  MCPs-->>MCPc: tool_result
  MCPc-->>Agent: result
  Agent->>GuardOut: enforce_policies(confirmation)
  GuardOut-->>Agent: safe_confirmation
  Agent->>LS: end_trace(status=ok, tokens, latency)
  Agent-->>UI: confirmation + request_id
  UI-->>Emp: "Leave submitted. ID: LV-2025-1034"

15. Configuration (LLM Switching & Cost Controls)
# config.yaml
llm:
  provider: openai            # openai | anthropic | azure | ollama
  model_default: gpt-4o-mini
  model_premium: gpt-4o
  temperature: 0.2
  max_new_tokens:
    policy_search: 400
    leave_application: 250
routing:
  by_intent:
    policy_search: default
    leave_application: default
  fallbacks:
    - provider: anthropic
      model_default: claude-3-haiku
      model_premium: claude-3-sonnet
cost:
  per_request_token_cap: 8_000
  deny_if_estimated_tokens_exceed_cap: true
  downgrade_if_high_cost: true
embeddings:
  provider: openai
  model: text-embedding-3-large
vector_db:
  backend: chroma
  collection: hr_policies_v1
mcp:
  base_url: https://mcp.hr.example/tools
  tools:
    - leave.balance.get
    - leave.apply
    - calendar.validate_range
guardrails:
  policy_bundle: enterprise-hr-v1
langsmith:
  project: hr-assistant
  tracing: true
Provider Interface Sketch (pseudocode):
class LLMProvider:
    def chat(self, messages, **opts): ...
class OpenAIProvider(LLMProvider): ...
class AnthropicProvider(LLMProvider): ...
def get_provider(cfg): ...

16. Appendix
16.1 Document Ingestion Pipeline
	•	Watch folder / API → parse → chunk → embed → upsert to Vector DB → verify counts → publish index.
16.2 Prompting Guidelines
	•	Retrieval-augmented templates; require citation IDs.
	•	JSON-mode for slot extraction.
	•	Refuse when low-confidence and no citations.
16.3 Risk Register (Selected)
	•	Provider outage → fallback chain.
	•	Policy drift → index freshness checks + re-embed cron.
	•	Cost spikes → routing rule to cheaper model + token caps.

