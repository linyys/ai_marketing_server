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
from src.test.test_utils import make_request_with_format, TestFormatter

# 创建测试数据库
test_db_path = os.path.join(os.path.dirname(__file__), "test_user.db")
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

class TestUser:
    """用户模块测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理测试数据
        db = TestingSessionLocal()
        try:
            db.execute(text("DELETE FROM users"))
            db.execute(text("DELETE FROM admins"))
            db.commit()
        finally:
            db.close()
    
    def test_user_register_success(self):
        """测试用户注册成功"""
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123",
            "phone": "13800138000"
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册成功",
            expected_status=200,
            json_data=user_data
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["username"] == "testuser"
        assert data["email"] == "user@example.com"
        assert data["phone"] == "13800138000"
        assert "uid" in data
        assert "created_time" in data
    
    def test_user_login_success(self):
        """测试用户登录成功"""
        # 先注册一个用户
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（为登录测试准备）",
            expected_status=200,
            json_data=user_data
        )
        
        # 登录
        login_data = {
            "email": "user@example.com",
            "password": "password123"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/login",
            test_name="用户登录成功",
            expected_status=200,
            json_data=login_data
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user_info" in data
        assert data["user_info"]["email"] == "user@example.com"
    
    def test_get_user_success(self):
        """测试获取用户信息成功"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        register_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（为获取用户信息测试准备）",
            expected_status=200,
            json_data=user_data
        )
        user_uid = register_result["output_params"]["body"]["uid"]
        
        # 创建token
        token = create_access_token(data={"sub": user_uid})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户信息
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/user/get/{user_uid}",
            test_name="获取用户信息成功",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["username"] == "testuser"
        assert data["email"] == "user@example.com"
        assert data["uid"] == user_uid
    
    def test_get_users_list_by_admin_success(self):
        """测试管理员获取用户列表成功"""
        # 先注册几个用户
        for i in range(3):
            user_data = {
                "username": f"testuser{i}",
                "email": f"user{i}@example.com",
                "password": "password123"
            }
            make_request_with_format(
                client=client,
                method="POST",
                route="/api/user/register",
                test_name=f"用户注册{i}（为获取用户列表测试准备）",
                expected_status=200,
                json_data=user_data
            )
        
        # 注册管理员
        admin_data = {
            "username": "testadmin",
            "email": "admin@example.com",
            "password": "password123"
        }
        admin_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为获取用户列表测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = admin_result["output_params"]["body"]["uid"]
        
        # 使用管理员token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户列表
        result = make_request_with_format(
            client=client,
            method="GET",
            route="/api/user/list?skip=0&limit=10",
            test_name="管理员获取用户列表成功",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 3
        assert data["total"] >= 3
    
    def test_search_users_by_admin_success(self):
        """测试管理员搜索用户成功"""
        # 先注册用户
        user_data = {
            "username": "searchuser",
            "email": "search@example.com",
            "password": "password123"
        }
        make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（为搜索用户测试准备）",
            expected_status=200,
            json_data=user_data
        )
        
        # 注册管理员
        admin_data = {
            "username": "testadmin",
            "email": "admin@example.com",
            "password": "password123"
        }
        admin_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为搜索用户测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = admin_result["output_params"]["body"]["uid"]
        
        # 使用管理员token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 搜索用户
        search_params = {
            "username": "search"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/search?skip=0&limit=10",
            test_name="管理员搜索用户成功",
            expected_status=200,
            json_data=search_params,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 1
        assert "searchuser" in [item["username"] for item in data["items"]]
    
    def test_update_user_by_admin_success(self):
        """测试管理员更新用户信息成功"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        user_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（为更新用户信息测试准备）",
            expected_status=200,
            json_data=user_data
        )
        user_uid = user_result["output_params"]["body"]["uid"]
        
        # 注册管理员
        admin_data = {
            "username": "testadmin",
            "email": "admin@example.com",
            "password": "password123"
        }
        admin_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为更新用户信息测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = admin_result["output_params"]["body"]["uid"]
        
        # 使用管理员token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 更新用户信息
        update_data = {
            "username": "updateduser",
            "phone": "13900139000"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/user/update?uid={user_uid}",
            test_name="管理员更新用户信息成功",
            expected_status=200,
            json_data=update_data,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["username"] == "updateduser"
        assert data["phone"] == "13900139000"
    
    def test_update_password_success(self):
        """测试用户修改密码成功"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        user_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（为修改密码测试准备）",
            expected_status=200,
            json_data=user_data
        )
        user_uid = user_result["output_params"]["body"]["uid"]
        
        # 创建用户token
        token = create_access_token(data={"sub": user_uid})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 修改密码
        password_data = {
            "old_password": "password123",
            "new_password": "newpassword123"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/user/update/password?uid={user_uid}",
            test_name="用户修改密码成功",
            expected_status=200,
            json_data=password_data,
            headers=headers
        )
        
        assert result["is_passed"]
        
        # 验证新密码可以登录
        login_data = {
            "email": "user@example.com",
            "password": "newpassword123"
        }
        login_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/login",
            test_name="验证新密码登录",
            expected_status=200,
            json_data=login_data
        )
        assert login_result["is_passed"]
    
    def test_delete_user_by_admin_success(self):
        """测试管理员删除用户成功"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        user_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（为删除用户测试准备）",
            expected_status=200,
            json_data=user_data
        )
        user_uid = user_result["output_params"]["body"]["uid"]
        
        # 注册管理员
        admin_data = {
            "username": "testadmin",
            "email": "admin@example.com",
            "password": "password123"
        }
        admin_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（为删除用户测试准备）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = admin_result["output_params"]["body"]["uid"]
        
        # 使用管理员token
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 删除用户
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/user/delete?uid={user_uid}",
            test_name="管理员删除用户成功",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]

if __name__ == "__main__":
    pytest.main(["-v", __file__])