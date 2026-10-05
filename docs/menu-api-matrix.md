# 菜单 × 接口覆盖矩阵（迁移进度跟踪）

配合 [全部菜单接通开发规划](menu-integration-plan.md) 使用。每迁完一个菜单，就把“状态”改为“已接通”，并填上对应的 E2E 用例文件。

状态取值：未开始 / 进行中 / 已接通。缺口规模：无 / 小改 / 新增。

| 菜单 | Hash 路由 | 前端文件 | 查看所需权限 | 主要后端接口 | 后端缺口 | 阶段 | 状态 | E2E |
|---|---|---|---|---|---|---|---|---|
| 工作台 | `#dashboard` | `pages/Overview.jsx` | 已登录 | `/api/analytics/overview`、`/api/alerts`、`/api/alerts/stores/overview` | 小改：`/api/activity`、测评计数 | P7 | 未开始 | |
| 预警中心 | `#alerts` | `pages/Overview.jsx` | `alert.view` | `/api/alerts`、`/exceptions`、`/stores/overview`、`dismiss`、`handle` | 无 | P7 | 未开始 | |
| 员工档案 | `#employees` | `pages/People.jsx` | `employee.view` | `/api/employees/*`、`/api/attachments/*`、`health-cert` | 小改：工号、手机号检索列、身份证查重 | P3 | 未开始 | |
| 新人培训中心 | `#training` | `pages/People.jsx` | `training.own` | `/api/training/*`（23 个） | 新增：3 个正式资料状态、下店门禁、到岗转试用 | P5 | 未开始 | |
| 转正提醒 | `#probation` | `pages/People.jsx` | `probation.view` | `/api/employees/probation/list`、`eval`、`decide` | 无（前端补“延长”和“不继续”） | P3 | 未开始 | |
| 招人需求 | `#demands` | `pages/Recruitment.jsx` | `recruit.need_view` | `/api/recruit/needs*` | 无 | P4 | 未开始 | |
| 招聘工作台 | `#recruitment` | `pages/Recruitment.jsx` | `talent.view` | `/api/recruit/resume-inbox/*`、`/api/talents/*`、`/api/analytics/recruit` | 小改：按来源统计、批量加入人才库 | P4 | 未开始 | |
| 候选人跟进 | `#candidates` | `pages/Recruitment.jsx` | `recruit.candidate_view` | `/api/recruit/candidates*` | 新增：负责人、下次联系、跟进记录、编辑、测评复核 | P4 | 未开始 | |
| 我的上报 | `#reports` | `pages/Insights.jsx` | `hr.work_log` | `/api/hr/work-logs*`、`upload-photo`、`my-summary` | 小改：撤回 | P6 | 未开始 | |
| 我的月度 | `#monthly` | `pages/Insights.jsx` | `hr.score_view` | `/api/hr/monthly-progress`、`targets` | 无 | P6 | 未开始 | |
| 入职素质测评 | `#assessment` | `pages/Insights.jsx` | `assessment.own.view`（新增） | `/api/quiz/admin/*` | 新增：维度、关键题、阈值、权限、汇总分析 | P5 | 未开始 | |
| 老带新奖励 | `#rewards` | `pages/Insights.jsx` | `reward.view`（新增） | `/api/referral/*` | 新增：介绍关系接口、奖励权限 | P6 | 未开始 | |
| 招人分析 | `#analytics` | `pages/Insights.jsx` | `recruit.candidate_view` | `/api/analytics/recruit`、`manager` | 小改：按来源统计、日期范围 | P6 | 未开始 | |
| 人事专员绩效 | `#performance` | `pages/Insights.jsx` | `hr.score_view` | `/api/hr/targets`、`score-dims`、`score`、`specialists` | 无 | P6 | 未开始 | |
| 二维码中心 | `#qrcodes` | `pages/SelfService.jsx` | `self.task_view` | `/api/self/tasks*` | 小改：重新启用 | P5 | 未开始 | |
| 员工提交资料 | `#submissions` | `pages/SelfService.jsx` | `self.submission_view` | `/api/self/submissions*` | 新增：正式资料核对、缺失项清单、先认领后处理 | P5 | 未开始 | |
| 扫码表单配置 | `#formconfig` | `pages/SelfService.jsx` | `form.manage` | `/api/form-schemas/{type}` | 小改：字段名统一、可配置必填 | P5 | 未开始 | |
| 门店管理 | `#stores` | `pages/Admin.jsx` | `org.store_view` | `/api/org/stores*` | 小改：编号唯一 | P2 | 未开始 | |
| 账号管理 | `#accounts` | `pages/Admin.jsx` | `org.user_view` | `/api/org/users*`、`/api/org/positions` | 无 | P2 | 未开始 | |
| 权限管理 | `#permissions` | `pages/Admin.jsx` | `permission.manage` | `/api/permissions*`、`/api/admin/backups*` | 小改：新增 14 项权限 | P2 | 未开始 | |
| 扫码填报页 | `/self?code=`（`#publicform`） | `pages/SelfService.jsx` | 公开 | `/api/self/public/*`、`/api/quiz/public/*`、`/api/form-schemas/*` | 新增：分步入职、问卷绑定会话、正式资料链接 | P5 | 未开始 | |
| 登录 / 改密 / 退出 | `#login` | `pages/Login.jsx`（新增） | 公开 | `/api/auth/*` | 小改：会话 Cookie、CSRF、退出 | P1 | 未开始 | |
