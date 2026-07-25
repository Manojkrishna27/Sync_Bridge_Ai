from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.mapping_service import MappingService
from app.services.schema_analyzer import SchemaAnalyzer

ns = Namespace('schema', description='Visual Mapping Studio, AI Schema Intelligence & Schema Comparison API')
api = ns

service = MappingService()

upload_schema_model = ns.model('UploadSchema', {
    'client_id': fields.String(required=True, description='Tenant Client ID'),
    'name': fields.String(required=True, description='Schema Identifier Name'),
    'format': fields.String(required=True, description='Format (JSON, XML, SOAP, CSV, OPENAPI, XSD)'),
    'raw_schema': fields.String(required=True, description='Raw Schema or sample payload string'),
    'description': fields.String(description='Description of schema')
})

compare_schema_model = ns.model('CompareSchema', {
    'source_schema_id': fields.String(required=True, description='Source Schema ID'),
    'target_schema_id': fields.String(required=True, description='Target Schema ID')
})

map_schema_model = ns.model('GenerateAIMapping', {
    'source_schema_id': fields.String(required=True, description='Source Schema ID'),
    'target_schema_id': fields.String(required=True, description='Target Schema ID'),
    'mapping_id': fields.String(description='Optional existing mapping ID for context')
})

save_mapping_model = ns.model('SaveMapping', {
    'client_id': fields.String(required=True, description='Client ID'),
    'name': fields.String(required=True, description='Mapping Title'),
    'rules': fields.List(fields.Raw, required=True, description='List of mapping rule definitions'),
    'source_schema_id': fields.String(description='Source Schema ID'),
    'target_schema_id': fields.String(description='Target Schema ID'),
    'integration_id': fields.String(description='Associated Integration ID'),
    'mapping_id': fields.String(description='Mapping ID if updating existing'),
    'change_description': fields.String(description='Version change notes')
})

simulate_model = ns.model('SimulateMapping', {
    'source_payload': fields.Raw(required=True, description='Sample input payload dictionary'),
    'rules': fields.List(fields.Raw, required=True, description='Mapping rules to test')
})

@ns.route('/upload')
class SchemaUploadResource(Resource):
    @ns.doc('upload_schema')
    @ns.expect(upload_schema_model)
    def post(self):
        """Upload a new schema (JSON, XML, SOAP, CSV, OpenAPI, XSD) and generate hierarchical tree nodes."""
        data = request.json or {}
        try:
            schema = service.upload_schema(
                client_id=data.get('client_id'),
                name=data.get('name'),
                format_type=data.get('format', 'JSON'),
                raw_schema=data.get('raw_schema'),
                description=data.get('description')
            )
            v = schema.versions[0]
            return {
                'id': schema.id,
                'name': schema.name,
                'format': schema.format,
                'version': v.version_number,
                'parsed_tree': v.parsed_tree
            }, 201
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/analyze')
class SchemaAnalyzeResource(Resource):
    @ns.doc('analyze_schema')
    def post(self):
        """Analyze raw schema text on the fly without saving."""
        data = request.json or {}
        raw = data.get('raw_schema', '')
        fmt = data.get('format', 'JSON')
        try:
            tree = SchemaAnalyzer.analyze(raw, fmt)
            flat_fields = SchemaAnalyzer.extract_flat_fields(tree)
            return {'parsed_tree': tree, 'flat_fields': flat_fields}, 200
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/compare')
class SchemaCompareResource(Resource):
    @ns.doc('compare_schemas')
    @ns.expect(compare_schema_model)
    def post(self):
        """Compare two schemas or schema versions and return missing/extra fields, type changes, breaking changes, and compatibility score."""
        data = request.json or {}
        try:
            result = service.compare_schemas(data.get('source_schema_id'), data.get('target_schema_id'))
            return result, 200
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/map')
class SchemaAIMapResource(Resource):
    @ns.doc('generate_ai_mapping')
    @ns.expect(map_schema_model)
    def post(self):
        """Generate hybrid AI & heuristic schema mapping suggestions with confidence scores and reasoning."""
        data = request.json or {}
        try:
            suggestions = service.generate_ai_suggestions(
                source_schema_id=data.get('source_schema_id'),
                target_schema_id=data.get('target_schema_id'),
                mapping_id=data.get('mapping_id')
            )
            return {'suggestions': suggestions, 'total': len(suggestions)}, 200
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/validate')
class SchemaValidateMappingResource(Resource):
    @ns.doc('validate_mapping_rules')
    def post(self):
        """Validate mapping rules for circular references, duplicate targets, type mismatches, and orphan fields with severity diagnostics."""
        data = request.json or {}
        rules = data.get('rules', [])
        target_schema_id = data.get('target_schema_id')
        result = service.validate_mapping_rules(rules, target_schema_id)
        return result, 200

@ns.route('/preview')
class SchemaPreviewSimulationResource(Resource):
    @ns.doc('preview_simulation')
    @ns.expect(simulate_model)
    def post(self):
        """Simulate mapping run against sample payload without external HTTP side-effects."""
        data = request.json or {}
        payload = data.get('source_payload', {})
        rules = data.get('rules', [])
        result = service.simulate_mapping(payload, rules)
        return result, 200

@ns.route('/<string:id>')
@ns.param('id', 'Schema ID')
class SchemaDetailResource(Resource):
    @ns.doc('get_schema_detail')
    def get(self, id):
        """Get schema details, raw schema definition, and tree nodes."""
        try:
            schema = service.get_schema(id)
            v = schema.versions[-1] if schema.versions else None
            return {
                'id': schema.id,
                'name': schema.name,
                'format': schema.format,
                'description': schema.description,
                'latest_version': v.version_number if v else 1,
                'raw_schema': v.raw_schema if v else None,
                'parsed_tree': v.parsed_tree if v else {}
            }, 200
        except ValueError as e:
            return {'message': str(e)}, 404

# --- Mappings Endpoints ---
@ns.route('/mappings/save')
class MappingSaveResource(Resource):
    @ns.doc('save_mapping')
    @ns.expect(save_mapping_model)
    def post(self):
        """Save or update visual schema mapping, snapshot version, and create mapping rules."""
        data = request.json or {}
        try:
            mapping = service.save_mapping(
                client_id=data.get('client_id'),
                name=data.get('name'),
                rules=data.get('rules', []),
                source_schema_id=data.get('source_schema_id'),
                target_schema_id=data.get('target_schema_id'),
                integration_id=data.get('integration_id'),
                mapping_id=data.get('mapping_id'),
                change_description=data.get('change_description', 'Saved mapping update')
            )
            return {
                'id': mapping.id,
                'name': mapping.name,
                'version': mapping.version,
                'rules_count': len(mapping.rules)
            }, 200
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/mappings/<string:id>')
@ns.param('id', 'Mapping ID')
class MappingDetailResource(Resource):
    @ns.doc('get_mapping_detail')
    def get(self, id):
        """Get mapping definition, rules, and version history."""
        from app.models.schema_model import Mapping
        mapping = Mapping.query.filter_by(id=id).first()
        if not mapping:
            return {'message': 'Mapping not found'}, 404

        return {
            'id': mapping.id,
            'name': mapping.name,
            'version': mapping.version,
            'client_id': mapping.client_id,
            'source_schema_id': mapping.source_schema_id,
            'target_schema_id': mapping.target_schema_id,
            'rules': [
                {
                    'source_path': r.source_path,
                    'target_path': r.target_path,
                    'rule_type': r.rule_type,
                    'strategy_used': r.strategy_used,
                    'config': r.config
                } for r in mapping.rules
            ],
            'versions': [
                {
                    'version_number': v.version_number,
                    'change_description': v.change_description,
                    'created_by': v.created_by,
                    'created_at': v.created_at.isoformat() if v.created_at else None
                } for v in mapping.versions
            ]
        }, 200

@ns.route('/mappings/<string:id>/rollback')
@ns.param('id', 'Mapping ID')
class MappingRollbackResource(Resource):
    @ns.doc('rollback_mapping')
    def post(self, id):
        """Rollback mapping definition to a specific historical version."""
        data = request.json or {}
        version_number = data.get('version_number')
        if not version_number:
            return {'message': 'version_number parameter is required'}, 400
        try:
            mapping = service.rollback_mapping(id, version_number)
            return {
                'id': mapping.id,
                'name': mapping.name,
                'new_version': mapping.version,
                'message': f'Successfully rolled back to version {version_number}'
            }, 200
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/mappings/templates')
class MappingTemplatesResource(Resource):
    @ns.doc('get_mapping_templates')
    def get(self):
        """Get pre-built reusable enterprise mapping templates (SAP -> Salesforce, SOAP -> JSON, etc.)."""
        templates = MappingService.get_templates()
        return {'templates': templates}, 200
