# syntax=docker/dockerfile:1.4

ARG PYTHON_VERSION="3.11.4"
FROM python:${PYTHON_VERSION}-slim-bullseye as e2e_base

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# Setup Pip
ARG PIP_VERSION="23.2.1"
ENV PIP_VERSION=${PIP_VERSION}

RUN pip install --no-cache-dir --upgrade "pip==${PIP_VERSION}" && pip --version

ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
RUN mkdir /component
WORKDIR /component

# Install streamlit and components
ARG STREAMLIT_VERSION="latest"
ENV E2E_STREAMLIT_VERSION=${STREAMLIT_VERSION}

FROM e2e_base as e2e_pip

RUN <<"EOF"
if [[ "${E2E_STREAMLIT_VERSION}" == "latest" ]]; then
  pip install --no-cache-dir "streamlit"
elif [[ "${E2E_STREAMLIT_VERSION}" == "nightly" ]]; then
  pip uninstall --yes streamlit
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

FROM e2e_base as e2e_whl

COPY lib/dist/ /streamlit-dist/

RUN <<"EOF"
if [[ "${E2E_STREAMLIT_VERSION}" == "development" ]]; then
  pip uninstall --yes streamlit
  pip install --no-cache-dir "streamlit-dist/*.whl"
else
  echo "Unsupported Streamlit version: ${E2E_STREAMLIT_VERSION}"
  exit 1
fi

# Coherence check
installed_streamlit_version=$(python -c "import streamlit; print(streamlit.__version__)")
echo "Installed Streamlit version: ${installed_streamlit_version}"
echo "${installed_streamlit_version}" | grep -v 'dev'
EOF