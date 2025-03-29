import os
import subprocess
import tempfile
import shutil
from typing import Tuple, Dict, Any
import psutil
import hashlib
import re

from app.celery import celery_app


# 安全配置
MAX_EXECUTION_TIME = 30  # 秒
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB
ALLOWED_TYPES = {"python", "shell"}
MAX_SCRIPT_SIZE = 100 * 1024  # 100KB
SAFE_COMMANDS = {"python": ["python3", "-u"], "shell": ["/bin/bash", "--noprofile", "--norc"]}


class ExecutionTimeout(Exception):
    pass


def create_temp_script(script_content: str, script_type: str) -> str:
    """创建临时脚本文件"""
    valid_extensions = {"python": ".py", "shell": ".sh"}

    # 生成安全文件名
    content_hash = hashlib.sha256(script_content.encode()).hexdigest()[:16]
    filename = f"script_{content_hash}{valid_extensions[script_type]}"

    temp_dir = tempfile.mkdtemp(prefix="script_runner_", dir="/tmp")
    script_path = os.path.join(temp_dir, filename)

    # 写入脚本内容
    with open(script_path, "w") as f:
        f.write(script_content)

    # 设置文件权限
    os.chmod(script_path, 0o500)  # 只读且可执行
    os.chmod(temp_dir, 0o700)  # 限制目录权限

    return script_path, temp_dir


def validate_script_content(script_content: str, script_type: str) -> bool:
    """验证脚本内容安全性"""
    # 基础校验
    if len(script_content) > MAX_SCRIPT_SIZE:
        return False

    # 类型特定校验
    if script_type == "shell":
        # 必须包含合法的 shebang
        if not script_content.startswith("#!"):
            return False
        # 禁止危险命令
        dangerous_patterns = [r"\brm\s+-rf", r"\bdd\s+if=", r"\bchmod\s+[0-7]{3,4}", r"\bmkfs", r"\bmount\b"]
        for pattern in dangerous_patterns:
            if re.search(pattern, script_content):
                return False

    elif script_type == "python":
        # 禁止危险模块导入
        dangerous_imports = ["os.system", "subprocess.run", "shutil.rmtree", "ctypes"]
        for imp in dangerous_imports:
            if f"import {imp}" in script_content:
                return False

    return True


def run_process(command: list, timeout: int) -> Tuple[str, str, int]:
    """安全执行进程（保持原实现）"""

    def preexec_function():
        """子进程环境设置"""
        # 限制资源（Linux only）
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
        os.setsid()

    try:
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=preexec_function, text=True
        )

        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # 终止整个进程组
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            raise ExecutionTimeout("Execution timed out")

        return stdout[:MAX_OUTPUT_SIZE], stderr[:MAX_OUTPUT_SIZE], proc.returncode

    except Exception as e:
        return "", str(e)[:MAX_OUTPUT_SIZE], -1


@celery_app.task(bind=True, max_retries=3)
def execute_script_content(self, script_content: str, script_type: str, params: Dict[str, Any] = None):
    """基于内容的脚本执行任务"""
    temp_paths = {}
    try:
        # 参数校验
        params = params or {}
        if script_type not in ALLOWED_TYPES:
            raise ValueError("Invalid script type")

        # 内容安全校验
        if not validate_script_content(script_content, script_type):
            raise ValueError("Script content validation failed")

        # 创建临时脚本文件
        script_path, temp_dir = create_temp_script(script_content, script_type)
        temp_paths = {"script_path": script_path, "temp_dir": temp_dir}

        # 准备执行命令
        command = SAFE_COMMANDS[script_type].copy()
        if script_type == "python":
            command.append(script_path)
        elif script_type == "shell":
            command.append(script_path)

        # 添加用户参数
        if params.get("args"):
            command += params["args"]

        # 执行脚本
        timeout = params.get("timeout", MAX_EXECUTION_TIME)
        stdout, stderr, returncode = run_process(command, timeout)

        # 记录结果
        result = {"stdout": stdout, "stderr": stderr, "returncode": returncode, "success": returncode == 0}

        return result

    except Exception as e:
        self.retry(exc=e, countdown=2**self.request.retries)
    finally:
        # 清理临时文件
        if temp_paths.get("temp_dir"):
            try:
                shutil.rmtree(temp_paths["temp_dir"])
            except Exception as e:
                print(f"Cleanup failed: {str(e)}")
