# Docker Commands — Day 8

## Images
docker pull nginx
docker images
docker history nginx
docker rmi imagename

## Containers
docker run -d -p 8080:80 --name mywebserver nginx
docker ps
docker ps -a
docker stop container
docker start container
docker rm container
docker exec -it container bash
docker logs container
docker inspect container
docker stats container

## Resource Limits
docker run --memory="256m" --cpus="0.5" nginx

## Networking
docker network ls
docker network create devops-network
docker network inspect devops-network
docker network rm devops-network

## Key concepts
- Custom networks have built-in DNS
- Containers find each other by NAME on custom networks
- Default bridge = by IP only
- Resource limits prevent one container crashing the server
