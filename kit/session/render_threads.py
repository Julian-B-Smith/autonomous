#!/usr/bin/env python3
"""render_threads — the Threads Board: every integrations exchange, fleet-wide.

The question it answers is the one the human kept having to ask in chat: "is
anything waiting on anyone?" `governor/ball_scan.py` already knows — it reads
every repo's `integrations/` and works out who holds the ball and what is
overdue. This renders that answer as a page, ordered by what needs a human
first: overdue, then obligations open, then everything else.

How it stays current — honestly. The Session Board is event-driven because its
source changes only at three commands. Threads change whenever ANY session
files or answers a brief, and those sessions run no command that could
republish. So this is a SWEEP: re-rendered by the boards routine on a cadence
(`kit/session/boards.py`, K5) and by the standards repo's session at its own
boundaries, and republished only when something other than the clock changed.
There is no webhook into this machine, so "a merge touched a mailbox" becomes
"within one cadence tick of any mailbox change" — stated on the page, because
the "as of" stamp is the truth about freshness.

  render_threads.py > threads.html
  render_threads.py --check-changed > threads.html   # empty stdout if unchanged
"""
import datetime, hashlib, html, json, os, re, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "governor"))
sys.path.insert(0, os.path.join(_ROOT, "kit", "sweep"))
import ball_scan  # noqa: E402
import sweep      # noqa: E402


def gather():
    today = datetime.date.today()
    with open(os.path.join(_ROOT, "registry.json"), encoding="utf-8") as fh:
        projects = sweep.resolve(json.load(fh))
    rows, awaiting = [], []
    paths = [p["path"] for p in projects]
    for p in projects:
        if not os.path.isdir(os.path.join(p["path"], "integrations")):
            continue
        try:
            for t in ball_scan.scan_repo(p["path"], p["name"], today):
                t = dict(t, repo=p["name"])
                rows.append(t)
            for a in ball_scan.responses_awaiting(p["name"], paths, today):
                awaiting.append(dict(a, repo=p["name"]))
        except Exception:
            continue                    # one broken mailbox never blanks the page
    return rows, awaiting, today


def render():
    rows, awaiting, today = gather()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    overdue = [r for r in rows if r.get("days_overdue")]
    owed = [r for r in rows if r.get("ours") and not r.get("days_overdue")]
    rest = [r for r in rows if not r.get("ours")]

    def esc(x): return html.escape(str(x if x is not None else ""))

    def table(items, kind):
        if not items:
            return ""
        trs = []
        for r in sorted(items, key=lambda x: (-(x.get("days_overdue") or 0), x["repo"], x["id"])):
            od = r.get("days_overdue")
            trs.append(f"""<tr class="{kind}">
  <td class="repo"><code>{esc(r['repo'])}</code></td>
  <td class="id"><code>{esc(r['id'])}</code> <span class="dir">{esc(r.get('dir',''))}</span></td>
  <td>{esc(r.get('status'))}</td>
  <td>{esc(r.get('ball'))}</td>
  <td class="num">{esc(r.get('respond_by') or '—')}</td>
  <td class="num">{(str(od) + 'd') if od else ''}</td>
</tr>""")
        return f"""<div class="scroll"><table>
<thead><tr><th>Holder</th><th>Thread</th><th>Status</th><th>Ball</th><th>Respond by</th><th>Overdue</th></tr></thead>
<tbody>{''.join(trs)}</tbody></table></div>"""

    aw_html = ""
    if awaiting:
        aw_html = "<ul>" + "".join(
            f"<li><code>{esc(a['repo'])}</code> has an answer to <code>{esc(a['id'])}</code> "
            f"waiting in <code>{esc(a['in_repo'])}</code></li>" for a in awaiting) + "</ul>"
    else:
        aw_html = '<p class="empty">Nothing answered elsewhere is waiting to be read.</p>'

    n_repos = len({r["repo"] for r in rows})
    return f"""<title>Threads Board</title>
<style>
:root {{ --bg:#F5F4EF; --panel:#FFFFFF; --ink:#1B1D22; --ink-2:#6B6F7A; --line:#DDDCD4;
  --accent:#0F6E68; --accent-ink:#0B4F4B; --warn:#B36B00; --warn-bg:#FBF0DC; --bad:#9A2F2F; --bad-bg:#F8E4E4;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#16181C; --panel:#1E2126; --ink:#E8E7E1; --ink-2:#9A9EA8; --line:#2E323A;
  --accent:#4FB3AC; --accent-ink:#7ED0C9; --warn:#E0A03A; --warn-bg:#332A18; --bad:#E06B6B; --bad-bg:#3A1F1F; }} }}
:root[data-theme="dark"] {{
  --bg:#16181C; --panel:#1E2126; --ink:#E8E7E1; --ink-2:#9A9EA8; --line:#2E323A;
  --accent:#4FB3AC; --accent-ink:#7ED0C9; --warn:#E0A03A; --warn-bg:#332A18; --bad:#E06B6B; --bad-bg:#3A1F1F; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 var(--sans); }}
.wrap {{ max-width:960px; margin:0 auto; padding:40px 24px 70px; }}
h1 {{ font-size:26px; margin:0 0 2px; letter-spacing:-.01em; }}
.sub {{ color:var(--ink-2); font-size:13.5px; margin:0 0 22px; max-width:78ch; }}
.stats {{ display:flex; gap:12px; flex-wrap:wrap; margin:0 0 26px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); padding:12px 18px; min-width:120px; }}
.stat .n {{ font-size:28px; font-weight:600; line-height:1; color:var(--accent-ink); font-variant-numeric:tabular-nums; }}
.stat .n.bad {{ color:var(--bad); }} .stat .n.warn {{ color:var(--warn); }}
.stat .l {{ font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; color:var(--ink-2); margin-top:5px; }}
h2 {{ font-size:13px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-2); margin:28px 0 8px; padding-bottom:6px; border-bottom:1px solid var(--line); }}
h2 .c {{ font:600 12px var(--mono); margin-left:6px; }}
.scroll {{ overflow-x:auto; border:1px solid var(--line); background:var(--panel); }}
table {{ border-collapse:collapse; width:100%; min-width:720px; }}
th {{ text-align:left; font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; color:var(--ink-2); padding:9px 12px; border-bottom:1px solid var(--line); }}
td {{ padding:8px 12px; border-bottom:1px solid var(--line); font-size:13.5px; }}
tr:last-child td {{ border-bottom:0; }}
tr.overdue td {{ background:var(--bad-bg); }} tr.owed td {{ background:var(--warn-bg); }}
.repo code, .id code {{ font:12.5px var(--mono); }}
.dir {{ font:11px var(--mono); color:var(--ink-2); margin-left:6px; }}
.num {{ font-variant-numeric:tabular-nums; }}
.empty {{ background:var(--panel); border:1px solid var(--line); padding:16px; color:var(--ink-2); }}
ul {{ background:var(--panel); border:1px solid var(--line); margin:0; padding:12px 12px 12px 32px; }}
li {{ margin:3px 0; font-size:13.5px; }}
.foot {{ color:var(--ink-2); font-size:12.5px; margin-top:22px; max-width:78ch; }}
</style>
<div class="wrap">
<h1>Threads Board</h1>
<p class="sub">as of <b>{stamp}</b> · every <code>integrations/</code> exchange across the fleet, read by <code>ball_scan</code>. A <b>sweep</b>, not a live feed: re-rendered by the boards routine on a cadence and at the standards repo's session boundaries, republished only when something other than this stamp changed — so a brief filed after the stamp appears within one routine tick.</p>
<div class="stats">
  <div class="stat"><div class="n{' bad' if overdue else ''}">{len(overdue)}</div><div class="l">overdue</div></div>
  <div class="stat"><div class="n{' warn' if owed else ''}">{len(owed)}</div><div class="l">obligations open</div></div>
  <div class="stat"><div class="n">{len(awaiting)}</div><div class="l">answered, unread</div></div>
  <div class="stat"><div class="n">{len(rows)}</div><div class="l">threads · {n_repos} repos</div></div>
</div>
<h2>Overdue — a human should look <span class="c">{len(overdue)}</span></h2>
{table(overdue, 'overdue') or '<p class="empty">Nothing overdue.</p>'}
<h2>Obligations open — the ball is on that repo <span class="c">{len(owed)}</span></h2>
{table(owed, 'owed') or '<p class="empty">No open obligations.</p>'}
<h2>Answered elsewhere, not yet read <span class="c">{len(awaiting)}</span></h2>
{aw_html}
<h2>Everything else — waiting on the other side, or closed <span class="c">{len(rest)}</span></h2>
{table(rest, 'rest') or '<p class="empty">—</p>'}
<p class="foot">"Holder" is the repo whose mailbox the thread sits in; "ball" says who must act next (<code>provider</code> = the holder, <code>consumer</code> = the filer). Overdue means <code>respond-by</code> has passed <i>and</i> the ball is on the holder — a missed date with the ball elsewhere is not the holder's fault. Source: <code>governor/ball_scan.py</code> · renderer: <code>kit/session/render_threads.py</code>. Private page: it names private repos.</p>
</div>"""


MARKER = ".threads-render"


if __name__ == "__main__":
    # Same contract as render_registry: from any repo but the standards repo,
    # say so and write nothing; otherwise print CHANGED/UNCHANGED on stderr and
    # the page on stdout only when it changed. Days-overdue moves at midnight,
    # so an idle fleet still republishes about once a day — correctly.
    sys.path.insert(0, _HERE)
    import render_registry  # noqa: E402
    if "--check-changed" in sys.argv and not render_registry.is_publisher():
        print("NOT-PUBLISHER", file=sys.stderr)
        sys.exit(0)
    page = render()
    if "--check-changed" in sys.argv:
        is_new, digest = render_registry.changed(page, marker=MARKER)
        if is_new:
            render_registry.record(digest, marker=MARKER)
        print("CHANGED" if is_new else "UNCHANGED", file=sys.stderr)
        sys.stdout.write(page if is_new else "")
        sys.exit(0)
    sys.stdout.write(page)
