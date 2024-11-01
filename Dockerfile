# syntax=docker/dockerfile:1.4

ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-bullseye as e2e_base

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# Setup Pip
ARG PIP_VERSION="24.3.1"
ENV PIP_VERSION=${PIP_VERSION}

RUN pip install --no-cache-dir --upgrade "pip==${PIP_VERSION}" && pip --version

# Setup Playwright
ARG PLAYWRIGHT_VERSION="1.48.0"
ENV PLAYWRIGHT_VERSION=${PLAYWRIGHT_VERSION}

RUN pip install --no-cache-dir playwright=="${PLAYWRIGHT_VERSION}" && playwright install webkit chromium firefox --with-deps

ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
RUN mkdir /component
WORKDIR /component

FROM e2e_base AS e2e_pip

# Install streamlit and components
ARG STREAMLIT_VERSION="latest"
ENV E2E_STREAMLIT_VERSION=${STREAMLIT_VERSION}

RUN <<"EOF"
if [[ "${E2E_STREAMLIT_VERSION}" == "latest" ]]; then
  pip install --no-cache-dir "streamlit"
elif [[ "${E2E_STREAMLIT_VERSION}" == "nightly" ]]; then
  pip uninstall --yes "streamlit"
  pip install --no-cache-dir "streamlit-nightly"
else
  pip install --no-cache-dir "streamlit==${E2E_STREAMLIT_VERSION}"
fi

# Coherence check
installed_streamlit_version=$(python -c "import streamlit; print(streamlit.__version__)")
echo "Installed Streamlit version: ${installed_streamlit_version}"
if [[ "${E2E_STREAMLIT_VERSION}" == "nightly" ]]; then
  echo "${installed_streamlit_version}" | grep 'dev'
else
  echo "${installed_streamlit_version}" | grep -v 'dev'
fi
EOF

FROM e2e_base AS e2e_whl

ARG STREAMLIT_WHEEL_PATH

RUN --mount=type=bind,source=./buildcontext,target=/buildcontext <<"EOF"
pip uninstall --yes "streamlit" "streamlit-nightly"
find /buildcontext/ -name '*.whl'| xargs -t pip install --no-cache-dir

# Coherence check
installed_streamlit_version=$(python -c "import streamlit; print(streamlit.__version__)")
echo "Installed Streamlit version: ${installed_streamlit_version}"
EOF
