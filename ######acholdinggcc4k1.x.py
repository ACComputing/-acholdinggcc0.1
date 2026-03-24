"""A.C Holdings gcc 0.1 — Our Own Compiler (lexer)
Built together. Real lexer added. /pr and /files=off respected."""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import sys
import io
import contextlib

def manifest_md_path():
    return os.path.splitext(os.path.abspath(__file__))[0] + ".md"

# ====================== REAL LEXER ======================
class Lexer:
    KEYWORDS = {
        'int', 'void', 'main', 'if', 'else', 'while', 'for', 'return',
        'char', 'float', 'double', 'long', 'short', 'unsigned', 'signed'
    }

    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []

    def peek(self):
        return self.code[self.pos] if self.pos < len(self.code) else '\0'

    def advance(self):
        ch = self.peek()
        if ch == '\n':
            self.line += 1
        self.pos += 1
        return ch

    def skip_whitespace(self):
        while self.peek().isspace():
            self.advance()

    def skip_comment(self):
        if self.peek() == '/':
            self.advance()
            if self.peek() == '/':          # // comment
                while self.peek() not in '\0\n':
                    self.advance()
            elif self.peek() == '*':        # /* comment */
                self.advance()
                while True:
                    if self.peek() == '*' and self.code[self.pos+1:self.pos+2] == '/':
                        self.advance()
                        self.advance()
                        break
                    if self.peek() == '\0':
                        break
                    self.advance()

    def read_number(self):
        start = self.pos
        while self.peek().isdigit() or self.peek() == '.':
            self.advance()
        return self.code[start:self.pos]

    def read_identifier(self):
        start = self.pos
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        return self.code[start:self.pos]

    def read_string(self):
        self.advance()  # skip opening "
        start = self.pos
        while self.peek() != '"' and self.peek() != '\0':
            self.advance()
        value = self.code[start:self.pos]
        self.advance()  # skip closing "
        return value

    def tokenize(self):
        while self.pos < len(self.code):
            self.skip_whitespace()
            ch = self.peek()

            if ch == '\0':
                break
            if ch == '/' and (self.code[self.pos+1:self.pos+2] in ('/', '*')):
                self.skip_comment()
                continue

            # Numbers
            if ch.isdigit() or (ch == '.' and self.code[self.pos+1:self.pos+2].isdigit()):
                num = self.read_number()
                self.tokens.append(('NUMBER', num))
                continue

            # Identifiers & Keywords
            if ch.isalpha() or ch == '_':
                ident = self.read_identifier()
                token_type = 'KEYWORD' if ident in self.KEYWORDS else 'IDENTIFIER'
                self.tokens.append((token_type, ident))
                continue

            # Strings
            if ch == '"':
                s = self.read_string()
                self.tokens.append(('STRING', s))
                continue

            # Single-character tokens
            if ch in '(){};,+-*/=!<>':
                self.tokens.append((ch, ch))
                self.advance()
                continue

            # Two-character operators
            if ch == '=' and self.peek() == '=':
                self.tokens.append(('==', '=='))
                self.advance()
                self.advance()
                continue
            if ch == '!' and self.peek() == '=':
                self.tokens.append(('!=', '!='))
                self.advance()
                self.advance()
                continue

            # Unknown character
            self.tokens.append(('ERROR', ch))
            self.advance()

        self.tokens.append(('EOF', 'EOF'))
        return self.tokens


class ACCompiler:
    def __init__(self, log_callback):
        self.log = log_callback
        self.version = "A.C Holdings gcc 0.1"

    def log_manifest(self):
        self.log(">> /pr — PROJECT MANIFEST\n")
        try:
            with open(manifest_md_path(), encoding="utf-8") as f:
                self.log(f.read().rstrip())
            self.log("\n" + "-" * 80)
        except Exception:
            self.log("(No manifest .md found)")

    def compile(self, source_code, output_dir, filename, files_off=False, pr=False, run_after=False):
        self.log(f"{self.version} $ Starting OUR compiler...")

        if pr:
            self.log_manifest()

        # === LEXER STAGE ===
        self.log("→ Running Lexer...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        if pr:
            self.log("=== LEXER OUTPUT (TOKENS) ===")
            for t in tokens:
                self.log(f"  {t}")
            self.log("============================")

        # TODO: Next stage will be Parser
        self.log("→ Lexer complete. Parser stage coming next...")

        # Temporary placeholder so GUI still runs
        if files_off:
            self.log("\n>> /files=off → In-memory execution (placeholder)")
            self.log("\n==== PROGRAM OUTPUT ====")
            self.log("(Lexer stage passed — real execution coming soon)")
            self.log("========================")
            return None
        else:
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ('.exe' if sys.platform == 'win32' else ''))
            self.log(f"→ Would create real binary: {output_path}")
            return output_path


# ====================== GUI (your exact style) ======================
class ACCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A.C Holdings gcc 0.1")
        self.root.geometry("740x600")
        self.root.configure(bg="#0c0c0c")

        self.files_off = tk.BooleanVar(value=True)
        self.pr = tk.BooleanVar(value=True)
        self.run_after = tk.BooleanVar(value=True)

        self.source_file = ""
        self.engine = ACCompiler(self.log_output)

        main = tk.Frame(root, bg="#0c0c0c")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Label(main, text="A.C Holdings gcc 0.1", 
                 bg="#0c0c0c", fg="#00ff00", font=("Consolas", 15, "bold")).pack(pady=8)
        tk.Label(main, text="the only gcc alternative !", 
                 bg="#0c0c0c", fg="#ffcc00").pack()

        # File selector
        ctrl = tk.Frame(main, bg="#1e1e1e", relief="groove", bd=2)
        ctrl.pack(fill=tk.X, pady=12)
        tk.Label(ctrl, text="Source .c:", bg="#1e1e1e", fg="#ddd").grid(row=0, column=0, padx=12, pady=10)
        self.lbl_file = tk.Label(ctrl, text="No file selected...", bg="#1e1e1e", fg="#aaa", width=55, anchor="w")
        self.lbl_file.grid(row=0, column=1, padx=8)
        tk.Button(ctrl, text="Browse", command=self.browse, bg="#333", fg="white").grid(row=0, column=2, padx=8)

        # Flags
        opts = tk.Frame(main, bg="#0c0c0c")
        opts.pack(fill=tk.X, pady=10)
        tk.Checkbutton(opts, text="/files=off", variable=self.files_off, bg="#0c0c0c", fg="#ddd").pack(side=tk.LEFT, padx=20)
        tk.Checkbutton(opts, text="/pr (show manifest + tokens)", variable=self.pr, bg="#0c0c0c", fg="#ddd").pack(side=tk.LEFT, padx=20)
        tk.Checkbutton(opts, text="Run after compile", variable=self.run_after, bg="#0c0c0c", fg="#ddd").pack(side=tk.LEFT, padx=20)

        tk.Button(main, text="COMPILE", command=self.run_compilation,
                  bg="#0066ff", fg="white", font=("Consolas", 14, "bold"), height=2).pack(fill=tk.X, pady=20)

        self.terminal = scrolledtext.ScrolledText(main, bg="black", fg="#00ff88", font=("Consolas", 10))
        self.terminal.pack(fill=tk.BOTH, expand=True)

        self.log_output("A.C Holdings gcc 0.1 — lexer stage loaded")
        self.log_output("Type any .c file and press compile with /pr on to see tokens")

    def log_output(self, msg):
        self.terminal.insert(tk.END, msg + "\n")
        self.terminal.see(tk.END)

    def browse(self):
        f = filedialog.askopenfilename(filetypes=[("C files", "*.c")])
        if f:
            self.source_file = f
            self.lbl_file.config(text=os.path.basename(f), fg="white")
            self.log_output(f"Loaded: {os.path.basename(f)}")

    def run_compilation(self):
        if not self.source_file:
            messagebox.showwarning("Error", "Select a .c file first!")
            return

        with open(self.source_file, encoding='utf-8', errors='replace') as f:
            code = f.read()

        self.log_output("-" * 90)
        self.engine.compile(
            code,
            os.path.dirname(self.source_file),
            os.path.basename(self.source_file),
            files_off=self.files_off.get(),
            pr=self.pr.get(),
            run_after=self.run_after.get()
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = ACCompilerApp(root)
    root.mainloop()
