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
    height: 5px;
    border-radius: 3px;
    background: #f3f4f6;
    margin: 10px 0 12px 0;
}
.score-bar-fill { height: 5px; border-radius: 3px; }
.insight-box {
    background: #f0f7ff;
    border-left: 3px solid #2563eb;
    border-radius: 0 6px 6px 0;
    padding: 14px 18px;
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 1.6;
    color: #1e3a5f;
}
.warning-box {
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    border-radius: 0 6px 6px 0;
    padding: 14px 18px;
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 1.6;
    color: #78350f;
}
.dim-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 10px;
}
.dim-cell { font-size: 11px; color: #6b7280; }
.dim-val { font-size: 14px; font-weight: 600; color: #111827; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

DEFAULT_CASES = [
    {
        "Use case": "Claims triage automation",
        "Owner": "James Tran",
        "Client priority": 5,
        "Strategic impact": 5,
        "Build ease": 3,
        "Data readiness": 3
    },
    {
        "Use case": "Marketing compliance checker",
        "Owner": "Melissa Hartley",
        "Client priority": 4,
        "Strategic impact": 3,
        "Build ease": 5,
        "Data readiness": 5
    },
    {
        "Use case": "At-risk member identification",
        "Owner": "David Nguyen",
        "Client priority": 4,
        "Strategic impact": 5,
        "Build ease": 2,
        "Data readiness": 2
    },
    {
        "Use case": "Policy document Q&A",
        "Owner": "Sandra Okafor",
        "Client priority": 3,
        "Strategic impact": 3,
        "Build ease": 4,
        "Data readiness": 4
    },
]

COLORS = ["#2563eb", "#7c3aed", "#0891b2", "#64748b"]
RANK_LABELS = ["First priority", "Second priority", "Third priority", "Fourth priority"]

if "cases" not in st.session_state:
    st.session_state.cases = [c.copy() for c in DEFAULT_CASES]

def calculate_scores(cases, w_priority, w_impact, w_ease, w_data):
    total_w = w_priority + w_impact + w_ease + w_data
    if total_w == 0:
        return [dict(**c, Score=0.0) for c in cases]
    results = []
    for c in cases:
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

with st.sidebar:
    st.markdown("### Scoring weights")
    st.caption(
        "Weights are auto-normalised. Adjust to reflect what matters most for your client."
    )
    w_priority = st.slider("Client priority", 0, 10, 5)
    w_impact = st.slider("Strategic impact", 0, 10, 6)
    w_ease = st.slider("Build ease", 0, 10, 5)
    w_data = st.slider("Data readiness", 0, 10, 4)

    st.divider()
    st.markdown("**Scoring guide**")
    st.markdown("""
    <div style="font-size:12px; color:#6b7280; line-height:1.8;">
    <b>Client priority</b> — urgency named by stakeholders<br>
    <b>Strategic impact</b> — value delivered if it works<br>
    <b>Build ease</b> — 5 = straightforward, 1 = complex<br>
    <b>Data readiness</b> — availability and quality of data needed
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("**About**")
    st.caption(
        "Built for discovery workshop synthesis. "
        "Pre-loaded with outputs from an Australian health insurer AI opportunity session. "
        "Switch to the Edit tab to load your own use cases."
    )
    if st.button("Reset to workshop data", use_container_width=True):
        st.session_state.cases = [c.copy() for c in DEFAULT_CASES]
        st.rerun()

st.markdown("## AI opportunity prioritiser")
st.caption(
    "Discovery workshop synthesis · Australian health insurer · Internal AI deployment"
)
st.divider()

scored = calculate_scores(
    st.session_state.cases, w_priority, w_impact, w_ease, w_data
)

tab1, tab2, tab3 = st.tabs(["Priority matrix", "Rankings", "Edit use cases"])

with tab1:
    fig = go.Figure()

    for i, row in enumerate(scored):
        color = COLORS[i % len(COLORS)]
        label = f"{i+1}. {row['Use case']}"
        fig.add_trace(go.Scatter(
            x=[row["Build ease"]],
            y=[row["Strategic impact"]],
            mode="markers+text",
            marker=dict(
                size=row["Data readiness"] * 10 + 20,
                color=color,
                opacity=0.85,
                line=dict(width=2, color="white")
            ),
            text=[f"  {row['Use case']}"],
            textposition="middle right",
            textfont=dict(size=12, color="#111827"),
            name=label,
            hovertemplate=(
                f"<b>{row['Use case']}</b><br>"
                f"Score: {row['Score']}%<br>"
                f"Build ease: {row['Build ease']}/5<br>"
                f"Strategic impact: {row['Strategic impact']}/5<br>"
                f"Data readiness: {row['Data readiness']}/5<br>"
                f"Owner: {row['Owner']}"
                "<extra></extra>"
            )
        ))

    fig.add_hline(y=3, line_dash="dot", line_color="#d1d5db", line_width=1)
    fig.add_vline(x=3, line_dash="dot", line_color="#d1d5db", line_width=1)

    annotations = [
        dict(x=4.6, y=4.8, text="Quick wins", font=dict(size=11, color="#9ca3af")),
        dict(x=1.5, y=4.8, text="Strategic bets", font=dict(size=11, color="#9ca3af")),
        dict(x=4.6, y=1.2, text="Fill-ins", font=dict(size=11, color="#9ca3af")),
        dict(x=1.5, y=1.2, text="Avoid", font=dict(size=11, color="#9ca3af")),
    ]
    for a in annotations:
        fig.add_annotation(
            x=a["x"], y=a["y"], text=a["text"],
            showarrow=False, font=a["font"], xanchor="center"
        )

    fig.update_layout(
        xaxis=dict(
            title="Build ease  (1 = complex · 5 = straightforward)",
            range=[0.5, 6.2],
            showgrid=False,
            zeroline=False,
            tickvals=[1, 2, 3, 4, 5]
        ),
        yaxis=dict(
            title="Strategic impact  (1 = low · 5 = high)",
            range=[0.5, 5.5],
            showgrid=False,
            zeroline=False,
            tickvals=[1, 2, 3, 4, 5]
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="left",
            x=0,
            font=dict(size=12)
        ),
        height=500,
        margin=dict(l=20, r=20, t=20, b=100),
        font=dict(family="sans-serif", size=12)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Bubble size reflects data readiness. "
        "Hover over any bubble for full scores. "
        "Adjust dimension weights in the sidebar to see rankings shift in real time."
    )

with tab2:
    insight_text, insight_type = generate_insight(scored)
    box_class = "warning-box" if insight_type == "warning" else "insight-box"
    st.markdown(
        f'<div class="{box_class}">{insight_text}</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### Ranked use cases")
        for i, row in enumerate(scored):
            color = COLORS[i % len(COLORS)]
            label = RANK_LABELS[i] if i < len(RANK_LABELS) else f"#{i+1}"
            score = row["Score"]
            st.markdown(f"""
            <div class="rec-card" style="border-left: 4px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-size:10px; color:{color}; font-weight:700;
                             letter-spacing:0.06em; margin-bottom:4px;">
                            {label.upper()}
                        </div>
                        <div style="font-size:16px; font-weight:600; color:#111827;
                             margin-bottom:2px;">{row['Use case']}</div>
                        <div style="font-size:12px; color:#6b7280;">{row['Owner']}</div>
                    </div>
                    <div style="text-align:right; flex-shrink:0; margin-left:16px;">
                        <div style="font-size:26px; font-weight:700;
                             color:{color}; line-height:1;">{score}%</div>
                        <div style="font-size:10px; color:#9ca3af;">weighted score</div>
                    </div>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill"
                         style="width:{score}%; background:{color};"></div>
                </div>
                <div class="dim-grid">
                    <div class="dim-cell">Client priority<div class="dim-val">{row['Client priority']}/5</div></div>
                    <div class="dim-cell">Strategic impact<div class="dim-val">{row['Strategic impact']}/5</div></div>
                    <div class="dim-cell">Build ease<div class="dim-val">{row['Build ease']}/5</div></div>
                    <div class="dim-cell">Data readiness<div class="dim-val">{row['Data readiness']}/5</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("#### What the scores reveal")
        st.markdown("""
        <div style="font-size:13px; color:#374151; line-height:1.8;">
        <p>Use cases in the top-right quadrant of the matrix are <b>quick wins</b>:
        high impact, easy to build, data is ready.</p>
        <p>Use cases with high impact but low data readiness are <b>strategic bets</b>:
        the opportunity is real but a data integration workstream must precede or accompany deployment.</p>
        <p>A use case that ranks first overall but carries a data readiness score of 2 or below
        should be phased: start scoping now, begin data preparation in parallel.</p>
        <p>Try adjusting the sidebar weights. If data readiness doubles in importance,
        watch how the ranking changes. That conversation belongs in the debrief.</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        df_export = pd.DataFrame(scored)
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="Export rankings to CSV",
            data=csv,
            file_name="ai_opportunity_priorities.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab3:
    st.markdown("#### Use case scores")
    st.caption(
        "Edit any score directly. Add rows for new use cases. "
        "All scores run from 1 (low) to 5 (high). "
        "For Build ease, 5 = easy to build, 1 = significant infrastructure required."
    )

    df_edit = pd.DataFrame(st.session_state.cases)

    edited = st.data_editor(
        df_edit,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Use case": st.column_config.TextColumn(
                "Use case", width="large", required=True
            ),
            "Owner": st.column_config.TextColumn("Owner", width="medium"),
            "Client priority": st.column_config.NumberColumn(
                "Client priority", min_value=1, max_value=5, step=1
            ),
            "Strategic impact": st.column_config.NumberColumn(
                "Strategic impact", min_value=1, max_value=5, step=1
            ),
            "Build ease": st.column_config.NumberColumn(
                "Build ease", min_value=1, max_value=5, step=1
            ),
            "Data readiness": st.column_config.NumberColumn(
                "Data readiness", min_value=1, max_value=5, step=1
            ),
        }
    )

    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("Apply changes", type="primary", use_container_width=True):
            st.session_state.cases = edited.to_dict("records")
            st.rerun()
    with col_b:
        st.caption(
            "Changes apply to the matrix and rankings instantly after clicking Apply."
        )
