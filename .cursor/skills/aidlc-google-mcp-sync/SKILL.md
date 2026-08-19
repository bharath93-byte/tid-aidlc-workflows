---
name: aidlc-google-mcp-sync
description: Sync an AI-DLC epic's Markdown docs to Google Drive as rendered Google Docs via the Google Drive MCP. Mirrors the epic's folder structure, ignores XML (and XML-only folders), strips the `.md` extension, and renames files/folders to human-readable titles. Use when the user asks to sync/push/upload aidlc-docs to Google Drive, convert epic .md files into Google Docs, or says "aidlc-google-mcp-sync".
disable-model-invocation: true
metadata:
  author: vselva1
  version: "1.0"
---

# aidlc-google-mcp-sync

Push an AI-DLC epic's Markdown documents to a Google Drive folder as **native
Google Docs** (Markdown is converted on upload, so headings/tables/lists render
like a preview — not raw `#`/`*` text). The Drive folder tree mirrors the epic's
on-disk structure, XML files (and folders that contain only XML) are skipped,
the `.md` extension is dropped, and every file/folder gets a human-readable title.

## Requirements

- Google Drive MCP server: `plugin-google-drive-google-drive`
- `python3` on PATH
- The script beside this skill: `scripts/prepare_payloads.py`

`<skill_path>` below = the directory containing this `SKILL.md`.

## Progress + reliability rules (read first)

Large inline payloads through the MCP can stall for minutes. To avoid this:

- **Never** pass `base64Content` for big docs. Always use `textContent` +
  `contentMimeType: "text/markdown"` (this triggers conversion to a Google Doc).
- Upload **one file per `create_file` call** and print a `X/N` progress line
  after each so nothing sits silent.
- Parallelize by handing the upload loop to one or more subagents (see Step 6).

## Workflow

```
- [ ] Step 1: Connect to the Google Drive MCP
- [ ] Step 2: Load epic state (state-loader) and resolve EPIC_DIR
- [ ] Step 3: Ask for the destination Drive folder
- [ ] Step 4: Build the upload plan (script)
- [ ] Step 5: Create the mirrored folder tree in Drive
- [ ] Step 6: Upload each .md as a Google Doc (subagents, in parallel)
- [ ] Step 7: Verify + report
```

### Step 1: Connect to the Google Drive MCP

Inspect `plugin-google-drive-google-drive`. If its status is `needsAuth` (or any
`create_file` call later fails with an auth error), call its `mcp_auth` tool
once, then re-inspect. Confirm `create_file`, `update_file`, and `search_files`
are available before proceeding.

### Step 2: Load epic state and resolve EPIC_DIR

Invoke the **state-loader** skill first. It loads
`.cursor/skills/state-loader/pipeline-config.json` and, if an epic is known from
context, that epic's `state.json`. This makes the flow resumable across sessions
and developers.

- **A. Existing epic (`state.json` present)** → this is a RESUME. Record
  `EPIC_DIR` and `status`, then go to Step 3.
- **B. No epic in context** → ask the user exactly once: *"Which epic under
  `aidlc-docs/` should I sync? Give me the folder name or Jira key."* Resolve
  `EPIC_DIR = aidlc-docs/<epic-name>_<epic-id>/`. Do not proceed until resolved.

### Step 3: Ask for the destination Drive folder

**Always ask the user explicitly** (never assume) for the target Google Drive
folder — accept a share URL or a folder ID:

> *"Which Google Drive folder should I push into? Paste the folder URL or ID."*

Extract the folder ID from a URL like
`https://drive.google.com/drive/folders/<FOLDER_ID>`. Verify with
`get_file_metadata` (`fileId=<FOLDER_ID>`); confirm `canAddChildren: true` and
show the folder title back to the user.

Also propose a friendly **root title** for the epic's top folder (the on-disk
name like `rate-limiting-user-userid` is usually not what the user wants) and let
them confirm or override.

### Step 4: Build the upload plan

Run the prep script. It collects every `.md` under `EPIC_DIR`, skips XML and
XML-only folders, mirrors the structure, assigns titles, and writes one JSON
payload per file plus a `manifest.json`:

```bash
python3 <skill_path>/scripts/prepare_payloads.py \
  --epic-dir <EPIC_DIR> \
  --root-title "<confirmed root title>" \
  --out /tmp/gdrive_sync_<epic>
```

The script prints the folder tree and file list. `manifest.json` contains:

- `root_title` — title for the epic's top-level Drive folder
- `folders[]` — `{rel_path, parent_rel, title}`, already ordered parent-before-child
  (`parent_rel: ""` means directly under the epic root folder)
- `files[]` — `{num, title, rel_parent, payload, chars}` (`rel_parent: ""` = epic root)

Title rules (in the script; extend the override maps there if needed):
`vision`→Vision Document, `high-level-design`→High-Level Design, `adr`→Architecture
Decision Records, `audit`→Audit Log, `LLD`→Low-Level Design, `*-EARS`→EARS
Specifications; otherwise hyphens/underscores become spaces in Title Case.

### Step 5: Create the mirrored folder tree in Drive

Create folders with `create_file` (`mimeType: application/vnd.google-apps.folder`)
and track a `rel_path -> driveFolderId` map. Independent folders at the same level
can be created in a single batch of parallel calls.

1. Create the **epic root folder** (`manifest.root_title`) under the destination
   `<FOLDER_ID>`. Map `"" -> <rootId>`.
2. For each entry in `manifest.folders` (already ordered), create it under
   `map[parent_rel]` and record `map[rel_path] = <newId>`.

### Step 6: Upload each `.md` as a Google Doc (parallel via subagents)

Hand the upload loop to one or more subagents so files upload concurrently while
you stay responsive. Give each subagent a slice of `manifest.files` **plus the
resolved `rel_parent -> driveFolderId` map** and these exact instructions:

For each assigned file, in order:
1. Read the payload JSON:
   `python3 -c "import json;print(json.dumps(json.load(open('<payload>'))))"`
2. Call `plugin-google-drive-google-drive` → `create_file` with:
   `title` = payload title, `parentId` = `map[rel_parent]`,
   `textContent` = payload textContent, `contentMimeType` = `"text/markdown"`.
   (Do **not** send `base64Content`.)
3. Print `Uploaded X/N: <title> -> <viewUrl>`.
4. On error, log it and continue; report failures at the end.

Confirm the returned `mimeType` is `application/vnd.google-apps.document`.

### Step 7: Verify + report

`search_files` with `query: "parentId = '<rootId>'"` (and per-subfolder as needed)
to confirm the tree. Report a final table of every created Doc with its URL, note
anything skipped (XML/XML-only folders) or failed, and share the destination
folder link.

## Notes

- Idempotency: re-running creates **new** Docs (Drive allows duplicate titles).
  To refresh instead of duplicate, first `search_files` for an existing Doc of
  the same title under the target folder and `trash_file` it, or tell the user
  duplicates will be created.
- The MCP uploads to whichever Google account authorized the server — confirm it
  owns (or can write to) the destination folder.
- Empty-after-filter folders (e.g. an XML-only `system-prompts/`) are intentionally
  not created.
