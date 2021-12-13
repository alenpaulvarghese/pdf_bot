FROM python:3.10

WORKDIR /app/

RUN apt update -y && apt-get install -y cmake

# install poppler
RUN git clone https://gitlab.freedesktop.org/poppler/poppler.git && cd poppler && \
    git checkout poppler-0.89.0 && mkdir build && cd build && cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX:PATH=/usr/local \
    -DENABLE_UNSTABLE_API_ABI_HEADERS=ON \
    -DBUILD_GTK_TESTS=OFF \
    -DBUILD_QT5_TESTS=OFF \
    -DBUILD_CPP_TESTS=OFF \
    -DENABLE_CPP=ON \
    -DENABLE_GLIB=OFF \
    -DENABLE_GOBJECT_INTROSPECTION=OFF \
    -DENABLE_GTK_DOC=OFF \
    -DENABLE_QT5=OFF \
    -DBUILD_SHARED_LIBS=ON \
    .. \
    && make && make install

ENV PKG_CONFIG_PATH /usr/local/lib/pkgconfig
ENV LD_LIBRARY_PATH /usr/local/lib:$LD_LIBRARY_PATH

COPY . /app/

RUN python -m pip install -r requirements.txt

CMD ["bash", "run.sh"]