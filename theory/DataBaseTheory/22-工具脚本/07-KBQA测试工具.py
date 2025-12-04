#!/usr/bin/env python3
"""
KBQA系统测试工具
用途: 测试Text-to-Cypher准确率、端到端性能
创建: 2025-12-04
"""

import requests
import json
import time
from typing import List, Dict

class KBQATester:
    """KBQA测试工具"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> List[Dict]:
        """加载测试用例"""
        return [
            {
                "question": "有多少员工?",
                "expected_type": "number",
                "expected_range": (0, 10000)
            },
            {
                "question": "张三在哪个部门?",
                "expected_type": "text",
                "expected_contains": ["部门", "中心"]
            },
            {
                "question": "研发中心的Python工程师",
                "expected_type": "list",
                "expected_min_count": 1
            },
            {
                "question": "每个部门的员工数",
                "expected_type": "aggregate",
                "expected_has_fields": ["部门", "数量"]
            }
        ]
    
    def test_accuracy(self) -> Dict:
        """测试准确率"""
        correct = 0
        total = len(self.test_cases)
        results = []
        
        for case in self.test_cases:
            try:
                response = requests.post(
                    f"{self.api_url}/api/ask",
                    json={"question": case["question"]},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_correct = self._validate_answer(data, case)
                    
                    if is_correct:
                        correct += 1
                    
                    results.append({
                        'question': case['question'],
                        'correct': is_correct,
                        'answer': data.get('answer'),
                        'latency_ms': data.get('latency_ms')
                    })
            
            except Exception as e:
                print(f"❌ 测试失败: {case['question']}, 错误: {e}")
        
        return {
            'accuracy': correct / total,
            'correct': correct,
            'total': total,
            'results': results
        }
    
    def test_performance(self, num_requests: int = 100) -> Dict:
        """测试性能"""
        latencies = []
        
        for _ in range(num_requests):
            question = "有多少员工?"
            
            start = time.time()
            response = requests.post(
                f"{self.api_url}/api/ask",
                json={"question": question},
                timeout=10
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                latencies.append(latency)
        
        latencies.sort()
        
        return {
            'avg_latency_ms': sum(latencies) / len(latencies),
            'p50_latency_ms': latencies[len(latencies)//2],
            'p95_latency_ms': latencies[int(len(latencies)*0.95)],
            'p99_latency_ms': latencies[int(len(latencies)*0.99)],
            'qps': 1000 / (sum(latencies) / len(latencies))
        }
    
    def _validate_answer(self, data: Dict, case: Dict) -> bool:
        """验证答案正确性"""
        answer = data.get('answer', '')
        
        if case['expected_type'] == 'number':
            # 提取数字
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                num = int(numbers[0])
                min_val, max_val = case['expected_range']
                return min_val <= num <= max_val
        
        elif case['expected_type'] == 'text':
            # 检查包含关键词
            return any(kw in answer for kw in case['expected_contains'])
        
        elif case['expected_type'] == 'list':
            # 检查返回了列表
            return len(data.get('query_results', [])) >= case['expected_min_count']
        
        return False

if __name__ == '__main__':
    tester = KBQATester('http://localhost:8000')
    
    # 测试准确率
    print("📊 测试准确率...")
    accuracy_result = tester.test_accuracy()
    print(f"✅ 准确率: {accuracy_result['accuracy']:.2%}")
    print(f"   正确: {accuracy_result['correct']}/{accuracy_result['total']}")
    
    # 测试性能
    print("\n⚡ 测试性能...")
    perf_result = tester.test_performance(num_requests=100)
    print(f"   平均延迟: {perf_result['avg_latency_ms']:.1f}ms")
    print(f"   P95延迟: {perf_result['p95_latency_ms']:.1f}ms")
    print(f"   QPS: {perf_result['qps']:.0f}")
