# 《韩院长头疗SPA 人事管理系统》MVP 第一阶段系统架构方案

## 0. 设计目标与边界
- **业务目标**：替代 Excel + 人工统计，实现员工档案、排班、考勤、薪资提成、报表导出的标准化与自动化。
- **系统形态**：支持单店快速上线，天然支持多门店扩展（tenant/store 维度隔离）。
- **设计原则**：
  1. 规则简单且可配置；
  2. 数据可追溯（操作日志 + 状态流转）；
  3. 薪资算法独立封装，后续易于调整；
  4. 权限严格 RBAC 控制。

---

## 1. 技术栈建议（适合中小连锁门店）

### 1.1 推荐方案（务实、易招人、上线快）
- **前端**：Vue 3 + TypeScript + Vite + Element Plus
  - 优势：中后台开发效率高、组件成熟、上手快。
- **后端**：NestJS（Node.js + TypeScript）
  - 优势：模块化清晰，适合权限、审批流、日志等业务；TypeScript 全栈统一。
- **数据库**：PostgreSQL
  - 优势：事务能力强，适合薪资核算等强一致场景；JSON 字段可兼容灵活规则。
- **缓存/队列（可选）**：Redis
  - 用于登录态、报表异步导出、排班发布通知等。
- **ORM**：Prisma
  - 优势：数据模型可视化、迁移管理稳定、类型安全。
- **鉴权与权限**：JWT + RBAC（role / permission / role_permission）
- **文件导出**：CSV（MVP 必选）+ Excel（二期可选）
- **部署**：Docker + Nginx，单机可跑；后续可平滑迁移云服务器。

### 1.2 为什么适合当前阶段
- 开发与维护成本低，适合 1~3 人技术团队。
- 技术成熟，招聘与交接风险小。
- 满足“快速迭代 + 可扩张”的业务节奏。

---

## 2. 数据库表结构设计（MVP）

> 说明：以下均建议含 `id, created_at, updated_at, created_by, updated_by` 通用字段；所有业务核心表建议带 `store_id` 实现门店维度隔离。

### 2.1 组织与权限

#### `store`（门店表）
- `id` PK
- `store_code` 门店编码（唯一）
- `store_name` 门店名称
- `status`（active/inactive）
- `address` 地址

#### `role`（角色表）
- `id` PK
- `role_key`（owner / manager / hr_finance / employee）
- `role_name` 角色名称
- `scope_level`（system/store/self）

#### `permission`（权限点表，建议补充）
- `id` PK
- `perm_key`（如 `employee.read.all`）
- `perm_name`
- `module`

#### `role_permission`（角色权限关联）
- `id` PK
- `role_id` FK
- `permission_id` FK

#### `user_account`（登录账号表，建议补充）
- `id` PK
- `username`（唯一）
- `password_hash`
- `employee_id` FK
- `role_id` FK
- `store_id` FK
- `status`

### 2.2 人员与档案

#### `employee`（员工档案）
- `id` PK
- `employee_no` 工号（唯一）
- `name`
- `mobile`
- `id_no`（可脱敏）
- `gender`
- `hire_date`
- `leave_date`
- `employment_status`（active/left）
- `position`（技师/顾问/前台/店长）
- `level`（初级/中级/高级）
- `base_salary`（底薪）
- `commission_plan_id` FK
- `store_id` FK

#### `commission_plan`（提成方案，建议补充）
- `id` PK
- `plan_name`
- `position`
- `service_rate` 服务提成比例
- `product_rate` 产品提成比例
- `is_active`

### 2.3 排班

#### `schedule`（排班主表）
- `id` PK
- `store_id` FK
- `week_start_date`
- `week_end_date`
- `status`（draft/published）
- `published_at`
- `published_by`

#### `schedule_item`（排班明细，建议补充）
- `id` PK
- `schedule_id` FK
- `employee_id` FK
- `work_date`
- `shift_code`（morning/mid/evening）
- `start_time`
- `end_time`

#### `shift_change_request`（调班申请，建议补充）
- `id` PK
- `store_id` FK
- `applicant_employee_id`
- `target_employee_id`
- `from_schedule_item_id`
- `to_schedule_item_id`
- `reason`
- `status`（pending/approved/rejected/cancelled）
- `approved_by`
- `approved_at`

### 2.4 考勤

#### `attendance`（考勤表）
- `id` PK
- `store_id` FK
- `employee_id` FK
- `work_date`
- `shift_code`
- `scheduled_start_time`
- `scheduled_end_time`
- `check_in_time`
- `check_out_time`
- `late_minutes`
- `is_late`（>10 分钟自动判定）
- `status`（normal/late/absent/leave）

#### `leave_request`（请假申请）
- `id` PK
- `store_id` FK
- `employee_id` FK
- `leave_type`（personal/sick/comp_off）
- `start_time`
- `end_time`
- `duration_hours`
- `reason`
- `status`（pending/approved/rejected/cancelled）
- `approved_by`
- `approved_at`

#### `attendance_patch_request`（补签申请，建议补充）
- `id` PK
- `store_id` FK
- `employee_id` FK
- `attendance_id` FK
- `patch_type`（check_in/check_out/both）
- `patch_check_in_time`
- `patch_check_out_time`
- `reason`
- `status`（pending/approved/rejected）
- `approved_by`

### 2.5 薪资与提成

#### `commission_record`（提成记录）
- `id` PK
- `store_id` FK
- `employee_id` FK
- `source_type`（service/product/refund）
- `source_order_no`
- `amount_base`（项目或销售金额）
- `rate`
- `workload_ratio`（多人分单工时占比）
- `commission_amount`
- `biz_date`
- `is_reversed`（冲减标记）
- `reversed_from_id`（原记录）

#### `payroll`（工资单）
- `id` PK
- `store_id` FK
- `employee_id` FK
- `pay_month`（YYYY-MM）
- `base_salary`
- `service_commission`
- `product_commission`
- `deduction_amount`
- `should_pay_amount`（应发）
- `actual_pay_amount`（实发，可后续扩展）
- `status`（draft/confirmed/paid）
- `calculated_at`
- `calculated_by`

#### `payroll_adjustment`（工资调整，建议补充）
- `id` PK
- `payroll_id` FK
- `adjust_type`（bonus/deduction）
- `amount`
- `reason`

### 2.6 审计与日志

#### `operation_log`（操作日志）
- `id` PK
- `store_id` FK
- `operator_id`
- `module`（employee/schedule/attendance/payroll/report）
- `action`（create/update/delete/approve/export/login）
- `biz_id`（业务主键）
- `before_data` JSON
- `after_data` JSON
- `ip`
- `user_agent`
- `created_at`

---

## 3. API 设计列表（MVP）

> 风格：RESTful + JWT；路径建议加 `/api/v1` 前缀。

### 3.1 认证与账号
- `POST /auth/login` 登录
- `POST /auth/logout` 退出
- `GET /auth/me` 当前用户信息（角色、权限、所属门店）

### 3.2 员工档案
- `GET /employees` 员工列表（支持门店、状态、岗位筛选）
- `POST /employees` 新增员工
- `GET /employees/{id}` 员工详情
- `PUT /employees/{id}` 更新员工
- `PATCH /employees/{id}/status` 入离职状态变更

### 3.3 排班
- `GET /schedules` 周排班列表
- `POST /schedules` 创建/保存草稿排班
- `GET /schedules/{id}` 排班详情
- `PUT /schedules/{id}` 修改排班
- `POST /schedules/{id}/publish` 发布排班
- `POST /shift-change-requests` 发起调班申请
- `GET /shift-change-requests` 调班申请列表
- `POST /shift-change-requests/{id}/approve` 审批通过
- `POST /shift-change-requests/{id}/reject` 审批拒绝

### 3.4 考勤
- `POST /attendance/check-in` 上班打卡
- `POST /attendance/check-out` 下班打卡
- `GET /attendance/me` 我的考勤记录
- `GET /attendance` 门店考勤记录（店长/人事可见）
- `POST /leave-requests` 发起请假
- `GET /leave-requests` 请假列表
- `POST /leave-requests/{id}/approve` 请假审批通过
- `POST /leave-requests/{id}/reject` 请假审批拒绝
- `POST /attendance-patch-requests` 发起补签申请
- `POST /attendance-patch-requests/{id}/approve` 补签审批通过
- `POST /attendance-patch-requests/{id}/reject` 补签审批拒绝

### 3.5 薪资核算
- `POST /payroll/calculate` 按月批量核算工资
- `GET /payroll` 工资单列表（支持门店、月份筛选）
- `GET /payroll/{id}` 工资单详情
- `POST /payroll/{id}/confirm` 确认工资单
- `GET /commissions` 提成记录查询

### 3.6 报表导出
- `GET /reports/employees/export` 员工花名册导出（CSV）
- `GET /reports/attendance/export` 考勤月报导出（CSV）
- `GET /reports/payroll/export` 工资表导出（CSV）

### 3.7 日志审计
- `GET /operation-logs` 日志查询（按模块、时间、操作者过滤）

---

## 4. 页面结构设计（Web 管理端 + 员工端）

### 4.1 登录与基础框架
1. 登录页
2. 首页仪表盘
   - 今日出勤、请假待审、当月工资核算进度、异常提醒

### 4.2 管理端（院长/店长/人事财务）
1. **员工管理**
   - 员工列表页
   - 员工详情/编辑页
   - 入离职记录
2. **排班管理**
   - 周视图排班页（拖拽/批量排班可二期）
   - 调班审批页
   - 排班发布记录
3. **考勤管理**
   - 考勤明细页（迟到、缺卡、异常）
   - 请假审批页
   - 补签审批页
4. **薪资管理**
   - 薪资规则设置页（底薪、提成方案）
   - 月度核算页
   - 工资单详情页
5. **报表中心**
   - 花名册导出
   - 考勤月报导出
   - 工资报表导出
6. **系统管理**
   - 角色权限（RBAC）
   - 操作日志

### 4.3 员工端（仅本人数据）
1. 我的排班
2. 我的考勤（打卡、记录查看）
3. 请假申请
4. 补签申请
5. 我的工资单

---

## 5. 开发任务拆分（MVP，10 个以内）

1. **项目基础搭建与多门店基础能力**
   - 内容：前后端脚手架、数据库连接、基础配置、`store_id` 贯穿。
2. **RBAC 权限系统**
   - 内容：角色、权限点、接口鉴权中间件、菜单级权限。
3. **员工档案模块**
   - 内容：员工增删改查、入离职、岗位等级、提成方案绑定。
4. **排班与发布模块**
   - 内容：周排班、班次配置、发布流程、变更日志。
5. **调班申请与审批模块**
   - 内容：员工发起调班、店长审批、审批后自动更新排班。
6. **考勤打卡与迟到规则模块**
   - 内容：上下班打卡、>10 分钟迟到判定、异常状态标记。
7. **请假/补签审批模块**
   - 内容：请假与补签流程、店长审批、数据回写考勤。
8. **薪资核算引擎模块（独立领域服务）**
   - 内容：底薪 + 服务提成 + 产品提成 - 扣款；退单冲减；多人分单分摊。
9. **报表导出模块**
   - 内容：花名册、考勤月报、工资报表 CSV 导出。
10. **操作日志与审计模块**
   - 内容：关键操作全链路日志记录、查询与追溯。

---

## 6. 每个任务的验收标准

1. **项目基础搭建与多门店基础能力**
   - 验收：系统可登录；所有核心业务表有 `store_id`；接口按门店自动过滤数据。

2. **RBAC 权限系统**
   - 验收：
     - 院长可查看全部门店数据；
     - 店长仅管理所属门店；
     - 员工仅可访问本人数据；
     - 未授权接口返回 403。

3. **员工档案模块**
   - 验收：支持新增、编辑、离职；员工列表可按状态/门店筛选；员工可绑定提成方案。

4. **排班与发布模块**
   - 验收：可创建周排班草稿并发布；发布后员工端可见；每次修改均写入操作日志。

5. **调班申请与审批模块**
   - 验收：员工可发起调班；店长可审批；审批通过后排班自动变更且留痕。

6. **考勤打卡与迟到规则模块**
   - 验收：支持上下班打卡；系统自动计算迟到分钟；超过 10 分钟标记迟到。

7. **请假/补签审批模块**
   - 验收：请假/补签流程闭环；审批结果回写考勤；审批动作有日志。

8. **薪资核算引擎模块（独立领域服务）**
   - 验收：
     - 公式正确：`当月工资 = 底薪 + 服务提成 + 产品提成 - 扣款`；
     - 支持多人分单按工时比例分摊；
     - 退单可冲减历史提成；
     - 算法逻辑与接口层分离（可单元测试）。

9. **报表导出模块**
   - 验收：可按月份/门店导出 3 类报表；导出字段与页面一致；CSV 可直接打开。

10. **操作日志与审计模块**
    - 验收：员工、排班、考勤、薪资、导出等关键动作均有日志；支持按时间/模块/人员检索。

---

## 7. 补充建议（进入编码前建议确认）
- 是否需要微信小程序员工端（若需要，API 命名与鉴权需提前兼容）。
- 是否需要与门店收银系统打通（影响 `commission_record` 数据来源）。
- 薪资发放口径（应发/实发、个税/社保是否纳入二期）。
- 连锁门店总部是否需要“跨店汇总看板”。

