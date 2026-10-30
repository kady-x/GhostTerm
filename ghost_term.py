#!/usr/bin/env python3
"""
👻 GhostTerm (NecroShell) - The Haunted Developer Companion
Hacktoberfest DEV Challenge Week 4: "Ghost in the Machine"

An eerie, local-first CLI assistant that analyzes developer commands,
grave-yard git histories, and fatal stack traces using Google DeepMind's
Gemma 2 open-weight model (via Ollama) with an offline spectral grimoire fallback.
"""

import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Ensure UTF-8 output encoding across Windows consoles and platforms
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
from rich.box import DOUBLE, ROUNDED, SIMPLE
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ---------------------------------------------------------------------------
# Spooky Color Palette & Constants
# ---------------------------------------------------------------------------
CYAN = "#00f0ff"
PURPLE = "#bd93f9"
DIM_PURPLE = "#70539c"
ORANGE = "#ffb86c"
BLOOD = "#ff5555"
GREEN = "#50fa7b"
DIM = "#6272a4"
TOMB = "#f8f8f2"
GOLD = "#f1fa8c"

GHOST_THEME = Theme({
    "cyan_ghost": CYAN,
    "purple_ghost": PURPLE,
    "blood_ghost": BLOOD,
    "green_ghost": GREEN,
    "dim_ghost": DIM,
    "tomb_ghost": TOMB,
    "gold_ghost": GOLD,
})

console = Console(theme=GHOST_THEME)

# ---------------------------------------------------------------------------
# Spooky ASCII Art & Banners
# ---------------------------------------------------------------------------
GHOST_BANNER = rf"""[{PURPLE}]
     .-.
    (o o)       [bold {CYAN}]G H O S T T E R M[/bold {CYAN}]
    | O \       [{DIM}]The Spirit in the Machine[/{DIM}]
     \   \      [dim {PURPLE}]Hacktoberfest 2026 • DEV Challenge Week 4[/dim {PURPLE}]
      `~~~'     [{BLOOD}]Local Gemma 2 Necromancy Engine[/{BLOOD}]
[/{PURPLE}]"""

TOMBSTONE_ART = rf"""[{DIM}]
          _______
         /  R.I.P \
        /  EXIT {{code}} \
       |-----------|
       |  DECEASED |
       |  PROCESS  |
       |___________|
[/{DIM}]"""

GRAVEYARD_ART = rf"""[{DIM_PURPLE}]
     +       _     +           _         +
    / \     / \   / \         / \       / \
   | R |   | I | | P |       | D |     | E |
   | O |   | S | | R |       | E |     | B |
   | T |   | S | | O |       | A |     | T |
   |___|   |___| |___|       | D |     |___|
   ///////////////////       |___|     /////
[/{DIM_PURPLE}]"""

# Default Model & Ollama Endpoint
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("GHOST_MODEL", "gemma2:2b")


# ---------------------------------------------------------------------------
# Fallback Spectral Grimoire (Offline Heuristic Engine)
# ---------------------------------------------------------------------------
class EldritchGrimoire:
    """Pre-tuned spooky heuristics & knowledge base when Ollama is offline."""

    ERROR_PATTERNS = [
        (
            r"SyntaxError: (.+)",
            "The ancient grammatical laws were shattered",
            "A mortal glyph was placed where forbidden void belongs. The parser choked upon your syntax heresy.",
            "Inspect the runes directly prior to line {line}. A missing colon, forgotten paren, or mismatched quote summons this demon.",
        ),
        (
            r"IndentationError: (.+)",
            "The sacred tabernacle of whitespace is misaligned",
            "Tab characters and wandering space entities have formed an unholy ritual of uneven depths.",
            "Standardize your spacing incantations. Use 4 spaces universally and purge invisible carriage ghosts.",
        ),
        (
            r"TypeError: 'NoneType' object is not (.+)",
            "You reached into the abyss, and the abyss held nothing",
            "A pointer sought life in the empty ethereal plane. A phantom function returned void where flesh was anticipated.",
            "Guaranty your variables exist before summoning their attributes: add `if obj is not None:` or default coalesce.",
        ),
        (
            r"ModuleNotFoundError: No module named '(.+?)'",
            "An invoked spirit failed to manifest from the astral registry",
            "The dependency exists solely in dreams and undocumented cache graveyards.",
            "Cast the summon spell: `pip install {match}` or inspect your virtual environment crypt.",
        ),
        (
            r"KeyError: (.+)",
            "A tomb was unlocked, but the relic was stolen",
            "The dictionary key was sought across empty halls. The spectral key does not reside in this mapping.",
            "Consult with `.get({match}, default)` or divine key existence using `if {match} in dict:`.",
        ),
        (
            r"IndexError: (.+)",
            "You stepped off the precipice of memory",
            "An array index ventured beyond the sacred bounds into cold, unallocated purgatory.",
            "Guard your borders: verify `len(sequence)` before reaching into indices of the void.",
        ),
        (
            r"RecursionError: maximum recursion depth exceeded",
            "The Ouroboros has consumed its own tail in eternity",
            "A function called itself without an escape ward, plunging the stack into an endless spiral of reincarnation.",
            "Carve a termination condition (base case) into the stone, or convert the recursive summoning into an iterative loop.",
        ),
        (
            r"Segmentation fault|SIGSEGV|core dumped",
            "The memory curtain was violently torn asunder",
            "A rogue pointer wandered into forbidden memory sanctums guarded by the operating system kernel.",
            "Examine dangling pointers, buffer overflows, double-frees, or uninitialized C-structs.",
        ),
        (
            r"ConnectionRefusedError|ECONNREFUSED|connect ECONNREFUSED (.+)",
            "The portal stands shuttered, cold, and dead",
            "You knocked on the network crypt gate, but no daemon answered from the nether realms.",
            "Ensure the destination daemon or service is awakened on that port, and no firewall ward blocks passage.",
        ),
        (
            r"git.*(CONFLICT|Merge conflict in (.+))",
            "Two parallel timelines collided and ruptured reality",
            "Mortals edited the same scroll across divergent dimensions. Git refuses to seal the rift automatically.",
            "Search for the sacred boundary markers `<<<<<<<`, `=======`, and `>>>>>>>`. Unify the realities manually.",
        ),
        (
            r"FileNotFoundError: \[Errno 2\] No such file or directory: '(.+?)'",
            "A parchment mentioned in prophecies has vanished from disk",
            "The file path is but a legend whispered by phantom configurations.",
            "Check relative working directory paths or summon the file into existence with `touch {match}`.",
        ),
        (
            r"ZeroDivisionError: (.+)",
            "The singularity opens: dividing by pure nothingness",
            "Mathematics collapsed when an equation attempted to partition reality by zero.",
            "Add a protective talisman: `if divisor != 0:` to prevent catastrophic collapse.",
        ),
    ]

    @classmethod
    def diagnose_error(cls, error_log: str) -> Dict[str, str]:
        """Pattern matches fatal error output to produce spectral diagnoses."""
        for pattern, curse_title, autopsy, exorcism in cls.ERROR_PATTERNS:
            match = re.search(pattern, error_log, re.IGNORECASE)
            if match:
                matched_group = match.group(1) if match.groups() else ""
                line_match = re.search(r"line (\d+)", error_log, re.IGNORECASE)
                line_no = line_match.group(1) if line_match else "unknown"

                return {
                    "title": curse_title,
                    "autopsy": autopsy.replace("{match}", matched_group).replace("{line}", line_no),
                    "exorcism": exorcism.replace("{match}", matched_group).replace("{line}", line_no),
                    "source": "Eldritch Grimoire (Offline Heuristic Engine)",
                }

        last_lines = [line.strip() for line in error_log.strip().splitlines() if line.strip()]
        last_line = last_lines[-1] if last_lines else "Unknown silent demise"

        return {
            "title": "A malevolent presence extinguished this execution",
            "autopsy": f"The process expired with ominous whispers: '{last_line[:120]}...'. Its life force severed before reaching the final return statement.",
            "exorcism": "Examine the final frames of the stack trace above. Ensure input variables contain valid essence and permissions are sanctified.",
            "source": "Eldritch Grimoire (Offline Heuristic Engine)",
        }

    @classmethod
    def general_oracle(cls, query: str) -> str:
        """Fallback spectral oracle for seance questions when Gemma 2 is sleeping."""
        q = query.lower()
        if "segfault" in q or "memory" in q:
            return (
                "The ghost whispers: *'Ah, memory corruption... the oldest phantom in computing. "
                "Check for use-after-free or array overruns. The kernel had no choice but to strike "
                "your process down with SIGSEGV to protect the mortal plane.'*"
            )
        elif "git" in q or "merge" in q or "conflict" in q:
            return (
                "The ghost whispers: *'Git tracks the ghosts of commits long buried. When branches collide, "
                "fear not the conflict markers `<<<<<<<` and `>>>>>>>`. They are mere sutures across time. "
                "Choose which timeline survives, then commit the peace treaty.'*"
            )
        elif "test" in q or "bug" in q:
            return (
                "The ghost whispers: *'You speak of bugs, but in truth they are poltergeists of skipped tests. "
                "Write an assertion where the failure occurs. Drag the invisible demon into the light of stdout.'*"
            )
        elif "deploy" in q or "production" in q:
            return (
                "The ghost whispers: *'It worked on your machine? Aye, but production is a consecrated graveyard "
                "with different environment variables, strict ports, and absent permissions. Check your `.env` "
                "and container permissions before midnight.'*"
            )
        else:
            return (
                f"The ghost stirs within the silicon: *'I hear your query regarding \"{query[:40]}\"... "
                "The spirits advise: simplify the architecture, cast away dead abstractions, "
                "and let logs illuminate the darkest pathways of your codebase.'*"
            )


# ---------------------------------------------------------------------------
# Gemma 2 / Ollama Spectral Engine
# ---------------------------------------------------------------------------
class SpectralEngine:
    """Interfaces with local Gemma 2 via Ollama, falling back gracefully."""

    def __init__(self, model: str = DEFAULT_MODEL, host: str = DEFAULT_OLLAMA_URL):
        self.model = model
        self.host = host.rstrip("/")
        self._is_online: Optional[bool] = None

    def check_connection(self) -> bool:
        """Checks if local Ollama daemon is reachable with minimal latency."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                self._is_online = True
                return True
        except Exception:
            pass
        self._is_online = False
        return False

    def query(self, prompt: str, system_prompt: Optional[str] = None) -> Tuple[str, str]:
        """
        Sends prompt to Gemma 2. Returns (response_text, provider_name).
        Gracefully falls back to EldritchGrimoire if Ollama is unreachable.
        """
        if self._is_online is None:
            self.check_connection()

        if self._is_online:
            default_system = (
                "You are GhostTerm, an eerie yet hyper-competent Victorian/eldritch compiler spirit "
                "trapped inside the developer's terminal. You speak with dark, atmospheric gothic wit, "
                "using ghostly metaphors, but you always deliver pinpoint, accurate, actionable technical solutions. "
                "Keep responses concise, punchy, and atmospheric. Never ramble."
            )
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt or default_system,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 350,
                },
            }
            try:
                resp = requests.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "").strip()
                    if response_text:
                        return response_text, f"Gemma 2 ({self.model} via Ollama)"
            except Exception:
                pass

        # Fallback to offline grimoire
        return EldritchGrimoire.general_oracle(prompt), "Eldritch Grimoire (Offline Engine)"

    def autopsy_error(self, cmd: str, returncode: int, error_output: str) -> Dict[str, str]:
        """Generates an eerie autopsy report of a crashed command."""
        if self._is_online is None:
            self.check_connection()

        if self._is_online:
            prompt = (
                f"A developer command just perished with exit code {returncode}.\n"
                f"Command: `{cmd}`\n"
                f"Fatal Output:\n```\n{error_output[-800:]}\n```\n\n"
                "Provide an eerie, haunted developer autopsy in 3 short sections:\n"
                "1. Curse Title: A spooky poetic title for this death.\n"
                "2. Autopsy: What killed the process in spectral gothic terms.\n"
                "3. Exorcism: The exact technical fix or command to resurrect it.\n"
                "Format strictly with headings: '### Title:', '### Autopsy:', '### Exorcism:'"
            )
            try:
                resp_text, provider = self.query(prompt)
                if "### Title:" in resp_text and "### Autopsy:" in resp_text:
                    parts = resp_text.split("###")
                    title = "The Process Succumbed"
                    autopsy = ""
                    exorcism = ""
                    for p in parts:
                        if p.strip().startswith("Title:"):
                            title = p.replace("Title:", "").strip()
                        elif p.strip().startswith("Autopsy:"):
                            autopsy = p.replace("Autopsy:", "").strip()
                        elif p.strip().startswith("Exorcism:"):
                            exorcism = p.replace("Exorcism:", "").strip()
                    if autopsy:
                        return {
                            "title": title,
                            "autopsy": autopsy,
                            "exorcism": exorcism or "Inspect parameters and re-summon the binary.",
                            "source": provider,
                        }
            except Exception:
                pass

        return EldritchGrimoire.diagnose_error(error_output)


# ---------------------------------------------------------------------------
# Feature 1: Haunt - Command Execution & Process Autopsy
# ---------------------------------------------------------------------------
def run_haunted_command(command_parts: List[str], engine: SpectralEngine):
    """Executes a developer command, capturing its life and performing an autopsy on death."""
    if not command_parts:
        console.print(f"[{ORANGE}]⚠ No command provided to haunt. Example: `ghost_term haunt python app.py`[/{ORANGE}]")
        return

    full_cmd = " ".join(command_parts)
    console.print(Panel(
        f"[{PURPLE}]👁 Possessing command:[/{PURPLE}] [bold {CYAN}]{full_cmd}[/bold {CYAN}]\n"
        f"[{DIM}]Spirits watch the standard descriptors...[/{DIM}]",
        box=ROUNDED,
        border_style=PURPLE,
        title=f"[bold {CYAN}]💀 GHOSTTERMD ACTIVE[/bold {CYAN}]",
    ))

    start_time = time.time()
    try:
        proc = subprocess.Popen(
            full_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout, stderr = proc.communicate()
        elapsed = time.time() - start_time
    except Exception as e:
        stdout, stderr = "", str(e)
        proc = subprocess.CompletedProcess(args=full_cmd, returncode=1)
        elapsed = time.time() - start_time

    if stdout:
        console.print(stdout.rstrip())
    if stderr:
        console.print(f"[{DIM}]{stderr.rstrip()}[/{DIM}]")

    if proc.returncode == 0:
        console.print()
        console.print(Panel(
            f"[{GREEN}]✦ The command completed intact in {elapsed:.2f}s.[/{GREEN}]\n"
            f"[{DIM}]The spirits withdraw into the silicon... for now. No blood was spilled.[/{DIM}]",
            box=ROUNDED,
            border_style=GREEN,
            title=f"[bold {GREEN}]🕯 SPECTRAL BENEDICTION[/bold {GREEN}]",
        ))
    else:
        console.print()
        tombstone = TOMBSTONE_ART.format(code=proc.returncode)
        console.print(tombstone)

        error_context = stderr if stderr.strip() else stdout
        with Progress(
            SpinnerColumn("bouncingBar", style=PURPLE),
            TextColumn(f"[{PURPLE}]Communing with the spirit world for diagnostic autopsy...[/{PURPLE}]"),
            transient=True,
        ) as progress:
            progress.add_task("autopsy", total=None)
            diagnosis = engine.autopsy_error(full_cmd, proc.returncode, error_context)

        autopsy_content = Text()
        autopsy_content.append(f"💀 Fatal Anomaly: ", style=f"bold {BLOOD}")
        autopsy_content.append(f"{diagnosis['title']}\n\n", style=f"bold {TOMB}")

        autopsy_content.append("📜 Post-Mortem Forensic:\n", style=f"bold {PURPLE}")
        autopsy_content.append(f"{diagnosis['autopsy']}\n\n", style=TOMB)

        autopsy_content.append("🔮 Exorcism & Resurrection:\n", style=f"bold {CYAN}")
        autopsy_content.append(f"{diagnosis['exorcism']}\n\n", style=f"bold {GREEN}")

        autopsy_content.append(f"✦ Channel: {diagnosis['source']}", style=f"dim {DIM}")

        console.print(Panel(
            autopsy_content,
            box=DOUBLE,
            border_style=BLOOD,
            title=f"[bold {BLOOD}]☠ POST-MORTEM AUTOPSY ☠[/bold {BLOOD}]",
            subtitle=f"[{DIM}]Exit Code {proc.returncode} • Duration {elapsed:.2f}s[/{DIM}]",
        ))


# ---------------------------------------------------------------------------
# Feature 2: Exhume - Git Graveyard & Broken Commit Forensic
# ---------------------------------------------------------------------------
def exhume_git_graveyard(limit: int, engine: SpectralEngine):
    """Exhumes recent commits, witching hour commits, and abandoned changes."""
    console.print(GRAVEYARD_ART)
    console.print(Panel(
        f"[{PURPLE}]Digging into repository crypts (last {limit} commits)...[/{PURPLE}]",
        box=ROUNDED,
        border_style=DIM_PURPLE,
        title=f"[bold {CYAN}]⚰ EXHUMING THE GIT GRAVEYARD[/bold {CYAN}]",
    ))

    try:
        git_log_cmd = f"git log -n {limit} --pretty=format:\"%h|%an|%ad|%s\" --date=format:\"%Y-%m-%d %H:%M\""
        log_res = subprocess.run(
            git_log_cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if log_res.returncode != 0:
            if "does not have any commits" in log_res.stderr or "fatal: your current branch" in log_res.stderr:
                console.print(Panel(
                    f"[{TOMB}]The cemetery grounds are fresh and newly consecrated. No commits have been interred yet.[/{TOMB}]\n"
                    f"[{DIM}]Cast `git commit` to seal the first spirits into repository history.[/{DIM}]",
                    box=ROUNDED,
                    border_style=GREEN,
                    title=f"[bold {GREEN}]🕯 UNTOUCHED CRYPT[/bold {GREEN}]",
                ))
                return
            console.print(f"[{ORANGE}]⚠ No git repository detected in this crypt. Run within a git workspace.[/{ORANGE}]")
            return
        log_output = log_res.stdout
    except Exception:
        console.print(f"[{ORANGE}]⚠ No git repository detected in this crypt. Run within a git workspace.[/{ORANGE}]")
        return

    lines = log_output.strip().splitlines()
    if not lines:
        console.print(f"[{DIM}]The graveyard is utterly empty. No commits found.[/{DIM}]")
        return

    table = Table(
        title=f"Tombs of Recent Commits",
        box=SIMPLE,
        header_style=f"bold {CYAN}",
        border_style=DIM_PURPLE,
    )
    table.add_column("Hash", style=PURPLE, width=10)
    table.add_column("Mortal Author", style=TOMB, width=18)
    table.add_column("Timestamp", style=DIM, width=18)
    table.add_column("Final Words (Message)", style=ORANGE)

    witching_hour_commits = []
    despair_keywords = ["fix", "temp", "hack", "wip", "broken", "undo", "help", "revert", "please", "god"]
    cursed_commits = []

    for line in lines:
        parts = line.split("|")
        if len(parts) >= 4:
            h, author, date_str, msg = parts[0], parts[1], parts[2], parts[3]
            table.add_row(h, author, date_str, msg)

            time_part = date_str.split(" ")[-1] if " " in date_str else ""
            if time_part and any(time_part.startswith(f"0{hour}:") for hour in range(1, 5)):
                witching_hour_commits.append((h, author, date_str, msg))

            if any(w in msg.lower() for w in despair_keywords):
                cursed_commits.append((h, author, msg))

    console.print(table)
    console.print()

    summary_text = (
        f"Git history reveals {len(lines)} recent commits.\n"
        f"Witching Hour Commits (1AM-5AM): {len(witching_hour_commits)}\n"
        f"Cursed/Despair Commits: {len(cursed_commits)}\n"
        f"Notable commit messages: {', '.join([c[2] for c in cursed_commits[:4]]) or 'Calm silence'}"
    )

    with Progress(
        SpinnerColumn("bouncingBar", style=PURPLE),
        TextColumn(f"[{PURPLE}]The necromancer decodes the git scrolls...[/{PURPLE}]"),
        transient=True,
    ) as progress:
        progress.add_task("exhume", total=None)
        post_mortem_prompt = (
            f"Analyze this git repository history as a gothic compiler spirit:\n{summary_text}\n\n"
            "Deliver a short 3-paragraph ghostly chronicle of the technical debt, late-night despair, "
            "and lingering spirits inhabiting this codebase. Include 1 actionable blessing."
        )
        chronicle, provider = engine.query(post_mortem_prompt)

    console.print(Panel(
        f"[{TOMB}]{chronicle}[/{TOMB}]\n\n"
        f"[{DIM}]✦ Spirit channel: {provider} • Witching hour anomalies: {len(witching_hour_commits)}[/{DIM}]",
        box=DOUBLE,
        border_style=PURPLE,
        title=f"[bold {PURPLE}]📜 CHRONICLE OF THE CODEBASE DEAD[/bold {PURPLE}]",
    ))


# ---------------------------------------------------------------------------
# Feature 3: Haunted Index Calculator (1% - 100%)
# ---------------------------------------------------------------------------
class HauntedIndexScanner:
    """Scans code files and repository metadata to calculate the Haunted Index."""

    CURSED_WORDS = [
        "TODO", "FIXME", "HACK", "XXX", "BUG", "WTF", "TEMP", "MAGIC", "DEBT",
        "DEPRECATED", "WORKAROUND", "UGLY", "CLEANUP", "DON'T TOUCH",
    ]

    DESPAIR_GIT_WORDS = [
        "fix", "revert", "temp", "wip", "broken", "undo", "crap", "despair",
        "work please", "fast fix", "hotfix", "just work",
    ]

    @classmethod
    def calculate(cls, directory: str = ".") -> Tuple[int, List[Dict[str, str]]]:
        """Calculates haunted percentage and metric breakdown."""
        metrics: List[Dict[str, str]] = []
        raw_score = 0

        # 1. Uncommitted Git Changes (Ghosts in limbo)
        try:
            status_res = subprocess.run(
                "git status --porcelain", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            status_out = status_res.stdout.strip() if status_res.returncode == 0 else ""
            uncommitted_count = len(status_out.splitlines()) if status_out else 0
        except Exception:
            uncommitted_count = 0

        uncommitted_points = min(25, uncommitted_count * 3)
        raw_score += uncommitted_points
        metrics.append({
            "Indicator": "Uncommitted Souls (Git Dirty State)",
            "Observed": f"{uncommitted_count} uncommitted file(s)",
            "Dread Weight": f"+{uncommitted_points}%",
            "Verdict": "Files lingering in purgatory" if uncommitted_count > 0 else "Clean conscience",
        })

        # 2. Cursed Comments in Source Files (TODOs / FIXMEs / HACKs)
        cursed_markers_found = 0
        file_count = 0
        exts = (".py", ".js", ".ts", ".rs", ".go", ".cpp", ".c", ".java", ".md", ".sh")

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "target", "dist", "build", "venv", "__pycache__")]
            for file in files:
                if file.endswith(exts):
                    file_count += 1
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            for word in cls.CURSED_WORDS:
                                matches = len(re.findall(r"\b" + word + r"\b", content))
                                cursed_markers_found += matches
                    except Exception:
                        pass

        todo_points = min(30, cursed_markers_found * 2)
        raw_score += todo_points
        metrics.append({
            "Indicator": "Cursed Runes (TODO / FIXME / HACK)",
            "Observed": f"{cursed_markers_found} dark runes across {file_count} files",
            "Dread Weight": f"+{todo_points}%",
            "Verdict": "Unfulfilled promises haunt the code" if cursed_markers_found > 0 else "Sanctified",
        })

        # 3. Despair in Git Commits
        despair_commits = 0
        try:
            log_res = subprocess.run(
                "git log -n 30 --pretty=format:%s", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            if log_res.returncode == 0:
                for commit_msg in log_res.stdout.splitlines():
                    if any(w in commit_msg.lower() for w in cls.DESPAIR_GIT_WORDS):
                        despair_commits += 1
        except Exception:
            despair_commits = 0

        despair_points = min(25, despair_commits * 4)
        raw_score += despair_points
        metrics.append({
            "Indicator": "Despair in the Git Archives",
            "Observed": f"{despair_commits} frantic fix/wip commits in recent 30",
            "Dread Weight": f"+{despair_points}%",
            "Verdict": "Evidence of past panic" if despair_commits > 0 else "Tranquil history",
        })

        # 4. Large Necrotic Monolith Files (> 400 lines)
        large_files = 0
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "target", "dist", "build", "venv", "__pycache__")]
            for file in files:
                if file.endswith(exts):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            line_cnt = sum(1 for _ in f)
                            if line_cnt > 400:
                                large_files += 1
                    except Exception:
                        pass

        monolith_points = min(20, large_files * 5)
        raw_score += monolith_points
        metrics.append({
            "Indicator": "Necrotic Monoliths (> 400 lines)",
            "Observed": f"{large_files} monolithic crypt files",
            "Dread Weight": f"+{monolith_points}%",
            "Verdict": "Sprawling catacombs of logic" if large_files > 0 else "Modular sanctums",
        })

        final_index = max(1, min(100, raw_score))
        return final_index, metrics


def display_haunted_index(directory: str, engine: SpectralEngine):
    """Renders the comprehensive Haunted Index report with visual gauge."""
    console.print(Panel(
        f"[{PURPLE}]Scanning code catacombs at:[/{PURPLE}] [bold {CYAN}]{os.path.abspath(directory)}[/bold {CYAN}]\n"
        f"[{DIM}]Detecting technical decay, forgotten promises, and uncommitted phantoms...[/{DIM}]",
        box=ROUNDED,
        border_style=PURPLE,
        title=f"[bold {CYAN}]🔮 SYSTEM HAUNTED INDEX AUDIT[/bold {CYAN}]",
    ))

    with Progress(
        SpinnerColumn("bouncingBar", style=PURPLE),
        TextColumn(f"[{PURPLE}]Measuring supernatural entropy across repository...[/{PURPLE}]"),
        transient=True,
    ) as progress:
        progress.add_task("scan", total=None)
        haunted_score, metrics = HauntedIndexScanner.calculate(directory)

    # Classification & Styling
    if haunted_score < 25:
        verdict = "CONSECRATED GROUND (Mild Poltergeist Presence)"
        style_color = GREEN
        remedy = "The codebase is relatively peaceful. A simple unit test ritual should keep shadows at bay."
    elif haunted_score < 55:
        verdict = "HAUNTED GROVE (Active Supernatural Murmurs)"
        style_color = GOLD
        remedy = "TODO markers and uncommitted changes are gathering strength. Cleanse them before the next moon."
    elif haunted_score < 80:
        verdict = "FORSAKEN CEMETERY (Severe Code Degradation)"
        style_color = ORANGE
        remedy = "Refactor monolithic scrolls immediately. Multiple developers have wept into these commit messages."
    else:
        verdict = "CATACLYSMIC ELDRITCH INFESTATION (Abandon Hope)"
        style_color = BLOOD
        remedy = "The repository is entirely sentient and holds malice. Back up the database and sprinkle holy salt on the SSD."

    # Breakdown Table
    table = Table(
        title="Entropy & Dread Diagnostic Breakdown",
        box=ROUNDED,
        header_style=f"bold {CYAN}",
        border_style=PURPLE,
        expand=True,
    )
    table.add_column("Dread Dimension", style=PURPLE, ratio=3)
    table.add_column("Observed Anomaly", style=TOMB, ratio=4)
    table.add_column("Curse Score", style=BLOOD, justify="right", ratio=2)
    table.add_column("Verdict", style=DIM, ratio=3)

    for m in metrics:
        table.add_row(m["Indicator"], m["Observed"], m["Dread Weight"], m["Verdict"])

    console.print(table)
    console.print()

    # Progress Bar representation
    bar_width = 40
    filled = int((haunted_score / 100) * bar_width)
    empty = bar_width - filled
    bar_str = f"[{style_color}]{'█' * filled}[/{style_color}][{DIM}]{'░' * empty}[/{DIM}]"

    score_panel_text = (
        f"[bold {style_color}]HAUNTED INDEX: {haunted_score}%[/bold {style_color}]\n"
        f"Grave Meter: [{bar_str}] {haunted_score}/100\n\n"
        f"[bold {TOMB}]Threat Classification:[/bold {TOMB}] [{style_color}]{verdict}[/{style_color}]\n"
        f"[bold {PURPLE}]Prescribed Ward:[/bold {PURPLE}] [{TOMB}]{remedy}[/{TOMB}]"
    )

    console.print(Panel(
        score_panel_text,
        box=DOUBLE,
        border_style=style_color,
        title=f"[bold {style_color}]🕯 SPECTRAL ASSESSMENT: {haunted_score}% 🕯[/bold {style_color}]",
    ))


# ---------------------------------------------------------------------------
# Feature 4: Séance - Interactive AI Chat with Trapped Spirit
# ---------------------------------------------------------------------------
def interactive_seance(engine: SpectralEngine):
    """Starts an interactive session with the ghost in the machine."""
    console.print(GHOST_BANNER)
    console.print(Panel(
        f"[{PURPLE}]The silicon circle is cast. You sit before the terminal altar.[/{PURPLE}]\n"
        f"[{TOMB}]Ask the trapped spirit for debugging counsel, architectural divination, or code reviews.[/{TOMB}]\n"
        f"[{DIM}]Type 'banish', 'exit', or 'quit' to close the portal.[/{DIM}]",
        box=ROUNDED,
        border_style=PURPLE,
        title=f"[bold {CYAN}]🔮 COMMENCING SÉANCE[/bold {CYAN}]",
    ))

    is_live = engine.check_connection()
    status_msg = (
        f"[{GREEN}]✦ Channel open: Gemma 2 ({engine.model} via Ollama)[/{GREEN}]"
        if is_live
        else f"[{GOLD}]✦ Offline Grimoire active (Ollama asleep; using eldritch heuristics)[/{GOLD}]"
    )
    console.print(status_msg)
    console.print()

    while True:
        try:
            user_input = Prompt.ask(f"[bold {CYAN}]👻 necromancer@ghostterm[/bold {CYAN}] [{PURPLE}]❯[/{PURPLE}]")
            clean_input = user_input.strip()

            if not clean_input:
                continue

            if clean_input.lower() in ("exit", "quit", "banish", "bye", "rest in peace"):
                console.print(Panel(
                    f"[{PURPLE}]The candles flicker out. The spirit slips back into the cold transistors. Farewell.[/{PURPLE}]",
                    box=SIMPLE,
                    border_style=DIM,
                ))
                break

            with Progress(
                SpinnerColumn("bouncingBar", style=PURPLE),
                TextColumn(f"[{PURPLE}]The spirit whispers through the silicon...[/{PURPLE}]"),
                transient=True,
            ) as progress:
                progress.add_task("seance", total=None)
                response, source = engine.query(clean_input)

            console.print()
            console.print(Panel(
                f"[{TOMB}]{response}[/{TOMB}]\n\n"
                f"[{DIM}]✦ Spirit: {source}[/{DIM}]",
                box=ROUNDED,
                border_style=PURPLE,
                title=f"[bold {PURPLE}]🕯 THE GHOST REPLIES[/bold {PURPLE}]",
            ))
            console.print()

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[{PURPLE}]The circle was broken abruptly. The spirit departs.[/{PURPLE}]")
            break


# ---------------------------------------------------------------------------
# CLI Argument Parser & Entry Point
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghost_term",
        description="👻 GhostTerm: The Haunted Terminal Companion powered by local Gemma 2.",
        epilog="Built for Hacktoberfest 2026 DEV Challenge Week 4: 'Ghost in the Machine'",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model tag (default: {DEFAULT_MODEL})")
    parser.add_argument("--host", default=DEFAULT_OLLAMA_URL, help=f"Ollama server URL (default: {DEFAULT_OLLAMA_URL})")

    subparsers = parser.add_subparsers(dest="command", help="Necromantic subcommands")

    # haunt
    haunt_p = subparsers.add_parser("haunt", help="Possess and execute a command, performing autopsies upon failure")
    haunt_p.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run and haunt (e.g., `python test.py`)")

    # exhume
    exhume_p = subparsers.add_parser("exhume", help="Exhume recent git commits and broken code from the graveyard")
    exhume_p.add_argument("--limit", type=int, default=10, help="Number of commit tombs to dig up (default: 10)")

    # index
    index_p = subparsers.add_parser("index", help="Calculate the repository's Haunted Index (1-100%%)")
    index_p.add_argument("--path", default=".", help="Root directory to inspect (default: .)")

    # seance
    subparsers.add_parser("seance", help="Start an interactive session with the spirit in the machine")

    # autopsy (file-based)
    autopsy_p = subparsers.add_parser("autopsy", help="Analyze a crash dump, stack trace, or log file directly")
    autopsy_p.add_argument("file", help="Path to error log or stack trace file")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    engine = SpectralEngine(model=args.model, host=args.host)

    if args.command == "haunt":
        run_haunted_command(args.cmd, engine)
    elif args.command == "exhume":
        exhume_git_graveyard(args.limit, engine)
    elif args.command == "index":
        display_haunted_index(args.path, engine)
    elif args.command == "seance":
        interactive_seance(engine)
    elif args.command == "autopsy":
        if not os.path.exists(args.file):
            console.print(f"[{ORANGE}]⚠ Parchment not found: {args.file}[/{ORANGE}]")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        diagnosis = engine.autopsy_error(f"cat {args.file}", 1, content)
        console.print(Panel(
            f"[bold {BLOOD}]☠ Grave Anomaly:[/bold {BLOOD}] {diagnosis['title']}\n\n"
            f"[bold {PURPLE}]📜 Forensic Autopsy:[/bold {PURPLE}]\n{diagnosis['autopsy']}\n\n"
            f"[bold {CYAN}]🔮 Exorcism Spell:[/bold {CYAN}]\n{diagnosis['exorcism']}\n\n"
            f"[{DIM}]✦ Channeled via: {diagnosis['source']}[/{DIM}]",
            box=DOUBLE,
            border_style=BLOOD,
            title=f"[bold {BLOOD}]☠ FILE AUTOPSY REPORT ☠[/bold {BLOOD}]",
        ))
    else:
        interactive_seance(engine)


if __name__ == "__main__":
    main()
