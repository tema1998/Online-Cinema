## Graduate work: Online cinema with microservice architecture

### Github URL
https://github.com/tema1998/graduate_work

### Team:
[Артем](https://github.com/tema1998) <br/> 
[Николай](https://github.com/NikolaySolop)

### Main services
Admin_service - Content management.<br/>
Auth_service - Registration and authorization of users in other services.<br/>
Content_service - Content delivery.<br/>
Billing_service - Content payment service.<br/>
Notification_service - Service for notifications about new content, payment status and mailing management.

### Supporting services
Billing_rabbitmq_init - Initialization of billing broker's queues.<br/>
Notification_rabbitmq_init - Initialization of notification broker's queues.<br/>
Billing_worker - Worker to set premium rights to user, change order's status, make request to notify user about payment status. <br/>
Consumer_messages - Worker to send notification about new content, payment status.<br/>
Notification_consumer_recorder_service - Worker to record messages to DB. <br/>
Nginx - web server software used for reverse proxy, load balancing, and caching. <br/>
Base_config - Main project settings.<br/>

### Scheme
<image src="readme/scheme.png" alt="Scheme"> </image>

### Environment
Create .env file using .env.example. Set your parameters.

