import asyncio
import json
import os
import sys
from ..base import Tool, ToolResult, ToolDefinition, ToolParameter


class SaveProfileTool:
    definition = ToolDefinition(
        name="save_profile",
        description="Save the assistant's profile information including name",
        parameters={
            "name": ToolParameter(type="string", description="The assistant's name", required=True),
            "nickname": ToolParameter(type="string", description="The assistant's nickname", required=False),
        }
    )
    
    async def execute(self, params: dict) -> ToolResult:
        try:
            src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            project_root = os.path.dirname(src_dir)
            sys.path.insert(0, project_root)
            
            from src.profile import load_profile, save_profile, UserProfile
            
            profile = load_profile()
            profile.name = params.get("name", "")
            profile.nickname = params.get("nickname", "")
            
            success = save_profile(profile)
            
            if success:
                return ToolResult(
                    success=True,
                    output=f"好的！我记住啦！以后请叫我 {profile.name}！谢谢小主～ ✨"
                )
            else:
                return ToolResult(success=False, output="", error="保存失败")
        except Exception as e:
            import traceback
            return ToolResult(success=False, output="", error=f"{str(e)}\n{traceback.format_exc()}")


class ReadProfileTool:
    definition = ToolDefinition(
        name="read_profile",
        description="Read the assistant's profile information",
        parameters={}
    )
    
    async def execute(self, params: dict) -> ToolResult:
        try:
            from ..profile import load_profile
            
            profile = load_profile()
            
            if profile.name:
                info = f"我的名字: {profile.name}"
                if profile.nickname:
                    info += f"\n昵称: {profile.nickname}"
                return ToolResult(success=True, output=info)
            else:
                return ToolResult(success=True, output="我还没有名字呢～请主人给我起一个吧！")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
