import streamlit as st

st.set_page_config(page_title="About · Flare AI", page_icon="🔥")
st.title("About Flare AI")
st.markdown(
    """
**Flare AI** was built for the NASA Space Apps Challenge 2026, *Flame in Freefall*.

**Data sources:** NASA Physical Sciences Informatics (psi.nasa.gov, CC0) and the NASA
Technical Reports Server (ntrs.nasa.gov). NASA does not endorse this project.

**Limitations**
- Flare AI is a research-navigation tool. It does not calculate fire probabilities or certify safety.
- Only records verified against their source by a second person are shown as findings.
- Where NASA did not test a condition, Flare AI says so instead of guessing.

**AI-use disclosure:** developed with AI assistance (Claude); the team reviews and verifies all data.

**Team:** Studio 628 / 628 Aerospace.
"""
)
