from typing import Dict, Any, Callable, List
from app.services.schema_analyzer import SchemaAnalyzer
from app.services.schema_comparator import SchemaComparator
from app.services.mapping_service import MappingService

class AITool:
    def __init__(self, tool_name: str, description: str, func: Callable, input_schema: dict = None):
        self.tool_name = tool_name
        self.description = description
        self.func = func
        self.input_schema = input_schema or {}
        self.version = "1.0"
        self.timeout = 10.0

    def execute(self, **kwargs) -> dict:
        try:
            res = self.func(**kwargs)
            return {"status": "SUCCESS", "result": res}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

class ToolRegistry:
    """Enterprise AI Tool Calling Registry."""

    def __init__(self):
        self.mapping_service = MappingService()
        self._tools: Dict[str, AITool] = {}
        self._register_default_tools()

    def register(self, tool: AITool):
        self._tools[tool.tool_name] = tool

    def get_tool(self, tool_name: str) -> AITool:
        return self._tools.get(tool_name)

    def list_tools(self) -> List[dict]:
        return [
            {
                "tool_name": t.tool_name,
                "description": t.description,
                "version": t.version
            } for t in self._tools.values()
        ]

    def _register_default_tools(self):
        # 1. analyze_schema
        self.register(AITool(
            "analyze_schema",
            "Analyzes raw JSON/XML/SOAP schema text and extracts fields",
            lambda raw_schema, format="JSON": SchemaAnalyzer.analyze(raw_schema, format)
        ))

        # 2. compare_schema
        self.register(AITool(
            "compare_schema",
            "Compares two schemas and calculates structural diffs and compatibility score",
            lambda source_tree, target_tree: SchemaComparator.compare(source_tree, target_tree)
        ))

        # 3. generate_mapping
        self.register(AITool(
            "generate_mapping",
            "Generates hybrid AI & heuristic field mapping suggestions",
            lambda source_tree, target_tree: self.mapping_service.ai_mapper.generate_hybrid_mappings(source_tree, target_tree)
        ))

        # 4. validate_mapping
        self.register(AITool(
            "validate_mapping",
            "Validates mapping rules for circular references and duplicate targets",
            lambda rules: self.mapping_service.validate_mapping_rules(rules)
        ))

        # 5. preview_mapping
        self.register(AITool(
            "preview_mapping",
            "Simulates mapping execution on sample input payload",
            lambda source_payload, rules: self.mapping_service.simulate_mapping(source_payload, rules)
        ))

tool_registry = ToolRegistry()
