FROM continuumio/miniconda3

WORKDIR /workspace

COPY requirements.txt .

RUN conda create -n sustain-lc python=3.10 -y && \
    conda run -n sustain-lc pip install -r requirements.txt && \
    conda run -n sustain-lc conda install -c conda-forge pyfmi -y

SHELL ["conda", "run", "-n", "sustain-lc", "/bin/bash", "-c"]

CMD ["/bin/bash"]
