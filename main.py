import collections
import random
import tkinter as tk
from tkinter import messagebox


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("스네이크 게임")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.timer_id = None
        self.grid_var = tk.StringVar(value="10")
        self.speed_var = tk.IntVar(value=180)
        self.main_container = tk.Frame(root, bg="#0f172a")
        self.main_container.pack(fill="both", expand=True)
        self.build_setup_view()
        self.root.bind("<Key>", self.on_key)

    def build_setup_view(self):
        self.clear_container()
        f = tk.Frame(self.main_container, bg="#0f172a", padx=40, pady=30)
        f.pack(expand=True)
        tk.Label(f, text="🐍 SNAKE GAME", font=("Helvetica", 22, "bold"), fg="#38bdf8", bg="#0f172a").pack(pady=10)
        tk.Label(f, text="격자 크기를 설정하세요 (3 ~ 10)", font=("Helvetica", 12), fg="#cbd5e1", bg="#0f172a").pack(pady=4)

        row = tk.Frame(f, bg="#0f172a")
        row.pack(pady=10)
        tk.Label(row, text="가로×세로 칸 수: ", font=("Helvetica", 12), fg="#f8fafc", bg="#0f172a").pack(side="left")
        tk.Spinbox(row, from_=3, to=10, textvariable=self.grid_var, width=5, font=("Helvetica", 13), justify="center").pack(side="left", padx=5)

        bf = tk.Frame(f, bg="#0f172a")
        bf.pack(pady=3)
        for s in (3, 5, 8, 10):
            tk.Button(bf, text=f"{s}×{s}", font=("Helvetica", 10), command=lambda v=s: self.grid_var.set(str(v))).pack(side="left", padx=3)

        sf = tk.Frame(f, bg="#0f172a")
        sf.pack(pady=8)
        tk.Label(sf, text="속도: ", font=("Helvetica", 11), fg="#cbd5e1", bg="#0f172a").pack(side="left")
        for lbl, ms in [("느림", 250), ("보통", 180), ("빠름", 120)]:
            tk.Radiobutton(sf, text=lbl, value=ms, variable=self.speed_var, font=("Helvetica", 10), bg="#0f172a", fg="#f8fafc", selectcolor="#1e293b").pack(side="left", padx=2)

        tk.Button(f, text="게임 시작", font=("Helvetica", 13, "bold"), bg="#22c55e", fg="white", padx=20, pady=6, command=self.start_game).pack(pady=15)
        tk.Label(f, text="이동: 방향키 (↑, ↓, ←, →)\n재시작: R  |  설정: ESC", font=("Helvetica", 10), fg="#94a3b8", bg="#0f172a", justify="center").pack()

    def clear_container(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        for w in self.main_container.winfo_children():
            w.destroy()

    def start_game(self):
        try:
            sz = int(self.grid_var.get().strip())
            if not (3 <= sz <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("입력 오류", "격자 크기는 3 이상 10 이하의 정수여야 합니다.")
            return

        self.grid_size = sz
        self.cell_size = 420 // sz
        self.board_px = self.grid_size * self.cell_size
        self.init_game_state()
        self.build_game_view()
        self.timer_id = self.root.after(self.speed_var.get(), self.run_tick)

    def init_game_state(self):
        mx, my = self.grid_size // 2, self.grid_size // 2
        length = 2 if self.grid_size <= 3 else 3
        self.snake = collections.deque([(mx - i, my) for i in range(length)])
        self.snake_set = set(self.snake)
        self.direction = self.current_direction = (1, 0)
        self.score, self.game_over, self.game_cleared, self.end_reason = 0, False, False, ""
        self.apple = self.spawn_apple()

    def spawn_apple(self):
        empty = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size) if (x, y) not in self.snake_set]
        return random.choice(empty) if empty else None

    def build_game_view(self):
        self.clear_container()
        top = tk.Frame(self.main_container, bg="#1e293b", padx=10, pady=8)
        top.pack(fill="x")
        tot = self.grid_size * self.grid_size
        self.lbl_score = tk.Label(top, text=f"점수: 0  |  길이: {len(self.snake)}/{tot}", font=("Helvetica", 11, "bold"), fg="#38bdf8", bg="#1e293b")
        self.lbl_score.pack(side="left")
        tk.Button(top, text="설정(ESC)", font=("Helvetica", 9), command=self.build_setup_view).pack(side="right", padx=4)
        tk.Button(top, text="재시작(R)", font=("Helvetica", 9), command=self.restart_game).pack(side="right", padx=4)

        self.canvas = tk.Canvas(self.main_container, width=self.board_px, height=self.board_px, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.draw()

    def on_key(self, event):
        k, dirs = event.keysym, {
            "Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0),
            "w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0),
            "W": (0, -1), "S": (0, 1), "A": (-1, 0), "D": (1, 0),
        }
        if k in dirs:
            ndx, ndy = dirs[k]
            cdx, cdy = self.current_direction
            if (ndx + cdx != 0 or ndy + cdy != 0) and (ndx != cdx or ndy != cdy):
                self.direction = (ndx, ndy)
        elif k in ("r", "R") and hasattr(self, "grid_size"):
            self.restart_game()
        elif k == "Escape":
            self.build_setup_view()

    def restart_game(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.init_game_state()
        self.draw()
        self.timer_id = self.root.after(self.speed_var.get(), self.run_tick)

    def run_tick(self):
        if self.game_over or self.game_cleared:
            return
        self.step()
        self.draw()
        if not (self.game_over or self.game_cleared):
            self.timer_id = self.root.after(self.speed_var.get(), self.run_tick)

    def step(self):
        self.current_direction = self.direction
        hx, hy = self.snake[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]

        if not (0 <= nx < self.grid_size and 0 <= ny < self.grid_size):
            self.game_over, self.end_reason = True, "벽에 부딪혔습니다!"
            return

        if (nx, ny) == self.apple:
            self.snake.appendleft((nx, ny))
            self.snake_set.add((nx, ny))
            self.score += 1
            if len(self.snake) == self.grid_size * self.grid_size:
                self.game_cleared = True
            else:
                self.apple = self.spawn_apple()
        else:
            tail = self.snake.pop()
            self.snake_set.remove(tail)
            if (nx, ny) in self.snake_set:
                self.snake.append(tail)
                self.game_over, self.end_reason = True, "자신의 몸에 부딪혔습니다!"
                return
            self.snake.appendleft((nx, ny))
            self.snake_set.add((nx, ny))

    def draw(self):
        self.canvas.delete("all")
        cs = self.cell_size
        for i in range(self.grid_size + 1):
            p = i * cs
            self.canvas.create_line(p, 0, p, self.board_px, fill="#1e293b", width=1)
            self.canvas.create_line(0, p, self.board_px, p, fill="#1e293b", width=1)

        if self.apple:
            ax, ay = self.apple
            self.canvas.create_oval(ax*cs+2, ay*cs+2, (ax+1)*cs-2, (ay+1)*cs-2, fill="#ef4444", outline="#f87171")

        for idx, (sx, sy) in enumerate(self.snake):
            color = "#16a34a" if idx == 0 else "#22c55e"
            self.canvas.create_rectangle(sx*cs+1, sy*cs+1, (sx+1)*cs-1, (sy+1)*cs-1, fill=color, outline="")

        tot = self.grid_size * self.grid_size
        self.lbl_score.config(text=f"점수: {self.score}  |  길이: {len(self.snake)}/{tot}")

        if self.game_over or self.game_cleared:
            cx, cy = self.board_px // 2, self.board_px // 2
            self.canvas.create_rectangle(cx - 150, cy - 75, cx + 150, cy + 75, fill="#020617", outline="#e2e8f0", width=2)
            title = "GAME CLEAR!" if self.game_cleared else "GAME OVER"
            t_col = "#eab308" if self.game_cleared else "#ef4444"
            msg = "모든 칸을 채웠습니다!" if self.game_cleared else self.end_reason
            self.canvas.create_text(cx, cy - 42, text=title, font=("Helvetica", 16, "bold"), fill=t_col)
            self.canvas.create_text(cx, cy - 18, text=msg, font=("Helvetica", 10), fill="#cbd5e1")
            self.canvas.create_text(cx, cy + 5, text=f"점수: {self.score} (길이: {len(self.snake)})", font=("Helvetica", 10), fill="#f8fafc")
            ov_f = tk.Frame(self.canvas, bg="#020617")
            tk.Button(ov_f, text="재도전 (R)", font=("Helvetica", 9, "bold"), bg="#22c55e", fg="black", command=self.restart_game).pack(side="left", padx=4)
            tk.Button(ov_f, text="설정 (ESC)", font=("Helvetica", 9), bg="#475569", fg="black", command=self.build_setup_view).pack(side="left", padx=4)
            self.canvas.create_window(cx, cy + 45, window=ov_f)

    def on_close(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
