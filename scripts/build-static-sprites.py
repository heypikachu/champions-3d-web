#!/usr/bin/env python3
"""Gera as versões estáticas para o widget dexH!P sem alterar sprites animados."""
from pathlib import Path
from PIL import Image, ImageOps, ImageStat

SOURCE = Path("front")
DESTINATION = Path("front-static")
MAX_SIZE = (384, 384)

def choose_frame(image):
    """Escolhe uma pose visível; nunca salva uma animação no destino."""
    image.seek(0)
    first = image.convert("RGBA")
    if getattr(image, "n_frames", 1) < 2:
        return first
    # Normalmente o quadro inicial é a pose padrão. Em animações que começam
    # transparentes, procura o primeiro quadro inteiramente visível.
    alpha = first.getchannel("A")
    ratio = ImageStat.Stat(alpha).mean[0] / 255
    if ratio >= 0.025:
        return first
    best, best_ratio = first, ratio
    for n in range(1, min(getattr(image, "n_frames", 1), 20)):
        image.seek(n)
        frame = image.convert("RGBA")
        score = ImageStat.Stat(frame.getchannel("A")).mean[0] / 255
        if score > best_ratio:
            best, best_ratio = frame, score
        if score >= 0.025:
            break
    return best

def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    count = 0
    bytes_total = 0
    for path in sorted(SOURCE.glob("*.webp")):
        destination = DESTINATION / path.name
        try:
            with Image.open(path) as source:
                frame = choose_frame(source)
                frame = ImageOps.contain(frame, MAX_SIZE, Image.Resampling.LANCZOS)
                frame.save(destination, format="WEBP", quality=84, method=5, save_all=False, exact=True)
            with Image.open(destination) as result:
                if getattr(result, "n_frames", 1) != 1:
                    raise RuntimeError("O arquivo resultante ainda está animado")
            count += 1
            bytes_total += destination.stat().st_size
        except Exception as error:
            raise RuntimeError(f"Falha ao converter {path}: {error}") from error
    print(f"{count} sprites convertidos para WebP estático; {bytes_total/1024/1024:.1f} MiB no total.")
    if count == 0:
        raise RuntimeError("Não há sprites em front/")

if __name__ == "__main__":
    main()
