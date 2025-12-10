# 前端框架搭建指南

> **技术栈**: React 18 + TypeScript + Vite
> **状态**: 📋 准备中

---

## 📋 项目初始化

### 创建React项目

```bash
# 使用Vite创建React + TypeScript项目
npm create vite@latest frontend -- --template react-ts

cd frontend
npm install
```

### 安装依赖

```bash
# UI组件库
npm install antd @ant-design/icons

# 路由
npm install react-router-dom

# 状态管理
npm install zustand

# HTTP客户端
npm install axios

# 图表库
npm install recharts

# 代码高亮
npm install prismjs
npm install @types/prismjs

# 工具库
npm install dayjs
npm install lodash
npm install @types/lodash
```

---

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/           # 组件
│   │   ├── common/           # 通用组件
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Loading.tsx
│   │   ├── questionnaire/    # 问答组件
│   │   │   ├── QuestionCard.tsx
│   │   │   ├── QuestionStep.tsx
│   │   │   └── ProgressBar.tsx
│   │   ├── recommendation/   # 推荐结果组件
│   │   │   ├── SolutionCard.tsx
│   │   │   ├── ComparisonTable.tsx
│   │   │   └── CodePreview.tsx
│   │   └── prediction/       # 性能预测组件
│   │       ├── PerformanceChart.tsx
│   │       └── MetricsCard.tsx
│   │
│   ├── pages/                # 页面
│   │   ├── Home.tsx          # 首页
│   │   ├── Questionnaire.tsx # 问答页面
│   │   ├── Recommendation.tsx # 推荐结果页面
│   │   └── Comparison.tsx    # 方案对比页面
│   │
│   ├── services/             # API服务
│   │   ├── api.ts            # API客户端
│   │   ├── recommendation.ts # 推荐服务
│   │   ├── prediction.ts    # 预测服务
│   │   └── code.ts          # 代码生成服务
│   │
│   ├── store/                # 状态管理
│   │   ├── useQuestionnaireStore.ts
│   │   ├── useRecommendationStore.ts
│   │   └── useComparisonStore.ts
│   │
│   ├── types/                # 类型定义
│   │   ├── recommendation.ts
│   │   ├── questionnaire.ts
│   │   └── api.ts
│   │
│   ├── utils/                # 工具函数
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   └── constants.ts
│   │
│   ├── App.tsx               # 根组件
│   ├── main.tsx              # 入口文件
│   └── vite-env.d.ts        # Vite类型定义
│
├── public/                   # 静态资源
│   └── favicon.ico
│
├── index.html               # HTML模板
├── package.json
├── tsconfig.json            # TypeScript配置
├── vite.config.ts           # Vite配置
└── .eslintrc.cjs            # ESLint配置
```

---

## 🔧 配置文件

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
})
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 📝 核心组件示例

### API服务 (services/api.ts)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 错误处理
    return Promise.reject(error);
  }
);

export default api;
```

### 推荐服务 (services/recommendation.ts)

```typescript
import api from './api';
import type { RecommendationRequest, RecommendationResponse } from '@/types/recommendation';

export const recommendationService = {
  async getRecommendation(
    request: RecommendationRequest
  ): Promise<RecommendationResponse> {
    return api.post('/recommend', request);
  },

  async getPrediction(
    solution: any,
    infrastructure: any
  ): Promise<any> {
    return api.post('/predict', { solution, infrastructure });
  },

  async compareSolutions(
    solutions: any[]
  ): Promise<any> {
    return api.post('/compare', { solutions });
  },
};
```

### 状态管理 (store/useQuestionnaireStore.ts)

```typescript
import { create } from 'zustand';

interface QuestionnaireState {
  currentStep: number;
  answers: Record<string, any>;
  setAnswer: (key: string, value: any) => void;
  nextStep: () => void;
  prevStep: () => void;
  reset: () => void;
}

export const useQuestionnaireStore = create<QuestionnaireState>((set) => ({
  currentStep: 0,
  answers: {},
  setAnswer: (key, value) =>
    set((state) => ({
      answers: { ...state.answers, [key]: value },
    })),
  nextStep: () =>
    set((state) => ({
      currentStep: state.currentStep + 1,
    })),
  prevStep: () =>
    set((state) => ({
      currentStep: Math.max(0, state.currentStep - 1),
    })),
  reset: () =>
    set({
      currentStep: 0,
      answers: {},
    }),
}));
```

---

## 🎨 UI组件示例

### 问答卡片组件 (components/questionnaire/QuestionCard.tsx)

```typescript
import React from 'react';
import { Card, Radio, Input, InputNumber } from 'antd';
import type { Question } from '@/types/questionnaire';

interface QuestionCardProps {
  question: Question;
  value?: any;
  onChange?: (value: any) => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  value,
  onChange,
}) => {
  const renderInput = () => {
    switch (question.type) {
      case 'radio':
        return (
          <Radio.Group value={value} onChange={(e) => onChange?.(e.target.value)}>
            {question.options?.map((option) => (
              <Radio key={option.value} value={option.value}>
                {option.label}
              </Radio>
            ))}
          </Radio.Group>
        );
      case 'number':
        return (
          <InputNumber
            value={value}
            onChange={onChange}
            style={{ width: '100%' }}
            {...question.props}
          />
        );
      case 'text':
        return (
          <Input
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            {...question.props}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Card title={question.title} style={{ marginBottom: 16 }}>
      {question.description && (
        <p style={{ color: '#666', marginBottom: 16 }}>
          {question.description}
        </p>
      )}
      {renderInput()}
    </Card>
  );
};
```

---

## 🚀 下一步

1. [ ] 创建React项目
2. [ ] 安装依赖
3. [ ] 配置TypeScript和Vite
4. [ ] 创建基础组件
5. [ ] 实现问答流程
6. [ ] 集成API服务
7. [ ] 实现推荐结果展示
8. [ ] 添加性能预测可视化

---

**文档版本**: 0.1.0
**创建日期**: 2025-12-05
