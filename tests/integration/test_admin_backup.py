import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch

@pytest.mark.asyncio
async def test_admin_backup_endpoint_success():
    from app.auth import get_admin_user
    
    # Override dependency to simulate admin user
    app.dependency_overrides[get_admin_user] = lambda: {"email": "gm@test.com", "is_admin": True}
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Mock BackupService.refresh_prewarm_data
            with patch('app.services.backup.BackupService.refresh_prewarm_data') as mock_backup:
                 mock_backup.return_value = {"status": "success", "uploaded": 5}
                 
                 response = await ac.post("/api/admin/backup-market-data")
                 
                 assert response.status_code == 200
                 assert response.json() == {"status": "success", "uploaded": 5}
                 mock_backup.assert_called_once()
    finally:
        app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_admin_backup_endpoint_fail_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/admin/backup-market-data")
        assert response.status_code in [401, 403]
