## Graduate work of Yandex middle python-developer course.

### Team:
[Артем](https://github.com/tema1998) <br/> 
[Николай](https://github.com/NikolaySolop)

### In project were used
* ![Docker][Docker]
* ![Fastapi][Fastapi]
* ![Django][Django]
* ![PostgreSQL][PostgreSQL]
* ![Redis][Redis]
* ![RabbitMQ][RabbitMQ]
* ![Elastic][Elastic]
* ![Nginx][Nginx]
* ![Yookassa][Yookassa]


### Main services
Admin_service(Django) - Content management.<br/>
Auth_service(FastAPI) - Registration and authorization of users in other services.<br/>
Content_service(FastAPI) - Content delivery.<br/>
Billing_service(FastAPI) - Content payment service.<br/>
Notification_service(FastAPI) - Service for notifications about new content, payment status and mailing management.

### Supporting services
Billing_rabbitmq_init - Initialization of billing broker's queues.<br/>
Notification_rabbitmq_init - Initialization of notification broker's queues.<br/>
Billing_worker - Worker to set premium rights to user, change order's status, make request to notify user about payment status. <br/>
Consumer_messages - Worker to send notification about new content, payment status.<br/>
Notification_consumer_recorder_service - Worker to record message's status to DB. <br/>
Nginx - Web server software used for reverse proxy, load balancing, and caching. <br/>
Base_config - Main project settings.<br/>

### Scheme of services
<image src="readme/scheme.png" alt="Scheme"> </image>

### Environment
Create .env file using .env.example.
Create account yookassa, set shop_id, secret_key. Set response URL in Yookassa settings to Billing service.
Create smtp account(google, yandex and etc.), set SMTP(host, port, email, pass)

### How to test Yookassa response without deploying
Ngrok  to expose a local development server to the Internet. Install Ngrok, set up Ngrok token.
```
ngrok http http://<billing-service-url>
```

### Run
```
docker compose up --build
```

### OPENAPI URL
```
docker compose up --build
```



[Docker]: https://img.shields.io/badge/docker-000000?style=for-the-badge&logo=docker&logoColor=blue
[FastAPI]: https://img.shields.io/badge/fastapi-000000?style=for-the-badge&logo=fastapi&logoColor=green
[Django]: https://img.shields.io/badge/django-000000?style=for-the-badge&logo=django&logoColor=white
[PostgreSQL]: https://img.shields.io/badge/postgresql-000000?style=for-the-badge&logo=postgresql&logoColor=blue
[Redis]: https://img.shields.io/badge/redis-000000?style=for-the-badge&logo=redis&logoColor=red
[Nginx]: https://img.shields.io/badge/nginx-000000?style=for-the-badge&logo=nginx&logoColor=green
[RabbitMQ]: https://img.shields.io/badge/rabbitmq-000000?style=for-the-badge&logo=rabbitmq&logoColor=orange
[Elastic]: https://img.shields.io/badge/elasticsearch-black?style=for-the-badge&logo=elasticsearch&logoColor=white
[Yookassa]: https://img.shields.io/badge/yookassa-black?style=for-the-badge&logo=yookassa&logoColor=white

