import random
from rich import print
from rich.panel import Panel
from rich.console import Console
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet as Cryptocurrency
from mnemonic import Mnemonic
from multiprocessing import Process, cpu_count

# Загружаем базу адресов
filename = '10000richAddressETH.txt'
with open(filename) as f:
    add = set(f.read().split())

console = Console()

def write_to_file(addr, priv, words):
    """Функция для записи совпадений в файл"""
    with open('Winner_ETH_WalletWinner.txt', 'a') as f:
        f.write(f'\nAddress     === {addr}')
        f.write(f'\nPrivateKey  === {priv}')
        f.write(f'\nMnemonic    === {words}')
        f.write('\n---------------------------------------------\n')

def mmdrza(worker_id):
    """
    Основная функция генерации мнемоник, проверки адресов и логирования результата.
    """
    total_checked = 0
    matches_found = 0

    while True:  # Бесконечный цикл
        # Генерация мнемонической фразы
        mne = Mnemonic("english")
        strength = random.choice([128])  # Выбираем длину фразы (12 или 24 слова)
        words = mne.generate(strength=strength)

        # Создание HDWallet из мнемоника
        bip44_hdwallet = BIP44HDWallet(cryptocurrency=Cryptocurrency)
        bip44_hdwallet.from_mnemonic(mnemonic=words, language="english")

        # Список для хранения сгенерированных адресов
        generated_addresses = {}
        priv_keys = {}

        # Перебираем иерархические пути и генерируем 1000 адресов
        for index in range(500):
            bip44_hdwallet.from_path(f"m/44'/60'/0'/0/{index}")

            addr = bip44_hdwallet.p2pkh_address()
            priv = bip44_hdwallet.private_key()

            # Сохраняем в словари
            generated_addresses[addr] = priv
            priv_keys[addr] = priv

            # Сбрасываем путь для следующей итерации
            bip44_hdwallet.clean_derivation()

        # Сравниваем с базой
        matching_addresses = add.intersection(generated_addresses)

        # Обрабатываем совпадения
        for match in matching_addresses:
            matches_found += 1
            write_to_file(match, priv_keys[match], words)

        # Обновляем общий счетчик проверок
        total_checked += 1000

        # Вывод прогресса в консоль
        panel = Panel(
            f"Worker: {worker_id}  |  Total Checked: {total_checked}  |  Matches Found: {matches_found}\n",
            title="Ethereum Mnemonic Checker",
            subtitle="Mmdrza.Com",
            style="gold1"
        )
        console.print(panel)

if __name__ == '__main__':
    num_workers = cpu_count()  # Определяем количество ядер процессора
    processes = []

    console.print(Panel(f"Starting {num_workers} workers...", style="bold green"))

    # Запускаем процессы
    for worker_id in range(num_workers):
        p = Process(target=mmdrza, args=(worker_id,))
        processes.append(p)
        p.start()

    # Ожидаем завершения процессов (они будут работать бесконечно)
    for p in processes:
        p.join()
