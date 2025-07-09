ARG USER="eclipse"
ARG PDM_VERSION="2.22.4"
ARG CONAN_VERSION="2.13.0"

FROM ubuntu:24.04 AS vaf-base
ARG TZ="Europe/Berlin"
ARG USER
ARG CONAN_VERSION

ENV LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

# Install common APT packages
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    ccache \
    cmake \
    g++-12 \
    git \
    pipx \
    python3-pip \
    python3.12 \
    python3.12-venv \
    sudo \
    ssh \
    && apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/* \
    && rm -rf /var/log/*

# Comment out and adapt the lines below to add SSL certificates if needed:
# ADD url-to-your-certificate-one /usr/local/share/ca-certificates/your-certificates-folder
# ADD url-to-your-certificate-two /usr/local/share/ca-certificates/your-certificates-folder
# RUN update-ca-certificates /usr/local/share/ca-certificates/
# ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Create working directory and add user
RUN mkdir -p /workspaces \
    # Create a default user
    && userdel -r ubuntu \
    && useradd -m -s /bin/bash -u 1000 ${USER} --groups sudo \
    # Allow usage of sudo without password
    && echo "${USER} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER}_all \
    && chown -R ${USER}:${USER} /workspaces
USER ${USER}

# Install common python dependencies
RUN pip3 install conan==${CONAN_VERSION} --break-system-packages\
    && rm -rf /home/${USER}/.cache/*

WORKDIR /workspaces

FROM vaf-base AS builder
ARG PDM_VERSION

# Install build dependencies
RUN pipx ensurepath \
    && pipx install pdm==${PDM_VERSION}

# Build SIL Kit
RUN mkdir -p /tmp/silkit \
    && git clone --recurse-submodules -j4 https://github.com/vectorgrp/sil-kit.git /tmp/silkit \
    && git -C /tmp/silkit checkout tags/v4.0.55 \
    && git -C /tmp/silkit submodule update --init --recursive \
    && mkdir /tmp/silkit/build \
    && cmake -DSILKIT_BUILD_DEMOS=OFF -DSILKIT_BUILD_TESTS=OFF -DSILKIT_BUILD_DASHBOARD=OFF -DSILKIT_BUILD_STATIC=ON \
    -DCMAKE_INSTALL_PREFIX=/tmp/silkit/install -S /tmp/silkit -B /tmp/silkit/build \
    && cmake --build /tmp/silkit/build --target install --parallel 12

# Build conan packages
RUN --mount=type=bind,source=SwLibraries/vaf_core_library,target=/tmp/vafcpp/src,readwrite \
    --mount=type=bind,source=Container/conan,target=/tmp/conan,readwrite \
    --mount=type=bind,source=version.txt,target=/tmp/version.txt \
    sudo chown -R 1000:1000 /tmp/vafcpp /tmp/conan \
    && export PATH="$PATH:/home/${USER}/.local/bin" \
    && cd /tmp/vafcpp/src \
    && conan create . --profile:all=./test_package/gcc12__x86_64-pc-linux-elf -s build_type=Release \
    && conan create . --profile:all=./test_package/gcc12__x86_64-pc-linux-elf -s build_type=Debug \
    && conan install /tmp/conan -pr:a=/tmp/conan/gcc12__x86_64-pc-linux-elf --build=missing \
    && conan install /tmp/conan -pr:a=/tmp/conan/gcc12__x86_64-pc-linux-elf --build=missing -s build_type=Debug \
    && conan cache clean

# Build vafcli
RUN --mount=type=bind,source=VAF,target=/tmp/vaf/src,readwrite \
    --mount=type=bind,source=version.txt,target=/tmp/version.txt \
    sudo chown -R 1000:1000 /tmp/vaf \
    && rm -f /tmp/vaf/.python-version \
    && export PATH="$PATH:/home/${USER}/.local/bin" \
    && export PDM_BUILD_SCM_VERSION=$(cat /tmp/version.txt) \
    && make -C /tmp/vaf/src clean build \
    && mv /tmp/vaf/src/dist/*.whl /tmp/vaf

FROM vaf-base AS devcontainer

# Install packages requiring root permissions
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bash-completion \
    clangd \
    emacs \
    gdb \
    && apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/* \
    && rm -rf /var/log/*

# Install SIL Kit
RUN --mount=type=bind,from=builder,source=/tmp/silkit,target=/tmp/silkit \
    cp /tmp/silkit/install/bin/* /usr/local/bin/ \
    && cp -r /tmp/silkit/install/include/silkit /usr/local/include/ \
    && cp -r /tmp/silkit/install/lib/cmake /usr/local/lib/ \
    # Workaround for broken installation when building statically linked libraries
    && cp /tmp/silkit/build/ThirdParty/_tp_spdlog/libspdlog.a /usr/local/lib/ \
    && cp /tmp/silkit/build/ThirdParty/_tp_yaml-cpp/libyaml-cpp.a /usr/local/lib/ \
    && cp /tmp/silkit/build/Release/libSilKit.a /usr/local/lib/

# Switch user and set environment variables
USER ${USER}
ENV PATH="$PATH:/home/${USER}/.local/bin"

# Install remaining artifacts from build stage
RUN --mount=type=bind,from=builder,source=/tmp/vaf,target=/tmp/vaf \
    # Install vafcli
    pip3 install /tmp/vaf/*.whl --break-system-packages \
    && rm -rf /home/${USER}/.cache/* \
    && _VAF_COMPLETE=bash_source vaf | sudo tee /usr/share/bash-completion/completions/vaf > /dev/null

COPY --from=builder /home/${USER}/.conan2 /home/${USER}/.conan2

# Add Demos
COPY Demo /opt/vaf/Demo
