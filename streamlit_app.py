import streamlit as st
from typing import Optional
import json

st.set_page_config(page_title="Shopper Agent — Demo", layout="wide")

st.title("Shopper Agent — RAG + Multi-step Demo")

st.markdown(
    "Enter a shopping-related question and the app will run the RAG retriever + multi-step agent to answer."
)

with st.sidebar:
    st.header("Settings")
    k = st.number_input("Retriever k (top docs)", min_value=1, max_value=10, value=3, step=1)
    run_button_label = st.button("Run Agent")

query = st.text_area("Question", height=140, placeholder="e.g. Compare top noise-cancelling headphones and summarize user reviews...")

if 'last_response' not in st.session_state:
    st.session_state['last_response'] = None

def _run_agent(question: str, k: int) -> str:
    try:
        # Import here to avoid costly imports when the UI is just idle
        from agent import run_rag_agent

        resp = run_rag_agent(question, k=k)
        return resp
    except Exception as e:
        return f"Error running agent: {e}"

if st.button("Submit") or run_button_label:
    if not query or not query.strip():
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("Running agent — this may take a few seconds..."):
            response = _run_agent(query.strip(), k)
            st.session_state['last_response'] = response

def _display_product_comparison_obj(obj):
    """Display a single ProductComparison-like dict in a clean layout."""
    # Basic keys we expect
    name = obj.get("product_name") or obj.get("Product Name") or obj.get("title")
    price = obj.get("price")
    battery = obj.get("battery_life") or obj.get("battery")
    pros = obj.get("pros_summary") or obj.get("pros") or []
    cons = obj.get("cons_summary") or obj.get("cons") or []

    st.subheader(name if name else "Product")
    col1, col2 = st.columns([2, 3])
    with col1:
        info = {}
        if price is not None:
            info["Price"] = price
        if battery:
            info["Battery life"] = battery
        if info:
            st.table(info.items())
        else:
            st.write("No basic spec fields available.")

    with col2:
        st.markdown("**Pros**")
        if pros:
            for p in pros:
                st.markdown(f"- {p}")
        else:
            st.markdown("- None reported")

        st.markdown("**Cons**")
        if cons:
            for c in cons:
                st.markdown(f"- {c}")
        else:
            st.markdown("- None reported")


if st.session_state.get('last_response'):
    resp = st.session_state['last_response']
    st.subheader("Agent response (raw)")
    with st.expander("Show raw response"):
        st.code(resp)

    # Try to parse JSON response; robust to single-object or list-of-objects
    parsed = None
    try:
        parsed = json.loads(resp)
    except Exception:
        parsed = None

    if parsed is None:
        st.subheader("Response (unstructured)")
        st.write(resp)
    else:
        # If it's a dict that looks like a ProductComparison
        if isinstance(parsed, dict) and ("product_name" in parsed or "price" in parsed or "pros_summary" in parsed):
            _display_product_comparison_obj(parsed)
        # If it's a list of product dicts, show a table summary and expanders
        elif isinstance(parsed, list) and parsed and all(isinstance(p, dict) for p in parsed):
            # Build table rows
            rows = []
            for p in parsed:
                rows.append({
                    "product_name": p.get("product_name") or p.get("title"),
                    "price": p.get("price"),
                    "battery_life": p.get("battery_life"),
                    "pros_summary": "; ".join(p.get("pros_summary") or p.get("pros") or []),
                    "cons_summary": "; ".join(p.get("cons_summary") or p.get("cons") or [])
                })
            st.subheader("Comparison table")
            st.table(rows)

            for i, p in enumerate(parsed):
                with st.expander(f"Details — {rows[i].get('product_name') or 'product ' + str(i+1)}"):
                    _display_product_comparison_obj(p)
        else:
            st.subheader("Parsed JSON")
            st.json(parsed)

st.markdown("---")
st.markdown("Built for quick prototyping. Ensure your environment has the required dependencies (see `requirement.txt`).")
