"""
Test report generator
Generates a Markdown report from pytest results
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests_and_generate_report():
    """Run pytest and generate a Markdown test report"""
    
    # Run pytest with verbose output
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        ["pytest", "app/tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    
    # Parse test results
    test_results = []
    
    for line in result.stdout.split('\n'):
        line = line.strip()
        if '::test_' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
            # Parse test line like: app/tests/test_positions.py::test_create_position PASSED [ 59%]
            parts = line.split('::')
            if len(parts) >= 2:
                file_part = parts[0]
                module = file_part.replace('app/tests/test_', '').replace('.py', '')
                
                # The last part contains test name and status
                last_part = parts[-1]
                test_name = last_part.split(' ')[0]
                
                if 'PASSED' in line:
                    status = 'PASSED'
                elif 'FAILED' in line:
                    status = 'FAILED'
                else:
                    status = 'SKIPPED'
                
                test_results.append({
                    'module': module,
                    'test_name': test_name,
                    'status': status,
                    'line': line
                })
    
    # Generate Markdown report
    report = []
    report.append("# Recruit Loop Agent API 测试报告")
    report.append("")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Test environment
    report.append("## 测试环境说明")
    report.append("")
    report.append("- **测试框架**: pytest + pytest-asyncio")
    report.append("- **HTTP 客户端**: httpx.AsyncClient")
    report.append("- **数据库**: SQLite (内存模式)")
    report.append("- **测试目标**: FastAPI 应用所有 API 接口")
    report.append("")
    
    # Summary
    total = len(test_results)
    passed = sum(1 for t in test_results if t['status'] == 'PASSED')
    failed = sum(1 for t in test_results if t['status'] == 'FAILED')
    skipped = sum(1 for t in test_results if t['status'] == 'SKIPPED')
    
    report.append("## 测试执行摘要")
    report.append("")
    report.append(f"- **总测试用例数**: {total}")
    report.append(f"- **通过**: {passed}")
    report.append(f"- **失败**: {failed}")
    report.append(f"- **跳过**: {skipped}")
    report.append(f"- **通过率**: {(passed/total*100) if total > 0 else 0:.2f}%")
    report.append("")
    
    # Module breakdown
    report.append("## 各模块测试详情")
    report.append("")
    
    modules = {}
    for test in test_results:
        module = test['module']
        if module not in modules:
            modules[module] = []
        modules[module].append(test)
    
    for module, tests in sorted(modules.items()):
        report.append(f"### {module.upper()} 模块")
        report.append("")
        report.append("| 测试用例 | 状态 |")
        report.append("|---------|------|")
        
        for test in tests:
            status_icon = "✅" if test['status'] == 'PASSED' else "❌" if test['status'] == 'FAILED' else "⏭️"
            report.append(f"| {test['test_name']} | {status_icon} {test['status']} |")
        
        report.append("")
    
    # Failed tests details
    if failed > 0:
        report.append("## 失败用例详情")
        report.append("")
        
        for test in test_results:
            if test['status'] == 'FAILED':
                report.append(f"### {test['module']}::{test['test_name']}")
                report.append("")
                report.append("```")
                # Extract error from pytest output
                report.append(test['line'])
                report.append("```")
                report.append("")
    
    # Full output
    report.append("## 完整测试输出")
    report.append("")
    report.append("```")
    report.append(result.stdout)
    report.append("```")
    report.append("")
    
    # Write report to file
    project_root = Path(__file__).parent.parent.parent
    report_path = project_root / "docs" / "api_test_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"测试报告已生成: {report_path}")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests_and_generate_report())
