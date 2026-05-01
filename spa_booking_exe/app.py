import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class BookingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("韩院长预约排班系统（桌面版）")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 680)

        self.bookings = []

        self._build_header()
        self._build_summary()
        self._build_form_and_schedule()
        self._build_table()

    def _build_header(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="韩院长预约排班系统", font=("Microsoft YaHei UI", 18, "bold")).pack(side=tk.LEFT)
        ttk.Label(
            frame,
            text=f"日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.RIGHT)

    def _build_summary(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        frame.pack(fill=tk.X)

        cards = [
            ("今日预约", "0 单"),
            ("服务中", "0 人"),
            ("空闲技师", "4 人"),
            ("空闲床位", "8 张"),
            ("今日营收", "¥ 0"),
        ]

        for title, value in cards:
            card = ttk.LabelFrame(frame, text=title, padding=10)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            ttk.Label(card, text=value, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W)

    def _build_form_and_schedule(self) -> None:
        container = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        container.pack(fill=tk.BOTH, expand=False)

        form = ttk.LabelFrame(container, text="快速预约", padding=10)
        form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.customer_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.service_var = tk.StringVar(value="足浴 | 60分钟")
        self.therapist_var = tk.StringVar(value="刘师傅")
        self.room_var = tk.StringVar(value="足浴1-1")
        self.time_var = tk.StringVar(value=datetime.now().strftime("%H:%M"))

        fields = [
            ("客户姓名", self.customer_var),
            ("手机号", self.phone_var),
            ("预约项目", self.service_var),
            ("预约技师", self.therapist_var),
            ("房间/床位", self.room_var),
            ("预约时间", self.time_var),
        ]

        for idx, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=idx, column=0, sticky=tk.W, pady=4)
            ttk.Entry(form, textvariable=var, width=30).grid(row=idx, column=1, sticky=tk.EW, pady=4)

        form.columnconfigure(1, weight=1)
        ttk.Button(form, text="确认预约", command=self.create_booking).grid(row=len(fields), column=0, columnspan=2, pady=8, sticky=tk.EW)

        schedule = ttk.LabelFrame(container, text="技师实时排班（示例）", padding=10)
        schedule.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        demo_lines = [
            "刘师傅：09:00-10:00 张女士 | 11:00-12:30 李先生",
            "王师傅：09:30-10:30 王先生 | 12:30-13:30 周先生",
            "李师傅：10:00-11:00 陈女士 | 14:00-15:00 空闲",
            "赵师傅：当前服务中",
        ]
        for line in demo_lines:
            ttk.Label(schedule, text=line).pack(anchor=tk.W, pady=3)

    def _build_table(self) -> None:
        frame = ttk.LabelFrame(self.root, text="今日预约列表", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        columns = ("time", "service", "customer", "phone", "therapist", "room", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        self.tree.pack(fill=tk.BOTH, expand=True)

        headings = {
            "time": "时间",
            "service": "项目",
            "customer": "客户",
            "phone": "电话",
            "therapist": "技师",
            "room": "房间/床位",
            "status": "状态",
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=130, anchor=tk.CENTER)

    def create_booking(self) -> None:
        customer = self.customer_var.get().strip()
        phone = self.phone_var.get().strip()
        if not customer or not phone:
            messagebox.showwarning("信息不完整", "请至少填写客户姓名和手机号。")
            return

        booking = (
            self.time_var.get().strip() or datetime.now().strftime("%H:%M"),
            self.service_var.get().strip() or "足浴 | 60分钟",
            customer,
            phone,
            self.therapist_var.get().strip() or "待分配",
            self.room_var.get().strip() or "待分配",
            "已预约",
        )
        self.bookings.append(booking)
        self.tree.insert("", tk.END, values=booking)
        messagebox.showinfo("预约成功", f"已为 {customer} 创建预约。")


def main() -> None:
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
