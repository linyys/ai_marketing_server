import os
import shutil
from typing import Union

from fastapi import Response, UploadFile

def write_to_file(file_path: str, content: str, mode: str = 'w') -> bool:
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"写入失败: {e}")
        return False

def file_to_str(uploaded_file) -> Union[str, None]:
    try:
        file_bytes = uploaded_file.read()
        return file_bytes.decode('utf-8')
    except AttributeError:
        print("无效文件")
    except UnicodeDecodeError as e:
        print(f"解码失败: {e}")
    except Exception as e:
        print(f"转换失败: {e}")
    return None

def directory_exists(dir_path: str) -> bool:
    return os.path.isdir(dir_path)

# 注意路径，谨慎使用
def clear_directory(dir_path: str) -> bool:
    try:
        if not directory_exists(dir_path):
            return True
            
        for entry in os.listdir(dir_path):
            entry_path = os.path.join(dir_path, entry)
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.unlink(entry_path)
            else:
                shutil.rmtree(entry_path)
        return True
    except Exception as e:
        print(f"清空目录失败: {e}")
        return False
    
async def save_uploaded_file(upload_file: UploadFile, save_directory: str, file_name: str):
    try:
        os.makedirs(save_directory, exist_ok=True)
        filename = os.path.basename(upload_file.filename)
        if not filename:
            raise ValueError("无效的文件名")
        
        file_path = os.path.join(save_directory, file_name)
        
        contents = await upload_file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        return file_path
    except Exception as e:
        if 'file_path' in locals():
            try:
                os.remove(file_path)
            except:
                pass
        raise

def create_directory(abs_path: str) -> str:
    normalized = os.path.normpath(abs_path)
    os.makedirs(normalized, exist_ok=True)
    return normalized

async def download_file(file_path: str, response: Response):
    with open(file_path, "rb") as file:
        contents = file.read()
        response.headers["Content-Disposition"] = f"attachment; filename={file_path}"
        response.body = contents
        return response