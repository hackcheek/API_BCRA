echo '[*] Construyendo el docker...'
sudo docker build --quiet --tag api_bcra .
sudo docker run -it --rm api_bcra ./exec.sh
