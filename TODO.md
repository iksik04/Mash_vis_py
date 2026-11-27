# Project Structure & Architectural Decisions

> Документ фиксирует текущее состояние проекта, принятые решения по рефакторингу
> и целевую структуру папок. Обновляется по мере продвижения работ.

---

## Содержание

1. [Текущее состояние (baseline)](#1-текущее-состояние-baseline)
2. [Принятые решения](#2-принятые-решения-зафиксировано)
3. [Целевая структура папок](#3-целевая-структура-папок)
4. [Ключевые сигнатуры](#4-ключевые-сигнатуры)
5. [MainWindow после рефакторинга](#5-mainwindow-после-рефакторинга-эскиз)
6. [Порядок работ](#6-порядок-работ)
7. [Что НЕ делаем](#7-что-не-делаем-явно)
8. [Открытые вопросы](#8-открытые-вопросы)

---

## 1. Текущее состояние (baseline)

### Файлы проекта
backend/
constants.py # пути, имена файлов, дефолты, цвета, пороги
img_process.py # RefImgContext, CurImgContext, extract_main_contour,

render_img, cv2qt_img, scale_pixmap, OCR_imgPreprocess
json_process.py # save/read_ref_context, save/read_MultiROI, _write_json/_read_json
geometry.py # rot_matrix_deg, rect_corners, normalize_angle_deg
workers/
camera_worker.py # CameraWorker (facade) + _CaptureThread (QThread)
sessions/
ref_context_session.py # RefContextSession (frozen frame + rebuild)
roi/
roi.py # SingleROI, MultiROI

ui/
main_wind.py # Ui_mainWindow (сгенерирован из .ui, не редактировать)
MainWindow.py # MainWindow(QMainWindow) — контроллер (рефакторится)

text

### Известные проблемы baseline

1. **Дубль `_on_save_refcontext`** в `MainWindow.py` — первое определение (строки ~107)
   мёртвое, второе (строки ~300) живое. Удалить первый.
2. **`MainWindow` — god object**: UI-события, камера, RefContext-сессия, парсинг,
   валидация, файлы — всё в одном классе (~330 строк, растёт).
3. **Дублирование состояния**: `MainWindow._last_frame` дублирует `CameraWorker.last_frame`.
4. **Хардкод диапазонов/расширений** в `MainWindow` (`0..255`, `.json`, `.jpg`, `127`).
5. **Рассинхрон slider ↔ edit-поле** при невалидном вводе (поле остаётся "abc",
   слайдер показывает default).
6. **`main_img` (QLabel) не перемасштабируется при ресайзе окна** во время паузы.
7. **`CameraWorker.stop()` без `wait()`** — риск при закрытии окна (см. п.4).
8. **`RefContextSession` не имеет конструктора из готового `RefImgContext`** —
   load требует пересборки.

---

## 2. Принятые решения (зафиксировано)

| # | Вопрос | Решение |
|---|--------|---------|
| 1 | Семантика `saveRefContext_btn` | Save = **сохранить + закрыть сессию** + resume live. Отдельная кнопка Cancel **не нужна**. |
| 2 | Семантика `loadRefContext_btn` | Диалог выбора JSON → `read_ref_context` → заполнить форму (threshold, min_len, имена) → **создать сессию** на загруженном `bgr_img` (заморозить live, показать preview). |
| 3 | `_check_version` в `json_process` | Не трогаем (не дебажим). |
| 4 | Имена файлов | Только имя, **без путей**. Пути жёсткие (из `constants`). Санитизация: запрет `/ \ : * ? " < > |`, `.`, `..`. |
| 5 | Сохранение имён между запусками | **Не нужно**. `QSettings` не вводим. |
| 6 | `MainWindow._last_frame` | **Убрать**. Брать `self.camera.last_frame`. |
| 7 | `CameraWorker.pause()` | Оставить как есть (`cap.read()` продолжает работать — осознанно). |
| 8 | `CameraWorker.stop()` / закрытие окна | Новый метод **`shutdown()` = `stop()` + `wait(1000)`**. Вызывать **только** из `closeEvent`. Обычный `stop()` остаётся лёгким (без `wait`). |
| 9 | `fps` камеры | Главное — не грузить CPU. `msleep(interval_ms)` уже есть. |
| 10 | Поток `CameraWorker` | В GUI-потоке, как есть. `last_frame` обновляется через queued signal — потокобезопасно. |
| 11 | ROI-инфраструктура | `MultiROI` / `SingleROI` готовы (`add/remove/get/set_contour/render_all/extract_all`). |
| 12–14 | ROI-хендлеры | **Пока не трогаем** — заглушки. `RoiController` закладываем пустым классом. |
| 15 | Канал логов | Единственный — `log_bar_panel` (`QPlainTextEdit`). Единого логгера нет. |
| 16 | Верхняя граница `min_contour_len` | **Доверять пользователю**. Только `max(0, ml)`. |
| 17 | Невалидный ввод в edit-поле | **Сбросить поле к валидному значению** + warn в лог. |
| 18 | Ресайз окна | **Нужен `resizeEvent`** → перемасштабировать последний `QPixmap`. |
| 19 | `scale_pixmap` (`SmoothTransformation`) | Не трогаем. |
| 20 | `setMaximumBlockCount` для лога | **Не нужен**. Лог растёт — осознанно. |
| 21 | Validation-страница | Планируется. `ValidationController` закладываем пустым классом. |
| 22 | Разбиение | **На папки** (см. п.3). |
| 23 | Тесты | Отсутствуют. Перед выносом — **smoke round-trip** для `save/read_ref_context` и `save/read_MultiROI` (скрипт, без pytest-инфраструктуры). |
| 24 | `QSettings` | Не нужен. |

---

## 3. Целевая структура папок
ui/
init.py
main_window.py # ~80-100 строк: connect + делегирование
controllers/
init.py
camera_controller.py # обёртка над CameraWorker + shutdown()
ref_context_controller.py # сессия, freeze/resume, save/load, preview
roi_controller.py # заглушка: MultiROI + add/copy/del/save (TODO)
validation_controller.py # заглушка: TODO
widgets/
init.py
int_slider_edit.py # синхронизация slider ↔ QLineEdit
int_line_edit.py # QLineEdit с парсингом/clamp/сбросом
image_view.py # show(frame) + resizeEvent + last_pixmap
helpers/
init.py
parsing.py # parse_int(text, default, lo, hi) -> (val, warn)
file_naming.py # sanitize_filename, with_ext
log_sink.py # тонкая обёртка над log_bar_panel (info/warn/error)

text

### Ответственности

| Модуль | Ответственность |
|--------|-----------------|
| `main_window.py` | Только `connect` сигналов и делегирование контроллерам. Никакой бизнес-логики. |
| `camera_controller.py` | `start/pause/resume/stop/shutdown`, проксирование `frame_ready`/`error`, `last_frame`. |
| `ref_context_controller.py` | Жизненный цикл `RefContextSession`, freeze/resume live, save/load, preview-рендер. |
| `roi_controller.py` | (TODO) `MultiROI`, add/copy/del/save. Пока — пустые слоты. |
| `validation_controller.py` | (TODO) Валидация. Пока — пустой класс. |
| `int_slider_edit.py` | Двусторонняя синхронизация `QSlider` ↔ `QLineEdit`, clamp, сброс к валидному (п.17). |
| `int_line_edit.py` | `QLineEdit` с парсингом, clamp, сбросом к валидному (п.17). |
| `image_view.py` | `show(bgr_frame)`, хранение `QPixmap`, `rescale()` на `resizeEvent` (п.18). |
| `parsing.py` | Чистая функция `parse_int`, без зависимости от UI. |
| `file_naming.py` | `sanitize_filename`, `with_ext` (п.4). |
| `log_sink.py` | `info/warn/error` → `appendPlainText` с префиксами `--MES/--WARN/--ERR`. |

---

## 4. Ключевые сигнатуры

### `CameraWorker` (изменения)

```python
class CameraWorker(QObject):
    ...
    @Slot()
    def shutdown(self):
        """stop() + wait(1000). Вызывать только из closeEvent."""
        if self._thread.isRunning():
            self._thread.stop()
            self._thread.wait(1000)
RefContextSession (добавление)
python
@classmethod
def from_context(cls, ctx: RefImgContext) -> "RefContextSession":
    self = cls.__new__(cls)
    self._frame = ctx.bgr_img.copy()
    self.bin_threshold = ctx.ref_low_threshold
    self.min_contour_len = int(ctx.min_ext_contour_length)
    self._context = ctx
    return self
RefContextController
python
class RefContextController:
    def __init__(self, ui, camera, image_view, log): ...
    def start_session(self): ...           # было _on_select_refcontext_params
    def load(self): ...                    # было _on_load_refcontext (вариант а)
    def save_and_close(self): ...          # было _on_save_refcontext (второй)
    def close(self, resume_live=True): ... # было _close_ref_session
    def _on_params_changed(self, bt, ml): ...
    def _render(self): ...                 # image_view.show(canvas)
IntSliderEdit / IntLineEdit (п.17)
python
class IntSliderEdit:
    def __init__(self, slider, edit, lo, hi, on_change, log): ...
    # при невалидном вводе: parse_int → default → edit.setText(str(default)) + log.warn
    # slider ↔ edit синхронизируются через blockSignals

class IntLineEdit:
    def __init__(self, edit, lo, hi, on_change, log): ...
    # при невалидном вводе: parse_int → default → edit.setText(str(default)) + log.warn
ImageView (п.18)
python
class ImageView:
    def __init__(self, label): ...
    def show(self, bgr_frame): ...        # cv2qt_img → _pixmap → _rescale()
    def _rescale(self): ...               # scale_pixmap(_pixmap, label.size())
    def on_resize(self): ...              # вызывать из MainWindow.resizeEvent
helpers/parsing.py
python
def parse_int(text: str, default: int,
              lo: int | None = None, hi: int | None = None
              ) -> tuple[int, str | None]:
    """Возвращает (value, warn_or_None). warn — текст для лога."""
helpers/file_naming.py (п.4)
python
_BAD = set('/\\:*?"<>|')

def sanitize_filename(name: str, default: str) -> str:
    name = name.strip()
    if not name or any(ch in _BAD for ch in name) or name in (".", ".."):
        return default
    return name

def with_ext(name: str, ext: str) -> str:
    return name if name.lower().endswith(ext) else name + ext
5. MainWindow после рефакторинга (эскиз)
python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self._log = LogSink(self.ui.log_bar_panel)
        self._camera = CameraController(self)
        self._image_view = ImageView(self.ui.main_img)
        self._ref = RefContextController(self.ui, self._camera, self._image_view, self._log)
        self._roi = RoiController(self.ui, self._log)                 # заглушка
        self._validation = ValidationController(self.ui, self._log)   # заглушка

        self._connect_signals()
        self._setup_initial_state()
        self._camera.start()

    def _connect_signals(self):
        # pages
        self.ui.settings_validation_page_btns.idClicked.connect(
            self.ui.validation_settings_stacked.setCurrentIndex)
        self.ui.RefContext_ROIs_page_btns.idClicked.connect(
            self.ui.RefContext_ROI_stacked.setCurrentIndex)
        # RefContext — делегирование
        self.ui.loadRefContext_btn.clicked.connect(self._ref.load)
        self.ui.saveRefContext_btn.clicked.connect(self._ref.save_and_close)
        self.ui.select_RefContext_params_btn.clicked.connect(self._ref.start_session)
        # ROI — заглушки
        self.ui.addROI_btn.clicked.connect(self._roi.add)
        self.ui.copyROI_btn.clicked.connect(self._roi.copy)
        self.ui.delROI_btn.clicked.connect(self._roi.delete)
        self.ui.saveROI_btn.clicked.connect(self._roi.save)
        # camera
        self._camera.frame_ready.connect(self._image_view.show)
        self._camera.error.connect(self._log.error)

    def resizeEvent(self, event):
        self._image_view.on_resize()
        super().resizeEvent(event)

    def closeEvent(self, event):
        self._ref.close(resume_live=False)
        self._camera.shutdown()
        super().closeEvent(event)
6. Порядок работ
Smoke round-trip для save/read_ref_context и save/read_MultiROI — скрипт,
без фреймворка (п.23).

helpers/parsing.py + helpers/file_naming.py + helpers/log_sink.py —
чистые функции, без UI-зависимостей.

widgets/int_slider_edit.py + widgets/int_line_edit.py + widgets/image_view.py —
изолированные классы.

controllers/camera_controller.py — обёртка над CameraWorker + shutdown()
(п.8).

controllers/ref_context_controller.py — перенос логики из MainWindow
(с from_context, sanitize_filename, IntSliderEdit).

main_window.py — сократить до connect + делегирования; удалить дубль
_on_save_refcontext; _on_frame_ready → image_view.show.

Заглушки RoiController, ValidationController — пустые классы с
сигнатурами хендлеров.

constants.py — добавить REF_CONTEXT_BIN_THRESHOLD_RANGE = (0, 255).

Проверка: MainWindow ≤ 100 строк, бизнес-логика вынесена.

7. Что НЕ делаем (явно)
Не вводим QSettings (п.5, 24).

Не трогаем _check_version (п.3).

Не трогаем scale_pixmap / SmoothTransformation (п.19).

Не вводим setMaximumBlockCount для лога (п.20).

Не реализуем ROI/Validation сейчас (п.12–14, 21) — только заглушки.

Не добавляем верхнюю границу для min_contour_len (п.16).

Не останавливаем cap.read() при паузе (п.7).

Не переносим CameraWorker в отдельный поток (п.10).

Не пишем полноценные unit-тесты — только smoke round-trip (п.23).

8. Открытые вопросы
Нет. Все блокирующие вопросы закрыты (п.1–24). Решение по CameraWorker.stop() —
вариант (в): новый shutdown() = stop() + wait(1000), вызывать только из
closeEvent.