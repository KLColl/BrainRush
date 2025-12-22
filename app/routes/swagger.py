from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import os
import yaml

swagger_bp = Blueprint('swagger', __name__, url_prefix='/api')

# Swagger UI конфігурація
SWAGGER_URL = '/api/docs'  # URL для Swagger UI
API_URL = '/api/swagger.yaml'  # URL для OpenAPI специфікації

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "BrainRush API Documentation",
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 3,
    }
)

@swagger_bp.route('/swagger.yaml')
def swagger_spec():
    """Повертає OpenAPI специфікацію у форматі YAML"""
    swagger_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'swagger.yaml'
    )

    try:
        with open(swagger_file, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec)
    except FileNotFoundError:
        return jsonify({"error": "Swagger specification not found"}), 404

@swagger_bp.route('/api-info')
def api_info():
    """Повертає базову інформацію про API"""
    return jsonify({
        "name": "BrainRush API",
        "version": "1.0.0",
        "description": "API for BrainRush",
        "documentation_url": SWAGGER_URL,
        "endpoints": {
            "user": "/api/v1/user/*",
            "shop": "/api/v1/shop/*",
            "feedback": "/api/v1/feedback/*",
            "stats": "/api/v1/stats/*",
        }
    })