#!/usr/bin/env python3
"""render_registry — the Session Board: which sessions are open, as a page.

Renders the session registry to self-contained HTML for publishing as an
artifact. No runtime capabilities: a hosted page cannot read this machine's
disk, and it does not need to — the registry changes ONLY at /wakeup,
/breakdown and /closeout, so those commands republishing the page makes it
current at every moment the truth changes. Event-driven beats polling when
the event set is closed.

Honest scope, stated on the page: this shows REGISTERED sessions. A session
that never ran /wakeup is invisible here — the board's coverage grows exactly
as fast as the wakeup habit does, and pretending otherwise would be the
declared-vs-effective trap with a nicer font.

  render_registry.py > board.html
"""
import datetime, hashlib, html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registry  # noqa: E402

STALE_HOURS = 12   # a row this old is probably an unclean shutdown, not work


def _age(opened_at, now):
    try:
        t = datetime.datetime.strptime(opened_at, "%Y-%m-%dT%H:%M:%SZ") \
            .replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None, "?"
    h = (now - t).total_seconds() / 3600
    if h < 1:
        return h, f"{int(h * 60)}m"
    if h < 48:
        return h, f"{h:.1f}h"
    return h, f"{h / 24:.1f}d"


def render():
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = registry.list_open()
    body = []
    for r in sorted(rows, key=lambda x: x.get("opened_at", "")):
        h, age = _age(r.get("opened_at"), now)
        stale = h is not None and h > STALE_HOURS
        body.append(f"""<tr class="{'stale' if stale else ''}">
  <td class="repo"><code>{html.escape(r.get('repo', '?'))}</code></td>
  <td><span class="chip">{html.escape(r.get('machine', '?'))}</span></td>
  <td class="num">{age}</td>
  <td class="sid">{html.escape(r.get('session_id', '')[:28])}</td>
  <td class="note">{'likely unclean shutdown — /wakeup there will offer the close' if stale else 'open'}</td>
</tr>""")
    n = len(rows)
    stale_n = sum(1 for r in rows if (_age(r.get("opened_at"), now)[0] or 0) > STALE_HOURS)
    table = (f"""<div class="scroll"><table>
  <thead><tr><th>Repo</th><th>Machine</th><th>Open for</th><th>Session</th><th>State</th></tr></thead>
  <tbody>{''.join(body)}</tbody></table></div>""" if rows else
             """<p class="empty">Nothing open. Every registered session has closed — the good kind of empty.</p>""")
    return f"""<title>Session Board</title>
<style>
:root {{ --bg:#F5F4EF; --panel:#FFFFFF; --ink:#1B1D22; --ink-2:#6B6F7A; --line:#DDDCD4;
  --accent:#0F6E68; --accent-ink:#0B4F4B; --warn:#B36B00; --warn-bg:#FBF0DC;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#16181C; --panel:#1E2126; --ink:#E8E7E1; --ink-2:#9A9EA8; --line:#2E323A;
  --accent:#4FB3AC; --accent-ink:#7ED0C9; --warn:#E0A03A; --warn-bg:#332A18; }} }}
:root[data-theme="dark"] {{
  --bg:#16181C; --panel:#1E2126; --ink:#E8E7E1; --ink-2:#9A9EA8; --line:#2E323A;
  --accent:#4FB3AC; --accent-ink:#7ED0C9; --warn:#E0A03A; --warn-bg:#332A18; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 var(--sans); }}
.wrap {{ max-width:760px; margin:0 auto; padding:40px 24px 70px; }}
h1 {{ font-size:26px; margin:0 0 2px; letter-spacing:-.01em; }}
.sub {{ color:var(--ink-2); font-size:13.5px; margin:0 0 24px; }}
.stats {{ display:flex; gap:12px; margin:0 0 22px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); padding:12px 18px; }}
.stat .n {{ font-size:28px; font-weight:600; line-height:1; color:var(--accent-ink);
  font-variant-numeric:tabular-nums; }}
.stat .n.warn {{ color:var(--warn); }}
.stat .l {{ font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; color:var(--ink-2); margin-top:5px; }}
.scroll {{ overflow-x:auto; border:1px solid var(--line); background:var(--panel); }}
table {{ border-collapse:collapse; width:100%; min-width:560px; }}
th {{ text-align:left; font-size:10.5px; letter-spacing:.07em; text-transform:uppercase;
  color:var(--ink-2); padding:9px 12px; border-bottom:1px solid var(--line); }}
td {{ padding:9px 12px; border-bottom:1px solid var(--line); font-size:13.5px; }}
tr:last-child td {{ border-bottom:0; }}
tr.stale td {{ background:var(--warn-bg); }}
.repo code {{ font:13px var(--mono); }}
.chip {{ font:600 10px var(--mono); letter-spacing:.06em; text-transform:uppercase;
  border:1px solid var(--accent); color:var(--accent); padding:2px 7px; }}
.num {{ font-variant-numeric:tabular-nums; }}
.sid {{ font:12px var(--mono); color:var(--ink-2); }}
.note {{ font-size:12.5px; color:var(--ink-2); }}
.empty {{ background:var(--panel); border:1px solid var(--line); padding:22px; color:var(--ink-2); }}
.foot {{ color:var(--ink-2); font-size:12.5px; margin-top:20px; max-width:70ch; }}
</style>
<div class="wrap">
<h1>Session Board</h1>
<p class="sub">as of <b>{now.strftime('%Y-%m-%d %H:%M UTC')}</b> · republished by <code>/wakeup</code>, <code>/breakdown</code> and <code>/closeout</code> in the standards repo, and by the boards routine on a cadence when a session has opened, closed, or gone stale. Ages are as of the stamp.</p>
<div class="stats">
  <div class="stat"><div class="n">{n}</div><div class="l">open sessions</div></div>
  <div class="stat"><div class="n{' warn' if stale_n else ''}">{stale_n}</div><div class="l">likely unclean</div></div>
</div>
{table}
<p class="foot">Shows <b>registered</b> sessions only — a session that never ran <code>/wakeup</code> is invisible here, so coverage grows exactly as fast as the habit does. Rows older than {STALE_HOURS}h are flagged: probably a shutdown nobody closed; <code>/wakeup</code> in that repo offers the reconciliation. Source: <code>~/.claude/session-registry/</code> · renderer: <code>kit/session/render_registry.py</code>.</p>
</div>"""


def _significant(page):
    """The page minus its own timestamp — what actually changed, if anything.

    The rendered clock moves every second, so a naive byte-compare always says
    CHANGED and the board republishes on every boundary a session hits. Three
    identical republishes in four minutes (2026-08-31, mind-lathe) is the
    symptom: noise that trains the reader to ignore the notification.

    Row ages ("Open for 39.2h") are stripped for the same reason once the
    boards routine runs on a cadence (K5): an age printed to a tenth of an
    hour changes every six minutes, so an hourly tick would republish a page
    with nothing new on it. What counts as change is a session opening,
    closing, or crossing the stale line — the `stale` row class stays in.
    """
    page = re.sub(r"as of <b>[^<]+</b>", "", page)
    return re.sub(r'<td class="num">[^<]*</td>', "", page)


def changed(page, root=None, marker=".board-render"):
    """(bool, digest). Compares against the last render recorded beside the
    registry — no state file, no board; absent marker means 'changed', which
    is the safe direction for a bookkeeping page. `marker` names the file, so
    each board keeps its own (the Threads Board uses `.threads-render`)."""
    import registry as _reg
    root = root or _reg.root()
    digest = hashlib.sha256(_significant(page).encode()).hexdigest()
    if not root:
        return True, digest
    path = os.path.join(root, marker)
    try:
        with open(path, encoding="utf-8") as fh:
            was = fh.read().strip()
    except OSError:
        was = None
    return digest != was, digest


def record(digest, root=None, marker=".board-render"):
    import registry as _reg
    root = root or _reg.root()
    if not root:
        return
    try:
        with open(os.path.join(root, marker), "w", encoding="utf-8") as fh:
            fh.write(digest)
    except OSError:
        pass


def is_publisher():
    """Only a session running IN the standards repo publishes the boards.

    Two sessions racing on one artifact means every boundary either hits is a
    publish conflict, and clearing one costs a full re-read of the page. Three
    in a row on 2026-09-02 (dispatch + autonomous both live) settled it: one
    home per artifact, everyone else points at it — the same rule the rest of
    the fleet already runs on. Other sessions still write the registry; the
    board catches up at the publisher's next boundary.
    """
    import subprocess
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return False
    here = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    return bool(top) and os.path.realpath(top) == here


if __name__ == "__main__":
    if "--check-changed" in sys.argv and not is_publisher():
        print("NOT-PUBLISHER", file=sys.stderr)   # registry written; board waits
        sys.exit(0)
    page = render()
    if "--check-changed" in sys.argv:
        is_new, digest = changed(page)
        if is_new:
            record(digest)
        print("CHANGED" if is_new else "UNCHANGED", file=sys.stderr)
        sys.stdout.write(page if is_new else "")
        sys.exit(0)
    sys.stdout.write(page)
