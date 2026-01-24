import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# 0. Определение путей и создание директорий
BASE_DIR = Path(__file__).parent.parent

NOTES_SERVICE_KEYS_DIR = BASE_DIR / "notes" / "core" / "security_keys"
NOTES_USERS_KEYS_DIR = BASE_DIR / "users" / "core" / "security_keys"

# Убедимся, что директории существуют
for d in [NOTES_SERVICE_KEYS_DIR, NOTES_USERS_KEYS_DIR]:
    if not d.exists():
        d.mkdir(parents=True, exist_ok=True) 
        print(f"Директория '{d}' была создана.")
    else:
        print(f"Директория '{d}' уже существует.")

# Имена файлов ключей
PRIVATE_KEY_FILENAME = "private_key.pem"
PUBLIC_KEY_FILENAME = "public_key.pem"

# Полный путь к приватному ключу для users сервиса
USERS_PRIVATE_KEY_PATH = NOTES_USERS_KEYS_DIR / PRIVATE_KEY_FILENAME
# Полный путь к публичным ключам для обоих сервисов
USERS_PUBLIC_KEY_PATH = NOTES_USERS_KEYS_DIR / PUBLIC_KEY_FILENAME
NOTES_PUBLIC_KEY_PATH = NOTES_SERVICE_KEYS_DIR / PUBLIC_KEY_FILENAME


# 1. Генерация ключей, только если приватный ключ еще не существует для users_service
if USERS_PRIVATE_KEY_PATH.exists():
    print(f"Приватный ключ уже существует по пути: {USERS_PRIVATE_KEY_PATH}. Новая генерация пропущена.")
else:
    print("Генерация новых ключей Ed25519...")
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # 2. Сериализация закрытого ключа в PEM-формат и запись в файл для notes_users
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(USERS_PRIVATE_KEY_PATH, "wb") as f:
        f.write(pem_private)
    print(f"Приватный ключ успешно записан в {USERS_PRIVATE_KEY_PATH}")

    # 3. Сериализация открытого ключа в PEM-формат и запись в файлы для обоих сервисов
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Записываем публичный ключ для notes_users
    with open(USERS_PUBLIC_KEY_PATH, "wb") as f:
        f.write(pem_public)
    print(f"Публичный ключ для notes_users успешно записан в {USERS_PUBLIC_KEY_PATH}")

    # Записываем публичный ключ для notes_service
    with open(NOTES_PUBLIC_KEY_PATH, "wb") as f:
        f.write(pem_public)
    print(f"Публичный ключ для notes_service успешно записан в {NOTES_PUBLIC_KEY_PATH}")

print("\nПроверка наличия ключей:")
print(f"  Приватный ключ users: {USERS_PRIVATE_KEY_PATH.exists()}")
print(f"  Публичный ключ users: {USERS_PUBLIC_KEY_PATH.exists()}")
print(f"  Публичный ключ notes: {NOTES_PUBLIC_KEY_PATH.exists()}")
