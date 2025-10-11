from main import *
from typing import Any, Literal
import math
import os  # Импортируем модуль os для работы с файловой системой


def create_bigram_dist_folder() -> str:
    """
    Создает папку bigram_dist в текущей директории и возвращает её абсолютный путь.
    """
    folder_name = "bigram_dist"
    # os.path.join используется для корректного создания пути в разных ОС
    # os.path.abspath возвращает абсолютный путь
    dist_path = os.path.abspath(folder_name)

    # os.path.exists проверяет, существует ли папка
    if not os.path.exists(dist_path):
        # os.makedirs создает папку, exist_ok=True предотвращает ошибку, если папка уже существует
        os.makedirs(dist_path, exist_ok=True)
        print(f"Папка {dist_path} создана.")
    else:
        print(f"Папка {dist_path} уже существует.")

    return dist_path


DIST_PATH = (
    create_bigram_dist_folder()
)  # Присваиваем абсолютный путь к папке переменной DIST_PATH


def create_bigram_alphabet_with_frequencies(text: str) -> dict[str, int]:
    """
    Создает алфавит биграмм с их частотами из текста.
    """
    bigram_alphabet: dict[str, int] = {}
    for i in range(len(text) - 1):
        bigram: str = text[i : i + 2]  # Берем пару символов
        if bigram in bigram_alphabet:
            bigram_alphabet[bigram] += 1
        else:
            bigram_alphabet[bigram] = 1
    return bigram_alphabet


def calculate_bigram_entropy(bigram_alphabet) -> float | int:
    """
    Вычисляет энтропию для биграмм.
    """
    total_bigrams: int = sum(bigram_alphabet.values())
    probabilities: list[float] = [
        freq / total_bigrams for freq in bigram_alphabet.values()
    ]
    entropy: float | int = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return entropy


def write_bigram_codes_to_csv(codes, csv_filename) -> None:
    """
    Записывает схему кодирования биграмм в CSV файл, используя функцию из main.py.
    Путь к файлу формируется с учетом DIST_PATH.
    """
    # Формируем полный путь к файлу внутри папки DIST_PATH
    full_csv_path: str = os.path.join(DIST_PATH, csv_filename)
    write_codes_to_csv(codes, full_csv_path)


def encode_text_bigrams(text: str, codes: dict[str, str]) -> str:
    """
    Кодирует текст, рассматривая его как последовательность биграмм.
    Каждая биграмма заменяется соответствующим кодом из словаря 'codes'.
    """
    encoded_text: str = ""
    # Проходим по тексту с шагом 2, чтобы получить биграммы
    for i in range(0, len(text) - 1, 2):
        bigram: str = text[i : i + 2]
        # Убедимся, что биграмма существует в словаре кодов
        if bigram in codes:
            encoded_text += codes[bigram]
        else:
            # Если биграмма из текста не найдена в словаре кодов, вызываем ошибку
            # Это не должно происходить, если текст, используемый для кодирования,
            # совпадает с текстом, использованным для построения алфавита биграмм и кодов.
            raise KeyError(f"Биграмма '{bigram}' не найдена в словаре кодирования.")

    # Если длина текста нечетная, последний символ не является частью биграммы.
    # В зависимости от требований, можно кодировать его отдельно или игнорировать.
    # В этом задании мы предполагаем, что длина текста четная или обрабатываем
    # нечетный символ отдельно, если это необходимо.
    # Поскольку исходный текст может иметь нечетное количество символов,
    # последний символ может не входить в биграмму кодирования.
    # Если последний символ нужно закодировать, потребуется другой подход
    # для дополнения или обработки одиночных символов.
    # Здесь мы просто отметим, что он не включен в биграммное кодирование.
    if len(text) % 2 == 1:
        last_char: str = text[-1]
        print(
            f"Примечание: Последний символ '{last_char}' не является частью биграммы и не закодирован."
        )

    return encoded_text


def decode_text_bigrams(encoded_text: str, codes: dict[str, str]) -> str:
    """
    Декодирует текст, где исходный текст был представлен как последовательность биграмм.
    Кодированный текст декодируется с использованием инвертированного словаря 'codes'.
    """
    # Инвертируем словарь кодов для декодирования
    inverted_codes: dict[str, str] = {code: bigram for bigram, code in codes.items()}

    decoded_text: str = ""
    code_buffer: str = ""  # Буфер для сбора битов кода

    for bit in encoded_text:
        code_buffer += bit
        if code_buffer in inverted_codes:
            decoded_text += inverted_codes[code_buffer]
            code_buffer = ""  # Сброс буфера после нахождения соответствия

    # Если буфер кода не пуст в конце, это означает, что кодированный текст
    # может быть поврежден или неполон.
    if code_buffer:
        print(
            f"Предупреждение: Неполная последовательность кода '{code_buffer}' найдена в конце кодированного текста при декодировании."
        )

    return decoded_text


def main() -> None:
    filename = "input.txt"
    text: str = read_text_from_file(filename).lower().strip()

    bigram_alphabet: dict[str, int] = create_bigram_alphabet_with_frequencies(text)
    bigram_entropy: float | int = calculate_bigram_entropy(bigram_alphabet)
    shannon_fano_bigram_codes: dict[Any, str] | Any = shannon_fano(bigram_alphabet)

    # Записываем схему кодирования Шеннона-Фано для биграмм в CSV файл в папку DIST_PATH
    write_bigram_codes_to_csv(
        shannon_fano_bigram_codes, "shannon_fano_bigram_codes.csv"
    )

    avg_bigram_code_length: float = calculate_average_code_length(
        shannon_fano_bigram_codes, bigram_alphabet
    )
    compression_efficiency_bigram: float = calculate_compression_efficiency(
        math.ceil(math.log2(len(bigram_alphabet))), avg_bigram_code_length
    )

    print(f"Энтропия буквосочетаний: {truncate(bigram_entropy)}")
    print(f"Средняя длина буквосочетаний: {truncate(avg_bigram_code_length)}")
    print(
        f"Эффективность сжатия буквосочетаний: {truncate(compression_efficiency_bigram)}"
    )

    # Кодируем текст с использованием кодов биграмм
    try:
        encoded_bigram_text: Any | Literal[""] = encode_text_bigrams(
            text, shannon_fano_bigram_codes
        )
    except KeyError as e:
        print(f"Ошибка при кодировании: {e}")
        return  # Выход, если произошла ошибка при кодировании

    # Декодируем текст с использованием кодов биграмм
    decoded_bigram_text: Any | Literal[""] = decode_text_bigrams(
        encoded_bigram_text, shannon_fano_bigram_codes
    )

    # Записываем закодированный и декодированный текст в файлы в папку DIST_PATH
    encoded_file_path: str = os.path.join(DIST_PATH, "encoded_bigram.txt")
    decoded_file_path: str = os.path.join(DIST_PATH, "decoded_bigram.txt")

    with open(encoded_file_path, "w", encoding="utf-8") as file:
        file.write(encoded_bigram_text)

    with open(decoded_file_path, "w", encoding="utf-8") as file:
        file.write(decoded_bigram_text)


if __name__ == "__main__":
    main()
