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

# 创建测试数据库
test_db_path = os.path.join(os.path.dirname(__file__), "test_knowledge.db")
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

class TestKnowledge:
    """知识库模块测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理测试数据
        db = TestingSessionLocal()
        try:
            db.execute(text("DELETE FROM knowledges"))
            db.execute(text("DELETE FROM admins"))
            db.execute(text("DELETE FROM users"))
            db.commit()
        finally:
            db.close()
    
    def _create_admin_and_get_token(self):
        """创建管理员并返回token"""
        admin_data = {
            "username": "testadmin",
            "email": "admin@example.com",
            "password": "password123"
        }
        admin_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/admin/register",
            test_name="管理员注册（辅助方法）",
            expected_status=200,
            json_data=admin_data
        )
        admin_uid = admin_result["output_params"]["body"]["uid"]
        token = create_access_token(data={"sub": admin_uid, "is_admin": True})
        return token, admin_uid
    
    def _create_user_and_get_token(self):
        """创建用户并返回token"""
        user_data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123"
        }
        user_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/user/register",
            test_name="用户注册（辅助方法）",
            expected_status=200,
            json_data=user_data
        )
        user_uid = user_result["output_params"]["body"]["uid"]
        token = create_access_token(data={"sub": user_uid})
        return token, user_uid
    
    def test_create_knowledge_success(self):
        """测试创建知识库成功"""
        token, user_uid = self._create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        knowledge_data = {
            "name": "测试知识库",
            "description": "这是一个测试知识库",
            "content": "知识库内容示例"
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建知识库成功",
            expected_status=200,
            json_data=knowledge_data,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "测试知识库"
        assert data["description"] == "这是一个测试知识库"
        assert data["from_user"] == user_uid
        assert data["content"] == "知识库内容示例"
        assert "uid" in data
        assert "created_time" in data
    
    def test_get_knowledge_success(self):
        """测试获取知识库详情成功"""
        # 先创建用户和知识库
        token, user_uid = self._create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        knowledge_data = {
            "name": "获取测试知识库",
            "description": "用于测试获取的知识库",
            "content": "获取测试内容"
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建知识库（为获取测试准备）",
            expected_status=200,
            json_data=knowledge_data,
            headers=headers
        )
        knowledge_uid = create_result["output_params"]["body"]["uid"]
        
        # 获取知识库详情
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/knowledge/get/{knowledge_uid}",
            test_name="获取知识库详情成功",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "获取测试知识库"
        assert data["description"] == "用于测试获取的知识库"
        assert data["from_user"] == user_uid
        assert data["content"] == "获取测试内容"
        assert data["uid"] == knowledge_uid
    
    def test_get_knowledges_list_by_admin_success(self):
        """测试管理员获取所有知识库列表成功"""
        # 先创建用户和知识库
        user_token, user_uid = self._create_user_and_get_token()
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        for i in range(3):
            knowledge_data = {
                "name": f"知识库{i}",
                "description": f"描述{i}",
                "content": f"内容{i}"
            }
            make_request_with_format(
                client=client,
                method="POST",
                route="/api/knowledge/create",
                test_name=f"创建知识库{i}（为管理员列表测试准备）",
                expected_status=200,
                json_data=knowledge_data,
                headers=user_headers
            )
        
        # 管理员获取所有知识库列表
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        result = make_request_with_format(
            client=client,
            method="GET",
            route="/api/knowledge/list?skip=0&limit=10",
            test_name="管理员获取所有知识库列表成功",
            expected_status=200,
            headers=admin_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 3
        assert data["total"] >= 3
    
    def test_get_user_knowledges_success(self):
        """测试获取指定用户的知识库列表成功"""
        # 先创建用户和知识库
        token, user_uid = self._create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        for i in range(2):
            knowledge_data = {
                "name": f"用户知识库{i}",
                "description": f"用户描述{i}",
                "content": f"用户内容{i}"
            }
            make_request_with_format(
                client=client,
                method="POST",
                route="/api/knowledge/create",
                test_name=f"创建用户知识库{i}（为用户列表测试准备）",
                expected_status=200,
                json_data=knowledge_data,
                headers=headers
            )
        
        # 获取用户自己的知识库列表
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/knowledge/list/{user_uid}?skip=0&limit=10",
            test_name="获取指定用户的知识库列表成功",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 2
        assert data["total"] >= 2
    
    def test_search_knowledges_success(self):
        """测试搜索知识库成功"""
        # 先创建用户和知识库
        token, user_uid = self._create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        knowledge_data = {
            "name": "搜索测试知识库",
            "description": "用于搜索测试的知识库",
            "content": "搜索测试内容"
        }
        make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建知识库（为搜索测试准备）",
            expected_status=200,
            json_data=knowledge_data,
            headers=headers
        )
        
        # 搜索知识库
        search_params = {
            "name": "搜索测试"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/search?skip=0&limit=10",
            test_name="搜索知识库成功",
            expected_status=200,
            json_data=search_params,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 1
        assert "搜索测试知识库" in [item["name"] for item in data["items"]]
    
    def test_update_knowledge_success(self):
        """测试更新知识库成功"""
        # 先创建用户和知识库
        token, user_uid = self._create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        knowledge_data = {
            "name": "原始知识库",
            "description": "原始描述",
            "content": "原始内容"
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建知识库（为更新测试准备）",
            expected_status=200,
            json_data=knowledge_data,
            headers=headers
        )
        knowledge_uid = create_result["output_params"]["body"]["uid"]
        
        # 更新知识库
        update_data = {
            "name": "更新后知识库",
            "description": "更新后描述",
            "content": "更新后内容"
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/knowledge/update?uid={knowledge_uid}",
            test_name="更新知识库成功",
            expected_status=200,
            json_data=update_data,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "更新后知识库"
        assert data["description"] == "更新后描述"
        assert data["from_user"] is None
        assert data["content"] == "更新后内容"
    
    def test_delete_knowledge_success(self):
        """测试删除知识库成功"""
        # 先创建用户和知识库
        token, user_uid = self._create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        knowledge_data = {
            "name": "待删除知识库",
            "description": "待删除描述",
            "content": "待删除内容"
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建知识库（为删除测试准备）",
            expected_status=200,
            json_data=knowledge_data,
            headers=headers
        )
        knowledge_uid = create_result["output_params"]["body"]["uid"]
        
        # 删除知识库
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/knowledge/delete?uid={knowledge_uid}",
            test_name="删除知识库成功",
            expected_status=200,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "message" in data or "success" in str(data).lower()
    
    def test_admin_access_all_knowledges_success(self):
        """测试管理员可以访问所有知识库"""
        # 先创建用户和私有知识库
        user_token, user_uid = self._create_user_and_get_token()
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        knowledge_data = {
            "name": "私有知识库",
            "description": "用户私有知识库",
            "content": "私有内容"
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建私有知识库（为管理员访问测试准备）",
            expected_status=200,
            json_data=knowledge_data,
            headers=user_headers
        )
        knowledge_uid = create_result["output_params"]["body"]["uid"]
        
        # 管理员访问用户的私有知识库
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/knowledge/get/{knowledge_uid}",
            test_name="管理员访问所有知识库成功",
            expected_status=200,
            headers=admin_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "私有知识库"
        assert data["from_user"] == user_uid
    
    def test_public_knowledge_access_success(self):
        """测试公共知识库可被其他用户访问"""
        # 管理员创建公共知识库
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        knowledge_data = {
            "name": "公共知识库",
            "description": "公共知识库描述",
            "content": "公共内容"
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/knowledge/create",
            test_name="创建公共知识库（为公共访问测试准备）",
            expected_status=200,
            json_data=knowledge_data,
            headers=admin_headers
        )
        knowledge_uid = create_result["output_params"]["body"]["uid"]
        
        # 用户访问公共知识库
        user_token, user_uid = self._create_user_and_get_token()
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/knowledge/get/{knowledge_uid}",
            test_name="公共知识库访问成功",
            expected_status=200,
            headers=user_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "公共知识库"
        assert data["from_user"] is None

if __name__ == "__main__":
    pytest.main(["-v", __file__])