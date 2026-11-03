# Конфигурация для тестового стенда

Сверено с [разделом 08.2 рабочей базы](https://app.notion.com/p/b3533dfca65f82159fb3016ca6537f4a) 2 ноября 2026 г. Это публичные коды встраивания, они не исполняются в локальном макете. После подключения тестового клуба используйте согласованные настройки стенда и отдельные контейнеры T123. До ввода данных проверить домен, режим тестирования, передачу согласия и кассу. Приведённые фрагменты относятся к рабочему клубу, для тестовой оплаты требуется отдельная конфигурация.

## Расписание

```html
<div id="mf_schedule_widget_cont_hik"></div>
<script type="text/javascript" async="async" id="mobifitness_personal_widget_script_hik" src="//mobifitness.ru/personal-widget/js/code.js" data-div="mf_schedule_widget_cont_hik" data-test="0" data-debug="0" data-domain="mobifitness.ru" data-code="308687" data-version="v6" data-type="schedule" data-language="" data-club="9514"></script>
```

## Личный кабинет

```html
<div id="mf_personal_widget_cont_5k3"></div>
<script type="text/javascript" async="async" id="mobifitness_personal_widget_script_5k3" src="//mobifitness.ru/personal-widget/js/code.js" data-div="mf_personal_widget_cont_5k3" data-test="0" data-debug="0" data-domain="mobifitness.ru" data-code="308687" data-version="v6" data-type="personal" data-language="" data-club="9514"></script>
```

## Магазин

```html
<div id="mf_shop_widget_cont_mng"></div>
<script type="text/javascript" async="async" id="mobifitness_personal_widget_script_mng" src="//mobifitness.ru/personal-widget/js/code.js" data-div="mf_shop_widget_cont_mng" data-test="0" data-debug="0" data-domain="mobifitness.ru" data-code="308687" data-version="v6" data-type="shop" data-language="" data-club="9514"></script>
```
