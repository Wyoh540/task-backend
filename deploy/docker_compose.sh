#!/bin/bash


# 启动数据库
function start_db() {
    docker-compose up --force-recreate -d mysql redis
}

# 数据库初始化
function init_db() {
    db_container=$(docker-compose ps | grep mysql | awk '{print $1}')
    docker-compose exec mysql /bin/bash -c \
            "printf 'wait db [DB default password: TCA!@#2021]\n'; \
            until \$(MYSQL_PWD=${DBPASSWD} mysql -u${DBUSER} -e '\s' > /dev/null 2>&1); do \
                printf '.' && sleep 1; \
            done; echo
            "
}

# Task服务初始化
function init_server() {
    docker-compose up -d task-server
    docker-compose exec task-server /bin/bash -c \
        "alembic upgrade head; \
        "
}

# 启动服务
function start_all_services() {
    docker-compose up -d
}

# 停止服务
function stop_all_services() {
    docker-compose stop
}

# 部署所有服务
function deploy_all_services() {
    start_db || error_exit "start db failed"
    init_db || error_exit "init db failed"
    init_server || error_exit "init task server failed"
    start_all_services
}


function docker_compose_main() {
    command=$1
    case $command in
        deploy)
            LOG_INFO "Deploy task docker-compose"
            deploy_all_services
        ;;
        start)
            LOG_INFO "Start task docker-compose"
            start_all_services
        ;;
        stop)
            LOG_INFO "Stop task docker-compose"
            stop_all_services
        ;;
        build)
            LOG_INFO "Build task image"
            docker-compose build task-server
        ;;
        *)
            LOG_ERROR "'$command' not support."
            exit 1
    esac
}