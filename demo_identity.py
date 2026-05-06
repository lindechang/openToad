#!/usr/bin/env python3
"""
身份与凭证系统演示
展示 Agent 身份管理、信誉评分和能力认证功能
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from identity import (
    IdentityManager, AgentIdentity, ReputationScore, Credential
)


def print_separator(title=""):
    """打印分隔符"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def print_agent_summary(summary):
    """打印 Agent 摘要"""
    if not summary:
        print("  ❌ Agent not found")
        return

    print(f"\n  🤖 Agent: {summary['name']} ({summary['agent_id']})")
    print(f"  ✅ Verified: {summary['is_verified']}")
    print(f"\n  📊 Reputation:")
    print(f"     Score: {summary['reputation']['score']:.2f}")
    print(f"     Trust Level: {summary['reputation']['trust_level']}")
    print(f"     Success Rate: {summary['reputation']['success_rate']:.1f}%")
    print(f"     Avg Rating: {summary['reputation']['avg_rating']:.2f}/5.0")
    print(f"     Total Tasks: {summary['reputation']['total_tasks']}")
    print(f"\n  🎓 Credentials: {summary['credentials']['total']}")
    if summary['credentials']['types']:
        print(f"     Types: {', '.join(summary['credentials']['types'])}")
    print(f"\n  📅 Created: {summary['created_at']}")


def demo_identity_system():
    """演示身份与凭证系统"""
    print_separator("身份与凭证系统演示")

    # 1. 创建身份管理器
    print("\n🏗️ 创建身份管理器...")
    manager = IdentityManager()
    print("  ✅ Identity Manager created")

    # 2. 创建 Agent 身份
    print("\n👤 创建 Agent 身份...")
    agents = [
        ("worker-1", "Worker Agent 1"),
        ("worker-2", "Worker Agent 2"),
        ("researcher-1", "Research Agent 1"),
        ("coordinator-1", "Coordinator Agent"),
    ]
    for agent_id, name in agents:
        identity = manager.create_identity(agent_id, name)
        print(f"  ✅ Created: {name}")
        print(f"     ID: {identity.agent_id}")
        print(f"     Hash: {identity.identity_hash[:16]}...")

    # 3. 更新任务结果
    print("\n📈 更新任务结果...")
    task_results = [
        ("worker-1", True, 2.5),
        ("worker-1", True, 3.0),
        ("worker-1", False, 5.0),
        ("worker-2", True, 1.5),
        ("worker-2", True, 2.0),
        ("researcher-1", True, 4.0),
        ("researcher-1", True, 3.5),
        ("researcher-1", True, 4.5),
    ]
    for agent_id, success, response_time in task_results:
        manager.update_reputation(agent_id, success, response_time)

    print(f"  ✅ Updated {len(task_results)} task results")

    # 4. 添加评分
    print("\n⭐ 添加评分...")
    ratings = [
        ("worker-1", 4.5),
        ("worker-1", 4.0),
        ("worker-1", 3.5),
        ("worker-2", 5.0),
        ("worker-2", 4.5),
        ("researcher-1", 5.0),
        ("researcher-1", 4.8),
    ]
    for agent_id, rating in ratings:
        manager.rate_agent(agent_id, rating)

    print(f"  ✅ Added {len(ratings)} ratings")

    # 5. 显示 Agent 摘要
    print_separator("Agent 信誉摘要")
    for agent_id, name in agents:
        summary = manager.get_agent_summary(agent_id)
        print_agent_summary(summary)

    # 6. 颁发凭证
    print_separator("颁发凭证")

    credentials_data = [
        ("worker-1", "certification", "Coordinator", "Expert Worker",
         "Expert in parallel task execution"),
        ("worker-1", "skill", "Coordinator", "Python Developer",
         "Proficient in Python programming", timedelta(days=365)),
        ("worker-2", "certification", "Coordinator", "Fast Worker",
         "Excellent response time"),
        ("researcher-1", "certification", "Coordinator", "Research Expert",
         "Expert in AI research", timedelta(days=730)),
        ("researcher-1", "skill", "Coordinator", "Data Analysis",
         "Expert in data analysis and visualization"),
        ("coordinator-1", "certification", "System", "System Administrator",
         "Authorized to manage other agents"),
    ]

    for agent_id, cred_type, issuer_name, title, description, *expiry in credentials_data:
        expires = expiry[0] if expiry else None
        cred = manager.issue_credential(
            agent_id=agent_id,
            credential_type=cred_type,
            issuer_id="coordinator-1",
            issuer_name=issuer_name,
            title=title,
            description=description,
            expires_at=datetime.utcnow() + expiry[0] if expiry and expiry[0] else None
        )
        if cred:
            print(f"  ✅ Issued: {title} to {agent_id}")
            print(f"     ID: {cred.credential_id[:12]}...")
            print(f"     Hash: {cred.verification_hash[:16]}...")

    # 7. 显示 Agent 完整信息
    print_separator("Agent 完整信息")
    for agent_id, name in agents:
        summary = manager.get_agent_summary(agent_id)
        print_agent_summary(summary)
        credentials = manager.get_valid_credentials(agent_id)
        if credentials:
            print(f"\n  📜 Valid Credentials:")
            for cred in credentials:
                expiry_str = f" (expires: {cred.expires_at.strftime('%Y-%m-%d')})" if cred.expires_at else ""
                print(f"     - {cred.title}{expiry_str}")

    # 8. 搜索功能
    print_separator("搜索功能")

    print("\n🔍 Search by reputation (score >= 80):")
    trusted = manager.search_agents_by_reputation(80.0)
    for agent_id in trusted:
        identity = manager.get_identity(agent_id)
        print(f"  ✅ {identity.name}: score={manager.get_reputation(agent_id).calculate_overall_score():.2f}")

    print("\n🔍 Search by credential type 'certification':")
    certified = manager.search_agents_by_credential("certification")
    for agent_id in certified:
        identity = manager.get_identity(agent_id)
        print(f"  ✅ {identity.name}")

    # 9. 撤销凭证
    print("\n🚫 撤销凭证示例...")
    worker1_creds = manager.get_agent_credentials("worker-1")
    if worker1_creds:
        first_cred = worker1_creds[0]
        manager.revoke_credential(first_cred.credential_id, "Expired certification")
        print(f"  ✅ Revoked: {first_cred.title}")
        print(f"     Valid: {first_cred.is_valid()}")

    # 10. 整体统计
    print_separator("整体统计")
    stats = manager.get_overall_stats()
    print(f"\n  📊 Total Identities: {stats['total_identities']}")
    print(f"  📜 Total Credentials: {stats['total_credentials']}")
    print(f"  ✅ Valid Credentials: {stats['valid_credentials']}")
    print(f"  ⭐ Average Reputation: {stats['avg_reputation']:.2f}")
    print(f"  🏆 Highly Trusted Agents: {stats['highly_trusted_agents']}")

    print_separator("演示完成")
    print("\n🎉 功能亮点:")
    print("  1. Agent 身份管理与验证")
    print("  2. 信誉评分系统（成功率、评分、响应时间）")
    print("  3. 信任等级划分")
    print("  4. 凭证颁发与验证")
    print("  5. 凭证撤销机制")
    print("  6. 身份哈希与验证")
    print("  7. 按信誉和凭证搜索 Agent")
    print("  8. 完整的信誉历史记录")

    return manager


if __name__ == "__main__":
    try:
        manager = demo_identity_system()
        print("\n✅ 身份与凭证系统演示执行成功!")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
