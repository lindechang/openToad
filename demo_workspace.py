#!/usr/bin/env python3
"""
共享工作区演示
展示多 Agent 协作的笔记、文件共享和活动记录功能
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from agent_network.workspace import (
    WorkspaceManager, Workspace, WorkspaceNote, WorkspaceFile, WorkspaceActivity
)


def print_separator(title=""):
    """打印分隔符"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def print_stats(stats, title="Stats"):
    """打印统计信息"""
    print_separator(title)
    for key, value in stats.items():
        if isinstance(value, int):
            print(f"  {key.replace('_', ' ').title()}: {value}")
        elif isinstance(value, datetime):
            print(f"  {key.replace('_', ' ').title()}: {value.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")


def demo_workspace():
    """演示共享工作区功能"""
    print_separator("共享工作区功能演示")

    # 1. 创建工作区管理器
    print("\n📦 创建工作区管理器...")
    manager = WorkspaceManager()

    # 2. 创建工作区
    print("\n🏗️ 创建共享工作区...")
    task_id = "task-12345"
    workspace = manager.create_workspace(
        task_id=task_id,
        name="AI Research Collaboration",
        description="Collaborative workspace for AI research",
        creator_agent_id="coordinator-1",
        creator_agent_name="Main Coordinator"
    )
    print(f"  ✅ 工作区已创建: {workspace.name}")
    print(f"    ID: {workspace.workspace_id[:12]}...")

    # 3. 添加参与者
    print("\n👥 添加团队成员...")
    agents = [
        ("researcher-1", "Research Agent"),
        ("writer-1", "Writer Agent"),
        ("worker-1", "Worker Agent")
    ]
    for agent_id, agent_name in agents:
        workspace.add_participant(agent_id, agent_name, role="member")
        print(f"  ✅ 加入: {agent_name}")

    # 4. 工作区统计
    print_stats(workspace.get_stats(), "工作区初始状态")

    # 5. 添加笔记
    print("\n📝 添加协作笔记...")
    note1 = workspace.add_note(
        "researcher-1",
        "Found interesting research paper on multi-agent systems. Here are the key findings:\n"
        "- Agents can communicate efficiently using message passing\n"
        "- Role-based collaboration improves task allocation\n"
        "- The system scales well with increasing agents",
        author_name="Research Agent",
        tags=["research", "multi-agent", "paper"]
    )
    print(f"  ✅ 笔记 1: {note1.content[:60]}...")

    note2 = workspace.add_note(
        "writer-1",
        "Draft introduction:\n"
        "This report presents our findings on multi-agent collaboration. "
        "We explore various architectures and their trade-offs.",
        author_name="Writer Agent",
        tags=["draft", "introduction"]
    )
    print(f"  ✅ 笔记 2: {note2.content[:60]}...")

    note3 = workspace.add_note(
        "worker-1",
        "To do list:\n1. Review the research paper\n2. Write code examples\n3. Test the system",
        author_name="Worker Agent",
        tags=["todo", "tasks"]
    )
    print(f"  ✅ 笔记 3: {note3.content[:60]}...")

    # 6. 上传文件
    print("\n📁 上传共享文件...")

    # 文本文件
    paper_content = b"Abstract: This paper discusses multi-agent systems and their applications..."
    file1 = workspace.add_file(
        "research_paper_summary.txt",
        "text/plain",
        paper_content,
        "researcher-1",
        uploaded_by_name="Research Agent",
        tags=["paper", "summary"]
    )
    print(f"  ✅ 文件 1: {file1.name} ({file1.file_size} bytes)")

    # 数据文件
    data_content = b"agent_id,role,status\n1,worker,online\n2,researcher,online"
    file2 = workspace.add_file(
        "agent_data.csv",
        "text/csv",
        data_content,
        "worker-1",
        uploaded_by_name="Worker Agent",
        tags=["data", "csv"]
    )
    print(f"  ✅ 文件 2: {file2.name} ({file2.file_size} bytes)")

    # 7. 更新笔记
    print("\n✏️ 更新笔记...")
    workspace.update_note(
        note1.note_id,
        "Found interesting research paper on multi-agent systems. Here are the key findings:\n"
        "- Agents can communicate efficiently using message passing\n"
        "- Role-based collaboration improves task allocation\n"
        "- The system scales well with increasing agents\n\n"
        "Updated: Added analysis of communication overhead.",
        "researcher-1"
    )
    print(f"  ✅ 笔记已更新: {note1.note_id[:12]}...")

    # 8. 搜索笔记
    print("\n🔍 搜索笔记...")
    search_query = "research"
    found_notes = workspace.search_notes(search_query)
    print(f"  搜索 '{search_query}': 找到 {len(found_notes)} 条笔记")
    for n in found_notes:
        print(f"    - {n.content[:50]}...")

    # 9. 显示最近活动
    print_separator("最近活动记录")
    recent_activities = workspace.get_recent_activities(10)
    for i, activity in enumerate(recent_activities, 1):
        time_str = activity.timestamp.strftime("%H:%M:%S")
        print(f"  {i}. [{time_str}] {activity.agent_name or activity.agent_id}: {activity.description}")

    # 10. 显示工作区统计
    print_stats(workspace.get_stats(), "工作区当前状态")

    # 11. 导出摘要
    print_separator("工作区摘要")
    summary = workspace.export_summary()
    print(f"  工作区: {summary['name']}")
    print(f"  任务: {summary['task_id']}")
    print(f"  参与者: {summary['participants_count']}")
    print(f"  笔记: {summary['notes_count']}")
    print(f"  文件: {summary['files_count']}")

    # 12. 创建第二个工作区
    print("\n🌐 创建第二个工作区...")
    workspace2 = manager.create_workspace(
        task_id="task-67890",
        name="Code Review",
        description="Workspace for code review and testing",
        creator_agent_id="worker-1",
        creator_agent_name="Worker Agent"
    )
    workspace2.add_participant("researcher-1", "Research Agent")
    workspace2.add_note(
        "worker-1",
        "Review checklist:\n- Code style\n- Performance\n- Documentation",
        author_name="Worker Agent",
        tags=["review", "checklist"]
    )
    print(f"  ✅ 工作区已创建: {workspace2.name}")

    # 13. 整体统计
    print_stats(manager.get_overall_stats(), "整体统计")

    print_separator("演示完成")
    print("\n🎉 功能亮点:")
    print("  1. 多 Agent 参与的共享工作区")
    print("  2. 协作笔记（添加、更新、搜索）")
    print("  3. 文件共享（上传、类型管理）")
    print("  4. 完整的活动时间线")
    print("  5. 工作区统计和摘要导出")
    print("  6. 支持多个并行工作区")

    return manager


if __name__ == "__main__":
    try:
        manager = demo_workspace()
        print("\n✅ 工作区演示执行成功!")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
