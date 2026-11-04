import collections, os, random, threading
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY", "cb_skku-assignment_e12ae4a3c82f71acb5e8ddb0e3184d67"); API_URL = os.getenv("API_URL", "https://api.example.com/ranking")
HEADERS = {"x-api-key": API_KEY, "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("스네이크 게임"); self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close); self.timer_id = None
        self.grid_var, self.speed_var, self.name_var = tk.StringVar(value="10"), tk.IntVar(value=180), tk.StringVar(value="신성하")
        self.rankings, self.rank_status, self.post_status = [], "조회 대기 중", ""
        self.main_container = tk.Frame(root, bg="#0f172a"); self.main_container.pack(fill="both", expand=True)
        self.fetch_rankings(); self.build_setup_view()
        self.root.bind("<Key>", self.on_key)

    def fetch_rankings(self):
        def _get():
            try:
                r = requests.get(API_URL, headers=HEADERS, timeout=3)
                d = r.json() if r.ok else []
                if isinstance(d, dict):
                    for k in ("ranking", "rankings", "data", "scores", "result"):
                        if k in d and isinstance(d[k], list): d = d[k]; break
                items = [{"name": str(x.get("name") or x.get("player") or x.get("nickname") or "익명"), "score": int(x.get("score", 0))} for x in d if isinstance(x, dict)]
                self.rankings = sorted(items, key=lambda x: x["score"], reverse=True)[:10]
                self.rank_status = f"갱신 완료 ({len(self.rankings)}명)" if r.ok else f"오류 ({r.status_code})"
            except Exception: self.rank_status = "서버 연결 불가"
            self.root.after(0, self.update_ranking_ui)
        self.rank_status = "조회 중..."; self.update_ranking_ui()
        threading.Thread(target=_get, daemon=True).start()

    def post_score(self):
        name = self.name_var.get().strip() or "Player"
        self.post_status = "점수 등록 중..."
        def _post():
            try:
                r = requests.post(API_URL, json={"name": name, "score": self.score}, headers=HEADERS, timeout=3)
                self.post_status = "점수 등록 완료!" if r.ok else f"등록 실패 ({r.status_code})"
            except Exception: self.post_status = "서버 연결 실패"
            self.fetch_rankings(); self.root.after(0, self.draw)
        threading.Thread(target=_post, daemon=True).start()

    def build_setup_view(self):
        self.clear_container()
        wrap = tk.Frame(self.main_container, bg="#0f172a", padx=16, pady=16); wrap.pack(expand=True)
        left = tk.Frame(wrap, bg="#0f172a", padx=6); left.pack(side="left", fill="y")
        tk.Label(left, text="🐍 SNAKE GAME", font=("Helvetica", 18, "bold"), fg="#38bdf8", bg="#0f172a").pack(pady=4)
        nf = tk.Frame(left, bg="#0f172a"); nf.pack(pady=4)
        tk.Label(nf, text="플레이어: ", font=("Helvetica", 11), fg="#cbd5e1", bg="#0f172a").pack(side="left")
        tk.Entry(nf, textvariable=self.name_var, width=10, font=("Helvetica", 11)).pack(side="left")
        row = tk.Frame(left, bg="#0f172a"); row.pack(pady=4)
        tk.Label(row, text="격자 크기: ", font=("Helvetica", 11), fg="#f8fafc", bg="#0f172a").pack(side="left")
        tk.Spinbox(row, from_=3, to=10, textvariable=self.grid_var, width=5, font=("Helvetica", 11), justify="center").pack(side="left", padx=4)
        bf = tk.Frame(left, bg="#0f172a"); bf.pack(pady=2)
        for s in (3, 5, 8, 10): tk.Button(bf, text=f"{s}×{s}", font=("Helvetica", 9), command=lambda v=s: self.grid_var.set(str(v))).pack(side="left", padx=2)
        sf = tk.Frame(left, bg="#0f172a"); sf.pack(pady=4)
        tk.Label(sf, text="속도: ", font=("Helvetica", 10), fg="#cbd5e1", bg="#0f172a").pack(side="left")
        for lbl, ms in [("느림", 250), ("보통", 180), ("빠름", 120)]:
            tk.Radiobutton(sf, text=lbl, value=ms, variable=self.speed_var, font=("Helvetica", 9), bg="#0f172a", fg="#f8fafc", selectcolor="#1e293b").pack(side="left")
        tk.Button(left, text="게임 시작", font=("Helvetica", 12, "bold"), bg="#22c55e", fg="black", padx=16, pady=4, command=self.start_game).pack(pady=8)
        tk.Label(left, text="이동: 방향키 / WASD\n재시작: R  |  설정: ESC", font=("Helvetica", 9), fg="#94a3b8", bg="#0f172a", justify="center").pack()

        right = tk.Frame(wrap, bg="#1e293b", padx=12, pady=10, relief="groove", bd=1); right.pack(side="left", padx=12, fill="both")
        rf = tk.Frame(right, bg="#1e293b"); rf.pack(fill="x")
        tk.Label(rf, text="🏆 랭킹보드 (TOP 10)", font=("Helvetica", 11, "bold"), fg="#facc15", bg="#1e293b").pack(side="left")
        tk.Button(rf, text="🔄", font=("Helvetica", 8), command=self.fetch_rankings).pack(side="right")
        self.lbl_rank_status = tk.Label(right, text=self.rank_status, font=("Helvetica", 8), fg="#94a3b8", bg="#1e293b"); self.lbl_rank_status.pack(pady=2)
        self.rank_box = tk.Frame(right, bg="#1e293b"); self.rank_box.pack(fill="both", expand=True)
        self.update_ranking_ui()

    def update_ranking_ui(self):
        if not hasattr(self, "rank_box") or not self.rank_box.winfo_exists(): return
        self.lbl_rank_status.config(text=self.rank_status)
        for w in self.rank_box.winfo_children(): w.destroy()
        if not self.rankings:
            tk.Label(self.rank_box, text="(랭킹 데이터 없음)", font=("Helvetica", 9), fg="#64748b", bg="#1e293b", pady=25).pack(); return
        for i, item in enumerate(self.rankings[:10], 1):
            nm, sc = str(item.get("name", "익명"))[:7], item.get("score", 0)
            col = "#facc15" if i == 1 else "#94a3b8" if i <= 3 else "#cbd5e1"
            tk.Label(self.rank_box, text=f"{i:>2}. {nm:<7} {sc:>4}점", font=("Courier", 9, "bold" if i <= 3 else "normal"), fg=col, bg="#1e293b", anchor="w").pack(fill="x")

    def clear_container(self):
        if self.timer_id: self.root.after_cancel(self.timer_id); self.timer_id = None
        for w in self.main_container.winfo_children(): w.destroy()

    def start_game(self):
        try:
            sz = int(self.grid_var.get().strip())
            if not (3 <= sz <= 10): raise ValueError
        except ValueError:
            messagebox.showerror("입력 오류", "격자 크기는 3 이상 10 이하의 정수여야 합니다."); return
        self.grid_size, self.cell_size = sz, 420 // sz
        self.board_px = self.grid_size * self.cell_size
        self.init_game_state(); self.build_game_view()
        self.timer_id = self.root.after(self.speed_var.get(), self.run_tick)

    def init_game_state(self):
        mx, my = self.grid_size // 2, self.grid_size // 2
        self.snake = collections.deque([(mx - i, my) for i in range(2 if self.grid_size <= 3 else 3)])
        self.snake_set, self.direction = set(self.snake), (1, 0)
        self.current_direction, self.score = (1, 0), 0
        self.game_over, self.game_cleared, self.end_reason = False, False, ""
        self.score_posted, self.apple = False, self.spawn_apple()

    def spawn_apple(self):
        empty = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size) if (x, y) not in self.snake_set]
        return random.choice(empty) if empty else None

    def build_game_view(self):
        self.clear_container()
        top = tk.Frame(self.main_container, bg="#1e293b", padx=10, pady=8); top.pack(fill="x")
        tot = self.grid_size * self.grid_size
        pname = self.name_var.get().strip() or "Player"
        self.lbl_score = tk.Label(top, text=f"{pname} | 점수: 0 | 길이: {len(self.snake)}/{tot}", font=("Helvetica", 10, "bold"), fg="#38bdf8", bg="#1e293b")
        self.lbl_score.pack(side="left")
        tk.Button(top, text="설정(ESC)", font=("Helvetica", 9), command=self.build_setup_view).pack(side="right", padx=4)
        tk.Button(top, text="재시작(R)", font=("Helvetica", 9), command=self.restart_game).pack(side="right", padx=4)
        self.canvas = tk.Canvas(self.main_container, width=self.board_px, height=self.board_px, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10); self.draw()

    def on_key(self, event):
        k, dirs = event.keysym, {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0), "w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        k = k.lower() if len(k) == 1 else k
        if k in dirs:
            ndx, ndy = dirs[k]; cdx, cdy = self.current_direction
            if (ndx + cdx != 0 or ndy + cdy != 0) and (ndx, ndy) != (cdx, cdy): self.direction = (ndx, ndy)
        elif k in ("r", "R") and hasattr(self, "grid_size"): self.restart_game()
        elif k == "Escape": self.build_setup_view()

    def restart_game(self):
        if self.timer_id: self.root.after_cancel(self.timer_id); self.timer_id = None
        self.init_game_state(); self.draw()
        self.timer_id = self.root.after(self.speed_var.get(), self.run_tick)

    def run_tick(self):
        if self.game_over or self.game_cleared: return
        self.step(); self.draw()
        if not (self.game_over or self.game_cleared): self.timer_id = self.root.after(self.speed_var.get(), self.run_tick)

    def step(self):
        self.current_direction = self.direction
        hx, hy = self.snake[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]
        if not (0 <= nx < self.grid_size and 0 <= ny < self.grid_size):
            self.game_over, self.end_reason = True, "벽에 부딪혔습니다!"; return
        if (nx, ny) == self.apple:
            self.snake.appendleft((nx, ny)); self.snake_set.add((nx, ny)); self.score += 1
            if len(self.snake) == self.grid_size * self.grid_size: self.game_cleared = True
            else: self.apple = self.spawn_apple()
        else:
            tail = self.snake.pop(); self.snake_set.remove(tail)
            if (nx, ny) in self.snake_set:
                self.snake.append(tail); self.game_over, self.end_reason = True, "자신의 몸에 부딪혔습니다!"; return
            self.snake.appendleft((nx, ny)); self.snake_set.add((nx, ny))

    def draw(self):
        self.canvas.delete("all")
        cs = self.cell_size
        for i in range(self.grid_size + 1):
            p = i * cs
            self.canvas.create_line(p, 0, p, self.board_px, fill="#1e293b")
            self.canvas.create_line(0, p, self.board_px, p, fill="#1e293b")
        if self.apple:
            ax, ay = self.apple
            self.canvas.create_oval(ax*cs+2, ay*cs+2, (ax+1)*cs-2, (ay+1)*cs-2, fill="#ef4444", outline="#f87171")
        for idx, (sx, sy) in enumerate(self.snake):
            self.canvas.create_rectangle(sx*cs+1, sy*cs+1, (sx+1)*cs-1, (sy+1)*cs-1, fill="#16a34a" if idx == 0 else "#22c55e", outline="")
        tot = self.grid_size * self.grid_size
        pname = self.name_var.get().strip() or "Player"
        self.lbl_score.config(text=f"{pname} | 점수: {self.score} | 길이: {len(self.snake)}/{tot}")
        if self.game_over or self.game_cleared:
            if not self.score_posted:
                self.score_posted = True; self.post_score()
            cx, cy = self.board_px // 2, self.board_px // 2
            self.canvas.create_rectangle(cx - 160, cy - 90, cx + 160, cy + 90, fill="#020617", outline="#e2e8f0", width=2)
            title, col = ("GAME CLEAR!", "#eab308") if self.game_cleared else ("GAME OVER", "#ef4444")
            msg = "모든 칸을 채웠습니다!" if self.game_cleared else self.end_reason
            self.canvas.create_text(cx, cy - 58, text=title, font=("Helvetica", 15, "bold"), fill=col)
            self.canvas.create_text(cx, cy - 35, text=msg, font=("Helvetica", 10), fill="#cbd5e1")
            self.canvas.create_text(cx, cy - 12, text=f"점수: {self.score} (길이: {len(self.snake)})", font=("Helvetica", 10, "bold"), fill="#f8fafc")
            self.canvas.create_text(cx, cy + 12, text=f"📡 {self.post_status}", font=("Helvetica", 9), fill="#38bdf8")
            ov_f = tk.Frame(self.canvas, bg="#020617")
            tk.Button(ov_f, text="재도전 (R)", font=("Helvetica", 9, "bold"), bg="#22c55e", fg="black", command=self.restart_game).pack(side="left", padx=3)
            tk.Button(ov_f, text="설정/랭킹 (ESC)", font=("Helvetica", 9), bg="#475569", fg="black", command=self.build_setup_view).pack(side="left", padx=3)
            self.canvas.create_window(cx, cy + 55, window=ov_f)

    def on_close(self):
        if self.timer_id: self.root.after_cancel(self.timer_id)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); SnakeGame(root); root.mainloop()
