
# Foodgram - Вдохновляйтесь и делитесь вкусными блюдами со всем миром!

***

#### Ссылка на проект: primestr.sytes.net

***

# Русская версия

Looking for English version? Check here --> [click](#english-version) or scroll down.

***
***

## Технологии:

[![Python](https://img.shields.io/badge/Python-%203.10-blue?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-%203.2.3-blue?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DjangoRESTFramework-%20-blue?style=flat-square&logo=django)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-%2024.0.5-blue?style=flat-square&logo=docker)](https://www.docker.com/)
[![DockerCompose](https://img.shields.io/badge/Docker_Compose-%202.21.0-blue?style=flat-square&logo=docsdotrs)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-%20-blue?style=flat-square&logo=githubactions)](https://github.com/features/actions)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-%2020.1.0-blue?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![Nginx](https://img.shields.io/badge/Nginx-%20-blue?style=flat-square&logo=nginx)](https://www.nginx.com/)
[![React](https://img.shields.io/badge/React-%20-blue?style=flat-square&logo=react)](https://react.dev/)
[![React](https://img.shields.io/badge/certbot-%20-blue?style=flat-square&logo=letsencrypt)](https://certbot.eff.org/)

***

## Функционал:

Foodgram предоставляет следующие возможности:

- Добавление и редактирование рецептов: Создайте красиво оформленные рецепты, добавляйте фотографии ваших блюд и расскажите другим, как приготовить их шаг за шагом.

- Поиск рецептов: Ищите рецепты по тегам и авторам.

- Сохранение в избранное: Добавляйте понравившиеся рецепты в свою коллекцию избранных, чтобы легко найти их в будущем.

- Список покупок: Создавайте список покупок на основе ингредиентов, необходимых для приготовления выбранных блюд, и сохраняйте его. Позже вы сможете скачать этот список в формате PDF и распечатать, чтобы ничего не забыть при походе в магазин.

- Подписка на авторов: Вы можете подписываться на авторов, чьи рецепты вас вдохновляют, чтобы всегда быть в курсе их новых кулинарных идей.

***

## Технические особенности:

Репозиторий включает в себя два файла **docker-compose.yml** и 
**docker-compose.production.yml**, что позволяет развернуть проект на
локальном или удалённом серверах.

Данная инструкция подразумевает, что на вашем локальном/удалённом сервере уже установлен Git, Python 3.10, пакетный менеджер pip, Docker, Docker Compose, утилита виртуального окружения python3-venv.

В проекте предусмотрена возможность запуска БД SQLite3 и PostgreSQL. Выбор БД осуществляется сменой значения DEBUG на True или False. True = SQLite3, False = PostgreSQL.

С подробными инструкциями запуска вы можете ознакомиться ниже.

***

## Запуск проекта локально в Docker-контейнерах с помощью Docker Compose

Склонируйте проект из репозитория:

```shell
git clone https://github.com/PrimeStr/foodgram-project-react.git
```


Перейдите в директорию проекта:

```shell
cd foodgram-project-react/
```

Перейдите в директорию **infra** и создайте файл **.env**:

```shell
cd infra/
```

```shell
nano .env
```

Добавьте строки, содержащиеся в файле **.env.example** и подставьте 
свои значения.

Пример из .env файла:

```dotenv
# БД выбирается автоматически на основе константы DEBUG. Если DEBUG = True , используется SQLite3.
# Если DEBUG = False , используется PostgreSQL.

POSTGRES_USER=django_user            # Ваше имя пользователя для бд
POSTGRES_PASSWORD=django             # Ваш пароль для бд
POSTGRES_DB=django                   # Название вашей бд
DB_HOST=db                           # Стандартное значение - db
DB_PORT=5432                         # Стандартное значение - 5432


SECRET_KEY=DJANGO_SECRET_KEY         # Ваш секретный ключ Django
DEBUG=False                          # True - включить Дебаг. Или оставьте пустым для False
IS_LOGGING=False                     # True - включить Логирование. Или оставьте пустым для False
ALLOWED_HOSTS=127.0.0.1              # Список адресов, разделенных пробелами

# Помните, если вы выставляете DEBUG=False, то необходимо будет настроить список ALLOWED_HOSTS.
# 127.0.0.1 является стандартным значением. Без пробелов и иных символов.
```

В директории **infra** проекта находится файл **docker-compose.yml**, с 
помощью которого вы можете запустить проект локально в Docker контейнерах.

Находясь в директории **infra** выполните следующую команду:
> **Примечание.** Если нужно - добавьте в конец команды флаг **-d** для запуска
> в фоновом режиме.
```shell
sudo docker compose -f docker-compose.yml up
```

Она сбилдит Docker образы и запустит backend, frontend, СУБД и Nginx в 
отдельных Docker контейнерах.

Выполните миграции в контейнере с backend:

```shell
sudo docker compose -f docker-compose.yml exec foodgram-backend python manage.py migrate
```

Соберите статику backend'a:

```shell
sudo docker compose -f docker-compose.yml exec foodgram-backend python manage.py collectstatic
```

По завершении всех операции проект будет запущен и доступен по адресу
http://127.0.0.1/

Для остановки Docker контейнеров, находясь в директории **infra** выполните 
следующую команду:

```shell
sudo docker compose -f docker-compose.yml down
```

Либо просто завершите работу Docker Compose в терминале, в котором вы его
запускали, сочетанием клавиш **CTRL+C**.

***

# CI/CD - Развёртка проекта на удаленном сервере

В проекте уже настроен Workflow для GitHub Actions.

Ваш GitHub Actions самостоятельно запустит:

- 🧪 Тесты: Запускаются тесты для вашего проекта.
- 🏗️ Сборку образов: Git Action создает Docker-образы вашего приложения.
- 🚀 Деплой: Образы отправляются на ваш репозиторий DockerHub, проект
деплоится на сервер.
- ✉️ Уведомление: В случае успеха вы получите уведомление в Telegram.

Форкните репозиторий, перейдите в GitHub в настройки репозитория — 
**Settings**, найдите на панели слева пункт
**Secrets and Variables**, перейдите в **Actions**, нажмите
**New repository secret**.

Создайте следующие ключи:

> **Примечание.** При подключении к вашему удалённому серверу воркер GitHub 
> Actions создаст .env файл, создаст БД и запустит контейнер с backend'ом, 
> используя эти константы.

```
# Общие секреты
DOCKER_USERNAME (Ваш логин в DockerHub)
DOCKER_PASSWORD (Ваш пароль в DockerHub)
HOST (IP адрес вашего удалённого сервера)
USER (Логин вашего удалённого сервера)
SSH_KEY (SSH ключ вашего удалённого сервера)
SSH_PASSPHRASE (Пароль вашего удалённого сервера)
TELEGRAM_TO (Ваш ID пользователя в Telegram)
TELEGRAM_TOKEN (Токен вашего бота в Telegram)

# PostgreSQL
POSTGRES_USER(Ваше имя пользователя для бд)
POSTGRES_PASSWORD(Ваш пароль для бд)
POSTGRES_DB(Название вашей бд)
DB_HOST(Адрес бд. Стандартное значение - db)
DB_PORT(Порт бд. Стандартное значение - 5432)

# Django
SECRET_KEY(Ваш секретный ключ Django)
DEBUG(Вкл/выкл DEBUG)
IS_LOGGING(Вкл/выкл Логирование)
ALLOWED_HOSTS(Список адресов, разделенных пробелами)
```

> **Внимание!** Для корректного отображения изображений не забудьте помимо 
localhost и 127.0.0.1 добавить в ALLOWED_HOSTS доменное имя вашего сайта.

Пример PostgreSQL и Django констант из .env файла:

```dotenv
POSTGRES_USER=django_user            # Ваше имя пользователя для бд
POSTGRES_PASSWORD=django             # Ваш пароль для бд
POSTGRES_DB=django                   # Название вашей бд
DB_HOST=db                           # Стандартное значение - db
DB_PORT=5432                         # Стандартное значение - 5432

SECRET_KEY=DJANGO_SECRET_KEY         # Ваш секретный ключ Django
DEBUG=False                          # True - включить Дебаг. Или оставьте пустым для False
IS_LOGGING=False                     # True - включить Логирование. Или оставьте пустым для False
ALLOWED_HOSTS=127.0.0.1              # Список адресов, разделенных пробелами
```

### **Теперь можно приступать к деплою**

> **Внимание!** Дальнейшие действия подразумевают что на вашем удалённом 
> сервере Nginx установлен и настроен как прокси-сервер. Изначально Nginx в 
> Docker-контейнере слушает порт 8500.

В локальном проекте замените в файле **docker-compose.production.yml** названия
образов в соответствии с вашим логином на DockerHub в нижнем регистре
(Например **your_name/foodgram_backend**)

Аналогично измените названия образов и в файле **main.yml**, который находится
в директории **/.github/workflows/**.

Подключитесь к вашему удалённому серверу любым удобным способом. Создайте в
домашней директории директорию с названием **foodgram** и перейдите в неё.

```shell
mkdir foodgram
```

Готово.

Весь процесс автоматизирован! Как только вы инициируете коммит на локальной 
машине и отправите изменения на GitHub, GitHub Actions берет дело в свои руки:

```shell
git add .
```

```shell
git commit -m "Ваше сообщение для коммита."
```

```shell
git push
```

После успешной отправки изменений перейдите в своём репозитории на GitHub во
вкладку **Actions**. Вы увидите процесс работы Actions. После окончания работы
воркера в ваш Telegram придёт сообщение от бота:

> Деплой проекта Foodgram успешно выполнен!

**Данное сообщение означает что проект успешно запущен на сервере, проведены 
миграции и собрана статика backend'а.**

После этого можно вернуться на удалённый сервер, в директорию **foodgram** и
создать суперпользователя: 

```shell
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

>**Внимание! :** Для полноценной работы проекта на вашем удалённом сервере 
должен быть установлен, настроен и запущен **Nginx**. Удостоверьтесь что 
в конфиге по вашему доменному имени настроена переадресация всех запросов на
**127.0.0.1:8500** и добавлена переадресация заголовков.

### Настройка SSL шифрования через Let's Encrypt

Чтобы проект отвечал базовым стандартам безопасности необходимо настроить
SSL сертификат.

Установите **certbot**:

```shell
sudo apt install snapd
```

```shell
sudo snap install core; sudo snap refresh core
```

```shell
sudo snap install --classic certbot
```

```shell
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Запустите sertbot и получите свой SSL сертификат:

```shell
sudo certbot --nginx
```

После перезапустите Nginx:

```shell
sudo systemctl reload nginx
```  

```shell
sudo certbot certificates
```  

> **Примечание.** SSL-сертификаты от Let's Encrypt действительны в течение 
90 дней. Их нужно постоянно обновлять. Если вы не хотите делать это 
самостоятельно, вы можете настроить автоматическое обновление сертификата 
с помощью команды ниже.

```shell
sudo certbot renew --dry-run
```  

**Теперь вы можете получить доступ к сайту по его доменному имени.**

**Как только убедитесь, что все рецепты отображаются корректно и без проблем, 
вы можете начать приглашать пользователей делиться своими 
кулинарными шедеврами.**

***

## Автор

**Максим Головин**\
Вы можете заглянуть в другие мои репозитории в моем профиле GitHub. 
Нажмите [здесь](https://github.com/PrimeStr).

***
***

# Foodgram - Get inspired and share delicious dishes with the whole world!

***

#### Project link: primestr.sytes.net

***

# English version

Ищете Русскую версию? Вам сюда --> [click](#русская-версия) или листайте вверх.

***
***

## Stack:

[![Python](https://img.shields.io/badge/Python-%203.10-blue?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-%203.2.3-blue?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DjangoRESTFramework-%20-blue?style=flat-square&logo=django)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-%2024.0.5-blue?style=flat-square&logo=docker)](https://www.docker.com/)
[![DockerCompose](https://img.shields.io/badge/Docker_Compose-%202.21.0-blue?style=flat-square&logo=docsdotrs)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-%20-blue?style=flat-square&logo=githubactions)](https://github.com/features/actions)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-%2020.1.0-blue?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![Nginx](https://img.shields.io/badge/Nginx-%20-blue?style=flat-square&logo=nginx)](https://www.nginx.com/)
[![React](https://img.shields.io/badge/React-%20-blue?style=flat-square&logo=react)](https://react.dev/)
[![React](https://img.shields.io/badge/certbot-%20-blue?style=flat-square&logo=letsencrypt)](https://certbot.eff.org/)

***

## Functionality:

Foodgram provides the following features:

- **Adding and editing recipes**: Create beautifully designed recipes, add 
photos of your dishes and tell others how to cook it step by step.

- **Search for recipes**: Search for recipes by tags and authors.

- **Save to Favorites**: Add your favorite recipes to your favorites 
collection to easily find them in the future.

- **Shopping List**: Create a shopping list based on the ingredients needed to 
prepare selected dishes and save it. Later you will be able to download this 
list in PDF format and print it out so that you don't forget anything when 
going to the store.

- **Subscribe to authors**: You can subscribe to authors whose recipes inspire 
you to always be aware of their new culinary ideas.

***

## Technical features:

The repository includes two files **docker-compose.yml** and
**docker-compose.production.yml**, which allows you to deploy the project on
local or remote servers.

This instruction implies that Git, Python 3.10, pip package manager, Docker, 
Docker Compose and python3-venv virtual environment utility are already 
installed on your local/remote server.

The project provides the ability to run SQLite3 and PostgreSQL databases. 
The database is selected by changing the DEBUG value to True or False. 
True = SQLite3, False = PostgreSQL.

Detailed launch instructions can be found below.

***

## Running a project locally in Docker-containers using Docker Compose:

Clone the project from the repository:

```shell
git clone https://github.com/PrimeStr/foodgram-project-react.git
```


Go to the project directory:

```shell
cd foodgram-project-react/
```

Go to the **infra** directory and create the **.env** file:

```shell
cd infra/
```

```shell
nano .env
```

Add the lines contained in the **.env.example** file and 
substitute your values.

Example from .env file:

```dotenv
# DB is selected automatically based on the DEBUG constant. If DEBUG = True, SQLite3 is used.
# If DEBUG = False, PostgreSQL is used.

POSTGRES_USER=django_user            # Your db username
POSTGRES_PASSWORD=django             # Your db password
POSTGRES_DB=django                   # Name of your database
DB_HOST=db                           # The standard value is db
DB_PORT=5432                         # The standard value is 5432


SECRET_KEY=DJANGO_SECRET_KEY         # Your Django Secret Key
DEBUG=False                          # True - enable Debug. Or leave it empty for False
IS_LOGGING=False                     # True - enable Logging. Or leave it empty for False
ALLOWED_HOSTS=127.0.0.1              # A list of addresses separated by spaces

# Remember, if you set DEBUG=False, you will need to configure the ALLOWED_HOSTS list.
# 127.0.0.1 is the standard value. Without spaces or other characters.
```

The **infra** directory of the project contains the **docker-compose.yml** 
file, with which you can run the project locally in Docker containers.

While in the **infra** directory, run the following command:

> **Note.** If necessary, add the **-d** flag to the end of the command to run
> it in the background.

```shell
sudo docker compose -f docker-compose.yml up
```

It will build Docker images and run backend, frontend, DBMS and Nginx in 
separate Docker containers.

Perform migrations in a container with a backend:

```shell
sudo docker compose -f docker-compose.yml exec foodgram-backend python manage.py migrate
```

Collect backend static:

```shell
sudo docker compose -f docker-compose.yml exec foodgram-backend python manage.py collectstatic
```

Upon completion of all operations, the project will be launched and available 
at http://127.0.0.1/

To stop Docker containers while in the **infra** directory, run 
the following command:

```shell
sudo docker compose -f docker-compose.yml down
```

Or simply shut down Docker Compose in the terminal in which you
launched it, using the keyboard shortcut **CTRL+C**.

***

# CI/CD - Project deployment on a remote server

Workflow for GitHub Actions is already configured in the project.

Your GitHub Actions will independently launch:

- 🧪 Tests: Run tests for your project.
- 🏗️ Image Assembly: Get Action creates Docker images of your application.
- 🚀 Deployment: Images are sent to your DockerHub repository, the project 
is deployed to the server.
- ✉️ Notification: If successful, you will receive a notification in Telegram.

Fork the repository, go to GitHub in the repository settings —
**Settings**, find the item on the left panel
**Secrets and Variables**, go to **Actions**, click
**New repository secret**.

Create the following keys:

> **Note.** When connecting to your remote server GitHub Actions worker will 
> create a .env file, create a database and launch a container with a backend,
> using these constants.

```
# Shared secrets
DOCKER_USERNAME (Your login in DockerHub)
DOCKER_PASSWORD (Your password in DockerHub)
HOST (IP address of your remote server)
USER (Login of your remote server)
SSH_KEY (SSH key of your remote server)
SSH_PASSPHRASE (Password of your remote server)
TELEGRAM_TO (Your user ID in Telegram)
TELEGRAM_TOKEN (Token of your bot in Telegram)

# PostgreSQL
POSTGRES_USER (Your db username)
POSTGRES_PASSWORD (Your db password)
POSTGRES_DB (Your DB name)
DB_HOST (Db address. The standard value is db)
DB_PORT (Db port. The standard value is 5432)

# Django
SECRET_KEY (Your Django Secret key)
DEBUG (On/Off DEBUG)
IS_LOGGING (On/Off Logging)
ALLOWED_HOSTS (A list of addresses separated by spaces)
```

> **Attention!** For the correct display of images, do not forget to add the 
> domain name of your site to ALLOWED_HOSTS in addition to localhost 
> and 127.0.0.1.

Example of PostgreSQL and Django constants from .env file:

```dotenv
POSTGRES_USER=django_user            # Your db username
POSTGRES_PASSWORD=django             # Your db password
POSTGRES_DB=django                   # Name of your DB
DB_HOST=db                           # Standard value - db
DB_PORT=5432                         # The standard value is 5432

SECRET_KEY=DJANGO_SECRET_KEY         # Your Django Secret Key
DEBUG=False                          # True - enable Debug. Or leave it empty for False
IS_LOGGING=False                     # True - enable Logging. Or leave it empty for False
ALLOWED_HOSTS=127.0.0.1              # A list of addresses separated by spaces
```

### **Now you can proceed to the deployment**

> **Attention!** Further actions imply that on your remote server
> Nginx is installed and configured as a proxy server. Initially Nginx in
> Docker container listens on port 8500.

In the local project, replace the image names in the 
**docker-compose.production.yml** file in accordance with your login to 
DockerHub in lowercase (For example **your_name/foodgram_backend**)

Similarly, change the names of the images in the **main.yml** file, which 
is located in the **/.github/workflows/** directory.

Connect to your remote server in any convenient way. Create a directory in
your home directory with the name **foodgram** and go to it.

```shell
mkdir foodgram
```

Done.

The whole process is automated! As soon as you initiate a commit on the local 
machine and send the changes to GitHub, GitHub Actions takes matters 
into its own hands:

```shell
git add .
```

```shell
git commit -m "Your message for the commit."
```

```shell
git push
```

After successfully submitting the changes, go to the **Actions** tab in 
your GitHub repository. You will see the Actions process. After the end of
the worker's work, a message from the bot will come to your Telegram:

> Деплой проекта Foodgram успешно выполнен!

**This message means that the project has been successfully launched on the 
server, migrations have been performed and backend static has been collected.**

After that, you can return to the remote server, to the **foodgram** directory 
and create a superuser:

```shell
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

>**Attention! :** For the project to work properly, **Nginx** must be 
installed, configured and running on your remote server. Make sure that 
the config for your domain name is configured to forward all requests to
**127.0.0.1:8500** and header forwarding is added.

### Configuring SSL encryption via Let's Encrypt

In order for the project to meet the basic security standards, you need to 
configure SSL certificate.

Install **certbot**:

```shell
sudo apt install snapd
```

```shell
sudo snap install core; sudo snap refresh core
```

```shell
sudo snap install --classic certbot
```

```shell
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Launch sertbot and get your SSL certificate:

```shell
sudo certbot --nginx
```

Then restart Nginx:

```shell
sudo systemctl reload nginx
```  

```shell
sudo certbot certificates
```  

> **Note.** SSL certificates from Let's Encrypt are valid for 90 days. 
They need to be constantly updated. If you don't want to do this yourself, 
you can configure automatic certificate renewal using the command below.

```shell
sudo certbot renew --dry-run
```  

**Now you can access the site by its domain name.**

**As soon as you make sure that all recipes are displayed correctly and 
without problems, you can start inviting users to share their 
culinary masterpieces.**

***

## Author

**Maxim Golovin**\
You can take a look at my other repositories in my GitHub profile. 
Click [here](https://github.com/PrimeStr).
