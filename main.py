import os
import tempfile
import shutil
import streamlit as st
from git import Repo, GitCommandError
from agent import agent

st.set_page_config(page_title="README Generator", layout="wide")
st.title("🦆 README Generator (Kimi K2 + Agno)")

repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/user/repo")

if st.button("Generate README"):
    if not repo_url.strip():
        st.warning("Please enter a repo URL.")
        st.stop()

    with st.spinner("Cloning & analysing…"):
        tmp_dir = tempfile.mkdtemp()
        try:
            # ---------- clone ----------
            try:
                Repo.clone_from(repo_url, tmp_dir, depth=1)
            except GitCommandError as e:
                st.error("Unable to clone repository. Please check the URL and try again.")
                st.caption(str(e))
                st.stop()

            # ---------- collect interesting files ----------
            snippets = []
            for root, _, files in os.walk(tmp_dir):
                for f in files:
                    if f.lower().endswith(
                        (".py", ".md", ".txt", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini")
                    ):
                        path = os.path.join(root, f)
                        rel_path = os.path.relpath(path, tmp_dir)
                        try:
                            with open(path, "r", encoding="utf-8") as fh:
                                content = fh.read(4000)
                                snippets.append(
                                    f"### {rel_path}\n```\n{content}\n```"
                                )
                        except Exception:
                            pass

            if not snippets:
                st.error("The repository appears to be empty or contains no readable files.")
                st.stop()

            repo_context = "\n\n".join(snippets)

            # ---------- generate README ----------
            prompt = (
                "Below is the cloned repository.\n"
                f"{repo_context}\n\n"
                "Generate a complete, polished README.md (raw markdown ONLY). "
                "Include: shields.io badges, install steps, usage, tech stack, "
                "and contribution guide. Do NOT add explanatory text."
            )
            readme = agent.run(prompt, markdown=True).content
            st.session_state["readme"] = readme

        except Exception as e:
            st.error("Something went wrong while processing the repository.")
            st.caption(str(e))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

# ---------- display / download ----------
if "readme" in st.session_state:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Markdown")
        st.code(st.session_state["readme"], language="markdown")
    with col2:
        st.subheader("Preview")
        st.markdown(st.session_state["readme"])

    st.download_button(
        label="📥 Download README.md",
        data=st.session_state["readme"],
        file_name="README.md",
        mime="text/markdown"
    )

    if st.button("🔄 Regenerate"):
        del st.session_state["readme"]
        st.rerun()