#!/usr/bin/env python3
"""
自我进化系统演示
展示 A2A 系统如何自我评估、学习和优化
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from agent_network import (
    get_evolution_engine, init_evolution_system,
    EvolutionType, EvolutionState
)


def print_separator(title=""):
    """打印分隔符"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def demo_evolution_system():
    """演示自我进化系统"""
    print_separator("🤖 A2A 自我进化系统演示")
    print("\n  系统特点：")
    print("  • 自动性能监控和评估")
    print("  • 智能优化建议生成")
    print("  • 自动测试和部署进化")
    print("  • 知识积累和学习")
    
    # 1. 初始化进化引擎
    print_separator("1. 初始化进化引擎")
    engine = init_evolution_system()
    print("  ✅ 进化引擎初始化成功")
    
    # 2. 注册回调（可选）
    def on_evolution_event(event_type: str, data: dict):
        if event_type == "evolution_proposed":
            evo = data.get("evolution")
            print(f"  💡 新进化提案: {evo.description}")
        elif event_type == "evolution_deployed":
            evo = data.get("evolution")
            print(f"  🚀 进化已部署: {evo.description}")
    
    engine.register_callback(on_evolution_event)
    
    # 3. 模拟系统运行 - 记录指标
    print_separator("2. 模拟系统运行 - 记录指标")
    print("\n  正在运行模拟任务...")
    
    for i in range(10):
        # 模拟任务执行时间（逐渐优化）
        execution_time = max(2.0, 10.0 - i * 0.8)
        success_rate = min(1.0, 0.7 + i * 0.03)
        
        # 记录指标
        engine.record_metric("task_execution_time", execution_time, unit="s", target=5.0)
        engine.record_metric("task_success_rate", success_rate, target=0.95)
        engine.record_metric("system_health", 0.8 + i * 0.02)
        
        print(f"  任务 {i+1}: 时间={execution_time:.1f}s, 成功率={success_rate:.2f}")
        time.sleep(0.1)
    
    # 4. 运行进化步骤
    print_separator("3. 运行进化步骤")
    print("\n  🔍 分析系统性能...")
    engine.run_evolution_step()
    
    # 5. 获取进化摘要
    print_separator("4. 查看进化摘要")
    summary = engine.get_evolution_summary()
    
    print(f"\n  📊 进化统计：")
    print(f"  • 总提案: {summary['total_proposed']}")
    print(f"  • 已部署: {summary['total_deployed']}")
    print(f"  • 成功率: {summary['success_rate']:.1%}")
    print(f"  • 当前得分: {summary['current_score']:.2f}")
    print(f"  • 知识库大小: {summary['knowledge_count']}")
    
    if summary['recent_evolutions']:
        print(f"\n  📜 最近进化：")
        for evo in summary['recent_evolutions']:
            state_icon = {
                EvolutionState.PROPOSED: "💡",
                EvolutionState.TESTING: "🧪",
                EvolutionState.APPROVED: "✅",
                EvolutionState.DEPLOYED: "🚀"
            }.get(evo['state'], "❓")
            print(f"  {state_icon} {evo['description']}")
    
    # 6. 查看指标趋势
    print_separator("5. 指标趋势分析")
    time_trend = engine.collector.get_trend("task_execution_time")
    success_trend = engine.collector.get_trend("task_success_rate")
    
    print(f"\n  📈 执行时间趋势: {time_trend:+.2f}")
    if time_trend < -0.1:
        print(f"  ✅ 执行时间正在改善")
    elif time_trend > 0.1:
        print(f"  ⚠️ 执行时间在变慢")
    
    print(f"\n  📈 成功率趋势: {success_trend:+.2f}")
    if success_trend > 0.1:
        print(f"  ✅ 成功率正在提高")
    
    # 7. 导出状态
    print_separator("6. 导出系统状态")
    state_json = engine.export_state()
    print(f"  ✅ 状态已导出 (JSON: {len(state_json)} 字符)")
    
    # 8. 启动自动进化循环
    print_separator("7. 启动自动进化循环")
    print("\n  🚀 启动后台进化监控 (每5秒检查一次)...")
    engine.start_evolution_cycle(interval_seconds=5)
    
    try:
        print("\n  🎯 系统正在进化中... (按 Ctrl+C 停止)")
        for i in range(3):
            time.sleep(1)
            print(f"  {'.' * (i+1)}")
        
    except KeyboardInterrupt:
        print("\n\n  ⏸️  用户中断")
    finally:
        engine.stop_evolution_cycle()
    
    print_separator("演示完成")
    
    print("\n  🎊 自我进化能力总结：")
    print("  • ✅ 性能监控和指标记录")
    print("  • ✅ 智能瓶颈分析")
    print("  • ✅ 自动进化提案")
    print("  • ✅ 测试和部署流程")
    print("  • ✅ 知识积累")
    print("  • ✅ 自动进化循环")
    
    print("\n  🔮 下一步扩展方向：")
    print("  • 与真实 LLM 集成，实现代码自修改")
    print("  • 添加 A/B 测试框架")
    print("  • 实现真实的性能基线对比")
    print("  • 添加进化可视化 UI")


if __name__ == "__main__":
    try:
        demo_evolution_system()
        print("\n  ✅ 自我进化系统演示成功！")
    except Exception as e:
        print(f"\n  ❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
