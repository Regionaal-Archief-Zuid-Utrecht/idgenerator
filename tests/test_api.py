import json


class TestGenerateEndpoint:
    def test_generate_valid_request_returns_200(self, client):
        response = client.post('/generate',
            data=json.dumps({
                "producer": "g0352",
                "dataset": "689",
                "type": "Informatieobject",
                "aggregationlevel": "Archief"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "identifier" in data
        assert "is_new" in data
        assert "stepped_dir" in data
        assert data["identifier"] == "nl-wbdrazu-g0352-689-1"
        assert data["is_new"] is True
        assert data["stepped_dir"] == "000/000/"

    def test_generate_duplicate_request_returns_same_identifier(self, client):
        payload = {
            "producer": "g0352",
            "dataset": "689",
            "type": "Informatieobject",
            "aggregationlevel": "Archief"
        }
        
        response1 = client.post('/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response2 = client.post('/generate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        assert data1["identifier"] == data2["identifier"]
        assert data1["is_new"] is True
        assert data2["is_new"] is False
        assert data1["stepped_dir"] == data2["stepped_dir"]

    def test_generate_missing_producer_returns_400(self, client):
        response = client.post('/generate',
            data=json.dumps({
                "dataset": "689",
                "type": "Informatieobject",
                "aggregationlevel": "Archief"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_invalid_type_returns_400(self, client):
        response = client.post('/generate',
            data=json.dumps({
                "producer": "g0352",
                "dataset": "689",
                "type": "InvalidType",
                "aggregationlevel": "Archief"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_archief_with_inventarisnummer_returns_400(self, client):
        response = client.post('/generate',
            data=json.dumps({
                "producer": "g0352",
                "dataset": "689",
                "type": "Informatieobject",
                "aggregationlevel": "Archief",
                "inventarisnummer": "INV-001"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_archiefstuk_with_all_params_returns_200(self, client):
        response = client.post('/generate',
            data=json.dumps({
                "producer": "g0352",
                "dataset": "689",
                "type": "Informatieobject",
                "aggregationlevel": "Archiefstuk",
                "inventarisnummer": "INV-001",
                "filepath": "data/documents/file.pdf"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["identifier"].startswith("nl-wbdrazu-g0352-689-")
        assert data["is_new"] is True
        assert data["stepped_dir"] == "000/000/"

    def test_generate_malformed_json_returns_400(self, client):
        response = client.post('/generate',
            data='not valid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_generate_get_method_returns_405(self, client):
        response = client.get('/generate')
        assert response.status_code == 405


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
