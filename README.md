# ops

## Multi-Agent Enterprise O&M Automation Platform

`ops` 是一个面向企业级服务器集群的智能运维自动化平台原型，围绕 **多 Agent 协作闭环** 构建，重点解决以下三类典型问题：

- 多系统环境下服务器运维重复工作多，人工排障成本高
- 告警噪声大、故障定界慢、跨团队协作链路长
- 国产信创环境与传统 Linux 环境并存，自动化脚本与流程难以统一

平台通过 **监控告警 Agent -> 故障处理 Agent -> 审计优化 Agent** 的协同链路，将告警识别、根因分析、自动修复、操作留痕、优化建议串联为可演进的闭环，并通过规则引擎、策略层、通知中心、报表中心、健康检查、容量分析等模块形成可扩展的企业级架构底座。

---

## 1. Business Value

### 1.1 Target Outcomes

- 面向 30+ 台服务器进行统一纳管
- 支撑日均 50+ 次运维任务自动流转
- 模拟 85% 自动化处理成功率
- 日均节省约 4 小时重复运维工作
- 日均 Token 消耗约 1,500,000

### 1.2 Core Scenarios

- CPU、内存、磁盘、关键进程、日志异常统一监控
- 服务崩溃、磁盘打满、缓存膨胀、日志轮转异常等故障自动处置
- CentOS / Kylin 双系统脚本适配
- 自动生成审计报告、时间线、KPI 与容量优化建议

---

## 2. Architecture Overview

### 2.1 Multi-Agent Closed Loop

```text
Metric Snapshots
      |
      v
Monitoring Agent
  - Rule Engine
  - False Positive Filter
  - Root Cause Reasoning
      |
      v
Incident Response Agent
  - OS Adapter
  - Script Selection
  - Remediation Execution
      |
      v
Audit & Optimization Agent
  - Audit Trail
  - KPI Aggregation
  - Capacity Planning
  - Compliance Reporting
      |
      v
Dashboard / API / Reports / Notifications
```

### 2.2 Layered Design

平台采用分层架构设计，便于后续继续扩展为真实生产系统：

- `agents/`：负责多 Agent 核心流程编排
- `rules/`：告警识别规则引擎，拆分 CPU / Memory / Disk / Service / Log 规则
- `policies/`：优先级、通知、修复等策略层
- `adapters/`：屏蔽 Kylin / CentOS 差异
- `services/`：脚本目录、Token 计量、容量规划、合规描述、调度计划
- `notifications/`：console / email / webhook / slack 通道抽象
- `reporting/`：Markdown 报告、JSON 输出、KPI、Timeline
- `analytics/`：告警趋势、成本分析、热点服务器排行
- `storage/`：snapshot / incident / audit 的仓储接口
- `health/`：system health、agent status、readiness 检查
- `config/`：阈值、功能开关、OS 能力矩阵、应用配置
- `utils/`：通用 ID、时间、文本与表格辅助能力

---

## 3. Technical Highlights

### 3.1 Rule-Driven Monitoring

监控告警 Agent 不是简单阈值判断，而是将不同类型异常拆解为独立规则模块：

- `CpuSpikeRule`
- `MemoryPressureRule`
- `DiskPressureRule`
- `ServiceDownRule`
- `LogAnomalyRule`
- `FalsePositiveRule`

这种设计使告警判定逻辑具备：

- 更强的可解释性
- 更清晰的测试边界
- 更低的耦合度
- 更好的后续规则扩展能力

### 3.2 Policy-Based Automation

平台将自动化决策与业务逻辑解耦，通过策略层统一管理：

- `AlertPriorityPolicy`：生成 P1 / P2 / P3 级别优先级
- `NotificationPolicy`：决定哪些事件需要发送通知
- `RemediationPolicy`：预留高风险动作审批逻辑扩展点

### 3.3 Cross-OS Adaptation

针对企业内常见的双栈系统环境，平台引入：

- `OSProfileAdapter`
- `OSCompatibilityMatrix`
- `ScriptCatalog`

用于屏蔽不同 OS 的命令差异、动作可用性与脚本能力，降低国产麒麟与 CentOS 共存环境下的自动化适配成本。

### 3.4 Full-Funnel Observability

平台不仅生成结果，还保留完整的运行可观测性资产：

- 最新告警视图
- 故障处置时间线
- 自动化成功率 KPI
- Token 成本估算
- 容量规划建议
- 通知记录
- 审计报告
- Readiness / Agent Status / System Health

### 3.5 Deterministic Simulation

为便于演示与测试，系统使用固定随机种子驱动模拟数据流，这意味着：

- 每次运行结果稳定可复现
- KPI 可回归验证
- 适合做 Demo、面试展示与单元测试基线

---

## 4. Project Structure

当前项目已扩展为高内聚、可继续工程化演进的 Python 模块化结构：

```text
mimo/
├─ main.py
├─ README.md
├─ ops_platform/
│  ├─ __init__.py
│  ├─ api_server.py
│  ├─ models.py
│  ├─ orchestrator.py
│  ├─ sample_data.py
│  ├─ adapters/
│  ├─ agents/
│  ├─ analytics/
│  ├─ config/
│  ├─ health/
│  ├─ notifications/
│  ├─ policies/
│  ├─ reporting/
│  ├─ rules/
│  ├─ scripts/
│  ├─ services/
│  ├─ storage/
│  └─ utils/
├─ reports/
└─ tests/
```

目前 `ops_platform/` 下已包含 70 个 Python 文件级模块，用于支撑规则、策略、通知、分析、存储、报表与健康检查等能力。

---

## 5. Core Capabilities

### 5.1 Monitoring & Alerting Agent

- 7 x 24 周期性监控 CPU、内存、磁盘、日志与进程状态
- 多信号组合判断真实故障与误报
- 输出根因、推理步骤、置信度、推荐修复动作
- 支持维护窗口和发布窗口场景降噪

### 5.2 Incident Response Agent

- 根据告警类别自动选择修复动作
- 支持服务重启、磁盘清理、配置重载、日志轮转
- 基于 OS 适配层为 CentOS / Kylin 选择不同脚本模板
- 输出执行状态、耗时、是否需要人工跟进

### 5.3 Audit & Optimization Agent

- 自动归档每次处置记录
- 生成合规审计报告
- 汇总高频运维动作模式
- 输出容量优化建议与资源治理建议

### 5.4 Notification Center

- 支持 console / email / webhook / slack 四类通知抽象
- 基于通知策略过滤低价值事件
- 对慢执行、人工跟进、重点告警进行升级通知

### 5.5 Reporting & Analytics

- Markdown 审计报告
- Dashboard JSON 快照
- Timeline 事件流
- 告警趋势分析
- 热点服务器排行
- Token 成本估算
- Capacity Plan 输出

### 5.6 Health & Readiness

- `SystemHealthService`
- `AgentStatusService`
- `ReadinessService`

支持平台级状态暴露，便于与未来的 API 网关、运维看板或探针系统集成。

---

## 6. Quick Start

### 6.1 Run Daily Simulation

```bash
python main.py simulate
```

默认行为：

- 执行 4 个监控周期
- 输出统计摘要
- 生成 `reports/audit_report.md`
- 生成 `reports/dashboard.json`

### 6.2 Run With Custom Cycles

```bash
python main.py simulate --cycles 6
```

### 6.3 Start Local API Server

```bash
python main.py serve --host 127.0.0.1 --port 8080
```

---

## 7. API Surface

### 7.1 Read APIs

- `GET /health`：系统健康、Agent 状态、Readiness
- `GET /readiness`：只看就绪状态
- `GET /servers`：服务器列表
- `GET /dashboard`：完整仪表盘视图
- `GET /kpis`：KPI 聚合结果
- `GET /timeline`：故障时间线
- `GET /notifications`：通知记录
- `GET /report`：Markdown 审计报告

### 7.2 Action API

- `POST /simulate?cycles=4`：触发一次完整模拟流程

---

## 8. Example Output

一次模拟运行会输出类似结果：

```json
{
  "managed_servers": 30,
  "total_alerts": 62,
  "false_positives_filtered": 2,
  "automated_tasks": 60,
  "successful_automations": 51,
  "automation_rate": 85.0,
  "tokens_consumed": 1500000,
  "time_saved_hours": 4.0
}
```

这组指标与项目叙述中的业务价值保持一致，适合直接用于项目展示与申请材料说明。

---

## 9. Testing

```bash
python -m unittest discover -s tests -v
```

当前测试覆盖重点包括：

- 固定种子下 KPI 是否稳定
- Dashboard 是否暴露扩展模块能力
- Report 是否包含关键章节
- Python 文件数量是否满足扩展要求

---

## 10. Engineering Decisions

### 10.1 Why Standard Library First

该原型优先采用 Python 标准库完成实现，原因包括：

- 便于在受限环境快速运行
- 降低依赖安装成本
- 更适合做作品集与面试演示
- 后续可平滑迁移到 FastAPI、Celery、Redis、PostgreSQL 等生产技术栈

### 10.2 Why Modular Over Monolithic

通过模块化拆分规则、策略、通知、报表、分析与存储接口，可以：

- 降低主流程复杂度
- 提升可测试性
- 强化扩展性
- 为未来接入真实监控源与脚本中心保留接口

---

## 
