from flask import Flask, request, jsonify
from src.database import Database
from src.generator import IdentifierGenerator
from src.validator import ValidationError

app = Flask(__name__)

db = Database()
generator = IdentifierGenerator(db)


@app.route('/generate', methods=['POST'])
def generate_identifier():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    
    try:
        if data is None:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        
        producer = data.get('producer')
        dataset = data.get('dataset')
        type_val = data.get('type')
        aggregationlevel = data.get('aggregationlevel')
        inventarisnummer = data.get('inventarisnummer')
        filepath = data.get('filepath')
        
        identifier, is_new = generator.generate(
            producer, dataset, type_val, aggregationlevel,
            inventarisnummer, filepath
        )
        
        return jsonify({
            "identifier": identifier,
            "is_new": is_new
        }), 200
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
