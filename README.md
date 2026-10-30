# 👻 GhostTerm (NecroShell)
### *The Haunted Terminal Companion Powered by Local Gemma 2*

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026_DEV_Challenge_Week_4-ff5555.svg?style=for-the-badge&logo=hacktoberfest)](https://dev.to/challenges/hacktoberfest-2026-week-4)
[![Gemma 2](https://img.shields.io/badge/Model-Gemma_2_(Google_DeepMind)-00f0ff.svg?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemma/)
[![Privacy](https://img.shields.io/badge/Privacy-100%25_Local_&_Offline-50fa7b.svg?style=for-the-badge)](https://ollama.com)
[![GitHub](https://img.shields.io/badge/GitHub-kady--x%2FGhostTerm-bd93f9.svg?style=for-the-badge&logo=github)](https://github.com/kady-x/GhostTerm)
[![DEV.to](https://img.shields.io/badge/DEV.to-@kadyx-0a0a0a.svg?style=for-the-badge&logo=dev.to)](https://dev.to/kadyx)
[![License: MIT](https://img.shields.io/badge/License-MIT-f1fa8c.svg?style=for-the-badge)](LICENSE)

```
     .-.
    (o o)       G H O S T T E R M
    | O \       The Spirit in the Machine
     \   \      Hacktoberfest 2026 • DEV Challenge Week 4
      `~~~'     Local Gemma 2 Necromancy Engine
```

> *"Every codebase is a cemetery of forgotten decisions. GhostTerm gives the dead a voice."*

---

## 🕯 What is GhostTerm?

**GhostTerm** (or *NecroShell*) is an eerie, production-ready developer CLI assistant and process wrapper built by [@kady-x](https://github.com/kady-x) for the **Hacktoberfest DEV Challenge Week 4: "Ghost in the Machine"**. 

It transforms monotonous terminal debugging and cryptic errors into an atmospheric gothic séance. Running as an interactive shell wrapper, GhostTerm inspects your executing commands, fatal stack traces, and git graveyards, channeling **Google DeepMind's open-weight Gemma 2** model (via Ollama) to whisper haunted diagnostics, post-mortem autopsies, and actionable resurrecting fixes.

Best of all: **Zero cloud tokens. Zero telemetry. 100% private.** Your proprietary stack traces, sensitive environmental variables, and internal code never leave your machine.

---

## ⚡ Key Supernatural Features

| Rite / Command | Description |
| :--- | :--- |
| **`ghost_term haunt <cmd...>`** | **Process Possession & Fatal Autopsy.** Wraps any developer command (`python`, `npm`, `cargo`, `git`). If the process dies with a non-zero exit code, the spirit performs an atmospheric autopsy and prescribes an exact technical remedy. If it succeeds, it receives a reluctant spectral benediction. |
| **`ghost_term index [--path .]`** | **Repository Haunted Index (1% - 100%).** Audits your codebase for supernatural entropy: uncommitted ghosts in git limbo, cursed code runes (`TODO`, `FIXME`, `HACK`, `WTF`, `DEBT`), necrotic monolith files (>400 lines), and frantic 2 AM despair commits. |
| **`ghost_term exhume [--limit N]`** | **Git Graveyard Exhumation.** Digs through the repository's commit tombs to identify late-night "Witching Hour" commits (1:00 AM – 5:00 AM), abandoned hotfixes, and frantic commit messages, synthesizing an AI post-mortem chronicle. |
| **`ghost_term seance`** | **Interactive Spectral Séance.** An interactive REPL circle where developers can converse with the trapped compiler spirit about architectural sins, bizarre runtime bugs, or existential debugging dread. |
| **`ghost_term autopsy <file>`** | **Forensic Log Examination.** Scans crash logs, core dumps, or stack trace text files directly to deliver immediate forensic autopsies. |
| **🔮 Offline Spectral Grimoire** | **Seamless Offline Fallback.** If Ollama is offline or Gemma 2 is sleeping, GhostTerm falls back instantaneously to a built-in rule-based heuristic grimoire covering 30+ classical programming errors with zero crashes. |

---

## 🏛 Architecture & Open-Weight AI

```
 +-------------------------------------------------------------------------+
 |                              DEVELOPER CLI                              |
 |     $ python ghost_term.py haunt python script.py                       |
 +-------------------------------------------------------------------------+
                                      |
                                      v
 +-------------------------------------------------------------------------+
 |                           GHOSTTERM ORCHESTRATOR                        |
 |  - Subprocess Life Cycle Interceptor                                    |
 |  - Git Graveyard & Cursed Rune Scanner                                  |
 |  - Spooky Rich Palette (#00f0ff Cyan, #bd93f9 Purple, #ff5555 Blood)   |
 +-------------------------------------------------------------------------+
                                      |
                    +-----------------+-----------------+
                    |                                   |
         [Ollama Online]                      [Ollama Offline]
                    |                                   |
                    v                                   v
 +------------------------------------+  +--------------------------------+
 |     LOCAL GEMMA 2 (via Ollama)     |  |    ELDRITCH HEURISTIC GRIMOIRE |
 |   - Model: gemma2:2b / gemma2:9b   |  |  - 30+ Stack Trace Patterns    |
 |   - 100% Offline & On-Device       |  |  - Zero Network Dependencies   |
 |   - Zero Token Telemetry           |  |  - Instantaneous Determinism   |
 |   - Victorian Compiler Personality |  |  - Gothic Remedy Formulations  |
 +------------------------------------+  +--------------------------------+
                    |                                   |
                    +-----------------+-----------------+
                                      |
                                      v
 +-------------------------------------------------------------------------+
 |                         RICH SPECTRAL INTERFACE                         |
 |  - Terminal Tombstone Graphics (ASCII R.I.P banners)                    |
 |  - Diagnostic Threat Breakdown Tables                                   |
 |  - Atmospheric Actionable Resurrection Wards                            |
 +-------------------------------------------------------------------------+
```

### Why Open-Weight AI (Gemma 2) Matters for Developer Terminals:
Terminal output is the most sensitive data surface in modern software engineering. It frequently contains:
- Secret tokens and unmasked API keys in fatal crash reports
- Internal server URLs, database schemas, and file paths
- Proprietary algorithms and business logic in backtraces

By coupling GhostTerm with **Gemma 2 running locally via Ollama**, you achieve cutting-edge reasoning capabilities without sending a single byte over the public internet.

---

## 🚀 Quickstart

### 1. Clone & Install Dependencies
GhostTerm requires Python 3.10+ and minimal dependencies (`rich`, `requests`):

```bash
git clone https://github.com/kady-x/GhostTerm.git
cd GhostTerm
pip install -r requirements.txt
```

### 2. (Optional) Awaken Gemma 2 via Ollama
To empower the full spirit reasoning engine, ensure [Ollama](https://ollama.com) is running with Gemma 2:

```bash
# Pull the ultra-fast, lightweight Gemma 2 (2B) or Gemma 2 (9B)
ollama pull gemma2:2b
ollama run gemma2:2b
```

> **Note:** If Ollama is not installed or offline, GhostTerm **automatically and seamlessly switches** to its offline Eldritch Grimoire. You never have to worry about connection timeouts or unhandled exceptions breaking your flow!

---

## 🎮 Visual Walkthrough & Demos

### 1. Haunting a Command (`ghost_term haunt <cmd...>`)
Wraps any build, test, or run command with active process possession:

```bash
python ghost_term.py haunt python examples/cursed_script.py
```

![GhostTerm Process Haunting & Autopsy](assets/screenshots/haunt_autopsy.png)

---

### 2. Measuring Repository "Haunted Index" (`ghost_term index`)
Audits technical debt, uncommitted phantoms, and panic commits across the repo:

```bash
python ghost_term.py index
```

![GhostTerm Haunted Index Audit](assets/screenshots/haunted_index.png)

---

### 3. Exhuming the Git Graveyard (`ghost_term exhume`)
Unearths late-night commits and forgotten authors from the git crypt:

```bash
python ghost_term.py exhume --limit 10
```

![GhostTerm Exhuming Git Graveyard](assets/screenshots/exhume_graveyard.png)

---

### 4. Interactive Séance with the Machine Spirit (`ghost_term seance`)
Speak directly with the trapped spirit for architectural or code wisdom:

```bash
python ghost_term.py seance
```

![GhostTerm Interactive Séance](assets/screenshots/seance_session.png)

---

### 5. Direct Crash Log Autopsy (`ghost_term autopsy <file>`)
Examines server logs or crash dumps without rerunning:

```bash
python ghost_term.py autopsy examples/crashed_server.log
```

![GhostTerm File Autopsy Report](assets/screenshots/file_autopsy.png)

---

## ⚙️ Configuration & Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OLLAMA_HOST` | URL to your local Ollama server instance | `http://localhost:11434` |
| `GHOST_MODEL` | Ollama model tag to summon | `gemma2:2b` (or `gemma2:9b`, `gemma2:27b`) |

You can also pass `--model` and `--host` directly via the CLI:
```bash
python ghost_term.py --model gemma2:9b haunt python main.py
```

---

## 🎨 Spooky Palette Specification

GhostTerm renders high-contrast, spectral themes tuned for both dark and dim terminal emulators:
- **Spectral Cyan (`#00f0ff`)**: Highlights interactive prompts and summoned commands.
- **Phantom Purple (`#bd93f9`)**: Frame borders, tarot scrolls, and spirit messages.
- **Blood Orange (`#ff5555`)**: Fatal stack traces and catastrophic failure indicators.
- **Ectoplasm Green (`#50fa7b`)**: Clean executions and successful resurrection spells.
- **Tombstone Ash (`#f8f8f2`)**: Forensic autopsy narratives.

---

## 📜 License & Credits

- **Author**: Mohamed ElKady ([GitHub @kady-x](https://github.com/kady-x) • [DEV @kadyx](https://dev.to/kadyx))
- Developed for the **Hacktoberfest 2026 DEV Challenge Week 4: "Ghost in the Machine"**.
- Powered by Google DeepMind's **Gemma 2** open-weight model family.
- Licensed under the open and permissive [MIT License](LICENSE).
