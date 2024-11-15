docker build . -t fmm:0.1.0
#docker run -v "$(pwd)/data:/usr/src/app/data" -it fmm:0.1.0
docker run -i -v "$(pwd)/data:/fmm/data" -v "$(pwd)/porto:/fmm/porto" -t fmm:0.1.0
