# ClassifiedAds

Сайт объявлений: frontend (nginx), backend (Python), база Postgres. Запускается в Docker и в Kubernetes.




## Запуск в Kubernetes (Minikube)

1. Поднять кластер:
   minikube start --driver=docker --cni=bridge

2. Создать ConfigMap и Secret (пароль в Git не хранится, подставь свой):
   kubectl create configmap db-configmap --from-literal=POSTGRES_DB=classifieds --from-literal=POSTGRES_USER=postgres
   kubectl create secret generic db-secret --from-literal=POSTGRES_PASSWORD=<твой_пароль>

3. Применить манифесты:
   kubectl apply -f k8s/

4. Проверить:
   kubectl get pods
