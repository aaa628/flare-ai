import streamlit as st

from data import load_verified_experiments

st.set_page_config(page_title="Flame Explorer · Flare AI", page_icon="🔥", layout="wide")
st.title("Flame Explorer")

df = load_verified_experiments()
if df.empty:
    st.info("No verified experiments to explore yet. Add and verify records in `data/experiments.csv`.")
    st.stop()

q = st.text_input("Search")
cols = st.columns(3)
fuel = cols[0].multiselect("Fuel / material", sorted(df["fuel_material"].unique()))
grav = cols[1].multiselect("Gravity environment", sorted(df["gravity_env"].unique()))
prog = cols[2].multiselect("Program", sorted(df["program"].unique()))

view = df
if q:
    mask = view.apply(lambda r: q.lower() in " ".join(r.astype(str)).lower(), axis=1)
    view = view[mask]
if fuel:
    view = view[view["fuel_material"].isin(fuel)]
if grav:
    view = view[view["gravity_env"].isin(grav)]
if prog:
    view = view[view["program"].isin(prog)]

st.caption(f"{len(view)} of {len(df)} verified experiments")
st.dataframe(
    view[["id", "program", "title", "fuel_material", "gravity_env", "oxygen_pct", "outcome", "source_id"]],
    use_container_width=True,
    hide_index=True,
)
