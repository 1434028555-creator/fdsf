# 《韩院长头疗SPA 人事管理系统》MVP架构方案（第一阶段）

## 1. 技术栈建议（适合中小连锁门店）

### 1.1 总体建议
采用 **前后端分离 + 单体可扩展架构**，先保证 MVP 快速上线，再预留连锁多门店扩展能力。

- **前端**：Vue 3 + TypeScript + Element Plus + Pinia + Vue Router
- **后端**：NestJS（Node.js）+ TypeScript
- **数据库**：MySQL 8（主业务库）
- **缓存/队列（可选）**：Redis（用于登录会话、报表任务）
- **文件导出**：SheetJS（Excel）+ csv-writer（CSV）
- **认证授权**：JWT + RBAC（角色-权限模型）
- **部署**：Docker + Nginx（单机可跑，后续可平滑升级）
- **日志审计**：操作日志写入 operation_log 表 + 应用日志输出文件

### 1.2 为什么适合你们
- 成本低：一套代码可覆盖单店和连锁场景。
- 学习曲线平衡：Vue/NestJS 社区成熟，招聘和维护成本可控。
- 规则易改：薪资算法单独封装，后续可按门店差异配置。
- 数据可追溯：关键业务全量审计日志，便于复盘和内控。

### 1.3 分层架构建议
- **API 层**：参数校验、鉴权、统一返回。
- **应用层**：排班、考勤、薪资等业务流程编排。
- **领域层**：薪资计算、提成分摊、迟到规则等核心规则。
- **基础设施层**：数据库、导出、缓存、消息通知。

> 关键约束：薪资算法不可散落在 Controller/页面中，必须集中在 `PayrollEngine` 模块。

---

## 2. 数据库表结构设计（MVP）

> 设计原则：
> 1) 全表预留 `store_id`（多门店隔离）；
> 2) 审计字段统一；
> 3) 关键状态用枚举；
> 4) 薪资与提成拆表，便于追溯。

### 2.1 通用审计字段（建议所有业务表包含）
- `id` bigint PK
- `created_at` datetime
- `updated_at` datetime
- `created_by` bigint nullable
- `updated_by` bigint nullable
- `is_deleted` tinyint(1) default 0（软删除）

### 2.2 store（门店表）
- `id` PK
- `store_code` varchar(32) unique
- `store_name` varchar(64)
- `status` enum('active','inactive')
- `address` varchar(255)

### 2.3 role（角色表）
- `id` PK
- `role_code` varchar(32) unique（owner/manager/hr_finance/employee）
- `role_name` varchar(32)
- `data_scope` enum('self','store','all')

> RBAC 还需配套：`permission`、`role_permission`、`user_role` 三张关系表（MVP可简化为固定权限配置）。

### 2.4 employee（员工档案表）
- `id` PK
- `employee_no` varchar(32) unique
- `name` varchar(32)
- `mobile` varchar(20)
- `id_card` varchar(32) nullable
- `store_id` bigint index
- `role_id` bigint index
- `position` varchar(32)（技师/顾问/前台/店长等）
- `level` varchar(32)（初级/中级/高级）
- `base_salary` decimal(10,2)
- `commission_plan_id` bigint
- `hire_date` date
- `resign_date` date nullable
- `employment_status` enum('active','resigned','probation')
- `login_account_id` bigint（绑定登录用户）

### 2.5 schedule（排班主表）
- `id` PK
- `store_id` bigint index
- `week_start_date` date
- `status` enum('draft','published')
- `published_at` datetime nullable
- `published_by` bigint nullable

### 2.6 schedule_item（排班明细表）
- `id` PK
- `schedule_id` bigint index
- `employee_id` bigint index
- `work_date` date index
- `shift_code` varchar(16)（morning/middle/evening）
- `start_time` time
- `end_time` time
- `is_day_off` tinyint(1)

### 2.7 schedule_adjustment（调班申请表）
- `id` PK
- `store_id` bigint index
- `applicant_employee_id` bigint
- `target_employee_id` bigint nullable（换班对象）
- `from_schedule_item_id` bigint
- `to_schedule_item_id` bigint nullable
- `reason` varchar(255)
- `status` enum('pending','approved','rejected','cancelled')
- `approved_by` bigint nullable
- `approved_at` datetime nullable

### 2.8 attendance（考勤表）
- `id` PK
- `store_id` bigint index
- `employee_id` bigint index
- `work_date` date index
- `shift_code` varchar(16)
- `clock_in_time` datetime nullable
- `clock_out_time` datetime nullable
- `attendance_status` enum('normal','late','absent','leave','patch_pending')
- `late_minutes` int default 0
- `exception_note` varchar(255) nullable

### 2.9 attendance_patch_request（补签申请表）
- `id` PK
- `store_id` bigint index
- `employee_id` bigint index
- `attendance_id` bigint index
- `patch_type` enum('clock_in','clock_out','both')
- `requested_clock_in_time` datetime nullable
- `requested_clock_out_time` datetime nullable
- `reason` varchar(255)
- `status` enum('pending','approved','rejected')
- `approved_by` bigint nullable
- `approved_at` datetime nullable

### 2.10 leave_request（请假申请表）
- `id` PK
- `store_id` bigint index
- `employee_id` bigint index
- `leave_type` enum('personal','sick','time_off')
- `start_time` datetime
- `end_time` datetime
- `duration_hours` decimal(6,2)
- `reason` varchar(255)
- `status` enum('pending','approved','rejected','cancelled')
- `approved_by` bigint nullable
- `approved_at` datetime nullable

### 2.11 payroll（工资主表）
- `id` PK
- `store_id` bigint index
- `employee_id` bigint index
- `pay_month` char(7)（YYYY-MM）
- `base_salary_amount` decimal(10,2)
- `service_commission_amount` decimal(10,2)
- `product_commission_amount` decimal(10,2)
- `deduction_amount` decimal(10,2)
- `total_salary_amount` decimal(10,2)
- `status` enum('draft','confirmed','paid')
- `calculated_at` datetime
- `calculated_by` bigint

### 2.12 commission_record（提成明细表）
- `id` PK
- `store_id` bigint index
- `employee_id` bigint index
- `biz_date` date index
- `commission_type` enum('service','product','refund_reverse')
- `biz_order_no` varchar(64)
- `item_amount` decimal(10,2)
- `rate` decimal(5,4)
- `work_hour_ratio` decimal(5,4) default 1.0000
- `commission_amount` decimal(10,2)
- `is_refund` tinyint(1) default 0
- `related_record_id` bigint nullable（退单冲减关联）

### 2.13 payroll_deduction（扣款明细表）
- `id` PK
- `store_id` bigint index
- `employee_id` bigint index
- `pay_month` char(7)
- `deduction_type` enum('late','absence','other')
- `amount` decimal(10,2)
- `remark` varchar(255)

### 2.14 operation_log（操作日志表）
- `id` PK
- `store_id` bigint index nullable
- `operator_id` bigint index
- `operator_name` varchar(32)
- `module` varchar(32)（employee/schedule/attendance/payroll/report）
- `operation_type` varchar(32)（create/update/delete/approve/export/login）
- `biz_id` bigint nullable
- `request_path` varchar(128)
- `request_method` varchar(10)
- `request_payload` json
- `response_summary` varchar(255)
- `ip` varchar(45)
- `created_at` datetime

---

## 3. API 设计列表（MVP）

### 3.1 认证与权限
- `POST /api/auth/login` 登录
- `POST /api/auth/logout` 退出
- `GET /api/auth/me` 当前用户信息（含角色、门店数据权限）

### 3.2 员工档案
- `GET /api/employees` 员工分页查询（支持门店、状态、岗位筛选）
- `POST /api/employees` 新增员工
- `GET /api/employees/{id}` 员工详情
- `PUT /api/employees/{id}` 更新员工
- `POST /api/employees/{id}/resign` 办理离职

### 3.3 排班
- `GET /api/schedules` 查询周排班
- `POST /api/schedules` 新建/覆盖周排班草稿
- `POST /api/schedules/{id}/publish` 发布排班
- `GET /api/schedules/my` 员工查看我的排班
- `POST /api/schedule-adjustments` 发起调班申请
- `POST /api/schedule-adjustments/{id}/approve` 店长审批通过
- `POST /api/schedule-adjustments/{id}/reject` 店长驳回

### 3.4 考勤
- `POST /api/attendance/clock-in` 上班打卡
- `POST /api/attendance/clock-out` 下班打卡
- `GET /api/attendance/my` 我的考勤记录
- `GET /api/attendance` 门店考勤列表（店长/人事）
- `POST /api/attendance/patch-requests` 提交补签申请
- `POST /api/attendance/patch-requests/{id}/approve` 审批补签
- `POST /api/attendance/patch-requests/{id}/reject` 驳回补签

### 3.5 请假
- `POST /api/leave-requests` 提交请假
- `GET /api/leave-requests/my` 我的请假记录
- `GET /api/leave-requests` 门店请假列表
- `POST /api/leave-requests/{id}/approve` 审批通过
- `POST /api/leave-requests/{id}/reject` 审批驳回

### 3.6 薪资与提成
- `POST /api/payroll/calculate?month=YYYY-MM&storeId=xx` 月度批量核算
- `GET /api/payroll?month=YYYY-MM&storeId=xx` 工资单列表
- `GET /api/payroll/{id}` 工资明细
- `POST /api/payroll/{id}/confirm` 确认工资
- `GET /api/commissions?month=YYYY-MM&employeeId=xx` 提成明细

### 3.7 报表导出
- `GET /api/reports/employees/export` 导出员工花名册
- `GET /api/reports/attendance/export?month=YYYY-MM` 导出考勤月报
- `GET /api/reports/payroll/export?month=YYYY-MM` 导出工资表

### 3.8 日志审计
- `GET /api/operation-logs` 日志检索（按模块、操作人、日期）

---

## 4. 页面结构设计（Web 管理后台 + 员工端）

### 4.1 登录与门户
1. 登录页
2. 首页仪表盘（按角色展示）
   - 待审批（调班/请假/补签）
   - 今日出勤概览
   - 本月工资核算进度

### 4.2 员工档案模块
1. 员工列表页（筛选 + 导出）
2. 员工详情页（基础信息、岗位薪资、操作记录）
3. 新增/编辑员工页

### 4.3 排班模块
1. 周排班日历页（按门店）
2. 调班申请列表页（审批流）
3. 我的排班页（员工端）

### 4.4 考勤模块
1. 打卡页（员工端）
2. 我的考勤页（员工端）
3. 门店考勤台账页（异常标红）
4. 补签申请与审批页

### 4.5 请假模块
1. 请假申请页（员工端）
2. 请假审批页（店长）
3. 请假记录页（人事）

### 4.6 薪资模块
1. 薪资核算页（选择门店+月份，一键计算）
2. 工资列表页
3. 工资详情页（底薪、提成、扣款、合计）
4. 我的工资页（员工端）

### 4.7 报表与审计
1. 报表导出页
2. 操作日志页（可追溯）

---

## 5. 开发任务拆分（MVP，10个以内）

1. **项目初始化与基础框架**
   - 前后端脚手架、环境配置、基础中间件、统一错误码
2. **RBAC 权限体系与登录认证**
   - JWT 登录、角色权限、数据范围（self/store/all）控制
3. **员工档案管理模块**
   - 员工 CRUD、入离职、岗位等级、门店归属
4. **排班与发布模块**
   - 周排班、班次配置、发布机制、员工可见
5. **调班申请审批模块**
   - 员工申请、店长审批、变更落库、日志记录
6. **考勤打卡与异常规则模块**
   - 上下班打卡、迟到10分钟规则、异常状态判定
7. **请假与补签审批模块**
   - 请假申请、补签申请、审批流与状态联动
8. **薪资核算引擎模块**
   - 底薪+服务提成+产品提成-扣款；分单比例；退单冲减
9. **报表导出模块**
   - 花名册、考勤月报、工资表 CSV/Excel 导出
10. **操作日志与审计模块**
   - 关键行为自动审计、日志查询界面

---

## 6. 每个任务的验收标准（Definition of Done）

### 任务1：项目初始化与基础框架
- 完成前后端仓库初始化，支持本地一键启动。
- 完成数据库连接、迁移脚本、基础健康检查接口。
- 统一 API 返回结构与错误码文档可用。

### 任务2：RBAC 权限体系与登录认证
- 四类角色可登录并获得对应菜单与接口权限。
- 员工无法访问他人薪资/考勤明细。
- 店长仅可管理所属门店数据，院长可看全门店。

### 任务3：员工档案管理模块
- 可新增/编辑/查询/离职员工。
- 员工列表可按门店、状态、岗位筛选。
- 关键字段（基础工资、提成方案）变更可追溯。

### 任务4：排班与发布模块
- 支持按周创建草稿排班并发布。
- 发布后员工端可见，不可随意静默覆盖。
- 排班变更留痕并可追踪操作人。

### 任务5：调班申请审批模块
- 员工可提交调班申请并查看审批状态。
- 店长可审批通过/驳回，审批后排班自动更新。
- 全流程写入操作日志。

### 任务6：考勤打卡与异常规则模块
- 员工可完成上/下班打卡。
- 超过班次开始 10 分钟自动标记迟到。
- 当日考勤可正确展示 normal/late/absent 等状态。

### 任务7：请假与补签审批模块
- 支持事假/病假/调休申请。
- 支持漏打卡补签并走审批流。
- 审批通过后自动联动考勤状态更新。

### 任务8：薪资核算引擎模块
- 指定月份可一键核算员工工资。
- 提成计算支持项目提成、产品提成、多人分单比例。
- 退单后对应提成自动冲减并可追溯来源。

### 任务9：报表导出模块
- 可导出员工花名册、考勤月报、工资表。
- 导出的 CSV/Excel 字段完整、金额一致。
- 导出行为写入 operation_log。

### 任务10：操作日志与审计模块
- 员工档案、排班、审批、薪资、导出等关键操作均记录日志。
- 日志支持按时间、模块、操作人检索。
- 审计数据不可被普通角色修改。

---

## 补充建议（进入编码前建议确认）
1. **先固定 2~3 套提成方案模板**（技师/顾问/店长），避免第一版过度参数化。
2. **确认跨店任职规则**：一名员工是否允许多门店排班（若允许，需 employee_store_rel 表）。
3. **确认工资锁定机制**：工资确认后是否允许反结算。
4. **明确数据权限边界**：人事/财务是否跨店查看全部。
5. **确认与收银系统对接节奏**：若暂不对接，佣金流水先支持手工导入。
