import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Opportunity Prioritiser",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #fafafa; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.rec-card {
    padding: 16px 20px; border-radius: 10px;
    border: 1px solid #e5e7eb; margin-bottom: 12px; background: white;
}
.rec-card.urgent { border-left: 4px solid #dc2626 !important; }
.rec-card.bumped { border-style: dashed; }
.score-bar-bg { height: 5px; border-radius: 3px; background: #f3f4f6; margin: 10px 0 12px 0; }
.score-bar-fill { height: 5px; border-radius: 3px; }
.insight-box {
    background: #f0f7ff; border-left: 3px solid #2563eb;
    border-radius: 0 6px 6px 0; padding: 14px 18px;
    margin-bottom: 20px; font-size: 14px; line-height: 1.6; color: #1e3a5f;
}
.warning-box {
    background: #fffbeb; border-left: 3px solid #f59e0b;
    border-radius: 0 6px 6px 0; padding: 14px 18px;
    margin-bottom: 20px; font-size: 14px; line-height: 1.6; color: #78350f;
}
.empty-state { text-align: center; padding: 60px 20px; color: #9ca3af; }
.dim-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; }
.dim-cell { font-size: 11px; color: #6b7280; }
.dim-val { font-size: 14px; font-weight: 600; color: #111827; margin-top: 2px; }
.suggest-card {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
}
.suggest-title { font-size: 11px; font-weight: 700; color: #1d4ed8; letter-spacing: 0.06em; margin-bottom: 4px; }
.suggest-score { font-size: 28px; font-weight: 700; color: #1d4ed8; line-height: 1; }
.suggest-kw { font-size: 11px; color: #3b82f6; margin-top: 2px; }
.suggest-reason { font-size: 12px; color: #1e40af; margin-top: 6px; line-height: 1.5; }
.legend-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 12px; }
.legend-table td { padding: 6px 10px; border-bottom: 0.5px solid #f3f4f6; }
.legend-table tr:last-child td { border-bottom: none; }
.badge {
    display: inline-block; font-size: 10px; font-weight: 600;
    padding: 2px 8px; border-radius: 10px; margin-left: 6px;
    vertical-align: middle;
}
.badge-urgent { background: #fee2e2; color: #dc2626; }
.badge-bumped { background: #fef3c7; color: #d97706; }
.badge-low-conf { background: #f3f4f6; color: #6b7280; }
.conf-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
</style>
""", unsafe_allow_html=True)

# ── KEYWORD MAP ────────────────────────────────────────────────────────────────
KEYWORD_MAP = {
    "chatbot":             (4, "Established pattern, many off-the-shelf frameworks"),
    "chat":                (4, "Established pattern, many off-the-shelf frameworks"),
    "q&a":                 (4, "RAG architecture is well-documented and deployable"),
    "faq":                 (4, "RAG architecture is well-documented and deployable"),
    "knowledge base":      (4, "RAG architecture is well-documented and deployable"),
    "document":            (4, "Document retrieval is a solved problem with good tooling"),
    "search":              (4, "Search and retrieval tooling is mature"),
    "summaris":            (4, "LLM summarisation is reliable and easy to deploy"),
    "summariz":            (4, "LLM summarisation is reliable and easy to deploy"),
    "dashboard":           (4, "BI tooling is mature, low custom build required"),
    "report":              (4, "Reporting pipelines are straightforward to automate"),
    "classifier":          (3, "Requires labelled training data and model tuning"),
    "classif":             (3, "Requires labelled training data and model tuning"),
    "triage":              (3, "Rule logic plus human override layer adds complexity"),
    "routing":             (3, "Routing logic requires careful edge-case handling"),
    "automation":          (3, "Depends heavily on quality of upstream data and APIs"),
    "automat":             (3, "Depends heavily on quality of upstream data and APIs"),
    "compliance":          (3, "Compliance rules must be codified precisely before automation"),
    "recommendation":      (3, "Recommendation engines require user behaviour data at scale"),
    "personalisation":     (3, "Personalisation requires integrated member data"),
    "personalization":     (3, "Personalisation requires integrated member data"),
    "prediction":          (2, "Predictive models require clean historical data and retraining pipelines"),
    "predictive":          (2, "Predictive models require clean historical data and retraining pipelines"),
    "forecast":            (2, "Forecasting models require significant data preparation"),
    "machine learning":    (2, "Custom ML requires data science resources and MLOps infrastructure"),
    "at-risk":             (2, "Requires integrated behavioural and transactional data"),
    "churn":               (2, "Churn models require longitudinal member data across systems"),
    "sentiment":           (2, "Sentiment models need labelled data and ongoing calibration"),
    "risk model":          (2, "Risk modelling requires actuarial input and regulatory sign-off"),
    "integrated platform": (1, "Cross-system integration is the highest complexity build"),
    "integration":         (1, "Cross-system integration is the highest complexity build"),
    "data layer":          (1, "Data infrastructure work precedes any AI deployment"),
    "data platform":       (1, "Data infrastructure work precedes any AI deployment"),
    "unified":             (2, "Unification requires data mapping and governance work"),
}

def suggest_build_ease(name):
    name_lower = name.lower()
    for kw, (score, reason) in KEYWORD_MAP.items():
        if kw in name_lower:
            return score, reason, kw
    return None, None, None

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
WORKSHOP_CASES = [
    {"Use case": "Claims triage automation", "Owner": "James Tran",
     "Client priority": 5, "Strategic impact": 5, "Build ease": 3, "Data readiness": 3,
     "Urgent": True, "Confidence": "High", "Quote": "We spend hours manually reviewing straightforward claims that could be routed automatically."},
    {"Use case": "Marketing compliance checker", "Owner": "Melissa Hartley",
     "Client priority": 4, "Strategic impact": 3, "Build ease": 5, "Data readiness": 5,
     "Urgent": False, "Confidence": "High", "Quote": "Every campaign goes through a manual compliance review that takes two days minimum."},
    {"Use case": "At-risk member identification", "Owner": "David Nguyen",
     "Client priority": 4, "Strategic impact": 5, "Build ease": 2, "Data readiness": 2,
     "Urgent": False, "Confidence": "Medium", "Quote": "We know some members are about to churn but we only find out after they leave."},
    {"Use case": "Policy document Q&A", "Owner": "Sandra Okafor",
     "Client priority": 3, "Strategic impact": 3, "Build ease": 4, "Data readiness": 4,
     "Urgent": False, "Confidence": "High", "Quote": "Staff spend time searching policy documents for answers members could find themselves."},
]

EMPTY_CASE = {"Use case": "", "Owner": "", "Client priority": 3, "Strategic impact": 3,
              "Build ease": 3, "Data readiness": 3, "Urgent": False, "Confidence": "High", "Quote": ""}

COLORS      = ["#2563eb", "#7c3aed", "#0891b2", "#64748b", "#d97706", "#059669"]
RANK_LABELS = ["First priority", "Second priority", "Third priority",
               "Fourth priority", "Fifth priority", "Sixth priority"]
CONF_COLORS = {"High": "#22c55e", "Medium": "#f59e0b", "Low": "#ef4444"}

PHASE_1_MAX = 2
PHASE_2_MAX = 3

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "cases" not in st.session_state:
    st.session_state.cases = []

# ── SCORING ────────────────────────────────────────────────────────────────────
def calculate_scores(cases, w_priority, w_impact, w_ease, w_data):
    valid = [c for c in cases if str(c.get("Use case", "")).strip()]
    if not valid:
        return []
    total_w = w_priority + w_impact + w_ease + w_data
    if total_w == 0:
        return [dict(**c, Score=0.0) for c in valid]
    results = []
    for c in valid:
        raw = (c["Client priority"] * w_priority + c["Strategic impact"] * w_impact +
               c["Build ease"] * w_ease + c["Data readiness"] * w_data)
        score = round(raw / (5 * total_w) * 100, 1)
        results.append(dict(**c, Score=score))
    return sorted(results, key=lambda x: (x.get("Urgent", False), x["Score"]), reverse=True)

def base_phase(row):
    if row["Data readiness"] <= 2:
        return 3, "Requires data integration work before deployment"
    if row["Score"] >= 65:
        return 1, "High score and data is ready"
    if row["Score"] >= 50:
        return 2, "Strong candidate for second wave"
    return 3, "Lower priority or dependency on earlier phases"

def assign_phases(scored):
    phases = {1: [], 2: [], 3: []}
    for row in scored:
        if row.get("Urgent", False):
            phases[1].append({**row, "bumped": False,
                              "phase_reason": "Marked urgent — overrides scoring"})
            continue
        target, reason = base_phase(row)
        if target == 1:
            if len(phases[1]) < PHASE_1_MAX:
                phases[1].append({**row, "bumped": False, "phase_reason": reason})
            elif len(phases[2]) < PHASE_2_MAX:
                phases[2].append({**row, "bumped": True,
                                  "phase_reason": reason + " (moved — Phase 1 at capacity)"})
            else:
                phases[3].append({**row, "bumped": True,
                                  "phase_reason": reason + " (moved — Phases 1 and 2 at capacity)"})
        elif target == 2:
            if len(phases[2]) < PHASE_2_MAX:
                phases[2].append({**row, "bumped": False, "phase_reason": reason})
            else:
                phases[3].append({**row, "bumped": True,
                                  "phase_reason": reason + " (moved — Phase 2 at capacity)"})
        else:
            phases[3].append({**row, "bumped": False, "phase_reason": reason})
    return phases

def generate_insight(scored):
    if not scored:
        return "", "insight"
    top = scored[0]
    blocked = [s for s in scored if s["Strategic impact"] >= 4 and s["Data readiness"] <= 2]
    if blocked:
        names = " and ".join(s["Use case"] for s in blocked)
        return (f"<b>Structural alert:</b> {names} score highly on strategic impact but depend on "
                f"data that is not yet integrated or ready. A data integration workstream must run "
                f"in parallel or these use cases will underperform regardless of build quality. "
                f"Recommended first move: <b>{top['Use case']}</b>."), "warning"
    return (f"Based on current weights, <b>{top['Use case']}</b> is the strongest first deployment. "
            f"It scores highest across client urgency, impact, and feasibility."), "insight"

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Scoring weights")
    st.caption("Auto-normalised. Adjust to reflect what matters most for this client.")
    w_priority = st.slider("Client priority",  0, 10, 5)
    w_impact   = st.slider("Strategic impact", 0, 10, 6)
    w_ease     = st.slider("Build ease",       0, 10, 5)
    w_data     = st.slider("Data readiness",   0, 10, 4)
    st.divider()
    st.markdown("**Scoring guide**")
    st.markdown("""<div style="font-size:12px;color:#6b7280;line-height:1.9;">
    <b>Client priority</b> — urgency named by stakeholders<br>
    <b>Strategic impact</b> — value if successfully deployed<br>
    <b>Build ease</b> — 5 = simple · 1 = complex infrastructure<br>
    <b>Data readiness</b> — quality and availability of required data<br>
    <b>Urgent flag</b> — overrides scoring, forces Phase 1<br>
    <b>Confidence</b> — how certain are we about these scores
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"**Phase capacity**")
    st.caption(f"Phase 1: max {PHASE_1_MAX} items · Phase 2: max {PHASE_2_MAX} items")
    st.divider()
    if st.button("Load health insurer example", use_container_width=True):
        st.session_state.cases = [c.copy() for c in WORKSHOP_CASES]
        st.rerun()
    if st.button("Clear all", use_container_width=True):
        st.session_state.cases = []
        st.rerun()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("## AI opportunity prioritiser")
st.caption("Discovery workshop synthesis tool — score use cases, surface priorities, defend recommendations.")
st.divider()

scored = calculate_scores(st.session_state.cases, w_priority, w_impact, w_ease, w_data)

tab1, tab2, tab3, tab4 = st.tabs(["Priority matrix", "Rankings", "Phase timeline", "Edit use cases"])

# ── TAB 1: MATRIX ──────────────────────────────────────────────────────────────
with tab1:
    if not scored:
        st.markdown('<div class="empty-state"><div style="font-size:32px;margin-bottom:12px;">◈</div><div style="font-size:16px;font-weight:500;color:#6b7280;margin-bottom:8px;">No use cases yet</div><div style="font-size:13px;color:#9ca3af;">Add use cases in the Edit tab or load the example from the sidebar.</div></div>', unsafe_allow_html=True)
    else:
        fig = go.Figure()
        for i, row in enumerate(scored):
            color = COLORS[i % len(COLORS)]
            urgent_ring = dict(width=3, color="#dc2626") if row.get("Urgent") else dict(width=2, color="white")
            quote_text = f"<br><i>\"{row['Quote']}\"</i><br>— {row['Owner']}" if row.get("Quote") else f"<br>Owner: {row['Owner']}"
            fig.add_trace(go.Scatter(
                x=[row["Build ease"]],
                y=[row["Strategic impact"]],
                mode="markers+text",
                marker=dict(
                    size=row["Data readiness"] * 10 + 22,
                    color=color, opacity=0.88,
                    line=urgent_ring
                ),
                text=[str(i + 1)],
                textposition="middle center",
                textfont=dict(size=11, color="white", family="sans-serif"),
                name=f"{i+1}. {row['Use case']}",
                hovertemplate=(
                    f"<b>{row['Use case']}</b><br>"
                    f"Score: {row['Score']}%<br>"
                    f"Build ease: {row['Build ease']}/5<br>"
                    f"Strategic impact: {row['Strategic impact']}/5<br>"
                    f"Data readiness: {row['Data readiness']}/5"
                    f"{quote_text}<extra></extra>"
                )
            ))

        fig.add_hline(y=3, line_dash="dot", line_color="#d1d5db", line_width=1)
        fig.add_vline(x=3, line_dash="dot", line_color="#d1d5db", line_width=1)
        for ann in [
            (4.5, 5.35, "Quick wins"), (1.6, 5.35, "Strategic bets"),
            (4.5, 0.7, "Fill-ins"),   (1.6, 0.7, "Avoid"),
        ]:
            fig.add_annotation(x=ann[0], y=ann[1], text=ann[2], showarrow=False,
                font=dict(size=11, color="#c4c4c4"), xanchor="center")

        fig.update_layout(
            xaxis=dict(title="Build ease  (1 = complex · 5 = straightforward)",
                       range=[0.5, 5.8], showgrid=False, zeroline=False, tickvals=[1,2,3,4,5]),
            yaxis=dict(title="Strategic impact  (1 = low · 5 = high)",
                       range=[0.5, 5.6], showgrid=False, zeroline=False, tickvals=[1,2,3,4,5]),
            plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
            height=480, margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family="sans-serif", size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Legend table below chart
        rows_html = ""
        for i, row in enumerate(scored):
            color = COLORS[i % len(COLORS)]
            urgent_badge = '<span class="badge badge-urgent">URGENT</span>' if row.get("Urgent") else ""
            conf = row.get("Confidence", "High")
            conf_color = CONF_COLORS.get(conf, "#6b7280")
            rows_html += f"""<tr>
                <td><span style="display:inline-block;width:20px;height:20px;border-radius:50%;
                    background:{color};color:white;font-size:10px;font-weight:700;
                    text-align:center;line-height:20px;">{i+1}</span></td>
                <td style="color:#111827;font-weight:500;">{row['Use case']}{urgent_badge}</td>
                <td style="color:#6b7280;">{row['Owner']}</td>
                <td style="color:#111827;font-weight:600;">{row['Score']}%</td>
                <td><span class="conf-dot" style="background:{conf_color};"></span>
                    <span style="font-size:12px;color:{conf_color};">{conf}</span></td>
            </tr>"""
        st.markdown(f"""
        <table class="legend-table">
            <thead><tr>
                <th style="font-size:10px;color:#9ca3af;text-align:left;padding:4px 10px;">#</th>
                <th style="font-size:10px;color:#9ca3af;text-align:left;padding:4px 10px;">Use case</th>
                <th style="font-size:10px;color:#9ca3af;text-align:left;padding:4px 10px;">Owner</th>
                <th style="font-size:10px;color:#9ca3af;text-align:left;padding:4px 10px;">Score</th>
                <th style="font-size:10px;color:#9ca3af;text-align:left;padding:4px 10px;">Confidence</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)
        st.caption("Bubble size = data readiness. Hover for scores and stakeholder quotes. Red ring = urgent.")

# ── TAB 2: RANKINGS ────────────────────────────────────────────────────────────
with tab2:
    if not scored:
        st.markdown('<div class="empty-state"><div style="font-size:32px;margin-bottom:12px;">◈</div><div style="font-size:16px;font-weight:500;color:#6b7280;">No use cases scored yet</div></div>', unsafe_allow_html=True)
    else:
        insight_text, insight_type = generate_insight(scored)
        st.markdown(f'<div class="{"warning-box" if insight_type=="warning" else "insight-box"}">{insight_text}</div>', unsafe_allow_html=True)

        left, right = st.columns([3, 2])
        with left:
            st.markdown("#### Ranked use cases")
            for i, row in enumerate(scored):
                color = COLORS[i % len(COLORS)]
                label = RANK_LABELS[i] if i < len(RANK_LABELS) else f"#{i+1}"
                score = row["Score"]
                conf = row.get("Confidence", "High")
                conf_color = CONF_COLORS.get(conf, "#6b7280")
                urgent_badge = '<span class="badge badge-urgent">URGENT</span>' if row.get("Urgent") else ""
                quote_block = (f'<div style="font-size:12px;color:#6b7280;font-style:italic;'
                               f'margin-top:8px;padding-top:8px;border-top:0.5px solid #f3f4f6;">'
                               f'"{row["Quote"]}" <span style="font-style:normal;">— {row["Owner"]}</span></div>'
                               if row.get("Quote") else "")
                st.markdown(f"""
                <div class="rec-card {"urgent" if row.get("Urgent") else ""}"
                     style="border-left:4px solid {color};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div style="flex:1;">
                            <div style="font-size:10px;color:{color};font-weight:700;
                                 letter-spacing:0.06em;margin-bottom:4px;">
                                {label.upper()}{urgent_badge}
                            </div>
                            <div style="font-size:16px;font-weight:600;color:#111827;margin-bottom:2px;">
                                {row['Use case']}
                            </div>
                            <div style="display:flex;align-items:center;gap:6px;">
                                <span class="conf-dot" style="background:{conf_color};"></span>
                                <span style="font-size:12px;color:{conf_color};">{conf} confidence</span>
                            </div>
                        </div>
                        <div style="text-align:right;flex-shrink:0;margin-left:16px;">
                            <div style="font-size:26px;font-weight:700;color:{color};line-height:1;">{score}%</div>
                            <div style="font-size:10px;color:#9ca3af;">weighted score</div>
                        </div>
                    </div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:{score}%;background:{color};"></div>
                    </div>
                    <div class="dim-grid">
                        <div class="dim-cell">Client priority<div class="dim-val">{row['Client priority']}/5</div></div>
                        <div class="dim-cell">Strategic impact<div class="dim-val">{row['Strategic impact']}/5</div></div>
                        <div class="dim-cell">Build ease<div class="dim-val">{row['Build ease']}/5</div></div>
                        <div class="dim-cell">Data readiness<div class="dim-val">{row['Data readiness']}/5</div></div>
                    </div>
                    {quote_block}
                </div>""", unsafe_allow_html=True)

        with right:
            st.markdown("#### What the scores reveal")
            st.markdown("""<div style="font-size:13px;color:#374151;line-height:1.8;">
            <p>Top-right = <b>quick wins</b>: high impact, easy to build, data ready.</p>
            <p>High impact + low data readiness = <b>strategic bet</b>: the opportunity is real
            but data preparation must run in parallel.</p>
            <p><b>Low confidence</b> scores flag use cases where you need more information
            before committing to a recommendation.</p>
            <p>Adjust sidebar weights to reflect client priorities and watch rankings shift.</p>
            </div>""", unsafe_allow_html=True)
            st.divider()
            csv = pd.DataFrame(scored).to_csv(index=False)
            st.download_button("Export to CSV", csv,
                "ai_opportunity_priorities.csv", "text/csv", use_container_width=True)

# ── TAB 3: PHASE TIMELINE ──────────────────────────────────────────────────────
with tab3:
    if not scored:
        st.markdown('<div class="empty-state"><div style="font-size:32px;margin-bottom:12px;">◈</div><div style="font-size:16px;font-weight:500;color:#6b7280;">No use cases yet</div></div>', unsafe_allow_html=True)
    else:
        phases = assign_phases(scored)

        st.markdown("#### Recommended deployment sequence")
        col_info = st.columns(3)
        phase_meta = {
            1: ("Deploy now",          "#2563eb", f"Max {PHASE_1_MAX} items"),
            2: ("Second wave",         "#7c3aed", f"Max {PHASE_2_MAX} items"),
            3: ("After data foundation","#64748b", "No cap — data prep required"),
        }
        for idx, (ph, (label, color, cap)) in enumerate(phase_meta.items()):
            with col_info[idx]:
                count = len(phases[ph])
                st.markdown(f"""<div style="border-left:3px solid {color};padding:8px 12px;
                    background:#fafafa;border-radius:0 6px 6px 0;">
                    <div style="font-size:10px;color:{color};font-weight:700;
                         letter-spacing:0.05em;">PHASE {ph}</div>
                    <div style="font-size:15px;font-weight:600;color:#111827;">{label}</div>
                    <div style="font-size:11px;color:#9ca3af;">{count} use case{'s' if count!=1 else ''} · {cap}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        phase_colors = {1: "#2563eb", 2: "#7c3aed", 3: "#64748b"}
        x_ranges = {1: (0, 2.5), 2: (3, 5.5), 3: (6, 8.5)}

        fig2 = go.Figure()
        y_pos = 0
        y_max = 0

        for ph in [1, 2, 3]:
            items = phases[ph]
            color = phase_colors[ph]
            x0, x1 = x_ranges[ph]
            for item in items:
                bar_color = "#f59e0b" if item.get("bumped") else (
                    "#dc2626" if item.get("Urgent") else color)
                dash = "dot" if item.get("bumped") else "solid"
                fig2.add_trace(go.Scatter(
                    x=[x0, x1], y=[y_pos, y_pos],
                    mode="lines",
                    line=dict(color=bar_color, width=16, dash=dash),
                    hovertemplate=(
                        f"<b>{item['Use case']}</b><br>"
                        f"Phase {ph}<br>"
                        f"Score: {item['Score']}%<br>"
                        f"{item['phase_reason']}"
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))
                badges = ""
                if item.get("Urgent"):
                    badges += " [URGENT]"
                if item.get("bumped"):
                    badges += " [capacity overflow]"
                fig2.add_annotation(
                    x=x1 + 0.15, y=y_pos,
                    text=f"  {item['Use case']}  {item['Score']}%{badges}",
                    showarrow=False, xanchor="left", yanchor="middle",
                    font=dict(size=12, color="#111827" if not item.get("bumped") else "#d97706")
                )
                y_pos += 1
            if items:
                y_pos += 0.4
            y_max = y_pos

        for ph in [1, 2, 3]:
            x0, x1 = x_ranges[ph]
            fig2.add_vrect(x0=x0, x1=x1, fillcolor=phase_colors[ph],
                           opacity=0.04, layer="below", line_width=0)
            fig2.add_annotation(
                x=(x0 + x1) / 2, y=y_max + 0.3,
                text=f"Phase {ph}", showarrow=False,
                font=dict(size=11, color=phase_colors[ph]),
                xanchor="center"
            )

        fig2.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 15]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-0.5, y_max + 0.8]),
            plot_bgcolor="white", paper_bgcolor="white",
            height=max(280, int(y_max * 80) + 120),
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(family="sans-serif", size=12)
        )
        st.plotly_chart(fig2, use_container_width=True)

        bumped = [i for ph in phases.values() for i in ph if i.get("bumped")]
        data_blocked = [i for i in phases[3] if i["Data readiness"] <= 2 and not i.get("bumped")]

        if bumped:
            names = ", ".join(i["Use case"] for i in bumped)
            st.markdown(f"""<div style="background:#fffbeb;border-left:3px solid #f59e0b;
                border-radius:0 6px 6px 0;padding:12px 16px;font-size:13px;
                color:#78350f;line-height:1.6;margin-bottom:10px;">
                <b>Capacity overflow:</b> {names} scored for an earlier phase but were moved
                due to phase capacity limits. Review capacity settings in the sidebar or
                adjust scores to reflect true priority ordering.
            </div>""", unsafe_allow_html=True)
        if data_blocked:
            st.markdown("""<div style="background:#f0f9ff;border-left:3px solid #0891b2;
                border-radius:0 6px 6px 0;padding:12px 16px;font-size:13px;
                color:#0c4a6e;line-height:1.6;">
                <b>Data foundation note:</b> Phase 3 contains use cases blocked by data readiness.
                A data integration workstream should begin in parallel with Phase 1
                so Phase 3 is not delayed when earlier phases complete.
            </div>""", unsafe_allow_html=True)

# ── TAB 4: EDIT ────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### Add a use case")
    st.caption("Type a name and the tool suggests a Build ease score from keywords. Override any suggestion before adding.")

    with st.expander("New use case", expanded=not bool(st.session_state.cases)):
        new_name  = st.text_input("Use case name", placeholder="e.g. Claims triage automation")
        new_owner = st.text_input("Stakeholder / owner", placeholder="e.g. James Tran")
        new_quote = st.text_input("Key quote from workshop (optional)",
                                  placeholder='e.g. "We spend hours on claims that could route automatically"')

        suggested_ease, reason, matched_kw = suggest_build_ease(new_name)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            new_priority = st.number_input("Client priority",  1, 5, 3, key="np")
        with c2:
            new_impact   = st.number_input("Strategic impact", 1, 5, 3, key="ni")
        with c3:
            if suggested_ease:
                st.markdown(f"""
                <div class="suggest-card">
                    <div class="suggest-title">BUILD EASE SUGGESTED</div>
                    <div class="suggest-score">{suggested_ease}<span style="font-size:14px;
                         font-weight:400;color:#60a5fa;">/5</span></div>
                    <div class="suggest-kw">matched keyword: "{matched_kw}"</div>
                    <div class="suggest-reason">{reason}</div>
                </div>""", unsafe_allow_html=True)
                new_ease = st.number_input("Override build ease", 1, 5, suggested_ease,
                                           key="ne", label_visibility="collapsed")
            else:
                new_ease = st.number_input("Build ease", 1, 5, 3, key="ne")
        with c4:
            new_data = st.number_input("Data readiness", 1, 5, 3, key="nd")

        conf_col, urgent_col = st.columns(2)
        with conf_col:
            new_conf = st.selectbox("Confidence in scores",
                                    ["High", "Medium", "Low"], key="nc")
        with urgent_col:
            new_urgent = st.checkbox("Mark as urgent",
                help="Urgent use cases bypass scoring and go directly to Phase 1", key="nu")
            if new_urgent:
                st.markdown('<div style="font-size:12px;color:#dc2626;margin-top:4px;">'
                            'This use case will be placed in Phase 1 regardless of score.</div>',
                            unsafe_allow_html=True)

        if st.button("Add use case", type="primary"):
            if new_name.strip():
                st.session_state.cases.append({
                    "Use case": new_name.strip(), "Owner": new_owner.strip(),
                    "Client priority": new_priority, "Strategic impact": new_impact,
                    "Build ease": new_ease, "Data readiness": new_data,
                    "Urgent": new_urgent, "Confidence": new_conf,
                    "Quote": new_quote.strip()
                })
                st.rerun()
            else:
                st.warning("Please enter a use case name.")

    if st.session_state.cases:
        st.divider()
        st.markdown("#### Current use cases")
        st.caption("Edit any score directly. Delete rows by selecting and pressing backspace. Click Apply to update.")
        display_cols = ["Use case", "Owner", "Client priority", "Strategic impact",
                        "Build ease", "Data readiness", "Urgent", "Confidence"]
        df_edit = pd.DataFrame(st.session_state.cases)[display_cols]
        edited = st.data_editor(
            df_edit, num_rows="dynamic", use_container_width=True,
            column_config={
                "Use case":         st.column_config.TextColumn("Use case", width="large"),
                "Owner":            st.column_config.TextColumn("Owner", width="medium"),
                "Client priority":  st.column_config.NumberColumn("Client priority",  min_value=1, max_value=5, step=1),
                "Strategic impact": st.column_config.NumberColumn("Strategic impact", min_value=1, max_value=5, step=1),
                "Build ease":       st.column_config.NumberColumn("Build ease",       min_value=1, max_value=5, step=1),
                "Data readiness":   st.column_config.NumberColumn("Data readiness",   min_value=1, max_value=5, step=1),
                "Urgent":           st.column_config.CheckboxColumn("Urgent"),
                "Confidence":       st.column_config.SelectboxColumn("Confidence", options=["High","Medium","Low"]),
            }
        )
        ca, cb = st.columns([1, 3])
        with ca:
            if st.button("Apply changes", type="primary", use_container_width=True):
                records = edited.to_dict("records")
                existing_quotes = {c["Use case"]: c.get("Quote","")
                                   for c in st.session_state.cases}
                for r in records:
                    r["Quote"] = existing_quotes.get(r.get("Use case",""), "")
                st.session_state.cases = [r for r in records
                                          if str(r.get("Use case","")).strip()]
                st.rerun()
        with cb:
            st.caption("Quote field is preserved on apply. Edit quotes by removing and re-adding the use case.")
