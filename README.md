# CI/CD и GitOps с Argo CD

Проект демонстрирует полный цикл доставки простого Python-приложения: проверку кода, тестирование, сборку Docker-образа, публикацию в Docker Hub и развёртывание в Kubernetes через Argo CD.

Приложение — статический HTTP-сервер на Python, который слушает порт `8000` и отдаёт файл `server/index.html`.

## Схема работы

```text
push в dev
    └─ GitHub Actions: pylint → pytest → сборка и проверка контейнера

merge/push в main
    └─ GitHub Actions: сборка и публикация Docker-образа
       └─ обновление release-date в Kubernetes-манифесте
          └─ публикация манифеста в ветку release
             └─ Argo CD синхронизирует приложение с Kubernetes
```

Ветка `release` используется как GitOps-источник для Argo CD. Изменение метки `release-date` заставляет Kubernetes создать новый ReplicaSet даже при неизменном теге образа `latest`.

## Структура проекта

```text
.
├── .github/workflows/
│   ├── cicd.yml                 # проверки изменений в ветке dev
│   └── release.yml              # публикация образа и release-манифеста
├── server/
│   ├── application.py           # HTTP-сервер
│   ├── index.html               # содержимое главной страницы
│   ├── test_application.py      # модульные тесты
│   └── dockerfile               # образ приложения
├── server-k8s-manifests/
│   └── devops-psu.yml           # Namespace, Deployment и Service
├── results/                     # результаты проверок CI/CD, Argo CD и Kubernetes
└── requirements.txt             # инструменты тестирования и линтинга
```

## Локальный запуск

Требуется Python 3.10 или новее.

```bash
cd server
python3 application.py
```

После запуска приложение доступно по адресу <http://localhost:8000>.

## Тесты и линтинг

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=server pytest server/
pylint server/application.py
```

## Запуск в Docker

```bash
docker build -t devops-psu ./server --file ./server/dockerfile
docker run --rm -p 8000:8000 devops-psu
curl http://127.0.0.1:8000/
```

Контейнер запускается от непривилегированного пользователя `runner`.

## Развёртывание в Kubernetes

Манифест создаёт namespace `devops-psu`, один экземпляр приложения и сервис `LoadBalancer`. Сервис принимает трафик на порту `12345` и перенаправляет его на порт контейнера `8000`.

Для ручного развёртывания:

```bash
kubectl apply -f server-k8s-manifests/devops-psu.yml
kubectl get all -n devops-psu
kubectl rollout status deployment/devops-psu -n devops-psu
```

Проверить приложение без зависимости от реализации `LoadBalancer` можно через port-forward:

```bash
kubectl port-forward -n devops-psu service/service-devops 12345:12345
curl http://127.0.0.1:12345/
```

## Настройка CI/CD

Для workflow публикации в настройках GitHub-репозитория необходимы секреты:

- `DOCKER_USERNAME` — имя пользователя Docker Hub;
- `DOCKER_TOKEN` — access token Docker Hub.

Workflow работают следующим образом:

- `.github/workflows/cicd.yml` запускается при push в `dev`, выполняет `pylint`, `pytest`, собирает контейнер и проверяет HTTP-ответ;
- `.github/workflows/release.yml` запускается при push в `main`, публикует образ `<DOCKER_USERNAME>/devops-psu:latest` и принудительно обновляет ветку `release`;
- Argo CD должен следить за веткой `release` и каталогом `server-k8s-manifests`.

Текущий Kubernetes-манифест ссылается на образ `timerider33/devops-psu:latest`. Если используется другой Docker Hub-аккаунт, это значение нужно изменить в `server-k8s-manifests/devops-psu.yml` вместе с настройкой `DOCKER_USERNAME`.

## Проверка состояния

```bash
kubectl get applications -n argocd
kubectl get all -n devops-psu
kubectl get service service-devops -n devops-psu
```

Примеры успешного прохождения конвейера и синхронизации находятся в каталоге `results/`.
