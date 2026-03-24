#!/bin/bash
# 启动 Neo4j Docker 容器的脚本

echo "Starting Neo4j Docker container..."
docker run -d --name neo4j-container -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

echo "Neo4j container started!"
echo "Access Neo4j Browser at: http://localhost:7474"
echo "Username: neo4j"
echo "Password: password"

# 等待容器启动
sleep 10

# 检查容器状态
docker ps | grep neo4j-container