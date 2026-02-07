# BOSS_TBD
This file is owned by BOSS, prohibited from modification by any AI Agents on any platforms.

## Web APP Next to do

- [ ] Check every main tabs and sub-tabs can reuse the data lake, expecting a instant response or short time response.
- [ ] check compound interest tab
- [ ] check Cash Ladder tab

- [ ] **Phase 2 Scraper**: Fetch UNADJUSTED prices from TWSE/TPEx (Fix Wealth Bug).
    - [ ] Probe TWSE API (Verify 2006 price ~60).
    - [ ] Build `tests/ops_scripts/crawl_official.py`.
    - [ ] Re-ingest Data Lake.

---

## === Barrier === (DONT-TOUCH AREA)


- [ ] Multi-language (Deferred).
- [ ] AICopilot enhancement
- [ ] Test Google Cloud Run
- [ ] DB/Warm Staic files/locally cached files optimization
- [ ] Email support

---

## BOSS TBD (DONT-TOUCH AREA)

- switch to gh from git
- Study workflows suitable for AntiGravity
- Ralph Wiggum plugin/workflow suitable for AntiGravity
- Manus workflow
- study and integrate GEMINI CLI into AntiGravity
- study and integrate opencode into AntiGravity
- GEMENI CLI & Conductor
- Plan using Opus, Coding using Gemini 3 Pro High

---

## AI 工具 rules 目錄對照表 (DONT-TOUCH AREA)

| 平台 / 工具             | 專案目錄 (Project Scope) | 使用者全域目錄 (Global Scope)    |
| :---                   | :---                     | :---                           |
| **Google Antigravity** | `.agent/rules/`          | `~/.gemini/GEMINI.md`          |
| **Gemini CLI**         | `./GEMINI.md`            | `~/.gemini/GEMINI.md`          |
| **OpenCode**           | `./AGENTS.md`            | `~/.config/opencode/AGENTS.md` |

## AI 工具 Skills 目錄對照表

| 平台 / 工具               | 專案目錄 (Project Scope) | 使用者全域目錄 (Global Scope)             |
| :---                     | :---                     | :---                                    |
| **Google Antigravity**   | `.agent/skills/`         | `~/.gemini/antigravity/global_skills/`  |
| **Gemini CLI**           | `.gemini/skills/`        | `~/.gemini/skills/`                     |
| **OpenCode**             | `.opencode/skills/`      | `~/.config/opencode/skills/`            |

## AI 工具 workflows/commands 目錄對照表

| 平台 / 工具             | 專案目錄 (Project Scope)  | 使用者全域目錄 (Global Scope)              |
| :---                   | :---                     | :---                                      |
| **Google Antigravity** | `.agent/workflows/`      | `~/.gemini/antigravity/global_workflows`  |
| **Gemini CLI**         | `.gemini/commands/`      | `~/.gemini/commands/`                     |
| **OpenCode**           | `.opencode/commands/`    | `~/.config/opencode/commands/`            |
