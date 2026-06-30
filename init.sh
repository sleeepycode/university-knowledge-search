#!/usr/bin/env bash

set -Eeuo pipefail

API_URL="${API_URL:-http://localhost:8000/api/v1}"
HEALTH_URL="${HEALTH_URL:-${API_URL}/health}"
UPLOAD_URL="${UPLOAD_URL:-${API_URL}/documents/upload}"

TEMP_DIR="${TEMP_DIR:-./tmp/init-pdfs}"
WAIT_ATTEMPTS="${WAIT_ATTEMPTS:-30}"
WAIT_SECONDS="${WAIT_SECONDS:-2}"

PDF_URLS=(
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/c32185c7158955425455159a8455298b_MIT6_006F11_lec01.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/6b9b20992d8c6a0f3f10a34ff7878aa9_MIT6_006F11_lec02.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/90a37c49b07b105ea7a027abc67eddc6_MIT6_006F11_lec03.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/8ebfeb1c645b10b3709919603e7d51be_MIT6_006F11_lec04.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/d9c745bbfb610e9e53f6aef4261f3805_MIT6_006F11_lec05.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/83cdd705cd418d10d9769b741e34a2b8_MIT6_006F11_lec06.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/bf7d79105762bf79bbc0925438e1468a_MIT6_006F11_lec07.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/d3e4d64266d481c74c9e7c15e09999fe_MIT6_006F11_lec08.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf"
  "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/a7f609148928e4a10653d3f3be03a2b5_MIT6_006F11_lec10.pdf"
)

PDF_NAMES=(
  "mit_lecture_01_peak_finding.pdf"
  "mit_lecture_02_computation_models.pdf"
  "mit_lecture_03_insertion_merge_sort.pdf"
  "mit_lecture_04_heaps.pdf"
  "mit_lecture_05_binary_search_trees.pdf"
  "mit_lecture_06_avl_trees.pdf"
  "mit_lecture_07_counting_radix_sort.pdf"
  "mit_lecture_08_hashing_chaining.pdf"
  "mit_lecture_09_table_doubling.pdf"
  "mit_lecture_10_cryptographic_hashing.pdf"
)

cleanup() {
  rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

if ! command -v curl >/dev/null 2>&1; then
  echo "Ошибка: команда curl не найдена."
  echo "Запустите скрипт через Git Bash или установите curl."
  exit 1
fi

mkdir -p "$TEMP_DIR"

echo "Проверка доступности backend:"
echo "$HEALTH_URL"

backend_ready="false"

for ((attempt = 1; attempt <= WAIT_ATTEMPTS; attempt++)); do
  if curl \
    --silent \
    --show-error \
    --fail \
    "$HEALTH_URL" \
    >/dev/null; then

    backend_ready="true"
    echo "Backend доступен."
    break
  fi

  echo "Попытка ${attempt}/${WAIT_ATTEMPTS}: backend ещё не готов."
  sleep "$WAIT_SECONDS"
done

if [[ "$backend_ready" != "true" ]]; then
  echo "Ошибка: backend не стал доступен."
  echo "Проверьте контейнер командой:"
  echo "docker compose logs app --tail=200"
  exit 1
fi

total="${#PDF_URLS[@]}"
downloaded=0
uploaded=0
failed=0

for index in "${!PDF_URLS[@]}"; do
  number=$((index + 1))
  url="${PDF_URLS[$index]}"
  filename="${PDF_NAMES[$index]}"
  file_path="${TEMP_DIR}/${filename}"
  response_file="${TEMP_DIR}/response_${number}.json"

  echo
  echo "========================================"
  echo "[${number}/${total}] ${filename}"
  echo "========================================"

  echo "Скачивание PDF..."

  if ! curl \
    --silent \
    --show-error \
    --fail \
    --location \
    --retry 3 \
    --retry-delay 2 \
    --connect-timeout 20 \
    --max-time 180 \
    --output "$file_path" \
    "$url"; then

    echo "Ошибка скачивания: ${filename}"
    failed=$((failed + 1))
    continue
  fi

  if [[ "$(head -c 4 "$file_path")" != "%PDF" ]]; then
    echo "Ошибка: скачанный файл не является PDF."
    failed=$((failed + 1))
    continue
  fi

  downloaded=$((downloaded + 1))

  file_size="$(wc -c <"$file_path" | tr -d ' ')"

  echo "PDF скачан."
  echo "Размер: ${file_size} байт"
  echo "Загрузка через API..."

  http_code="$(
    curl \
      --silent \
      --show-error \
      --output "$response_file" \
      --write-out "%{http_code}" \
      --request POST \
      --form "file=@${file_path};type=application/pdf" \
      "$UPLOAD_URL" \
      || true
  )"

  if [[ "$http_code" == "201" ]]; then
    uploaded=$((uploaded + 1))

    echo "Документ успешно загружен."
    echo "HTTP: ${http_code}"

    if [[ -s "$response_file" ]]; then
      cat "$response_file"
      echo
    fi
  else
    failed=$((failed + 1))

    echo "Ошибка загрузки документа."
    echo "HTTP: ${http_code}"

    if [[ -s "$response_file" ]]; then
      cat "$response_file"
      echo
    fi
  fi
done

echo
echo "========================================"
echo "Результат начального наполнения"
echo "========================================"
echo "Всего документов: ${total}"
echo "Скачано: ${downloaded}"
echo "Загружено: ${uploaded}"
echo "Ошибок: ${failed}"

if [[ "$uploaded" -ne "$total" ]]; then
  echo "Начальное наполнение завершилось с ошибками."
  exit 1
fi

echo "Все 10 PDF успешно загружены."