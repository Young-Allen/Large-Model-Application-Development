import os
import subprocess

# 执行命令
def _exectue_command(self, command: str) -> str:
    """执行终端命令并返回结果"""
    """
    当前目录感知：使用 cwd 参数在正确的目录下执行命令
    错误处理：捕获并合并标准错误，提供完整的诊断信息
    返回码检查：非零返回码会被标记为警告
    容错设计：超时和异常都会被妥善处理，不会导致智能体崩溃
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(self.current_dir),  # 在当前工作目录执行
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env=os.environ.copy()
        )

        # 合并标准输出和标准错误
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"

        # 检查输出大小
        if len(output) > self.max_output_size:
            output = output[:self.max_output_size]
            output += f"\n\n⚠️ 输出被截断（超过 {self.max_output_size} 字节）"

        # 添加返回码信息
        if result.returncode != 0:
            output = f"⚠️ 命令返回码: {result.returncode}\n\n{output}"

        return output if output else "✅ 命令执行成功（无输出）"

    except subprocess.TimeoutExpired:
        return f"❌ 命令执行超时（超过 {self.timeout} 秒）"
    except Exception as e:
        return f"❌ 命令执行失败: {e}"


def _handle_cd(self, parts: List[str]) -> str:
    """处理 cd 命令"""
    if not self.allow_cd:
        return "❌ cd 命令已禁用"

    if len(parts) < 2:
        # cd 无参数，返回当前目录
        return f"当前目录: {self.current_dir}"

    target_dir = parts[1]

    # 处理相对路径
    if target_dir == "..":
        new_dir = self.current_dir.parent
    elif target_dir == ".":
        new_dir = self.current_dir
    elif target_dir == "~":
        new_dir = self.workspace
    else:
        new_dir = (self.current_dir / target_dir).resolve()

    # 检查是否在工作目录内
    try:
        new_dir.relative_to(self.workspace)
    except ValueError:
        return f"❌ 不允许访问工作目录外的路径: {new_dir}"

    # 检查目录是否存在
    if not new_dir.exists():
        return f"❌ 目录不存在: {new_dir}"

    if not new_dir.is_dir():
        return f"❌ 不是目录: {new_dir}"

    # 更新当前目录
    self.current_dir = new_dir
    return f"✅ 切换到目录: {self.current_dir}"
