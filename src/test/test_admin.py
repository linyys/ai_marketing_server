import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from db.database import get_db, Base
from main import app
from utils.jwt_utils import create_access_token
from test_utils import make_request_with_format, TestFormatter
import json

# 创建测试数据库
test_db_path = os.path.join(os.path.dirname(__file__), "test_admin.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{test_db_path}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class TestAdmin:
    """管理员模块测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理测试数据
        db = TestingSessionLocal()
        try:
            db.execute(text("DELETE FROM admins"))
            db.commit()
        finally:
            db.close()
    
    def test_admin_register_success(self):
        """测试管理员注册成功"""
        admin_data = {
            "username": "testadmin",
            "email": "test@example.com",
            "password": "password123",
            "phone": "13800138000"
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册成功",
            expected_status=200,
            json_data=admin_data
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["username"] == "testadmin"
        assert data["email"] == "test@example.com"
        assert data["phone"] == "13800138000"
        assert "uid" in data
        assert "created_time" in data
    

    
    def test_admin_login_success(self):
        """测试管理员登录成功"""
        # 先注册一个管理员
        admin_data = {
            "username": "testadmin",
            "email": "test@example.com",
            "password": "password123"
        }
        make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为登录测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        
        # 登录
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/login",
            test_name="管理员登录成功",
            expected_status=200,
            json_data=login_data
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "admin_info" in data
        assert data["admin_info"]["email"] == "test@example.com"
    

    
    def test_get_admin_profile_success(self):
        """测试获取管理员信息成功"""
        # 先注册并登录
        admin_data = {
            "username": "testadmin",
            "email": "test@example.com",
            "password": "password123"
        }
        register_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为获取信息测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = register_result["output_params"]["body"]["uid"]
        
        # 创建token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取个人信息
        result = make_request_with_format(
            client=client,
            method="GET",
            route="/api/admin/profile",
            test_name="获取管理员个人信息",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["username"] == "testadmin"
        assert data["email"] == "test@example.com"
        assert data["uid"] == admin_uid
    

    
    def test_get_admin_by_id_success(self):
        """测试根据ID获取管理员信息成功"""
        # 先注册管理员
        admin_data = {
            "username": "testadmin",
            "email": "test@example.com",
            "password": "password123"
        }
        register_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为ID查询测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_info = register_result["output_params"]["body"]
        admin_uid = admin_info["uid"]
        admin_id = admin_info["id"]
        
        # 创建token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 根据ID获取管理员信息
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/admin/{admin_id}",
            test_name="根据ID获取管理员信息",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["id"] == admin_id
        assert data["username"] == "testadmin"
        assert data["email"] == "test@example.com"
    
    def test_get_admin_by_uid_success(self):
        """测试根据UID获取管理员信息成功"""
        # 先注册管理员
        admin_data = {
            "username": "testadmin",
            "email": "test@example.com",
            "password": "password123"
        }
        register_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为UID查询测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_info = register_result["output_params"]["body"]
        admin_uid = admin_info["uid"]
        
        # 创建token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 根据UID获取管理员信息
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/admin/uid/{admin_uid}",
            test_name="根据UID获取管理员信息",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["uid"] == admin_uid
        assert data["username"] == "testadmin"
        assert data["email"] == "test@example.com"
    
    def test_get_admins_list_success(self):
        """测试获取管理员列表成功"""
        # 先注册几个管理员
        for i in range(3):
            admin_data = {
                "username": f"testadmin{i}",
                "email": f"test{i}@example.com",
                "password": "password123"
            }
            make_request_with_format(
                client=client,
                method="POST",
                route="/api/admin/register",
                test_name=f"管理员注册{i}（为列表测试准备）",
                expected_status=200,
                json_data=admin_data
            )
        
        # 使用第一个管理员的token
        admin_data = {
            "username": "testadmin_main",
            "email": "testmain@example.com",
            "password": "password123"
        }
        register_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="主管理员注册（用于获取列表）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = register_result["output_params"]["body"]["uid"]
        
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取管理员列表
        result = make_request_with_format(
            client=client,
            method="GET",
            route="/api/admin/",
            test_name="获取管理员列表",
            expected_status=200,
            params={"page": 1, "page_size": 10},
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 3
        assert data["total"] >= 3
    


if __name__ == "__main__":
    pytest.main(["-v", __file__])