# 系统前置信息：DemoLife HK eApp（模拟）

这份文档相当于 Tester 上手前要了解的系统背景。AI 在写需求文档、测试文档和执行测试时都会读它。
内容由人维护；系统流程有变化时更新这里，而不是改每个 story 的文档。

## 1. 系统简介

- 名称：DemoLife HK eApp，销售人员（Financial Planner，FP）用来为客户填写投保申请的 Web 系统
- 市场：香港（HK）
- 界面语言：英文（繁体中文版本由翻译团队另行提供文案）

## 2. 测试环境

| 项 | 值 |
|---|---|
| Test page | 以 story 的 `Test page` 字段为准；本仓库的模拟系统是 `http://localhost:4173` |
| 测试账号 | Staff ID `uat.fp01`，Password `Passw0rd!` |
| 测试数据 | 只能使用虚构客户信息，不得使用真实客户资料 |

## 3. 基本投保流程

登录后依次经过 4 个步骤，页面顶部有步骤条，每一步用 `Next` 前进、`Back` 返回。

| 步骤 | 页面标题 | 必填内容 | 说明 |
|---|---|---|---|
| 0 | Sign in | Staff ID、Password | 点 `Sign in` |
| 1 | Product | Product（下拉） | 产品决定后面页面的行为差异 |
| 2 | Life Insured | Full name、Date of birth、Gender | |
| 3 | Beneficiary | 每个受益人：Full name、Relationship to Life Insured、Share (%) | 见第 5 节 |
| 4 | Review & Submit | 无 | 显示申请摘要，可下载 Application Form PDF |

## 4. 产品清单（HK）

| 代码 | 名称 | 表单模板 |
|---|---|---|
| WL01 | WealthBuilder Whole Life Plan | 新模板 |
| SV02 | GoalSaver Endowment Plan | 新模板 |
| CI03 | CareShield Critical Illness Plan | 新模板 |
| TM04 | TermProtect Life Plan | 新模板 |
| UL05 | LegacyPlus Universal Life | 新模板 |
| QA06 | IncomeSecure Deferred Annuity (QDAP) | 旧模板 |
| SP07 | PrimeWealth Single Premium Plan | 旧模板 |
| JV08 | JuvenileStart Education Plan | 旧模板 |

## 5. Beneficiary 页面的既有规则

- 默认有 1 个受益人，点 `Add beneficiary` 增加，最多 4 个；多于 1 个时可以 `Remove`
- 所有受益人的 Share (%) 合计必须等于 100，否则点 `Next` 会被拦截
- Relationship 选 `Others` 时出现 `Please specify` 输入框，必填
- 校验不通过时停留在当前页，错误信息显示在对应字段下方

## 6. Application Form PDF

- 入口：Review & Submit 页面的 `Download application form (PDF)`
- 文件名：`ApplicationForm_<申请编号>.pdf`
- 内容分三部分：Product、Life Insured、Beneficiary Nomination

## 7. 常用术语

| 缩写 | 含义 |
|---|---|
| FP | Financial Planner，销售人员 |
| Bene | Beneficiary，受益人 |
| NIGO | Not In Good Order，申请资料不齐全或不合规 |
| NB | New Business，新契约部门 |
| TC / EN | 繁体中文 / 英文 |
