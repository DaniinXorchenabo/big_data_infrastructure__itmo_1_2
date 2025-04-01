# syntax = docker/dockerfile:1.2
# copied from https://gitlab.com/nvidia/container-images/cuda/-/blob/master/dist/12.2.2/ubuntu2204/runtime/Dockerfile
# https://gitlab.com/nvidia/container-images/cuda/-/tree/master

FROM python:3.11.8-slim-bullseye as base

FROM base as base-amd64

ENV NVARCH x86_64

ENV NVIDIA_REQUIRE_CUDA "cuda>=12.2 brand=tesla,driver>=470,driver<471 brand=unknown,driver>=470,driver<471 brand=nvidia,driver>=470,driver<471 brand=nvidiartx,driver>=470,driver<471 brand=geforce,driver>=470,driver<471 brand=geforcertx,driver>=470,driver<471 brand=quadro,driver>=470,driver<471 brand=quadrortx,driver>=470,driver<471 brand=titan,driver>=470,driver<471 brand=titanrtx,driver>=470,driver<471 brand=tesla,driver>=525,driver<526 brand=unknown,driver>=525,driver<526 brand=nvidia,driver>=525,driver<526 brand=nvidiartx,driver>=525,driver<526 brand=geforce,driver>=525,driver<526 brand=geforcertx,driver>=525,driver<526 brand=quadro,driver>=525,driver<526 brand=quadrortx,driver>=525,driver<526 brand=titan,driver>=525,driver<526 brand=titanrtx,driver>=525,driver<526"
ENV NV_CUDA_CUDART_VERSION 12.2.140-1
ENV NV_CUDA_COMPAT_PACKAGE cuda-compat-12-2

FROM base as base-arm64

ENV NVARCH sbsa
ENV NVIDIA_REQUIRE_CUDA "cuda>=12.2"
ENV NV_CUDA_CUDART_VERSION 12.2.140-1

FROM base-${TARGETARCH} as base_builder

ARG TARGETARCH

LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    curl -fsSLO https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/${NVARCH}/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    apt-get purge --autoremove -y curl \
    && rm -rf /var/lib/apt/lists/*

ENV CUDA_VERSION 12.2.2

# For libraries in the cuda-compat-* package: https://docs.nvidia.com/cuda/eula/index.html#attachment-a
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-cudart-12-2=${NV_CUDA_CUDART_VERSION} \
    ${NV_CUDA_COMPAT_PACKAGE} \
    && rm -rf /var/lib/apt/lists/*

# Required for nvidia-docker v1
RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf \
    && echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64

COPY ./docker/source/NGC-DL-CONTAINER-LICENSE /

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# =====================================================================


FROM base_builder as runtime_base

ENV NV_CUDA_LIB_VERSION 12.2.2-1

FROM runtime_base as runtime_base-amd64

ENV NV_NVTX_VERSION 12.2.140-1
ENV NV_LIBNPP_VERSION 12.2.1.4-1
ENV NV_LIBNPP_PACKAGE libnpp-12-2=${NV_LIBNPP_VERSION}
ENV NV_LIBCUSPARSE_VERSION 12.1.2.141-1

ENV NV_LIBCUBLAS_PACKAGE_NAME libcublas-12-2
ENV NV_LIBCUBLAS_VERSION 12.2.5.6-1
ENV NV_LIBCUBLAS_PACKAGE ${NV_LIBCUBLAS_PACKAGE_NAME}=${NV_LIBCUBLAS_VERSION}

ENV NV_LIBNCCL_PACKAGE_NAME libnccl2
ENV NV_LIBNCCL_PACKAGE_VERSION 2.19.3-1
ENV NCCL_VERSION 2.19.3-1
ENV NV_LIBNCCL_PACKAGE ${NV_LIBNCCL_PACKAGE_NAME}=${NV_LIBNCCL_PACKAGE_VERSION}+cuda12.2

FROM runtime_base as runtime_base-arm64

ENV NV_NVTX_VERSION 12.2.140-1
ENV NV_LIBNPP_VERSION 12.2.1.4-1
ENV NV_LIBNPP_PACKAGE libnpp-12-2=${NV_LIBNPP_VERSION}
ENV NV_LIBCUSPARSE_VERSION 12.1.2.141-1

ENV NV_LIBCUBLAS_PACKAGE_NAME libcublas-12-2
ENV NV_LIBCUBLAS_VERSION 12.2.5.6-1
ENV NV_LIBCUBLAS_PACKAGE ${NV_LIBCUBLAS_PACKAGE_NAME}=${NV_LIBCUBLAS_VERSION}

ENV NV_LIBNCCL_PACKAGE_NAME libnccl2
ENV NV_LIBNCCL_PACKAGE_VERSION 2.19.3-1
ENV NCCL_VERSION 2.19.3-1
ENV NV_LIBNCCL_PACKAGE ${NV_LIBNCCL_PACKAGE_NAME}=${NV_LIBNCCL_PACKAGE_VERSION}+cuda12.2

FROM base-${TARGETARCH} as runtime_builder

ARG TARGETARCH

ENV NV_CUDA_LIB_VERSION 12.2.2-1
ENV NV_NVTX_VERSION 12.2.140-1
ENV NV_LIBCUSPARSE_VERSION 12.1.2.141-1
ENV NV_LIBCUBLAS_PACKAGE_NAME libcublas-12-2
ENV NV_LIBNCCL_PACKAGE_NAME libnccl2


LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"

RUN apt-get update && apt-get install -y gnupg2
RUN apt-key adv --fetch-keys  http://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/3bf863cc.pub
RUN bash -c 'echo "deb http://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64 /" > /etc/apt/sources.list.d/cuda.list'


RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-libraries-12-2=${NV_CUDA_LIB_VERSION} \
    ${NV_LIBNPP_PACKAGE} \
    cuda-nvtx-12-2=${NV_NVTX_VERSION} \
    libcusparse-12-2=${NV_LIBCUSPARSE_VERSION} \
    ${NV_LIBCUBLAS_PACKAGE} \
    ${NV_LIBNCCL_PACKAGE} \
    && rm -rf /var/lib/apt/lists/*

# Keep apt from auto upgrading the cublas and nccl packages. See https://gitlab.com/nvidia/container-images/cuda/-/issues/88
RUN apt-mark hold ${NV_LIBCUBLAS_PACKAGE_NAME}
# RUN apt-mark hold ${NV_LIBNCCL_PACKAGE_NAME}

# Add entrypoint items
COPY ./docker/source/entrypoint.d/ /opt/nvidia/entrypoint.d/
COPY ./docker/source/nvidia_entrypoint.sh /opt/nvidia/
ENV NVIDIA_PRODUCT_NAME="CUDA"

RUN chmod +x /opt/nvidia/nvidia_entrypoint.sh &&  chmod -R +x /opt/nvidia/entrypoint.d/

ENTRYPOINT ["/opt/nvidia/nvidia_entrypoint.sh"]

# ===================================================================

FROM runtime_builder as cudnn_base

FROM cudnn_base as cudnn_base-amd64

ENV NV_CUDNN_VERSION 8.9.6.50
ENV NV_CUDNN_PACKAGE_NAME "libcudnn8"

ENV NV_CUDNN_PACKAGE "libcudnn8=$NV_CUDNN_VERSION-1+cuda12.2"

FROM cudnn_base as cudnn_base-amd64

ENV NV_CUDNN_VERSION 8.9.6.50
ENV NV_CUDNN_PACKAGE_NAME "libcudnn8"

ENV NV_CUDNN_PACKAGE "libcudnn8=$NV_CUDNN_VERSION-1+cuda12.2"

FROM cudnn_base-${TARGETARCH} as runtime_cudnn_builder

ARG TARGETARCH

LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"
LABEL com.nvidia.cudnn.version="${NV_CUDNN_VERSION}"

# ================================================================

# =======! CUDA !=======

# =====! Lib installers !=====
FROM cudnn_base-amd64  as neural_libs_installer_cuda

RUN apt-get update && apt-get install -y --no-install-recommends \
    ${NV_CUDNN_PACKAGE} \
    && apt-get install -y git \
    && apt-mark hold ${NV_CUDNN_PACKAGE_NAME} \
    && rm -rf /var/lib/apt/lists/*

ARG REQUIREMENTS_FILE=cu_12_2.txt

RUN mkdir -p /workspace/NN

# RUN git clone https://inkve.ddns.net:42379/inkve/NN
COPY ./requirements/${REQUIREMENTS_FILE} /workspace
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r /workspace/${REQUIREMENTS_FILE}


# ====! final builds !=====

FROM cudnn_base-amd64 as draft_base_build_cuda

LABEL authors="daniinxorchenabo"

RUN mkdir -p /workspace/NN
WORKDIR /workspace/NN

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 build-essential curl  -y --fix-missing


FROM draft_base_build_cuda as dev_build_cuda

COPY --from=neural_libs_installer_cuda /wheels /neural_wheels
RUN pip install --no-cache /neural_wheels/*  \
    && python -c """import nltk;nltk.download('popular');nltk.download('punkt');nltk.download('stopwords');nltk.download('averaged_perceptron_tagger_eng')"""  \
    && pip cache purge

CMD ["./docker/before_learn.sh"]



# ========! without CUDA !=======

FROM base  as neural_libs_installer

RUN apt-get update  \
    && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /workspace/NN

# RUN git clone https://inkve.ddns.net:42379/inkve/NN
COPY ./requirements/cpu.txt /workspace
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r /workspace/cpu.txt




FROM base  as web_libs_installer

RUN apt-get update  \
    && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/NN

# RUN git clone https://inkve.ddns.net:42379/inkve/NN
COPY ./requirements/prod.txt /workspace
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r /workspace/prod.txt




FROM base  as autotest_libs_installer

RUN apt-get update  \
    && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/NN

# RUN git clone https://inkve.ddns.net:42379/inkve/NN
COPY ./requirements/autotest.txt /workspace
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r /workspace/autotest.txt


# =====! final builds !=====

FROM base as final_base_build

LABEL authors="daniinxorchenabo"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 build-essential curl git -y --fix-missing
RUN mkdir -p /workspace/NN
WORKDIR /workspace/NN

FROM final_base_build as dev_build

COPY --from=neural_libs_installer /wheels /neural_wheels
RUN pip install --no-cache /neural_wheels/*  \
    && python -c """import nltk;nltk.download('popular');nltk.download('punkt');nltk.download('stopwords');nltk.download('averaged_perceptron_tagger_eng')"""  \
    && pip cache purge


CMD ["./docker/before_learn.sh"]


FROM  final_base_build as draft_producer_production_build

COPY --from=web_libs_installer /wheels /web_wheels

RUN pip install --no-cache /web_wheels/*  \
    && pip cache purge

FROM final_base_build as draft_consumer_production_build

COPY --from=neural_libs_installer /wheels /neural_wheels
COPY --from=web_libs_installer /wheels /web_wheels

RUN pip install --no-cache /neural_wheels/*  \
    && pip install --no-cache /web_wheels/*  \
    && pip cache purge

FROM  draft_producer_production_build as producer_production_build
COPY . /workspace/NN

FROM  draft_consumer_production_build as consumer_production_build
COPY . /workspace/NN

FROM  draft_producer_production_build as autotest_build

COPY --from=autotest_libs_installer /wheels /autotest_wheels
RUN pip install --no-cache /autotest_wheels/*  \
    && pip cache purge

COPY . /workspace/NN








FROM  dev_build_cuda as draft_consumer_production_build_cuda

COPY --from=neural_libs_installer_cuda /wheels /neural_wheels
COPY --from=web_libs_installer /wheels /web_wheels

RUN pip install --no-cache /neural_wheels/*  \
    && pip install --no-cache /web_wheels/*  \
    && pip cache purge

FROM  draft_consumer_production_build_cuda as consumer_production_build_cuda
COPY . /workspace/NN