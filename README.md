# 打印任务实验室

《基于 Python 的数据结构与算法》课程交互实验网页。

## 功能

- 登记姓名、页数并生成任务编号。
- 先来先服务，处理等待队首任务。
- 撤销最近一次处理，恢复到队首。
- 按编号查询，按等待或完成状态筛选。
- 观察数组登记表、循环队列槽位、完成链表和撤销栈。
- 载入三条课堂示例，检查状态一致性，查看运行日志。

默认最多登记 20 项任务，同时等待 5 项。完成记录仍保留在登记表中。
本网页只模拟打印，不连接打印机；数据只存在当前页面内存中，刷新即清空。

## 文件

- `index.html`：自包含网页，样式与 JavaScript 都已内嵌，无第三方运行依赖。
- `print_lab.py`：原始单文件 Python 程序，保持原样，供对照学习和命令行运行。
- `.nojekyll`：让 GitHub Pages 直接发布静态文件。

GitHub Pages 版用 JavaScript 实现与 Python 程序相同的数据结构和业务规则。
它不在服务器运行 Python。各结构均为显式教学实现，不用现成队列替代核心算法。

## 运行

直接双击 `index.html`，或在本目录执行：

```text
python -m http.server 8000
```

访问 `http://127.0.0.1:8000`。
原始命令行程序仍可运行 `python print_lab.py` 或 `python print_lab.py --demo`。

## GitHub Pages

仓库 Settings → Pages → Build and deployment：
Source 选择 Deploy from a branch，Branch 选择 main，目录选择 / (root)，保存。
网站地址为 https://ck10086-byte.github.io/print-lab/ 。

## 教学演示

1. 点击“载入示例”，得到任务 1、2、3。
2. 连续点击两次“处理下一项”，等待 [3]，完成 [1, 2]。
3. 点击“撤销最近处理”，等待 [2, 3]，完成 [1]。
4. 再处理一次，应优先处理任务 2；点击“检查状态”。

示例只可在空登记表载入，不会覆盖已有任务。
网页输入以文字节点渲染，姓名不会作为 HTML 执行。
