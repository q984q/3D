# Источники и лицензии визуального теста

Материалы ниже используются **только как заменяемые визуальные примеры**, они не устанавливают породы растений, тип/размеры покрытия или техническое решение проекта. Не использовать для ведомостей. В исходной сцене `palladium_reconstruction_03.blend` и GLB их нет.

## Shrub 02

- Автор: Rico Cilliers, Poly Haven. Оригинальная страница: https://polyhaven.com/a/shrub_02
- Лицензия: CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/
- Получено из GitHub-репозитория `ruralive/ruralive-models`, подтверждающего источник и лицензию: https://github.com/ruralive/ruralive-models/blob/36e72c6057f31c81325215c46e11d552b0429fee/CREDITS.md
- Файл: https://github.com/ruralive/ruralive-models/blob/36e72c6057f31c81325215c46e11d552b0429fee/models/shrub_02.glb
- Локальная копия `polyhaven/shrub_02.glb`, SHA-256 `fffb8218d61d11a22da2cba0e6ca8baf2bada017c29d3f7d6744e6f5a675b8f2`. Из набора используются экземпляры первого объекта, с равномерным уменьшением до приблизительной ширины 0,68 м по существующим девяти условным маркерам.

## Paving Stones 002

- Автор/источник: ambientCG, https://ambientcg.com/view?id=PavingStones002
- Лицензия всех материалов ambientCG: CC0 1.0, https://ambientcg.com/ ; https://creativecommons.org/publicdomain/zero/1.0/
- Исходные карты 2K получены из репозитория https://github.com/Calinou/godot-cmvalley/tree/40ad117a1ab307799e1a3eebbdb91433f3e58d2f/ambientcg (файлы `PavingStones002_2K_Color.jpg`, `_Normal.jpg`, `_Roughness.jpg`). Локальные копии уменьшены до 1024×1024 и пересохранены JPEG для скорости просмотра.
- Локальные SHA-256: Color `396b6300c8b84e5a5998bc74021701b87fbe33fdcea5c6cc942a32e2db40b1a0`; Normal `574f2e0f08e08e2e330217775b280609103de141e57529b37945520629074c87`; Roughness `6024da33969c5fff9319ef88cd12a52e007630c0ceab15d7ca081d13610398b1`.
- Повтор карты каждые 2 м, материал и рисунок заданы произвольно для теста и не совпадают с утверждённой схемой укладки, которая не предоставлена.

## Техническая проверка

Khronos glTF Validator: для исходного GLB сцены 0 ошибок; для загруженного GLB растения 0 ошибок и 4 предупреждения об отсутствии заранее сохранённых tangent-векторов (касательные могут рассчитываться рендерером по-разному). Отдельный Blender-файл содержит упакованные текстуры. Это не проверка проектного соответствия или совместимости со всеми браузерами.
