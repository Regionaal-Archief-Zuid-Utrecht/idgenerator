from flask import Flask, request, jsonify
from razu_idgenerator.database import Database
from razu_idgenerator.generator import IdentifierGenerator
from razu_idgenerator.validator import ValidationError

app = Flask(__name__)

db = Database()
generator = IdentifierGenerator(db)


@app.route('/generate', methods=['POST'])
def generate_identifier():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        producer = data.get('producer')
        dataset = data.get('dataset')
        type_val = data.get('type')
        aggregationlevel = data.get('aggregationlevel')
        inventarisnummer = data.get('inventarisnummer')
        filepath = data.get('filepath')
        
        identifier, is_new, stepped_dir = generator.generate(
            producer, dataset, type_val, aggregationlevel,
            inventarisnummer, filepath
        )
        
        return jsonify({
            "identifier": identifier,
            "is_new": is_new,
            "stepped_dir": stepped_dir
        }), 200
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")

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
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
