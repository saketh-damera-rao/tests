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
    padding: 16px 20px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
    background: white;
}
.score-bar-bg {
    height: 5px; border-radius: 3px;
    background: #f3f4f6; margin: 10px 0 12px 0;
}
.score-bar-fill { height: 5px; border-radius: 3px; }
.insight-box {
    background: #f0f7ff; border-left: 3px solid #2563eb;
    border-radius: 0 6px 6px 0; padding: 14px 18px;
    margin-bottom: 20px; font-size: 14px;
    line-height: 1.6; color: #1e3a5f;
}
.warning-box {
    background: #fffbeb; border-left: 3px solid #f59e0b;
    border-radius: 0 6px 6px 0; padding: 14px 18px;
    margin-bottom: 20px; font-size: 14px;
    line-height: 1.6; color: #78350f;
}
.empty-state {
    text-align: center; padding: 60px 20px; color: #9ca3af;
}
.dim-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 10px; margin-top: 10px;
}
.dim-cell { font-size: 11px; color: #6b7280; }
.dim-val { font-size: 14px; font-weight: 600; color: #111827; margin-top: 2px; }
.kw-tag {
    display: inline-block; font-size: 10px; padding: 2px 8px;
    border-radius: 10px; background: #eff6ff; color: #1d4ed8;
    margin-right: 4px; margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# --- Keyword to Build ease mapping ---
# Higher = easier to build. Scale 1-5.
KEYWORD_MAP = {
    "chatbot":             {"Build ease": 4, "reason": "Established pattern, many off-the-shelf frameworks"},
    "chat":                {"Build ease": 4, "reason": "Established pattern, many off-the-shelf frameworks"},
    "q&a":                 {"Build ease": 4, "reason": "RAG architecture is well-documented and deployable"},
    "faq":                 {"Build ease": 4, "reason": "RAG architecture is well-documented and deployable"},
    "knowledge base":      {"Build ease": 4, "reason": "RAG architecture is well-documented and deployable"},
    "document":            {"Build ease": 4, "reason": "Document retrieval is a solved problem with good tooling"},
    "search":              {"Build ease": 4, "reason": "Search and retrieval tooling is mature"},
    "dashboard":           {"Build ease": 4, "reason": "BI tooling is mature, low custom build required"},
    "report":              {"Build ease": 4, "reason": "Reporting pipelines are straightforward to automate"},
    "summaris":            {"Build ease": 4, "reason": "LLM summarisation is reliable and easy to deploy"},
    "summariz":            {"Build ease": 4, "reason": "LLM summarisation is reliable and easy to deploy"},
    "classifier":          {"Build ease": 3, "reason": "Requires labelled training data and model tuning"},
    "classif":             {"Build ease": 3, "reason": "Requires labelled training data and model tuning"},
    "triage":              {"Build ease": 3, "reason": "Rule logic plus human override layer adds complexity"},
    "routing":             {"Build ease": 3, "reason": "Routing logic requires careful edge-case handling"},
    "automation":          {"Build ease": 3, "reason": "Depends heavily on quality of upstream data and APIs"},
    "automat":             {"Build ease": 3, "reason": "Depends heavily on quality of upstream data and APIs"},
    "compliance":          {"Build ease": 3, "reason": "Compliance rules must be codified precisely before automation"},
    "recommendation":      {"Build ease": 3, "reason": "Recommendation engines require user behaviour data at scale"},
    "personalisation":     {"Build ease": 3, "reason": "Personalisation requires integrated member data"},
    "personalization":     {"Build ease": 3, "reason": "Personalisation requires integrated member data"},
    "prediction":          {"Build ease": 2, "reason": "Predictive models require clean historical data and retraining pipelines"},
    "predictive":          {"Build ease": 2, "reason": "Predictive models require clean historical data and retraining pipelines"},
    "forecast":            {"Build ease": 2, "reason": "Forecasting models require significant data preparation"},
    "machine learning":    {"Build ease": 2, "reason": "Custom ML requires data science resources and MLOps infrastructure"},
    "ml model":            {"Build ease": 2, "reason": "Custom ML requires data science resources and MLOps infrastructure"},
    "risk model":          {"Build ease": 2, "reason": "Risk modelling requires actuarial input and regulatory sign-off"},
    "at-risk":             {"Build ease": 2, "reason": "Requires integrated behavioural and transactional data"},
    "churn":               {"Build ease": 2, "reason": "Churn models require longitudinal member data across systems"},
    "sentiment":           {"Build ease": 2, "reason": "Sentiment models need labelled data and ongoing calibration"},
    "integrated platform": {"Build ease": 1, "reason": "Cross-system integration is the highest complexity build"},
    "integration":         {"Build ease": 1, "reason": "Cross-system integration is the highest complexity build"},
    "data layer":          {"Build ease": 1, "reason": "Data infrastructure work precedes any AI deployment"},
    "data platform":       {"Build ease": 1, "reason": "Data infrastructure work precedes any AI deployment"},
    "unified":             {"Build ease": 2, "reason": "Unification requires data mapping and governance work"},
}

def suggest_build_ease(name):
    name_lower = name.lower()
    for keyword, vals in KEYWORD_MAP.items():
        if keyword in name_lower:
            return vals["Build ease"], vals["reason"], keyword
    return None, None, None

WORKSHOP_CASES = [
    {"Use case": "Claims triage automation", "Owner": "James Tran",
     "Client priority": 5, "Strategic impact": 5, "Build ease": 3, "Data readiness": 3},
    {"Use case": "Marketing compliance checker", "Owner": "Melissa Hartley",
     "Client priority": 4, "Strategic impact": 3, "Build ease": 5, "Data readiness": 5},
    {"Use case": "At-risk member identification", "Owner": "David Nguyen",
     "Client priority": 4, "Strategic impact": 5, "Build ease": 2, "Data readiness": 2},
    {"Use case": "Policy document Q&A", "Owner": "Sandra Okafor",
     "Client priority": 3, "Strategic impact": 3, "Build ease": 4, "Data readiness": 4},
]

EMPTY_ROW = {
    "Use case": "", "Owner": "",
    "Client priority": 3, "Strategic impact": 3,
    "Build ease": 3, "Data readiness": 3
}

COLORS = ["#2563eb", "#7c3aed", "#0891b2", "#64748b", "#d97706", "#dc2626"]
RANK_LABELS = ["First priority", "Second priority", "Third priority", "Fourth priority"]

if "cases" not in st.session_state:
    st.session_state.cases = []

def calculate_scores(cases, w_priority, w_impact, w_ease, w_data):
    valid = [c for c in cases if str(c.get("Use case", "")).strip()]
    if not valid:
        return []
    total_w = w_priority + w_impact + w_ease + w_data
    if total_w == 0:
        return [dict(**c, Score=0.0) for c in valid]
    results = []
    for c in valid:
        raw = (
            c["Client priority"] * w_priority +
            c["Strategic impact"] * w_impact +
            c["Build ease"] * w_ease +
            c["Data readiness"] * w_data
        )
        score = round(raw / (5 * total_w) * 100, 1)
        results.append(dict(**c, Score=score))
    return sorted(results, key=lambda x: x["Score"], reverse=True)

def generate_insight(scored):
    if not scored:
        return "", "insight"
    top = scored[0]
    high_impact_low_data = [
        s for s in scored
        if s["Strategic impact"] >= 4 and s["Data readiness"] <= 2
    ]
    if high_impact_low_data:
        names = " and ".join(s["Use case"] for s in high_impact_low_data)
        return (
            f"<b>Structural alert:</b> {names} score highly on strategic impact "
            f"but depend on data that is not yet integrated or ready. "
            f"These use cases require a data layer workstream to run in parallel "
            f"or they will underperform regardless of how well the tool is built. "
            f"Recommended first move: <b>{top['Use case']}</b>, which balances "
            f"impact with feasibility given current data maturity."
        ), "warning"
    return (
        f"Based on current weights, <b>{top['Use case']}</b> is the strongest "
        f"first deployment. It scores highest across client urgency, impact, and "
        f"feasibility. Proceed to scoping with the relevant stakeholder."
    ), "insight"

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Scoring weights")
    st.caption("Weights are auto-normalised. Adjust to reflect what matters most for your client.")
    w_priority = st.slider("Client priority", 0, 10, 5)
    w_impact   = st.slider("Strategic impact", 0, 10, 6)
    w_ease     = st.slider("Build ease", 0, 10, 5)
    w_data     = st.slider("Data readiness", 0, 10, 4)
    st.divider()
    st.markdown("**Scoring guide**")
    st.markdown("""
    <div style="font-size:12px; color:#6b7280; line-height:1.8;">
    <b>Client priority</b> — urgency named by stakeholders<br>
    <b>Strategic impact</b> — value if successfully deployed<br>
    <b>Build ease</b> — 5 = straightforward · 1 = complex<br>
    <b>Data readiness</b> — availability and quality of data needed
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    if st.button("Load health insurer example", use_container_width=True):
        st.session_state.cases = [c.copy() for c in WORKSHOP_CASES]
        st.rerun()
    if st.button("Clear all", use_container_width=True):
        st.session_state.cases = []
        st.rerun()

# --- Header ---
st.markdown("## AI opportunity prioritiser")
st.caption("Discovery workshop synthesis tool — score use cases, surface priorities, defend recommendations.")
st.divider()

scored = calculate_scores(st.session_state.cases, w_priority, w_impact, w_ease, w_data)

tab1, tab2, tab3, tab4 = st.tabs(["Priority matrix", "Rankings", "Phase timeline", "Edit use cases"])

# ── TAB 1: MATRIX ──────────────────────────────────────────────────────────────
with tab1:
    if not scored:
        st.markdown('<div class="empty-state"><div style="font-size:32px;margin-bottom:12px;">◈</div><div style="font-size:16px;font-weight:500;color:#6b7280;margin-bottom:8px;">No use cases yet</div><div style="font-size:13px;color:#9ca3af;">Go to the Edit tab to add use cases,<br>or load the health insurer example from the sidebar.</div></div>', unsafe_allow_html=True)
    else:
        fig = go.Figure()
        for i, row in enumerate(scored):
            color = COLORS[i % len(COLORS)]
            fig.add_trace(go.Scatter(
                x=[row["Build ease"]], y=[row["Strategic impact"]],
                mode="markers",
                marker=dict(size=row["Data readiness"] * 10 + 20, color=color,
                            opacity=0.85, line=dict(width=2, color="white")),
                name=f"{i+1}. {row['Use case']} ({row['Score']}%)",
                hovertemplate=(
                    f"<b>{row['Use case']}</b><br>Score: {row['Score']}%<br>"
                    f"Build ease: {row['Build ease']}/5<br>"
                    f"Strategic impact: {row['Strategic impact']}/5<br>"
                    f"Data readiness: {row['Data readiness']}/5<br>"
                    f"Owner: {row['Owner']}<extra></extra>"
                )
            ))
            fig.add_annotation(
                x=row["Build ease"], y=row["Strategic impact"],
                text=f"  {i+1}. {row['Use case']}",
                showarrow=False, xanchor="left", yanchor="middle",
                font=dict(size=12, color="#111827"),
                xshift=row["Data readiness"] * 5 + 14
            )
        fig.add_hline(y=3, line_dash="dot", line_color="#d1d5db", line_width=1)
        fig.add_vline(x=3, line_dash="dot", line_color="#d1d5db", line_width=1)
        for ann in [
            dict(x=4.5, y=5.35, text="Quick wins"),
            dict(x=1.6, y=5.35, text="Strategic bets"),
            dict(x=4.5, y=0.7,  text="Fill-ins"),
            dict(x=1.6, y=0.7,  text="Avoid"),
        ]:
            fig.add_annotation(x=ann["x"], y=ann["y"], text=ann["text"],
                showarrow=False, font=dict(size=11, color="#c4c4c4"), xanchor="center")
        fig.update_layout(
            xaxis=dict(title="Build ease  (1 = complex · 5 = straightforward)",
                       range=[0.5, 8.5], showgrid=False, zeroline=False, tickvals=[1,2,3,4,5]),
            yaxis=dict(title="Strategic impact  (1 = low · 5 = high)",
                       range=[0.5, 5.6], showgrid=False, zeroline=False, tickvals=[1,2,3,4,5]),
            plot_bgcolor="white", paper_bgcolor="white", showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0, font=dict(size=12)),
            height=520, margin=dict(l=20, r=20, t=20, b=110),
            font=dict(family="sans-serif", size=12)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Bubble size reflects data readiness. Hover any bubble for full scores. Adjust weights in the sidebar to watch rankings shift.")

# ── TAB 2: RANKINGS ────────────────────────────────────────────────────────────
with tab2:
    if not scored:
        st.markdown('<div class="empty-state"><div style="font-size:32px;margin-bottom:12px;">◈</div><div style="font-size:16px;font-weight:500;color:#6b7280;margin-bottom:8px;">No use cases scored yet</div><div style="font-size:13px;color:#9ca3af;">Add use cases in the Edit tab to see ranked recommendations here.</div></div>', unsafe_allow_html=True)
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
                st.markdown(f"""
                <div class="rec-card" style="border-left:4px solid {color};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div style="font-size:10px;color:{color};font-weight:700;letter-spacing:0.06em;margin-bottom:4px;">{label.upper()}</div>
                            <div style="font-size:16px;font-weight:600;color:#111827;margin-bottom:2px;">{row['Use case']}</div>
                            <div style="font-size:12px;color:#6b7280;">{row['Owner']}</div>
                        </div>
                        <div style="text-align:right;flex-shrink:0;margin-left:16px;">
                            <div style="font-size:26px;font-weight:700;color:{color};line-height:1;">{score}%</div>
                            <div style="font-size:10px;color:#9ca3af;">weighted score</div>
                        </div>
                    </div>
                    <div class="score-bar-bg"><div class="score-bar-fill" style="width:{score}%;background:{color};"></div></div>
                    <div class="dim-grid">
                        <div class="dim-cell">Client priority<div class="dim-val">{row['Client priority']}/5</div></div>
                        <div class="dim-cell">Strategic impact<div class="dim-val">{row['Strategic impact']}/5</div></div>
                        <div class="dim-cell">Build ease<div class="dim-val">{row['Build ease']}/5</div></div>
                        <div class="dim-cell">Data readiness<div class="dim-val">{row['Data readiness']}/5</div></div>
                    </div>
                </div>""", unsafe_allow_html=True)
        with right:
            st.markdown("#### What the scores reveal")
            st.markdown("""<div style="font-size:13px;color:#374151;line-height:1.8;">
            <p>Top-right quadrant = <b>quick wins</b>: high impact, easy to build, data is ready.</p>
            <p>High impact but low data readiness = <b>strategic bet</b>: opportunity is real but data preparation must run first.</p>
            <p>Adjust sidebar weights to reflect what your client values most and watch rankings respond in real time.</p>
            </div>""", unsafe_allow_html=True)
            st.divider()
            csv = pd.DataFrame(scored).to_csv(index=False)
            st.download_button("Export rankings to CSV", csv,
                "ai_opportunity_priorities.csv", "text/csv", use_container_width=True)

# ── TAB 3: PHASE TIMELINE ──────────────────────────────────────────────────────
with tab3:
    if not scored:
        st.markdown('<div class="empty-state"><div style="font-size:32px;margin-bottom:12px;">◈</div><div style="font-size:16px;font-weight:500;color:#6b7280;margin-bottom:8px;">No use cases yet</div><div style="font-size:13px;color:#9ca3af;">Add and score use cases first to generate a phase timeline.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown("#### Recommended deployment sequence")
        st.caption("Phases are assigned based on weighted score and data readiness. Use cases with low data readiness are pushed to later phases regardless of score.")

        def assign_phase(row):
            if row["Data readiness"] <= 2:
                return 3, "Requires data integration work first"
            if row["Score"] >= 65:
                return 1, "High score and data is ready — deploy first"
            if row["Score"] >= 50:
                return 2, "Strong candidate for second wave"
            return 3, "Lower priority or dependency on earlier phases"

        phases = {1: [], 2: [], 3: []}
        for row in scored:
            phase, reason = assign_phase(row)
            phases[phase].append({**row, "reason": reason})

        phase_colors = {1: "#2563eb", 2: "#7c3aed", 3: "#64748b"}
        phase_labels = {
            1: "Phase 1 — Deploy now",
            2: "Phase 2 — Second wave",
            3: "Phase 3 — After data foundation"
        }

        fig2 = go.Figure()
        y_pos = 0
        y_labels = []
        y_ticks = []
        shapes = []

        phase_order = [1, 2, 3]
        x_start = {1: 0, 2: 3, 3: 6}
        x_end   = {1: 2.5, 2: 5.5, 3: 9}

        for phase in phase_order:
            items = phases[phase]
            color = phase_colors[phase]
            for item in items:
                y_ticks.append(y_pos)
                y_labels.append(item["Use case"])
                fig2.add_trace(go.Scatter(
                    x=[x_start[phase], x_end[phase]],
                    y=[y_pos, y_pos],
                    mode="lines",
                    line=dict(color=color, width=14),
                    hovertemplate=(
                        f"<b>{item['Use case']}</b><br>"
                        f"{phase_labels[phase]}<br>"
                        f"Score: {item['Score']}%<br>"
                        f"{item['reason']}"
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))
                fig2.add_annotation(
                    x=x_end[phase] + 0.15, y=y_pos,
                    text=f"  {item['Use case']}  ({item['Score']}%)",
                    showarrow=False, xanchor="left", yanchor="middle",
                    font=dict(size=12, color="#111827")
                )
                y_pos += 1

            if items:
                y_pos += 0.3

        for phase in phase_order:
            fig2.add_vrect(
                x0=x_start[phase], x1=x_end[phase],
                fillcolor=phase_colors[phase], opacity=0.04,
                layer="below", line_width=0
            )
            fig2.add_annotation(
                x=(x_start[phase] + x_end[phase]) / 2,
                y=y_pos + 0.2,
                text=phase_labels[phase],
                showarrow=False,
                font=dict(size=11, color=phase_colors[phase], family="sans-serif"),
                xanchor="center"
            )

        fig2.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 14]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-0.5, y_pos + 0.8]),
            plot_bgcolor="white", paper_bgcolor="white",
            height=max(300, y_pos * 80 + 120),
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(family="sans-serif", size=12)
        )

        st.plotly_chart(fig2, use_container_width=True)

        if phases[3]:
            st.markdown("""
            <div style="background:#fffbeb;border-left:3px solid #f59e0b;border-radius:0 6px 6px 0;
            padding:12px 16px;font-size:13px;color:#78350f;line-height:1.6;">
            <b>Data foundation note:</b> Phase 3 use cases depend on data that is not yet integrated or ready.
            A data integration workstream should begin in parallel with Phase 1 deployment
            so Phase 3 is not blocked when Phase 2 completes.
            </div>""", unsafe_allow_html=True)

# ── TAB 4: EDIT ────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### Add use cases")
    st.caption("Type a use case name and the tool will suggest a Build ease score based on keywords. You can override any suggestion before applying.")

    with st.expander("Add a new use case", expanded=not bool(st.session_state.cases)):
        new_name = st.text_input("Use case name", placeholder="e.g. Claims triage automation")
        new_owner = st.text_input("Owner / stakeholder", placeholder="e.g. James Tran")

        suggested_ease, reason, matched_kw = suggest_build_ease(new_name)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_priority = st.number_input("Client priority", 1, 5, 3, key="np")
        with col2:
            new_impact = st.number_input("Strategic impact", 1, 5, 3, key="ni")
        with col3:
            if suggested_ease:
                st.markdown(f"""
                <div style="font-size:11px;color:#6b7280;margin-bottom:4px;">Build ease</div>
                <span class="kw-tag">suggested: {suggested_ease} via "{matched_kw}"</span>
                """, unsafe_allow_html=True)
                new_ease = st.number_input("Override build ease", 1, 5, suggested_ease, key="ne",
                                           label_visibility="collapsed")
                st.caption(reason)
            else:
                new_ease = st.number_input("Build ease", 1, 5, 3, key="ne")
        with col4:
            new_data = st.number_input("Data readiness", 1, 5, 3, key="nd")

        if st.button("Add use case", type="primary"):
            if new_name.strip():
                st.session_state.cases.append({
                    "Use case": new_name.strip(),
                    "Owner": new_owner.strip(),
                    "Client priority": new_priority,
                    "Strategic impact": new_impact,
                    "Build ease": new_ease,
                    "Data readiness": new_data,
                })
                st.rerun()
            else:
                st.warning("Please enter a use case name.")

    if st.session_state.cases:
        st.divider()
        st.markdown("#### Current use cases")
        st.caption("Edit scores directly in the table. Click Apply to update the matrix.")

        df_edit = pd.DataFrame(st.session_state.cases)
        edited = st.data_editor(
            df_edit, num_rows="dynamic", use_container_width=True,
            column_config={
                "Use case":        st.column_config.TextColumn("Use case", width="large"),
                "Owner":           st.column_config.TextColumn("Owner", width="medium"),
                "Client priority": st.column_config.NumberColumn("Client priority", min_value=1, max_value=5, step=1),
                "Strategic impact":st.column_config.NumberColumn("Strategic impact", min_value=1, max_value=5, step=1),
                "Build ease":      st.column_config.NumberColumn("Build ease", min_value=1, max_value=5, step=1),
                "Data readiness":  st.column_config.NumberColumn("Data readiness", min_value=1, max_value=5, step=1),
            }
        )
        col_a, col_b = st.columns([1, 3])
        with col_a:
            if st.button("Apply changes", type="primary", use_container_width=True):
                records = edited.to_dict("records")
                st.session_state.cases = [r for r in records if str(r.get("Use case","")).strip()]
                st.rerun()
        with col_b:
            st.caption("Only rows with a use case name are included in scoring.")
