from flask import request, Response
from flask_restx import Namespace, Resource, fields
from app.ai.services.copilot_service import CopilotService
from app.ai.tools.tool_registry import tool_registry
from app.ai.prompts.prompt_manager import PromptManager
from app.models.copilot_model import Conversation, Message

ns = Namespace('copilot', description='AI Integration Copilot, Multi-Agent RAG Assistant & Explainability APIs')
api = ns

copilot_service = CopilotService()

chat_model = ns.model('CopilotChatRequest', {
    'query': fields.String(required=True, description='User query or prompt text'),
    'user_id': fields.String(required=True, description='User ID'),
    'client_id': fields.String(description='Optional Tenant Client ID context'),
    'conversation_id': fields.String(description='Optional existing Conversation ID')
})

@ns.route('/chat')
class CopilotChatResource(Resource):
    @ns.doc('copilot_chat')
    @ns.expect(chat_model)
    def post(self):
        """Submit a prompt query to the AI Copilot for Multi-Agent & RAG synthesis with explainability metadata."""
        data = request.json or {}
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        user_id = data.get('user_id')
        if not user_id:
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity() or request.headers.get('X-User-ID')
            except Exception:
                user_id = request.headers.get('X-User-ID')
        try:
            res = copilot_service.process_chat_query(
                user_query=data.get('query'),
                user_id=user_id,
                client_id=data.get('client_id'),
                conversation_id=data.get('conversation_id')
            )
            return res, 200
        except Exception as e:
            return {'message': str(e)}, 400

@ns.route('/stream')
class CopilotStreamResource(Resource):
    @ns.doc('copilot_stream_sse')
    def get(self):
        """Stream real-time Copilot execution progress events via Server-Sent Events (SSE)."""
        query = request.args.get('query', 'Explain integration')
        return Response(
            copilot_service.stream_chat_events(query),
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'}
        )

@ns.route('/tools')
class CopilotToolsResource(Resource):
    @ns.doc('get_copilot_tools')
    def get(self):
        """Get list of generic AI callable tools (analyze_schema, compare_schema, generate_mapping, etc.)."""
        return {'tools': tool_registry.list_tools()}, 200

@ns.route('/conversations')
class ConversationListResource(Resource):
    @ns.doc('get_conversations')
    def get(self):
        """Get list of user conversations."""
        user_id = request.args.get('user_id')
        query = Conversation.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        convs = query.order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc()).all()
        return {
            'conversations': [
                {
                    'id': c.id,
                    'title': c.title,
                    'is_pinned': c.is_pinned,
                    'is_archived': c.is_archived,
                    'created_at': c.created_at.isoformat() if c.created_at else None
                } for c in convs
            ]
        }, 200

@ns.route('/conversations/<string:id>')
@ns.param('id', 'Conversation ID')
class ConversationDetailResource(Resource):
    @ns.doc('get_conversation_detail')
    def get(self, id):
        """Get conversation messages and explainability metadata history."""
        conv = Conversation.query.filter_by(id=id).first()
        if not conv:
            return {'message': 'Conversation not found'}, 404

        return {
            'id': conv.id,
            'title': conv.title,
            'messages': [
                {
                    'id': m.id,
                    'role': m.role,
                    'content': m.content,
                    'sources': m.sources,
                    'agents_executed': m.agents_executed,
                    'confidence_score': m.confidence_score,
                    'total_time_ms': m.total_time_ms,
                    'created_at': m.created_at.isoformat() if m.created_at else None
                } for m in conv.messages
            ]
        }, 200

    @ns.doc('delete_conversation')
    def delete(self, id):
        """Delete a conversation."""
        conv = Conversation.query.filter_by(id=id).first()
        if not conv:
            return {'message': 'Conversation not found'}, 404
        from app.core.extensions import db
        db.session.delete(conv)
        db.session.commit()
        return {'message': 'Conversation deleted successfully'}, 200

@ns.route('/prompts')
class CopilotPromptsResource(Resource):
    @ns.doc('get_copilot_prompts')
    def get(self):
        """Get prompt templates across categories (SYSTEM, MAPPING, TROUBLESHOOTING, PERFORMANCE)."""
        from app.models.copilot_model import PromptTemplate
        prompts = PromptTemplate.query.all()
        return {
            'prompts': [
                {
                    'id': p.id,
                    'category': p.category,
                    'name': p.name,
                    'version': p.version,
                    'template_text': p.template_text
                } for p in prompts
            ]
        }, 200
