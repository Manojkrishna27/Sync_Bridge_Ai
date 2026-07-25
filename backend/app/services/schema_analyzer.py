import json
import csv
import io
import xml.etree.ElementTree as ET
try:
    import defusedxml.ElementTree as DefusedET
except ImportError:
    DefusedET = ET

class SchemaAnalyzer:
    """
    Schema Analyzer Service.
    Parses JSON, XML, SOAP, CSV, OpenAPI, Swagger, and XSD schemas into unified tree structures.
    """

    @staticmethod
    def analyze(raw_schema: str, format_type: str = "JSON") -> dict:
        if not raw_schema or not raw_schema.strip():
            return {"fields": [], "root_type": "object"}

        fmt = format_type.upper()

        if fmt == "JSON":
            return SchemaAnalyzer._analyze_json(raw_schema)
        elif fmt in ["XML", "SOAP", "XSD"]:
            return SchemaAnalyzer._analyze_xml(raw_schema, fmt)
        elif fmt == "CSV":
            return SchemaAnalyzer._analyze_csv(raw_schema)
        elif fmt in ["OPENAPI", "SWAGGER"]:
            return SchemaAnalyzer._analyze_openapi(raw_schema)
        else:
            return SchemaAnalyzer._analyze_json(raw_schema)

    @staticmethod
    def extract_flat_fields(schema_tree: dict, parent_path: str = "") -> list:
        fields = []
        nodes = schema_tree.get("fields", [])
        for node in nodes:
            path = f"{parent_path}.{node['name']}" if parent_path else node['name']
            fields.append({
                "path": path,
                "name": node.get("name"),
                "type": node.get("type", "string"),
                "required": node.get("required", False),
                "nullable": node.get("nullable", True),
                "description": node.get("description"),
                "example": node.get("example"),
                "enum": node.get("enum")
            })
            if node.get("children"):
                sub_tree = {"fields": node["children"]}
                fields.extend(SchemaAnalyzer.extract_flat_fields(sub_tree, path))
        return fields

    @staticmethod
    def _analyze_json(raw_str: str) -> dict:
        try:
            data = json.loads(raw_str)
            fields = SchemaAnalyzer._parse_dict_to_nodes(data)
            return {"root_type": "object", "fields": fields}
        except Exception as e:
            raise ValueError(f"JSON Schema Parsing Error: {str(e)}")

    @staticmethod
    def _parse_dict_to_nodes(obj, prefix="") -> list:
        nodes = []
        if isinstance(obj, dict):
            # Check if JSON Schema standard format
            if "properties" in obj:
                props = obj.get("properties", {})
                reqs = obj.get("required", [])
                for k, v in props.items():
                    ftype = v.get("type", "string") if isinstance(v, dict) else "string"
                    node = {
                        "name": k,
                        "type": ftype,
                        "required": k in reqs,
                        "description": v.get("description") if isinstance(v, dict) else None,
                        "example": v.get("example") if isinstance(v, dict) else None,
                        "enum": v.get("enum") if isinstance(v, dict) else None
                    }
                    if ftype == "object" and "properties" in v:
                        node["children"] = SchemaAnalyzer._parse_dict_to_nodes(v)
                    nodes.append(node)
                return nodes

            for k, v in obj.items():
                node = {
                    "name": k,
                    "type": SchemaAnalyzer._python_type_name(v),
                    "required": True,
                    "example": str(v)[:100] if not isinstance(v, (dict, list)) else None
                }
                if isinstance(v, dict):
                    node["type"] = "object"
                    node["children"] = SchemaAnalyzer._parse_dict_to_nodes(v)
                elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    node["type"] = "array"
                    node["children"] = SchemaAnalyzer._parse_dict_to_nodes(v[0])
                nodes.append(node)
        return nodes

    @staticmethod
    def _analyze_xml(raw_str: str, fmt: str) -> dict:
        try:
            root = DefusedET.fromstring(raw_str.strip())
            tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            nodes = [SchemaAnalyzer._xml_node_to_schema_node(root)]
            return {"root_type": "xml_element", "root_tag": tag, "fields": nodes}
        except Exception as e:
            raise ValueError(f"XML/SOAP Schema Parsing Error: {str(e)}")

    @staticmethod
    def _xml_node_to_schema_node(elem) -> dict:
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        children = list(elem)
        
        node = {
            "name": tag,
            "type": "object" if children else "string",
            "required": True,
            "example": elem.text.strip() if elem.text and elem.text.strip() else None
        }

        if children:
            node["children"] = [SchemaAnalyzer._xml_node_to_schema_node(c) for c in children]

        return node

    @staticmethod
    def _analyze_csv(raw_str: str) -> dict:
        f = io.StringIO(raw_str.strip())
        reader = csv.reader(f)
        header = next(reader, [])
        first_row = next(reader, [])

        fields = []
        for idx, col_name in enumerate(header):
            val = first_row[idx] if idx < len(first_row) else None
            fields.append({
                "name": col_name,
                "type": "string",
                "required": True,
                "example": val
            })
        return {"root_type": "csv_table", "fields": fields}

    @staticmethod
    def _analyze_openapi(raw_str: str) -> dict:
        data = json.loads(raw_str)
        schemas = data.get("components", {}).get("schemas", {}) or data.get("definitions", {})
        first_schema = list(schemas.values())[0] if schemas else data
        fields = SchemaAnalyzer._parse_dict_to_nodes(first_schema)
        return {"root_type": "openapi_spec", "fields": fields}

    @staticmethod
    def _python_type_name(val) -> str:
        if isinstance(val, bool): return "boolean"
        if isinstance(val, int): return "integer"
        if isinstance(val, float): return "number"
        if isinstance(val, list): return "array"
        if isinstance(val, dict): return "object"
        return "string"
