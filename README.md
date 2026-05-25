# Підготовка до ЄВІ з англійської — матеріали для викладача

Усі матеріали зібрані в двох папках:

| Папка | Зміст |
|-------|--------|
| [markdown/](markdown/) | 44 файли Markdown (редагування, Git) |
| [pdf/](pdf/) | PDF-версії тих самих файлів (друк, надсилання студенту) |

## Швидкий старт

1. [markdown/README.md](markdown/README.md) — навігація по курсу
2. [markdown/00-teachers-guide.md](markdown/00-teachers-guide.md) — посібник викладача
3. [markdown/day-01/lesson-plan.md](markdown/day-01/lesson-plan.md) — День 1

## Оновлення PDF

Після зміни `.md` файлів:

```bash
python3 evi-prep/scripts/convert-md-to-pdf.py
```

## Структура

```
evi-prep/
├── README.md          ← цей файл
├── markdown/          ← усі .md
├── pdf/               ← усі .pdf
└── scripts/
    └── convert-md-to-pdf.py
```
