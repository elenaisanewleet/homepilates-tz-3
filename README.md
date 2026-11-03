# HomePilates V4 · Атлас движения

Откройте [галерею сравнения](review/index.html) или [главную V4](review/site/index.html) в браузере из локальной копии. В галерее есть все восемь страниц и снимки V3 и V4 при одинаковой ширине экрана. Ветка разработки — `design/v4-refinement`. [Опубликованная V3](https://homepilates-tz-3.vercel.app/site/index.html).

Для локального просмотра по HTTP запустите из корня репозитория:

```sh
python3 -m http.server 8444 --bind 127.0.0.1 --directory review
```

Откройте [галерею](http://127.0.0.1:8444/) или [главную](http://127.0.0.1:8444/site/index.html). Для пересборки нужны Python 3 и `cwebp`. Команда `python3 design/build.py` записывает результат в `review/site/`.

[Изменения и ограничения V4](review/v4.md) · [Проверки в браузерах](review/verification/v4-browser.json) · [Карта сборки в Tilda](review/tilda-map.md) · [Приёмка интеграций](review/acceptance.md) · [Архив V3](https://github.com/elenaisanewleet/homepilates-tz-3/raw/refs/heads/main/HomePilates-review.zip).
