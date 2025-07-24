import os
import tempfile
import shutil
import streamlit as st
from git import Repo, GitCommandError
from agent import build_agent


st.set_page_config(page_title="README Generator", layout="wide")
import streamlit as st
import streamlit as st

# CSS to make the sidebar a vertical flex container
st.markdown("""
    <style>
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .sidebar-content {
        flex: 1;
    }

    .sidebar-footer {
        
        font-size: 0.9em;
        padding: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar layout using flexbox
with st.sidebar:
    # Wrap main content in a container
    with st.container():
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

        st.header("🔑 Settings")
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get one at https://openrouter.ai/keys"
        )

        st.markdown("---")
        st.markdown("**⚡Model:** moonshotai/kimi-k2")
        # Download button placeholder
        download_placeholder = st.empty()

        st.markdown("</div>", unsafe_allow_html=True)  # Close content div

    # Footer (sticky at bottom)
    st.markdown("""
        <div class="sidebar-footer" text-align="left">
              </br></br></br></br></br></br></br></br></br>
              ❤️ Built by <a href="https://buildfastwithai.com" target="_blank">Build Fast with AI</a>
        </div>
    """, unsafe_allow_html=True)



st.title("🦆 Github README File Generator (Kimi K2 + Agno)")
repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/user/repo")

if st.button("Generate README"):
    if not repo_url.strip():
        st.warning("Please enter a repo URL.")
        st.stop()
    if not api_key.strip():
        st.error("🔑 API key required. Paste your OpenRouter key in the sidebar first.")
        st.stop()

    agent = build_agent(api_key)   # build agent only when needed

    with st.spinner("Cloning & analysing…"):
        tmp_dir = tempfile.mkdtemp()
        try:
            try:
                Repo.clone_from(repo_url, tmp_dir, depth=1)
            except GitCommandError as e:
                st.error("Unable to clone repository. Check the URL.")
                st.caption(str(e))
                st.stop()

            snippets = []
            for root, _, files in os.walk(tmp_dir):
                for f in files:
                    if f.lower().endswith(
                        (".py", ".js" , ".ts" , ".jsx" , ".html" ,".css" , ".tsx" , ".php" , ".java", ".cpp", ".txt", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini")
                    ):
                        path = os.path.join(root, f)
                        rel_path = os.path.relpath(path, tmp_dir)
                        try:
                            with open(path, "r", encoding="utf-8") as fh:
                                content = fh.read(4000)
                                snippets.append(f"### {rel_path}\n```\n{content}\n```")
                        except Exception:
                            pass

            if not snippets:
                st.error("Repository appears empty or has no readable files.")
                st.stop()

            repo_context = "\n\n".join(snippets)
            prompt = (
                "Below is the cloned repository.\n"
                f"{repo_context}\n\n"
                "Generate a complete, polished README.md (raw markdown ONLY). "
                "Include: shields.io badges, install steps, usage, tech stack, "
                "and contribution guide. "
                "Do NOT wrap the output in triple back-ticks."
            )
            readme = agent.run(prompt, markdown=True).content
            st.session_state["readme"] = readme

        except Exception as e:
            st.error("Something went wrong while processing the repository.")
            st.caption(str(e))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if "readme" in st.session_state:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Markdown")
        st.code(st.session_state["readme"], language="markdown")
    with col2:
        st.subheader("Preview")
        st.markdown(st.session_state["readme"])

    with st.sidebar:
        st.download_button(
            label="📥 Download README.md",
            data=st.session_state["readme"],
            file_name="README.md",
            mime="text/markdown",
            use_container_width=True
        )

