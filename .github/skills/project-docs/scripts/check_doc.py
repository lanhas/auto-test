#!/usr/bin/env python3
"""检查 Markdown 文档是否符合 project-docs 技能的表达风格规范。

用法：
    python3 check_doc.py 文档1.md [文档2.md ...]

输出四类信息：
    错误    必须修改后再交付
    警告    逐条判断；确有必要保留的可以保留
    统计    带编号条目的数量，用于核对文中的合计数字
    待补充  文中尚未填写的信息，交付时须告知用户

存在错误时退出码为 1。只依赖 Python 3 标准库。
"""

import re
import sys

# 一句话的建议长度上限（不含空格与 Markdown 符号）
MAX_SENTENCE_LEN = 60

# 错误：出现即须修改。键为正则表达式，值为修改建议。
ERROR_RULES = {
    # 行话
    r"赋能": "写明具体提供了什么能力，或带来了什么结果",
    r"抓手": "改为“方法”“措施”，或写明具体做法",
    r"闭环": "写明流程从哪里开始、到哪里结束、由谁完成",
    r"打通": "改为“连接”“接入”“统一”，并写明对象",
    r"拉通": "改为“协调”“统一”",
    r"沉淀": "改为“整理”“积累”“记录”",
    r"颗粒度": "改为“详细程度”或“粒度”",
    r"痛点": "改为“问题”，并写明具体是什么问题",
    r"心智": "改为“认知”“印象”，或写明用户的具体行为",
    r"组合拳": "改为“多项措施”，并逐项列出",
    r"护城河": "改为“竞争优势”，并写明具体优势",
    r"底层逻辑": "改为“原理”“原因”",
    r"顶层设计": "改为“总体设计”",
    r"方法论": "改为“方法”",
    r"一盘棋": "改为“统一规划”",
    r"倒逼": "改为“促使”",
    r"触达": "改为“通知到”“送达”",
    r"卡点": "改为“阻塞点”，或写明具体问题",
    r"落地(?!页)": "改为“实施”“上线”“完成”",
    r"降本增效|提质增效": "写明降低了哪项成本、提高了哪项效率，并给出数字",
    # 空话与夸张
    r"旨在|致力于": "删除，直接写目标或做法",
    r"助力": "改为“帮助”，或写明具体作用",
    r"全方位|多维度|深层次": "删除，或逐项写出具体方面",
    r"无缝": "写明具体表现，例如“无须重新登录”",
    r"一站式": "写明包含哪些功能",
    r"卓越|极致|完美": "删除，改用数据说明",
    r"保驾护航|添砖加瓦|新高度|新台阶|重要意义|深远影响": "删除，改写为具体事实",
    # 套话与过渡语
    r"综上所述|总而言之|总的来说|由此可见": "删除；结论应写在段首",
    r"值得注意的是|需要指出的是|需要强调的是|值得一提的是|需要注意的是": "删除，直接写内容",
    r"众所周知|不言而喻|毋庸置疑|不难看出": "删除",
    r"随着.{0,20}的(快速|不断|飞速|持续|高速|日益)?(发展|普及|增长|提高|提升)": "删除开场白，直接写问题与数据",
    r"在当今": "删除开场白，直接写问题与数据",
    r"(下面|接下来|以下)(我们)?将|本(节|章|文|文档)(将|主要|旨在)": "删除引导句，直接写内容",
    # 口语
    r"搞": "改为“完成”“处理”“实现”等具体动词",
    r"扛(得住|不住|住)": "改为“可承受”“无法承受”，并给出数字",
    r"盯": "改为“监控”“关注”",
    r"啥": "改为“什么”",
    r"咋": "改为“如何”",
    r"挂了|挂掉": "改为“不可用”“发生故障”",
    r"跑(一遍|通|一下|起来|用例|不通)": "改为“执行”“运行”",
    r"打满": "改为“耗尽”“达到上限”",
    r"踩坑|填坑|踩过的坑": "改为“问题”，并写明具体问题",
    r"拍板": "改为“决定”，并写明决定人",
    r"靠谱": "改为“可靠”",
    r"一堆|一大堆": "写出具体数量",
    r"说白了|老实说|讲真|说实话": "删除",
    r"咱们|咱": "改为“我们”或“本项目”",
    r"这块|这一块|那块": "改为“这部分”，或写出具体名称",
    r"就行|就好了|就可以了": "改为“即可”",
    r"开小差": "改为“异常”",
    r"甩锅|背锅": "改为“责任归属”等中性说法",
    r"砍掉": "改为“取消”“删除”",
    r"丢了": "改为“丢失”",
    r"拦住": "改为“拦截”",
    r"没问题": "改为“正常”，或写明具体结果",
    r"差不多": "改为“约”，并给出数字",
    # 未替换的模板占位符
    r"\{\{[^}]*(\}\})?": "模板占位符尚未替换；无法填写时改为【待补充：缺什么，向谁要】",
}

# 警告：需要逐条判断。
WARN_RULES = {
    # 模糊词
    r"较(高|低|大|小|多|少|好|差|快|慢|长|短|强|弱|为)": "给出数字或比较对象",
    r"显著|大幅|极大|明显": "给出数字",
    r"尽快|尽早|适时|择机|近期": "给出日期或触发条件",
    r"及时": "写明时限，例如“5 分钟内”",
    r"适当|合理(?!性)|酌情|视情况|必要时": "写明条件或数值",
    r"一定程度|某种程度|很大程度": "写明具体程度",
    r"若干|大量|少量": "给出数量",
    r"等等": "列全，或删除“等等”",
    r"大概|大致|基本上": "给出数字，或写明例外情况",
    r"非常|十分(?![钟之])|极其|相当(?!于)": "删除程度副词，改用数据",
    r"有效地?(提升|降低|避免|解决|保障|防止|减少|提高|缓解)": "删除“有效”，写出具体数字或机制",
    r"全面(提升|升级|革新|保障|优化)|充分(考虑|利用|发挥|保障|验证)": "写出具体范围或做法",
    r"高效|便捷|流畅|友好": "写出可衡量的标准",
    r"相关(人员|部门|方|团队|同学)|有关(人员|部门|方面)": "写明具体是谁",
    r"后续(再|会|将|需|可)": "写明时间或触发条件",
    # 套路句式
    r"不仅.{0,30}(而且|更是|还|也)": "删除修辞，直接写事实",
    r"不是.{0,20}而是": "直接写“是什么”",
    r"！": "删除感叹号",
    # 冗余动词与公文腔
    r"进行(?!中)": "直接使用动词，例如“进行校验”改为“校验”",
    r"实现对": "直接使用动词，例如“实现对频率的限制”改为“限制频率”",
    r"加以|予以": "删除，直接使用动词",
    r"兹|特此|鉴于": "改为直白的说法（如“由于”），或删除",
    r"切实|扎实推进|稳步推进|大力推动|高度重视|进一步加强": "写明具体动作",
    r"(?<![模虚比草])拟(采用|于|定|将|对)": "改为“计划”",
    # 需结合语境判断的行话
    r"兜底": "改为“后备措施”，并写明具体措施",
    r"(?<![左右中端部])对齐(?!方式)": "若指“统一认识”，改为“确认”“达成一致”",
    r"聚焦|发力|体系化|精细化": "写明具体做法",
}

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
FENCE = re.compile(r"^\s*(```|~~~)")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
ID_CELL = re.compile(r"^([A-Z]{1,5})-?(\d+)(-\d+)?$")
TODO = re.compile(r"【待补充[^】]*】")


def clean(line):
    """去掉行内代码与链接地址，避免配置项、字段名、网址触发规则。"""
    line = INLINE_CODE.sub("", line)
    return LINK.sub(r"\1", line)


def sentences(line):
    """把一行拆成句子；表格行先按单元格拆分。"""
    parts = re.split(r"\||<br\s*/?>", line)
    for part in parts:
        for sentence in re.split(r"[。！？；]", part):
            text = re.sub(r"[\s*#>\-]", "", sentence)
            if text:
                yield text


def id_group(cell):
    """把首列编号归类，例如 TC-01 归为 TC，R1-1 归为 验收标准。"""
    match = ID_CELL.match(cell)
    if not match:
        return None
    prefix, _, sub = match.groups()
    if prefix == "P":  # P0、P1、P99 是优先级或指标，不是编号
        return None
    if prefix == "R":
        return "验收标准（R?-?）" if sub else "需求（R?）"
    return prefix


def check(path):
    errors, warnings, todos = [], [], []
    stats, seen_ids = {}, set()
    in_code = False

    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    for number, raw in enumerate(lines, 1):
        if FENCE.match(raw):
            in_code = not in_code
            continue
        if in_code or TABLE_SEPARATOR.match(raw):
            continue

        for todo in TODO.findall(raw):
            todos.append((number, todo))

        line = clean(raw)

        for pattern, advice in ERROR_RULES.items():
            for match in re.finditer(pattern, line):
                errors.append((number, f"「{match.group(0)}」→ {advice}"))
        for pattern, advice in WARN_RULES.items():
            for match in re.finditer(pattern, line):
                warnings.append((number, f"「{match.group(0)}」→ {advice}"))

        if EMOJI.search(line):
            warnings.append((number, "含表情或图形符号 → 改用文字，例如“是 / 否”“达标 / 未达标”"))

        if raw.startswith("#"):
            title = line.lstrip("#").strip()
            if raw.startswith("#####"):
                warnings.append((number, "标题层级过深 → 章节编号最多三级（如 5.2.1）"))
            if re.search(r"[？?]$|为什么|怎么|怎样|如何", title):
                warnings.append((number, f"标题「{title}」→ 改为名词短语，例如“背景与问题”"))

        for sentence in sentences(line):
            if len(sentence) > MAX_SENTENCE_LEN:
                warnings.append(
                    (number, f"句子偏长（{len(sentence)} 字）→ 拆成两句：{sentence[:20]}……")
                )

        if raw.lstrip().startswith("|"):
            cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
            group = id_group(cells[0]) if cells else None
            if group and cells[0] not in seen_ids:
                seen_ids.add(cells[0])
                counter = stats.setdefault(group, {"合计": 0})
                counter["合计"] += 1
                for cell in cells[1:]:
                    if cell in ("P0", "P1", "P2", "是", "否"):
                        counter[cell] = counter.get(cell, 0) + 1

    return errors, warnings, stats, todos


def report(path, errors, warnings, stats, todos):
    print(f"== {path} ==")
    for title, items in (("错误", errors), ("警告", warnings), ("待补充", todos)):
        if items:
            print(f"{title}（{len(items)}）")
            for number, message in items:
                print(f"  第 {number} 行  {message}")
    if stats:
        print("统计（请与文中的合计数字核对）")
        for group, counter in stats.items():
            detail = "，".join(
                f"{key} {counter[key]}" for key in ("P0", "P1", "P2", "是", "否") if key in counter
            )
            suffix = f"（{detail}）" if detail else ""
            print(f"  {group}：{counter['合计']} 条{suffix}")
    if not (errors or warnings or todos):
        print("未发现问题")
    print()


def main(paths):
    if not paths:
        print(__doc__)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    total_errors = total_warnings = 0
    for path in paths:
        errors, warnings, stats, todos = check(path)
        report(path, errors, warnings, stats, todos)
        total_errors += len(errors)
        total_warnings += len(warnings)

    print(f"合计：错误 {total_errors} 处，警告 {total_warnings} 处")
    return 1 if total_errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:  # 输出被 head 等命令提前截断
        sys.exit(1)
