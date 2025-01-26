import threading
import tkinter as tk

from lol_audit import LolAudit


class LolAuditUi:
    def __init__(self):
        self.lol_audit = LolAudit()
        threading.Thread(target=self.__init_ui).start()

        self.lol_audit.start_main(self.__update_label)

    def __init_ui(self):
        self.root = tk.Tk()
        self.root.title("League of Legends")
        self.root.geometry("300x150+800+400")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # 設定接受對戰延遲時間
        self.accept_delay_value = tk.IntVar()
        self.accept_delay_value.set(self.lol_audit.get_accept_delay())
        self.accept_delay_value.trace_add("write", self.lol_audit.set_accept_delay)
        self.accept_delay = tk.Entry(
            self.root, width=5, justify="center", textvariable=self.accept_delay_value
        )
        self.accept_delay.pack(pady=10)

        # 開始列隊按鈕
        self.match_button = tk.Button(
            self.root, text="開始列隊", command=self.__toggle_matchmaking
        )
        self.match_button.pack(pady=5)

        # 顯示訊息
        self.label = tk.Label(self.root, text="讀取中...", font=("Arial", 14))
        self.label.pack(pady=20)

        # 自動接受對戰
        self.auto_accept_status = tk.IntVar()
        self.auto_accept_status.set(self.lol_audit.get_auto_accept())
        self.auto_accept_status.trace_add("write", self.__toggle_auto_accept)
        self.auto_accept_checkbutton = tk.Checkbutton(
            self.root, text="自動接受", variable=self.auto_accept_status
        )
        self.auto_accept_checkbutton.place(x=220, y=10)  # x=250, y=10 位置為右上角

        # 超時自動重排
        self.auto_rematch_status = tk.IntVar()
        self.auto_rematch_status.set(self.lol_audit.get_auto_rematch())
        self.auto_rematch_status.trace_add("write", self.__toggle_auto_rematch)
        self.auto_rematch_checkbutton = tk.Checkbutton(
            self.root, text="超時重排", variable=self.auto_rematch_status
        )
        self.auto_rematch_checkbutton.place(x=220, y=40)

        self.root.mainloop()
        self.lol_audit.stop_main()

    def __update_label(self, text):
        self.label.config(text=text)

    def __start_matchmaking(self):
        self.lol_audit.start_matchmaking()

    def __stop_matchmaking(self):
        self.lol_audit.stop_matchmaking()

    def __toggle_matchmaking(self):
        if self.match_button.cget("text") == "開始列隊":
            self.match_button.config(text="停止列隊")
            self.__start_matchmaking()
        else:
            self.match_button.config(text="開始列隊")
            self.__stop_matchmaking()

    def __toggle_auto_accept(self, *arg):
        self.lol_audit.set_auto_accept(self.auto_accept_status.get())

    def __toggle_auto_rematch(self, *arg):
        self.lol_audit.set_auto_rematch(self.auto_rematch_status.get())


if __name__ == "__main__":
    lol_audit_ui = LolAuditUi()
