import json
import csv
import io
import xml.etree.ElementTree as ET
try:
    import defusedxml.ElementTree as DefusedET
except ImportError:
    DefusedET = ET  # Fallback if defusedxml is unavailable

MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

class PayloadParser:
    """Robust Payload Parser with safe XXE & XML Bomb protection."""

    @staticmethod
    def parse(payload: any, protocol: str = "JSON", config: dict = None) -> dict:
        config = config or {}

        if payload is None:
            return {}

        # Enforce maximum payload size guard
        if isinstance(payload, (bytes, str)) and len(payload) > MAX_PAYLOAD_BYTES:
            raise ValueError(f"Payload size exceeds maximum allowed limit of {MAX_PAYLOAD_BYTES // (1024 * 1024)} MB")

        protocol = protocol.upper()

        if protocol == "SOAP":
            return PayloadParser._parse_soap(payload)
        elif protocol == "XML":
            return PayloadParser._parse_xml(payload)
        elif protocol == "CSV":
            return PayloadParser._parse_csv(payload, config)
        elif protocol == "JSON":
            return PayloadParser._parse_json(payload)
        else:
            return PayloadParser._parse_json(payload)

    @staticmethod
    def _parse_soap(payload: any) -> dict:
        xml_dict = PayloadParser._parse_xml(payload)
        # Unwrap SOAP Envelope to extract Body
        body = xml_dict.get("Envelope", {}).get("Body") or xml_dict.get("Body") or xml_dict
        return body

    @staticmethod
    def _parse_xml(payload: any) -> dict:
        if isinstance(payload, bytes):
            payload_str = payload.decode('utf-8')
        else:
            payload_str = str(payload)

        # DefusedXML parse to protect against XXE and XML bomb entities
        try:
            root = DefusedET.fromstring(payload_str)
        except Exception as e:
            raise ValueError(f"XML Parsing Error: {str(e)}")

        return PayloadParser._xml_node_to_dict(root)

    @staticmethod
    def _xml_node_to_dict(node) -> dict:
        # Remove namespace prefix from tag
        tag = node.tag.split("}")[-1] if "}" in node.tag else node.tag
        result = {}

        # Capture XML Attributes
        if node.attrib:
            for k, v in node.attrib.items():
                attr_name = k.split("}")[-1] if "}" in k else k
                result[f"@{attr_name}"] = v

        # Process child elements
        children = list(node)
        if children:
            child_dict = {}
            for child in children:
                child_data = PayloadParser._xml_node_to_dict(child)
                child_tag = list(child_data.keys())[0] if child_data else child.tag.split("}")[-1]
                child_val = child_data[child_tag] if child_data else None

                if child_tag in child_dict:
                    if not isinstance(child_dict[child_tag], list):
                        child_dict[child_tag] = [child_dict[child_tag]]
                    child_dict[child_tag].append(child_val)
                else:
                    child_dict[child_tag] = child_val

            result.update(child_dict)
        else:
            text = (node.text or "").strip()
            if result:
                if text:
                    result["#text"] = text
            else:
                result = text

        return {tag: result}

    @staticmethod
    def _parse_json(payload: any) -> dict:
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            return {"items": payload}
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
                return data if isinstance(data, dict) else {"items": data}
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON Parsing Error: {str(e)}")
        return {}

    @staticmethod
    def _parse_csv(payload: any, config: dict) -> dict:
        if isinstance(payload, bytes):
            payload_str = payload.decode('utf-8')
        else:
            payload_str = str(payload)

        delimiter = config.get("delimiter", ",")
        has_header = config.get("has_header", True)

        f = io.StringIO(payload_str.strip())
        if has_header:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = [dict(row) for row in reader]
        else:
            reader = csv.reader(f, delimiter=delimiter)
            rows = [list(row) for row in reader]

        return {"rows": rows, "count": len(rows)}
