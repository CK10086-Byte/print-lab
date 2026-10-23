"""校园打印任务调度综合实验 单文件完整版

环境：Python 3.9 或更高版本，仅使用标准库，无须安装额外依赖。
运行菜单：python print_lab.py
固定演示：python print_lab.py --demo

数组登记表保存全部任务，循环队列管理等待任务，单链表记录完成顺序，
顺序栈支持撤销最近一次模拟处理。默认登记容量 20，等待容量 5。
数组使用预分配 list 模拟定长顺序存储。
数据仅保存在内存中，退出即清空；本程序不连接真实打印机。
"""


# 任务实体
from dataclasses import dataclass


@dataclass
class Job:
    job_id: int
    owner: str
    pages: int
    status: str = "等待"


# 四种数据结构
def check_capacity(capacity):
    if type(capacity) is not int or capacity <= 0:
        raise ValueError("容量必须是正整数")


class ArrayTable:
    """按创建顺序保存全部任务；任务完成后仍保留记录。"""

    def __init__(self, capacity=20):
        check_capacity(capacity)
        self.capacity = capacity
        self._data = [None] * capacity
        self._size = 0

    def __len__(self):
        return self._size

    def is_full(self):
        return self._size == self.capacity

    def append(self, job):
        if self.is_full():
            raise OverflowError("任务登记表已满")
        self._data[self._size] = job
        self._size += 1

    def find(self, job_id):
        for index in range(self._size):
            if self._data[index].job_id == job_id:
                return self._data[index]
        return None

    def get(self, index):
        if type(index) is not int or not 0 <= index < self._size:
            raise IndexError("登记表下标越界")
        return self._data[index]

    def to_list(self):
        return [self._data[i] for i in range(self._size)]


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class SinglyLinkedList:
    """头尾指针均保留，不带哨兵结点。"""

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def append(self, value):
        node = Node(value)
        if self.head is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def pop_tail(self):
        if self.head is None:
            raise IndexError("完成记录为空")
        value = self.tail.value
        if self.head is self.tail:
            self.head = self.tail = None
        else:
            previous = self.head
            while previous.next is not self.tail:
                previous = previous.next
            previous.next = None
            self.tail = previous
        self._size -= 1
        return value

    def to_list(self):
        result = []
        current = self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result


class ArrayStack:
    """栈顶位于 _size - 1，下一个空槽位于 _size。"""

    def __init__(self, capacity=20):
        check_capacity(capacity)
        self.capacity = capacity
        self._data = [None] * capacity
        self._size = 0

    def __len__(self):
        return self._size

    def is_full(self):
        return self._size == self.capacity

    def push(self, value):
        if self.is_full():
            raise OverflowError("撤销栈已满")
        self._data[self._size] = value
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise IndexError("撤销栈为空")
        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None
        return value

    def peek(self):
        if self._size == 0:
            raise IndexError("撤销栈为空")
        return self._data[self._size - 1]

    def to_list(self):
        """从栈底到栈顶，显示时不可误读成弹出顺序。"""
        return [self._data[i] for i in range(self._size)]


class CircularQueue:
    """front 指向队首，size 区分空与满，所有槽位均可使用。"""

    def __init__(self, capacity=5):
        check_capacity(capacity)
        self.capacity = capacity
        self._data = [None] * capacity
        self._front = 0
        self._size = 0

    def __len__(self):
        return self._size

    def is_full(self):
        return self._size == self.capacity

    def enqueue(self, value):
        if self.is_full():
            raise OverflowError("等待队列已满")
        rear = (self._front + self._size) % self.capacity
        self._data[rear] = value
        self._size += 1

    def dequeue(self):
        if self._size == 0:
            raise IndexError("等待队列为空")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self.capacity
        self._size -= 1
        return value

    def enqueue_front(self, value):
        """仅供撤销处理使用；普通提交必须走队尾。"""
        if self.is_full():
            raise OverflowError("等待队列已满，无法撤销")
        self._front = (self._front - 1) % self.capacity
        self._data[self._front] = value
        self._size += 1

    def peek(self):
        if self._size == 0:
            raise IndexError("等待队列为空")
        return self._data[self._front]

    def to_list(self):
        return [self._data[(self._front + i) % self.capacity]
                for i in range(self._size)]


# 任务调度业务
class PrintService:
    def __init__(self, table_capacity=20, queue_capacity=5):
        self.table = ArrayTable(table_capacity)
        self.waiting = CircularQueue(queue_capacity)
        self.completed = SinglyLinkedList()
        self.undo_stack = ArrayStack(table_capacity)
        self._next_id = 1

    def submit(self, owner, pages):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("姓名不能为空")
        if type(pages) is not int or pages <= 0:
            raise ValueError("页数必须是正整数")
        # 所有业务校验在修改结构之前完成，失败不消耗编号。
        if self.table.is_full():
            raise OverflowError("任务登记表已满")
        if self.waiting.is_full():
            raise OverflowError("等待队列已满")
        job = Job(self._next_id, owner.strip(), pages)
        self.table.append(job)
        self.waiting.enqueue(job)
        self._next_id += 1
        return job

    def process_next(self):
        if len(self.waiting) == 0:
            raise IndexError("等待队列为空")
        if self.undo_stack.is_full():
            raise OverflowError("撤销栈已满")
        job = self.waiting.dequeue()
        job.status = "完成"
        self.completed.append(job)
        self.undo_stack.push(job)
        return job

    def undo_process(self):
        if len(self.undo_stack) == 0:
            raise IndexError("没有可撤销的处理记录")
        if self.waiting.is_full():
            raise OverflowError("等待队列已满，无法撤销")
        # 先检查最近完成任务，避免在不一致状态下继续修改。
        job = self.undo_stack.peek()
        if self.completed.tail is None or self.completed.tail.value is not job:
            raise RuntimeError("完成链表与撤销栈不一致")
        self.undo_stack.pop()
        self.completed.pop_tail()
        job.status = "等待"
        self.waiting.enqueue_front(job)
        return job

    def find(self, job_id):
        if type(job_id) is not int or job_id <= 0:
            raise ValueError("编号必须是正整数")
        return self.table.find(job_id)

    def snapshot(self):
        """返回可比较的值快照，用于观察状态和测试失败前后的一致性。"""
        return {
            "all": [(j.job_id, j.owner, j.pages, j.status)
                    for j in self.table.to_list()],
            "waiting": [j.job_id for j in self.waiting.to_list()],
            "completed": [j.job_id for j in self.completed.to_list()],
            "undo_bottom_to_top": [j.job_id for j in self.undo_stack.to_list()],
            "next_id": self._next_id,
        }

    def check_invariants(self):
        """教学检查器，时间 O(n²)，不计入单步业务复杂度。"""
        all_jobs = self.table.to_list()
        waiting = self.waiting.to_list()
        completed = self.completed.to_list()
        stack = self.undo_stack.to_list()
        all_ids = [j.job_id for j in all_jobs]
        waiting_ids = [j.job_id for j in waiting]
        completed_ids = [j.job_id for j in completed]
        assert len(all_ids) == len(set(all_ids)), "登记表出现重复编号"
        assert len(waiting_ids) == len(set(waiting_ids)), "队列出现重复任务"
        assert len(completed_ids) == len(set(completed_ids)), "链表出现重复任务"
        assert set(waiting_ids).isdisjoint(completed_ids), "任务同时处于两个状态"
        assert set(all_ids) == set(waiting_ids) | set(completed_ids), "任务丢失"
        assert completed_ids == [j.job_id for j in stack], "完成顺序与栈不一致"
        for job in waiting:
            assert job.status == "等待", "队列中任务状态错误"
            assert self.table.find(job.job_id) is job, "任务对象未共享"
        for job in completed:
            assert job.status == "完成", "链表中任务状态错误"
            assert self.table.find(job.job_id) is job, "任务对象未共享"
        return True


# 交互菜单与演示入口
import argparse


def show_state(service):
    state = service.snapshot()
    print("等待队列（队首到队尾）：", state["waiting"])
    print("完成记录（先到后）：", state["completed"])
    print("撤销栈（栈底到栈顶）：", state["undo_bottom_to_top"])
    if not state["all"]:
        print("登记表为空")
    for job_id, owner, pages, status in state["all"]:
        print(f"#{job_id} | {owner} | {pages}页 | {status}")


def demo():
    service = PrintService()
    for owner, pages in [("小林", 3), ("小周", 5), ("小陈", 2)]:
        service.submit(owner, pages)
    print("提交任务 1、2、3")
    show_state(service)
    for _ in range(2):
        print("处理任务：", service.process_next().job_id)
    print("撤销最近一次处理：", service.undo_process().job_id)
    show_state(service)
    print("再次处理：", service.process_next().job_id)
    show_state(service)
    service.check_invariants()
    print("状态一致性检查通过")


def interactive():
    service = PrintService()
    menu = "\n1 提交  2 处理下一项  3 撤销处理  4 查看状态  5 按编号查询  0 退出"
    while True:
        print(menu)
        try:
            choice = input("请选择：").strip()
            if choice == "0":
                print("已退出；本实验数据仅保存在内存中。")
                return
            if choice == "1":
                owner = input("姓名：")
                pages = int(input("页数："))
                job = service.submit(owner, pages)
                print(f"提交成功，编号 {job.job_id}")
            elif choice == "2":
                print("处理完成：", service.process_next().job_id)
            elif choice == "3":
                print("已恢复到队首：", service.undo_process().job_id)
            elif choice == "4":
                show_state(service)
            elif choice == "5":
                job = service.find(int(input("任务编号：")))
                print(job if job is not None else "未找到任务")
            else:
                print("请输入菜单中的编号")
        except (ValueError, IndexError, OverflowError) as error:
            print("操作失败：", error)
        except NotImplementedError as error:
            print("请先补全 structures.py：", error)
        except (EOFError, KeyboardInterrupt):
            print("\n已退出")
            return


def main():
    parser = argparse.ArgumentParser(description="校园打印任务调度模拟")
    parser.add_argument("--demo", action="store_true", help="运行固定演示")
    args = parser.parse_args()
    if args.demo:
        try:
            demo()
        except NotImplementedError as error:
            print("学生版尚未完成，请补全 structures.py：", error)
            return 1
    else:
        interactive()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

