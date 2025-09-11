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
test_db_path = os.path.join(os.path.dirname(__file__), "test_copywriting_types.db")
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

class TestCopywritingTypes:
    """文案类型模块测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 清理测试数据
        db = TestingSessionLocal()
        try:
            db.execute(text("DELETE FROM copywriting_types"))
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
            test_name="注册管理员（辅助方法）",
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
            test_name="注册用户（辅助方法）",
            expected_status=200,
            json_data=user_data
        )
        user_uid = user_result["output_params"]["body"]["uid"]
        token = create_access_token(data={"sub": user_uid})
        return token, user_uid
    
    def test_create_copywriting_type_success(self):
        """测试创建文案类型成功"""
        token, admin_uid = self._create_admin_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        copywriting_type_data = {
            "name": "营销文案",
            "prompt": "请写一篇营销文案",
            "template": "标题：{title}\n内容：{content}",
            "description": "用于营销推广的文案类型",
            "updated_admin_uid": admin_uid
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/copywriting_types/create",
            test_name="创建文案类型成功",
            expected_status=200,
            json_data=copywriting_type_data,
            headers=headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "营销文案"
        assert data["prompt"] == "请写一篇营销文案"
        assert data["template"] == "标题：{title}\n内容：{content}"
        assert data["description"] == "用于营销推广的文案类型"
        assert "uid" in data
        assert "created_time" in data
    
    def test_get_copywriting_type_success(self):
        """测试获取文案类型成功"""
        # 先创建管理员和文案类型
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        copywriting_type_data = {
            "name": "测试文案",
            "prompt": "测试提示词",
            "template": "测试模板",
            "description": "测试描述",
            "updated_admin_uid": admin_uid
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/copywriting_types/create",
            test_name="创建文案类型（获取测试前置）",
            expected_status=200,
            json_data=copywriting_type_data,
            headers=admin_headers
        )
        copywriting_type_uid = create_result["output_params"]["body"]["uid"]
        
        # 用户获取文案类型
        user_token, _ = self._create_user_and_get_token()
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        result = make_request_with_format(
            client=client,
            method="GET",
            route=f"/api/copywriting_types/get/{copywriting_type_uid}",
            test_name="获取文案类型成功",
            expected_status=200,
            headers=user_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "测试文案"
        assert data["prompt"] == "测试提示词"
        assert data["template"] == "测试模板"
        assert data["description"] == "测试描述"
        assert data["uid"] == copywriting_type_uid
    
    def test_get_copywriting_types_list_success(self):
        """测试获取文案类型列表成功"""
        # 先创建管理员和几个文案类型
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        for i in range(3):
            copywriting_type_data = {
                "name": f"文案类型{i}",
                "prompt": f"提示词{i}",
                "template": f"模板{i}",
                "description": f"描述{i}",
                "updated_admin_uid": admin_uid
            }
            make_request_with_format(
                client=client,
                method="POST",
                route="/api/copywriting_types/create",
                test_name=f"创建文案类型{i}（列表测试前置）",
                expected_status=200,
                json_data=copywriting_type_data,
                headers=admin_headers
            )
        
        # 用户获取文案类型列表
        user_token, _ = self._create_user_and_get_token()
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        result = make_request_with_format(
            client=client,
            method="GET",
            route="/api/copywriting_types/list?page=1&page_size=10",
            test_name="获取文案类型列表成功",
            expected_status=200,
            headers=user_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 3
        assert data["total"] >= 3
    
    def test_search_copywriting_types_success(self):
        """测试搜索文案类型成功"""
        # 先创建管理员和文案类型
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        copywriting_type_data = {
            "name": "搜索测试文案",
            "prompt": "搜索测试提示词",
            "template": "搜索测试模板",
            "description": "搜索测试描述",
            "updated_admin_uid": admin_uid
        }
        make_request_with_format(
            client=client,
            method="POST",
            route="/api/copywriting_types/create",
            test_name="创建文案类型（搜索测试前置）",
            expected_status=200,
            json_data=copywriting_type_data,
            headers=admin_headers
        )
        
        # 搜索文案类型
        search_params = {
            "name": "搜索测试"
        }
        result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/copywriting_types/search?page=1&page_size=10",
            test_name="搜索文案类型成功",
            expected_status=200,
            json_data=search_params,
            headers=admin_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 1
        assert "搜索测试文案" in [item["name"] for item in data["items"]]
    
    def test_update_copywriting_type_success(self):
        """测试更新文案类型成功"""
        # 先创建管理员和文案类型
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        copywriting_type_data = {
            "name": "原始文案",
            "prompt": "原始提示词",
            "template": "原始模板",
            "description": "原始描述",
            "updated_admin_uid": admin_uid
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/copywriting_types/create",
            test_name="创建文案类型（更新测试前置）",
            expected_status=200,
            json_data=copywriting_type_data,
            headers=admin_headers
        )
        copywriting_type_uid = create_result["output_params"]["body"]["uid"]
        
        # 更新文案类型
        update_data = {
            "name": "更新后文案",
            "prompt": "更新后提示词",
            "template": "更新后模板",
            "description": "更新后描述"
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/copywriting_types/update/{copywriting_type_uid}",
            test_name="更新文案类型成功",
            expected_status=200,
            json_data=update_data,
            headers=admin_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert data["name"] == "更新后文案"
        assert data["prompt"] == "更新后提示词"
        assert data["template"] == "更新后模板"
        assert data["description"] == "更新后描述"
    
    def test_delete_copywriting_type_success(self):
        """测试删除文案类型成功"""
        # 先创建管理员和文案类型
        admin_token, admin_uid = self._create_admin_and_get_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        copywriting_type_data = {
            "name": "待删除文案",
            "prompt": "待删除提示词",
            "template": "待删除模板",
            "description": "待删除描述",
            "updated_admin_uid": admin_uid
        }
        
        create_result = make_request_with_format(
            client=client,
            method="POST",
            route="/api/copywriting_types/create",
            test_name="创建文案类型（删除测试前置）",
            expected_status=200,
            json_data=copywriting_type_data,
            headers=admin_headers
        )
        copywriting_type_uid = create_result["output_params"]["body"]["uid"]
        
        # 删除文案类型
        delete_data = {
            "is_del": 1
        }
        
        result = make_request_with_format(
            client=client,
            method="POST",
            route=f"/api/copywriting_types/delete/{copywriting_type_uid}",
            test_name="删除文案类型成功",
            expected_status=200,
            json_data=delete_data,
            headers=admin_headers
        )
        
        assert result["is_passed"]
        data = result["output_params"]["body"]
        assert "message" in data or "success" in str(data).lower()

if __name__ == "__main__":
    pytest.main(["-v", __file__])