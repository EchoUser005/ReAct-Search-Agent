# ReAct Search Agent

基于 ReAct（Reasoning and Acting）范式的实时 AI 搜索助手，通过思考-行动-观察的循环模式，智能调用搜索工具回答用户问题。

## 核心亮点

**1. 启发式思考规划，发挥模型原生能力**

相比于 Reasoning 模型的黑盒推理，ReAct 范式通过显式的 Thought-Action-Observation 循环，让模型以更简洁自然的方式进行思考和规划。每一步的推理过程都清晰可见，充分发挥大语言模型的原生能力。

**2. 推理与行动深度结合，动态调整搜索策略**

根据外界工具返回的 Observation 实时调整搜索策略，给予模型充分的试错空间。不同于传统一次性搜索必须精准命中的硬性要求，Agent 可以在多个步骤中迭代优化查询关键词、调整时效性过滤、补充信息维度，最终收敛到高质量答案。

**3. 流式输出降低时延，可控的透明化体验**

相比于链式搜索-摘要模式需要等待全部完成才返回结果，本实现采用流式输出，用户可以实时看到 AI 的思考过程和中间结果。同时，思考过程的可见性、工具调用的展示均可灵活控制，在透明度和简洁性之间取得平衡，用户体验更加快捷友好。

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/EchoUser005/ReAct-Search-Agent.git
cd ReAct-Search-Agent

# 安装依赖
pip install -r requirements.txt
```

### 2. 申请 API Key

#### 通义千问 API Key（必需）

1. 访问 [阿里云通义千问控制台](https://dashscope.console.aliyun.com/)
2. 登录或注册阿里云账号
3. 开通 DashScope 服务
4. 在 API-KEY 管理页面创建新的 API Key
5. 复制生成的 API Key

#### Bocha 搜索 API Key（必需）

1. 访问 [Bocha API 官网](https://bochaapi.com)
2. 注册账号并登录
3. 在控制台获取 API Key

#### Tavily 搜索 API Key（可选）

1. 访问 [Tavily 官网](https://tavily.com)
2. 注册账号并获取 API Key（可选）

### 3. 配置环境变量

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Keys
```

`.env` 文件示例：
```env
# Bocha 搜索 API 配置
BOCHA_BASE_URL=https://api.bochaapi.com/v1/web-search
BOCHA_API_KEY=your_bocha_api_key_here

# Tavily 搜索 API 配置（可选）
TAVILY_API_KEY=your_tavily_api_key_here

# 通义千问 API 配置
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your_qwen_api_key_here
```

### 4. 运行应用

```bash
python app.py
```

访问终端显示的本地 URL（默认为 `http://0.0.0.0:7860`）即可使用。

## 使用指南

### 基本使用

1. 在"搜索"标签页输入问题
2. 点击"搜索"按钮或按 Enter
3. 实时查看 AI 的思考过程和搜索结果
4. 每一步都会显示：
   - **Thought**：AI 的思考分析
   - **Action**：选择的工具
   - **Action Input**：工具参数
   - **Observation**：工具返回结果
   - **Final Answer**：最终答案

### 提示词配置

在"提示词配置"标签页可以自定义：
- **System Prompt**：系统提示词，定义 AI 的行为规则
- **User Prompt**：用户提示词模板，支持变量插值（`{{question}}`, `{{history}}`）

### 示例问题

- "我附近有什么好吃的"（结合位置搜索）
- "最近有什么 AI 领域的重大新闻"（时效性搜索）
- "川普今天说了什么"（实时热点）

## ReAct 范式说明

ReAct 是一种结合推理（Reasoning）和行动（Acting）的 AI 范式：

```
循环流程：
1. Thought: AI 分析当前情况，规划下一步
2. Action: 选择并调用合适的工具
3. Observation: 获取工具返回的结果
4. 重复 1-3，直到获得足够信息
5. Final Answer: 综合所有信息给出最终答案
```

**优势**：
- 可解释性强：每一步思考和行动都清晰可见
- 可控性好：通过调整提示词控制推理流程
- 准确性高：多步推理降低错误率

## 参考文献

本项目基于以下研究工作：

**ReAct: Synergizing Reasoning and Acting in Language Models**
- 论文：[arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- 作者：Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
- GitHub：[ysymyth/ReAct](https://github.com/ysymyth/ReAct)

```bibtex
@article{yao2022react,
  title={ReAct: Synergizing Reasoning and Acting in Language Models},
  author={Yao, Shunyu and Zhao, Jeffrey and Yu, Dian and Du, Nan and Shafran, Izhak and Narasimhan, Karthik and Cao, Yuan},
  journal={arXiv preprint arXiv:2210.03629},
  year={2022}
}
```

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！