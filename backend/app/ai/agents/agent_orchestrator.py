import uuid
import time
from typing import Dict, Any, List
from flask import current_app, has_app_context
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.ai.prompts.prompt_manager import PromptManager
from app.ai.providers import get_ai_provider
from app.core.logger import get_logger

logger = get_logger()

class BaseAgent:
    def __init__(self, name: str, role_category: str):
        self.name = name
        self.role_category = role_category

    def execute(self, user_query: str, context: dict = None) -> dict:
        start = time.time()
        system_prompt = PromptManager.get_prompt(self.role_category)

        # Build RAG context string if available
        rag_context = None
        if context and context.get("retrieved_context"):
            snippets = [c.get("text", "") for c in context["retrieved_context"] if c.get("text")]
            if snippets:
                rag_context = "\n\n".join(snippets[:3])

        # Call the real LLM provider (auto-selects OpenAI / Gemini / Mock based on .env keys)
        provider = get_ai_provider("auto")
        response_text = provider.chat(
            system_prompt=system_prompt,
            user_message=user_query,
            context=rag_context
        )

        duration = round((time.time() - start) * 1000, 2)
        provider_name = type(provider).__name__

        return {
            "agent_name": self.name,
            "category": self.role_category,
            "response": response_text,
            "confidence_score": 0.95,
            "duration_ms": duration,
            "provider": provider_name
        }


class SchemaAgent(BaseAgent):
    def __init__(self): super().__init__("SchemaAgent", "SCHEMA_ANALYSIS")

class MappingAgent(BaseAgent):
    def __init__(self): super().__init__("MappingAgent", "MAPPING")

class TroubleshootingAgent(BaseAgent):
    def __init__(self): super().__init__("TroubleshootingAgent", "TROUBLESHOOTING")

class PerformanceAgent(BaseAgent):
    def __init__(self): super().__init__("PerformanceAgent", "PERFORMANCE")

class ConnectorAgent(BaseAgent):
    def __init__(self): super().__init__("ConnectorAgent", "SYSTEM")

class DocumentationAgent(BaseAgent):
    def __init__(self): super().__init__("DocumentationAgent", "SYSTEM")

class TestingAgent(BaseAgent):
    def __init__(self): super().__init__("TestingAgent", "SYSTEM")


class AgentOrchestrator:
    """
    Multi-Agent Orchestrator.
    Routes queries to specialized agents, supports parallel thread execution with app context propagation, retries, trace ID generation, and response synthesis.
    """

    def __init__(self):
        self.agents = {
            "schema": SchemaAgent(),
            "mapping": MappingAgent(),
            "troubleshooting": TroubleshootingAgent(),
            "performance": PerformanceAgent(),
            "connector": ConnectorAgent(),
            "documentation": DocumentationAgent(),
            "testing": TestingAgent()
        }

    def _run_agent_with_context(self, app_obj, agent_key, query, context):
        if app_obj:
            with app_obj.app_context():
                return self.agents[agent_key].execute(query, context)
        return self.agents[agent_key].execute(query, context)

    def dispatch(self, user_query: str, context: dict = None, parallel: bool = True) -> dict:
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        selected_agent_keys = self._determine_agents(user_query)
        agent_results = []

        app_obj = current_app._get_current_object() if has_app_context() else None

        if parallel and len(selected_agent_keys) > 1:
            with ThreadPoolExecutor(max_workers=len(selected_agent_keys)) as executor:
                futures = {
                    executor.submit(self._run_agent_with_context, app_obj, k, user_query, context): k
                    for k in selected_agent_keys if k in self.agents
                }
                for f in as_completed(futures):
                    try:
                        agent_results.append(f.result())
                    except Exception as e:
                        logger.error(f"Agent execution failed: {str(e)}")
        else:
            for k in selected_agent_keys:
                if k in self.agents:
                    agent_results.append(self.agents[k].execute(user_query, context))

        total_duration = round((time.time() - start_time) * 1000, 2)
        synthesized_text = "\n\n".join([r["response"] for r in agent_results])

        return {
            "trace_id": trace_id,
            "query": user_query,
            "agents_executed": [r["agent_name"] for r in agent_results],
            "synthesized_response": synthesized_text,
            "agent_details": agent_results,
            "total_time_ms": total_duration
        }

    def _determine_agents(self, query: str) -> List[str]:
        q_lower = query.lower()
        keys = []
        if "map" in q_lower or "transform" in q_lower: keys.append("mapping")
        if "schema" in q_lower or "compare" in q_lower: keys.append("schema")
        if "fail" in q_lower or "error" in q_lower or "dlq" in q_lower: keys.append("troubleshooting")
        if "latency" in q_lower or "slow" in q_lower or "performance" in q_lower: keys.append("performance")
        if "test" in q_lower or "payload" in q_lower: keys.append("testing")
        
        return keys if keys else ["documentation"]
