import threading
import tkinter as tk

from lol_audit import LolAudit


class LolAuditUi:
    def __init__(self):
        self.lol_audit = LolAudit()
        threading.Thread(target=self.__init_ui).start()

        self.lol_audit.start_main(self.__update)

    def __init_ui(self):
        self.root = tk.Tk()
        self.root.title("LOL Audit")
        self.root.geometry("300x170+800+400")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # 設定接受對戰延遲時間
        self.accept_delay_value = tk.IntVar(value=self.lol_audit.get_accept_delay())
        self.accept_delay_value.trace_add("write", self.__set_accept_delay)
        self.accept_delay = tk.Entry(
            self.root, width=5, justify="center", textvariable=self.accept_delay_value
        )
        self.accept_delay.pack(pady=10)

        # 開始列隊按鈕
        self.match_button = tk.Button(
            self.root, text="開始列隊", command=self.__toggle_matchmaking_button
        )
        self.match_button.pack(pady=5)

        # 顯示訊息
        self.label = tk.Label(self.root, text="...", font=("Arial", 14))
        self.label.pack(pady=20)

        # 自動接受對戰
        self.auto_accept_status = tk.BooleanVar(value=self.lol_audit.get_auto_accept())
        self.auto_accept_checkbutton = tk.Checkbutton(
            self.root,
            text="自動接受",
            variable=self.auto_accept_status,
            command=self.__toggle_auto_accept,
        )
        self.auto_accept_checkbutton.place(x=220, y=10)  # x=250, y=10 位置為右上角

        # 超時自動重排
        self.auto_rematch_status = tk.BooleanVar(
            value=self.lol_audit.get_auto_rematch()
        )
        self.auto_rematch_checkbutton = tk.Checkbutton(
            self.root,
            text="超時重排",
            variable=self.auto_rematch_status,
            command=self.__toggle_auto_rematch,
        )
        self.auto_rematch_checkbutton.place(x=220, y=40)

        self.root.mainloop()
        self.lol_audit.stop_main()

    def __update(self, text: str):
        if text == "未在列隊":
            self.match_button.config(text="開始列隊", state="normal")
        elif text.startswith("列隊中"):
            self.match_button.config(text="停止列隊", state="normal")
        else:
            self.match_button.config(state="disabled")
        self.label.config(text=text)

    def __start_matchmaking(self):
        self.lol_audit.start_matchmaking()

    def __stop_matchmaking(self):
        self.lol_audit.stop_matchmaking()

    def __set_accept_delay(self, *args):
        try:
            delay = self.accept_delay_value.get()
        except tk.TclError:
            delay = 0

        print(delay)
        self.lol_audit.set_accept_delay(delay)

    def __toggle_matchmaking_button(self):
        if self.match_button.cget("text") == "開始列隊":
            self.__start_matchmaking()
        else:
            self.__stop_matchmaking()

    def __toggle_auto_accept(self):
        self.lol_audit.set_auto_accept(self.auto_accept_status.get())

    def __toggle_auto_rematch(self):
        self.lol_audit.set_auto_rematch(self.auto_rematch_status.get())


if __name__ == "__main__":
    lol_audit_ui = LolAuditUi()
