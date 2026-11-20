TODO: 
core:
1) в checkROIcontours проверять не только форму контуров, но и их смещение

GUI:
1) ValidationRunner — принимает кадр + multi_roi, возвращает (result, canvases). Сейчас это 3 строки в on_btn_run_clicked, но туда неизбежно добавятся: обработка исключений extract_main_contour (кидает ValueError), замер времени, запись результата в JSON/лог, ретраи.

2) FailWindowManager — уже фактически есть (_fail_windows, _show_fail_window, _close_fail_windows, _forget_fail_window). Вынести в отдельный класс с методами show(title, img), close_all(). MainWindow будет вызывать self.fail_windows.show(...).

3) Обработка ошибок — сейчас их «съедает» тишина

4) show_validation_result — разделить ответственность
Метод делает три вещи: рисует main, закрывает старые fail-окна, открывает новые. Логично:

show_validation_result → тонкая обёртка: self._set_main_image(...), self.fail_windows.replace_all(fail_items).

Парсинг ключей "fail:" и вычисление stage — это скорее ответственность visualize (у него уже есть _stage_label). Можно сделать visualize.split_canvases(canvases) → (main, [(name, stage, img), ...]), чтобы MainWindow не знал про формат ключей. Это уменьшит связность.




