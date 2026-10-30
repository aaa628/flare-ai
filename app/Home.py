import streamlit as st

from data import overview_stats

st.set_page_config(page_title="Flare AI", page_icon="🔥", layout="wide")

st.markdown(
    "<div style='letter-spacing:.25em;font-size:.75rem;color:#8a97b2'>628 AEROSPACE &nbsp;·&nbsp; "
    "<span style='color:#3ddc97'>● SYSTEM ONLINE</span></div>",
    unsafe_allow_html=True,
)
st.title("Flare AI")
st.caption("Evidence-graded fire safety insights from NASA microgravity combustion data.")

st.markdown(
    "Without gravity, hot gas does not rise, so flames behave differently: they can "
    "turn spherical, burn at lower airflow, and may not extinguish the way they do on Earth. "
    "That matters for ISS, Moon and Mars missions. Flare AI organises what NASA's experiments "
    "actually showed, labels how strong the evidence is, and says so when the data runs out."
)

stats = overview_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Verified experiments", stats["records_verified"])
c2.metric("Records extracted", stats["records_total"])
c3.metric("Source documents", stats["sources"])
c4.metric("Dataset status", stats["status"])

if stats["records_verified"] == 0:
    st.info(
        "No verified records yet. Figures above are computed from `data/experiments.csv`, "
        "and only rows checked by a second team member are counted."
    )
else:
    st.write("Programs covered:", ", ".join(stats["programs"]))

st.divider()
st.subheader("Screens")
st.markdown(
    "- **Flame Explorer**: search and filter experiments\n"
    "- **Compare**: side-by-side, with missing-data flags\n"
    "- **Intelligence Lab**: cited answers with evidence grades\n"
    "- **Scenario Check**: spread/extinction check that abstains outside tested conditions\n"
    "- **About**: sources, credits, limitations"
)
