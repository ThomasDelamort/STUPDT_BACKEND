import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app as fastapi_app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_endpoint():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["online"] is True


@pytest.mark.anyio
async def test_content_endpoints():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Departments
        res_dept = await client.get("/api/departments")
        assert res_dept.status_code == 200
        assert len(res_dept.json()) == 7

        # Quotes
        res_quotes = await client.get("/api/quotes")
        assert res_quotes.status_code == 200
        assert len(res_quotes.json()) >= 10

        # Metrics GET
        res_get = await client.get("/api/metrics")
        assert res_get.status_code == 200

        # Metrics POST (update)
        res_post = await client.post("/api/metrics", json={
            "specialistsConsulted": 35,
            "internalMeetings": 150,
            "minutesWasted": 210,
            "userSatisfaction": -600,
            "chaosMeter": 95
        })
        assert res_post.status_code == 200
        data_post = res_post.json()
        assert data_post["specialistsConsulted"] == 35


@pytest.mark.anyio
async def test_captcha_server_flow():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fetch challenge
        res = await client.get("/api/captcha/challenge")
        assert res.status_code == 200
        ch = res.json()
        assert "challengeId" in ch
        assert "tiles" in ch
        assert len(ch["tiles"]) == 9
        # Verify secret fields are NOT leaked to client!
        assert "is_target" not in ch["tiles"][0]
        assert "answer" not in ch["mathProblem"]

        # 2. Test incorrect tile submission fails
        res_fail = await client.post("/api/captcha/verify-tiles", json={
            "challengeId": ch["challengeId"],
            "selectedIds": [999]
        })
        assert res_fail.status_code == 200
        assert res_fail.json()["valid"] is False

        # 3. Test incorrect math submission fails
        res_math_fail = await client.post("/api/captcha/verify-math", json={
            "challengeId": ch["challengeId"],
            "answer": "wrong-answer"
        })
        assert res_math_fail.status_code == 200
        assert res_math_fail.json()["approved"] is False


@pytest.mark.anyio
async def test_vision_endpoints():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Samples
        res_samples = await client.get("/api/vision/samples")
        assert res_samples.status_code == 200
        samples = res_samples.json()
        assert len(samples) >= 3

        # 2. Analyze sample
        res_analyze = await client.post("/api/vision/analyze", json={
            "sampleId": "rock"
        })
        assert res_analyze.status_code == 200
        data = res_analyze.json()
        assert "detectedItem" in data
        assert "verdict" in data
        assert "ingredients" in data
        assert data["confidence"] == "100.00%"

        # 3. Analyze synthetic uploaded image (1x1 red PNG)
        # 1x1 transparent/red PNG base64
        sample_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        res_upload = await client.post("/api/vision/analyze", json={
            "base64Data": sample_png_b64,
            "filename": "suspicious_pixel.png",
            "mimeType": "image/png"
        })
        assert res_upload.status_code == 200
        upload_data = res_upload.json()
        assert "detectedItem" in upload_data
        assert "verdict" in upload_data
        assert upload_data["confidence"] == "100.00%"

        # 4. History
        res_hist = await client.get("/api/vision/history")
        assert res_hist.status_code == 200
        assert len(res_hist.json()) >= 2


@pytest.mark.anyio
async def test_apology_endpoints():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Preview
        res_prev = await client.get("/api/apology/preview")
        assert res_prev.status_code == 200
        data_prev = res_prev.json()
        assert data_prev["formNumber"] == "FORM AP-999-REV-B"
        assert data_prev["totalPages"] == 3

        # 2. Download PDF
        res_pdf = await client.get("/api/apology/download?name=Batman&reason=Gotham+Bureaucracy")
        assert res_pdf.status_code == 200
        assert res_pdf.headers["content-type"] == "application/pdf"
        assert res_pdf.content.startswith(b"%PDF-")
        assert len(res_pdf.content) > 1000
