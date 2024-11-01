# clone valhalla docker repo
git clone https://github.com/nilsnolde/docker-valhalla.git [VALHALLA DIRECTORY]

# copy docker-compose files to valhalla directory
cp docker-compose.yml.1 docker-compose.yml.2 [VALHALLA DIRECTORY]

# nav to valhalla directory
cd [VALHALLA DIRECTORY]

# build image
docker build -t ghcr.io/gis-ops/docker-valhalla/valhalla:latest .

# build tiles (valhalla_tiles.tar)
docker compose up -f docker-compose.yml.1

# serve valhalla service w/ pre-built tiles
docker compose up -f docker-compose.yml.2

# now valhalla services can be accessed via the exposed port
see this link for explanation how to use the Meili API:
https://towardsdatascience.com/map-matching-done-right-using-valhallas-meili-f635ebd17053#:~:text=Sending%20a%20request%20to%20Meili

