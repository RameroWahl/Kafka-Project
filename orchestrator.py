import subprocess
import time

def run(cmd):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True)

run("kubectl apply -f kafka-cluster.yaml")

time.sleep(30)

run("kubectl wait --for=condition=ready pod -l app=kafka --timeout=180s")

run("kubectl apply -f topic-init.yaml")
time.sleep(10)

run("kubectl apply -f consumer.yaml")
run("kubectl apply -f producer.yaml")
run("kubectl apply -f schema-registry.yaml")
time.sleep(10)

print("System ready.")
run("kubectl apply -f kafka-ui.yaml")